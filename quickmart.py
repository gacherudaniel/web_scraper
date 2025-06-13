from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import time

# ======================
# CONFIGURATION
# ======================
MANUAL_CATEGORIES = [
    ("Landing_Page", "https://www.quickmart.co.ke"),

    ("Foods", "https://www.quickmart.co.ke/foods"),
    ("Fresh Produce", "https://www.quickmart.co.ke/fresh"),
    ("Personal Care", "https://www.quickmart.co.ke/personal-care"),
    # ("Liquor", "https://www.quickmart.co.ke/liquor")
    ("Household Items", "https://www.quickmart.co.ke/households"), 
    ("Home Care", "https://www.quickmart.co.ke/homecare"),
    ("Electronics", "https://www.quickmart.co.ke/electronics"),
    ("Textile","https://www.quickmart.co.ke/textile")
    
]

OUTPUT_FILE = "quickmart_products_12-06-2025.xlsx"  # Single output file for all categories
PAGE_LOAD_DELAY = 3  # Seconds to wait between page loads
MAX_PAGES = 150  # Safety limit to prevent infinite loops

# ======================
# SETUP SELENIUM DRIVER
# ======================
def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)
    return driver

# ======================
# SCRAPING FUNCTIONS
# ======================
def accept_store_modal(driver):
    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "shopPopupJs")))
        continue_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]")))
        continue_btn.click()
        print("✅ Store selection confirmed")
        time.sleep(3)  # Let page settle
        return True
    except Exception as e:
        print(f"❌ Failed to accept store modal: {str(e)}")
        return False

    
def scrape_products_page(driver, category_name):
    """Extracts products from current page"""
    products = []
    # Scroll to load lazy-loaded products
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)  # Wait for loading
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    for product in soup.select(".products.productInfoJs"):
        try:
            name = product.select_one(".products-title").get_text(strip=True)
            price_elem = (product.select_one(".products-price-new") or 
                         product.select_one(".products-price-old"))
            price = price_elem.get_text(strip=True) if price_elem else "Price not found"
            
            products.append({
                "Category": category_name,
                "Product Name": name,
                "Price": price
            })
        except Exception as e:
            print(f"⚠️ Error parsing product: {str(e)}")
            continue
    
    return products

def handle_pagination(driver, category_name):
    """Handles pagination for a single category"""
    all_products = []
    page = 1
    last_page_products = 0
    
    while page <= MAX_PAGES:
        print(f"   📄 Processing page {page}...")
        
        # Scrape current page
        current_products = scrape_products_page(driver, category_name)
        all_products.extend(current_products)
        print(f"   ✔ Found {len(current_products)} products on this page")
        
        # Check if we're getting duplicate content (stuck on same page)
        if len(current_products) == last_page_products and page > 1:
            print("   ⚠️ Possible duplicate page content detected")
            break
        last_page_products = len(current_products)
        
        # Try to find and click next page button
        try:
            next_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "li.next > button")))
            
            # Check if button is disabled (last page)
            if "disabled" in next_btn.get_attribute("class"):
                print("   ⏹ Reached last page (disabled button)")
                break
                
            # Scroll to button and click
            driver.execute_script("arguments[0].scrollIntoView();", next_btn)
            time.sleep(1)
            next_btn.click()
            time.sleep(PAGE_LOAD_DELAY)
            page += 1
            
            # Wait for new products to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".products.productInfoJs")))
            
        except TimeoutException:
            print("   ⏹ No more pages (next button not found)")
            break
        except Exception as e:
            print(f"   ❌ Pagination error: {str(e)}")
            break
    
    return all_products


def scrape_category(driver, category_name, category_url):
    """Handles pagination for a single category"""
    print(f"\n🔍 Scraping category: {category_name}")
    driver.get(category_url)
    time.sleep(PAGE_LOAD_DELAY)

    
    all_products = []
    page = 1
    
    while page <= MAX_PAGES:
        print(f"   📄 Processing page {page}...")
        
        # Scrape current page
        try:
            page_products = scrape_products_page(driver, category_name)
            all_products.extend(page_products)
            print(f"   ✔ Found {len(page_products)} products on this page")
        except Exception as e:
            print(f"   ❌ Page scraping failed: {str(e)}")
        
        # Try to go to next page
        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'next')]/button")))
            driver.execute_script("arguments[0].click();", next_btn)
            page += 1
            time.sleep(PAGE_LOAD_DELAY)
        except (TimeoutException, NoSuchElementException):
            print("   ⏹ Reached last page")
            break
        except Exception as e:
            print(f"   ❌ Pagination error: {str(e)}")
            break
    
    return all_products

# ======================
# MAIN EXECUTION
# ======================
def main():
    driver = setup_driver()
    
    try:
        # Open site and accept store modal
        driver.get("https://qsoko-test.quickmart.co.ke")
        if not accept_store_modal(driver):
            return
        
        # Scrape all categories
        all_products = []
        for cat_name, cat_url in MANUAL_CATEGORIES:
            category_products = scrape_category(driver, cat_name, cat_url)
            all_products.extend(category_products)
            print(f"✅ Finished '{cat_name}' with {len(category_products)} products")
        
        # Save results
        if all_products:
            df = pd.DataFrame(all_products)
            df.to_excel(OUTPUT_FILE, index=False)
            print(f"\n🎉 Success! Saved {len(all_products)} products to '{OUTPUT_FILE}'")
        else:
            print("⚠️ No products were scraped")
            
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")
    finally:
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    main()