# 📚 Web Scraper & Analytics Dashboard

A **Flask-based web application** that scrapes book data from [Books to Scrape](https://books.toscrape.com/), stores it in a database, and provides:  
✔ **Search, Filter, Sort & Pagination**  
✔ **Download as CSV**  
✔ **Analytics Dashboard with Charts (Price & Rating)**  

---

## 🚀 Features
- **Scraping**: Fetches book title, price, rating, and description.
- **Filters & Sorting**: Search by name, filter by price, sort by ascending/descending.
- **Pagination**: Displays 10 items per page.
- **Analytics Page**:
  - Price distribution (Histogram)
  - Rating distribution (Bar chart)
  - Summary stats (Total products, Avg price, Top rating)
- **Download**: Export filtered data as CSV.

---

## 🛠 Tech Stack
- **Backend**: Flask (Python)
- **Scraping**: BeautifulSoup, Requests
- **Database**: SQLite (Local)
- **Charts**: Matplotlib
- **Frontend**: HTML, Bootstrap 5
- **Deployment**: Render

---

## ✅ Installation (Run Locally)
1. **Clone the repository**
   ```bash
   git clone https://github.com/Sarthak210805/CANTILEVER.git
   cd CANTILEVER
