from flask import Flask, render_template, request, send_file, redirect, url_for
import sqlite3
import subprocess
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

DB_PATH = "products.db"
ITEMS_PER_PAGE = 10  # Pagination limit

# ✅ Ensure DB exists
def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price REAL,
            rating TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ✅ Check and scrape if DB empty
def check_and_scrape():
    initialize_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM products")
    count = c.fetchone()[0]
    conn.close()
    if count == 0:
        run_scraper()

# ✅ Run scraper.py to update DB
def run_scraper():
    print("Running scraper...")
    subprocess.run(["python", "scraper.py"], check=True)

# ✅ Home Page with Filters, Sorting, Pagination
@app.route('/')
def index():
    check_and_scrape()

    query = request.args.get('q', '').strip()
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    rating = request.args.get('rating')
    sort = request.args.get('sort', 'asc')
    page = int(request.args.get('page', 1))

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    sql = "SELECT * FROM products WHERE 1=1"
    params = []

    if query:
        sql += " AND title LIKE ?"
        params.append(f"%{query}%")
    if min_price:
        sql += " AND price >= ?"
        params.append(float(min_price))
    if max_price:
        sql += " AND price <= ?"
        params.append(float(max_price))
    if rating:
        sql += " AND rating = ?"
        params.append(rating)

    # Count total for pagination
    c.execute(sql, params)
    total_items = len(c.fetchall())

    # Sorting
    if sort == "asc":
        sql += " ORDER BY price ASC"
    else:
        sql += " ORDER BY price DESC"

    # Pagination
    offset = (page - 1) * ITEMS_PER_PAGE
    sql += f" LIMIT {ITEMS_PER_PAGE} OFFSET {offset}"

    c.execute(sql, params)
    rows = c.fetchall()
    conn.close()

    total_pages = (total_items // ITEMS_PER_PAGE) + (1 if total_items % ITEMS_PER_PAGE > 0 else 0)

    # ✅ Include description field
    data = [{"Title": r[1], "Price": r[2], "Rating": r[3], "Description": r[4]} for r in rows]

    return render_template('index.html',
                           data=data, query=query,
                           min_price=min_price, max_price=max_price, rating=rating,
                           sort=sort, page=page, total_pages=total_pages)

# ✅ Analytics Page with Summary Stats + Extra Charts
@app.route('/analytics')
def analytics():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()

    stats = {
        "total_books": len(df),
        "avg_price": round(df['price'].mean(), 2) if len(df) > 0 else 0,
        "top_rating": df['rating'].mode()[0] if not df['rating'].mode().empty else "N/A"
    }

    if not df.empty:
        # Price distribution
        plt.figure(figsize=(6, 4))
        df['price'].plot(kind='hist', bins=10, color='skyblue', edgecolor='black')
        plt.title('Price Distribution')
        plt.xlabel('Price (£)')
        plt.savefig('static/price_chart.png')
        plt.close()

        # Rating distribution
        plt.figure(figsize=(6, 4))
        df['rating'].value_counts().plot(kind='bar', color='orange')
        plt.title('Rating Distribution')
        plt.xlabel('Rating')
        plt.ylabel('Count')
        plt.savefig('static/rating_chart.png')
        plt.close()

        # Average Price by Rating
        plt.figure(figsize=(6, 4))
        df.groupby('rating')['price'].mean().sort_index().plot(kind='bar', color='green')
        plt.title('Average Price by Rating')
        plt.ylabel('Avg Price (£)')
        plt.savefig('static/price_vs_rating.png')
        plt.close()

        # Top 10 Expensive Books
        plt.figure(figsize=(8, 6))
        top_books = df.sort_values(by='price', ascending=False).head(10)
        plt.barh(top_books['title'], top_books['price'], color='purple')
        plt.gca().invert_yaxis()
        plt.title('Top 10 Expensive Books')
        plt.xlabel('Price (£)')
        plt.tight_layout()
        plt.savefig('static/top_books.png')
        plt.close()

    return render_template('analytics.html', stats=stats)

# ✅ Refresh Data
@app.route('/refresh')
def refresh_data():
    run_scraper()
    return redirect(url_for('index'))

# ✅ Download CSV
@app.route('/download')
def download_csv():
    query = request.args.get('q', '').strip()
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    rating = request.args.get('rating')
    sort = request.args.get('sort', 'asc')

    conn = sqlite3.connect(DB_PATH)
    sql = "SELECT * FROM products WHERE 1=1"
    params = []

    if query:
        sql += " AND title LIKE ?"
        params.append(f"%{query}%")
    if min_price:
        sql += " AND price >= ?"
        params.append(float(min_price))
    if max_price:
        sql += " AND price <= ?"
        params.append(float(max_price))
    if rating:
        sql += " AND rating = ?"
        params.append(rating)

    if sort == "asc":
        sql += " ORDER BY price ASC"
    else:
        sql += " ORDER BY price DESC"

    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()

    filename = "filtered_products.csv"
    df.to_csv(filename, index=False)
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    initialize_db()
    app.run(debug=True)
