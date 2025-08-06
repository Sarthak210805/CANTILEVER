import requests
from bs4 import BeautifulSoup
import sqlite3
import time

BASE_URL = "https://books.toscrape.com/catalogue/"
DB_PATH = "products.db"

def scrape_books():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS products")
    c.execute('''CREATE TABLE products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    price REAL,
                    rating TEXT,
                    description TEXT
                )''')

    data_to_insert = []
    total_books = 0

    for page in range(1, 6):  # First 5 pages
        print(f"📄 Scraping page {page}...")
        url = f"{BASE_URL}page-{page}.html"

        try:
            response = requests.get(url, timeout=10)
            response.encoding = 'utf-8'
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch page {page}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        books = soup.select('.product_pod')
        print(f"✅ Found {len(books)} books on page {page}")

        for idx, book in enumerate(books, start=1):
            title = book.h3.a.get('title', 'No title')

            # Price cleaning
            price_text = book.select_one('.price_color').get_text(strip=True)
            price = float(price_text.replace('Â', '').replace('£', ''))

            # Rating
            rating = book.p.get('class')[1] if len(book.p.get('class')) > 1 else 'No rating'

            # Detail page for description
            detail_href = book.h3.a['href'].replace('../../../', '')
            detail_url = BASE_URL + detail_href

            try:
                detail_response = requests.get(detail_url, timeout=10)
                detail_response.encoding = 'utf-8'
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
                desc_tag = detail_soup.select_one('#product_description ~ p')
                description = desc_tag.get_text(strip=True) if desc_tag else "No description available"
            except requests.exceptions.RequestException as e:
                print(f"❌ Failed to fetch detail page for {title}: {e}")
                description = "No description available"

            data_to_insert.append((title, price, rating, description))
            total_books += 1

            # Log progress
            print(f"   → [{idx}] {title} (£{price}, {rating})")

            # Short delay to avoid overwhelming the server
            time.sleep(0.3)

    # Insert into database
    c.executemany("INSERT INTO products (title, price, rating, description) VALUES (?, ?, ?, ?)", data_to_insert)
    conn.commit()
    conn.close()

    print(f"\n✅ Completed: {total_books} books scraped and saved to SQLite database.")

if __name__ == "__main__":
    scrape_books()
