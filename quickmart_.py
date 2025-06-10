from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import pandas as pd

# Step 1: Set up browser
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Step 2: Open site
driver.get("https://qsoko-test.quickmart.co.ke")

# Step 3: Select store
try:
    # Wait for modal to be visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "shopPopupJs"))
    )

    # Wait for the "Continue" button to be clickable
    continue_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
    )

    continue_btn.click()
    print("✅ Store confirmed by clicking 'Continue'")

    # Wait a bit for the site to finish loading
    time.sleep(2)

except Exception as e:
    print("❌ Error clicking 'Continue':", e)
    driver.quit()
    exit()

# After that, collect category links
categories = [
    ("foods", "https://www.quickmart.co.ke/foods")
    
    # Add more categories as needed
]
print(f"\n✅ Found {len(categories)} categories")


def scrape_current_page(driver, products, category_name=""):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_cards = soup.select(".products.productInfoJs")
    
    for product in product_cards:
        title = product.select_one(".products-title")
        price = product.select_one(".products-price-new") or product.select_one(".products-price-old")
        if title:
            name = title.get_text(strip=True)
            product_price = price.get_text(strip=True) if price else "No price"
            products.append({
                "Category": category_name,
                "Product Name": name, 
                "Price": product_price
            })

# Step 3: Select store (already handled above)


products = []

for cat_name, cat_url in categories:
    print(f"\n🔍 Scraping category: {cat_name} - {cat_url}")
    driver.get(cat_url)
    time.sleep(3)
    
    page = 1  # Initialize page counter
    scrape_current_page(driver, products)

    while True:
        print(f"   ↪ Page {page}")
        scrape_current_page(driver, products)

        # Try clicking the "next" button
        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'next')]/button"))
            )
            driver.execute_script("arguments[0].click();", next_btn)
            page += 1
            time.sleep(3)
        except TimeoutException:
            print("   ⚠️ No more pages in this category.")
            break



# Step 5: Convert to DataFrame and save to Excel
df = pd.DataFrame(products)
output_file = "foods.xlsx"
df.to_excel(output_file, index=False)
print(f"\n✅ Data saved to '{output_file}'")

# Step 6: Done
driver.quit()
