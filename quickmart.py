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

# # Step 4: Wait for search bar and search for "Fresh Dairy"
# try:
#     # Wait for the search input to be visible and clickable
#     search_input = WebDriverWait(driver, 15).until(
#         EC.element_to_be_clickable((By.ID, "keyword"))
#     )

#     driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
#     time.sleep(1)  # wait a moment after scrolling

#     search_input.clear()
#     search_input.send_keys("Fresh Dairy")
#     search_input.send_keys(Keys.RETURN)  # Triggers the form submission

#     print("✅ Searched for 'Fresh Dairy'")
#     time.sleep(3)

# except Exception as e:
#     print("❌ Error using search bar:", e)
#     with open("debug_search_page.html", "w", encoding="utf-8") as f:
#         f.write(driver.page_source)


# # Add this function to extract all category links
# def get_category_links(driver):
#     try:
#         # Step 1: Click "All Categories" button to open the menu
#         categories_btn = WebDriverWait(driver, 30).until(
#             EC.element_to_be_clickable((By.CSS_SELECTOR, ".categoriesMenuJs"))
#         )
#         driver.execute_script("arguments[0].click();", categories_btn)
#         print("✅ Clicked 'All Categories'")

#         # Step 2: Wait for offcanvas menu to appear
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.ID, "categories-menu"))
#         )
#         time.sleep(2)  # Wait extra time for animation/content

#         # Step 3: Scrape the category links inside the menu
#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         menu = soup.select_one("#categories-menu")
#         categories = []

#         if menu:
#             for a in menu.select("a"):
#                 name = a.get_text(strip=True)
#                 href = a.get("href")
#                 if href and "/category/" in href:
#                     full_url = "https://qsoko-test.quickmart.co.ke" + href
#                     categories.append((name, full_url))
#         else:
#             print("⚠️ Categories menu not found.")
#             with open("debug_categories_menu.html", "w", encoding="utf-8") as f:
#                 f.write(driver.page_source)

#         return categories

#     except TimeoutException:
#         print("❌ Timed out waiting for category menu.")
#         with open("debug_timeout_menu.html", "w", encoding="utf-8") as f:
#             f.write(driver.page_source)
#         return []

# 




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
# After that, collect category links
categories = [
    ("foods", "https://www.quickmart.co.ke/foods")
    
    # Add more categories as needed
]
print(f"\n✅ Found {len(categories)} categories")

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


# # Step 5: Paginated scraping
# products = []
# page = 1

# while True:
#     print(f"\n--- Scraping page {page} ---")
    
#     # Scroll to load products (if lazy loaded)
#     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#     time.sleep(2)  # Give time for JS to load more products
    
#     # Scrape this page
#     scrape_current_page(driver, products)

#     # Try clicking the "next" button
#     try:
#         next_btn = WebDriverWait(driver, 5).until(
#             EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'next')]/button"))
#         )
#         driver.execute_script("arguments[0].click();", next_btn)
#         page += 1
#         time.sleep(3)  # Wait for the new page to load
#     except TimeoutException:
#         print("⚠️ No more pages or failed to find next button.")
#         break



# Step 5.2: Convert to DataFrame and save to Excel
df = pd.DataFrame(products)
output_file = "foods.xlsx"
df.to_excel(output_file, index=False)
print(f"\n✅ Data saved to '{output_file}'")
# Step 6: Done
driver.quit()
