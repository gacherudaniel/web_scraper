from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

# ======================
# CONFIGURATION
# ======================
MANUAL_CATEGORIES = [
    ("Landing_Page", "https://www.quickmart.co.ke/foods"),
    ("Liquor", "https://www.quickmart.co.ke/liquor")
]

OUTPUT_FILE = "quickmart_products.xlsx"
PAGE_LOAD_DELAY = 3
MAX_PAGES = 40
DEBUG_SCREENSHOTS = True  # Set to True to save screenshots when errors occur
SCREENSHOT_DIR = "debug_screenshots"

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
# UTILITY FUNCTIONS
# ======================
def save_screenshot(driver, name):
    if not DEBUG_SCREENSHOTS:
        return
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SCREENSHOT_DIR, f"{timestamp}_{name}.png")
    driver.save_screenshot(path)
    print(f"📸 Saved screenshot to {path}")

# ======================
# MODAL HANDLING FUNCTIONS
# ======================
def accept_store_modal(driver):
    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "shopPopupJs")))
        
        continue_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]")))
        
        driver.execute_script("arguments[0].click();", continue_btn)
        print("✅ Store selection confirmed")
        
        WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "shopPopupJs")))
        
        time.sleep(2)
        return True
    except Exception as e:
        print(f"❌ Failed to accept store modal: {str(e)}")
        save_screenshot(driver, "store_modal_fail")
        return False

def handle_age_verification(driver):
    """Enhanced age verification handling with retries and better debugging"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Ensure no other modals are blocking
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.ID, "shopPopupJs")))
            
            # Check for age verification modal
            try:
                yes_button = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(@onclick, 'catConsent') and contains(., 'Yes')]")))
                
                print("🔍 Age verification modal detected")
                save_screenshot(driver, f"age_modal_attempt_{attempt+1}")
                
                # Scroll to button
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", yes_button)
                time.sleep(1)
                
                # Click using JavaScript
                driver.execute_script("arguments[0].click();", yes_button)
                print("✅ Clicked 'Yes' on age verification")
                
                # Verify modal disappeared
                WebDriverWait(driver, 5).until(
                    EC.invisibility_of_element_located((By.XPATH, "//button[contains(@onclick, 'catConsent')]")))
                
                return True
                
            except TimeoutException:
                print("ℹ️ No age verification modal found - proceeding")
                return True
                
        except Exception as e:
            print(f"⚠️ Age verification attempt {attempt+1} failed: {str(e)}")
            save_screenshot(driver, f"age_verify_fail_{attempt+1}")
            if attempt < max_retries - 1:
                print("🔄 Retrying...")
                time.sleep(2)
                driver.refresh()
                time.sleep(3)
            else:
                print("❌ Max retries reached for age verification")
                return False

# ======================
# SCRAPING FUNCTIONS
# ======================
def scrape_products_page(driver, category_name):
    """Extracts products from current page with better error handling"""
    products = []
    try:
        # Scroll to load lazy-loaded products
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Verify products are loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".products.productInfoJs")))
        
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
                
    except Exception as e:
        print(f"❌ Error scraping page: {str(e)}")
        save_screenshot(driver, "scrape_page_error")
        
    return products

def scrape_category(driver, category_name, category_url):
    """Enhanced category scraper with better error recovery"""
    print(f"\n🔍 Scraping category: {category_name}")
    try:
        driver.get(category_url)
        time.sleep(PAGE_LOAD_DELAY)
        
        if not handle_age_verification(driver):
            print("   ⚠️ Age verification failed - trying to continue anyway")
            # Continue scraping even if age verification failed
        
        all_products = []
        page = 1
        
        while page <= MAX_PAGES:
            print(f"   📄 Processing page {page}...")
            
            # Scrape current page
            page_products = scrape_products_page(driver, category_name)
            if not page_products:
                print("   ❌ No products found - possible page load issue")
                save_screenshot(driver, f"no_products_page_{page}")
                break
                
            all_products.extend(page_products)
            print(f"   ✔ Found {len(page_products)} products on this page")
            
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
                save_screenshot(driver, f"pagination_error_page_{page}")
                break
        
        return all_products
        
    except Exception as e:
        print(f"❌ Category scraping failed: {str(e)}")
        save_screenshot(driver, f"category_fail_{category_name}")
        return []

# ======================
# MAIN EXECUTION
# ======================
def main():
    driver = setup_driver()
    
    try:
        # Open site and accept store modal
        driver.get("https://www.quickmart.co.ke")
        if not accept_store_modal(driver):
            print("❌ Cannot proceed without store selection")
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
        save_screenshot(driver, "main_error")
    finally:
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    main()