# 🛒 Quickmart Web Scraper (Selenium + BeautifulSoup)

This Python project scrapes product data from the [Quickmart Kenya Test Website](https://qsoko-test.quickmart.co.ke), including product names and prices, and saves the results to an Excel file.

It uses:
- **Selenium WebDriver** for interacting with the dynamic website
- **BeautifulSoup** for HTML parsing
- **Pandas** for data storage and export

---

## 📦 Features

- Automatically selects a store to proceed past the popup
- Opens the "All Categories" menu and extracts category URLs
- Scrapes all product listings from each category, including paginated pages
- Stores product names and prices (with optional category name)
- Saves results in an Excel file: `all_products.xlsx`
- Includes debug support (HTML snapshots on error)

---

## 🧰 Requirements

Install the required Python libraries:

```bash
pip install selenium beautifulsoup4 pandas openpyxl
