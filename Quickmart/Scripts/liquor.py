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
    ("Landing_Page", "https://www.quickmart.co.ke"),
    ("Liquor", "https://www.quickmart.co.ke/liquor")
]

OUTPUT_FILE = "quickmart_liquor_products_12-06-2025.xlsx"
PAGE_LOAD_DELAY = 3
MAX_PAGES = 40
DEBUG_SCREENSHOTS = True
SCREENSHOT_DIR = "debug_screenshots"

# ======================
# SETUP SELENIUM DRIVER
# ======================
def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
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
        # First try to find and close any popup that might be blocking
        try:
            WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ".modal-content")))
            print("ℹ️ Found a modal - attempting to handle")
        except:
            print("ℹ️ No initial modal found - proceeding")
            return True

        # Try to find and click the continue button
        try:
            continue_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]")))
            driver.execute_script("arguments[0].click();", continue_btn)
            print("✅ Clicked 'Continue' on store modal")
            time.sleep(2)
            return True
        except:
            print("⚠️ Couldn't find continue button - trying alternative approach")
            
        # If that fails, try to select a store directly
        try:
            store_select = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".store-selector")))
            store_select.click()
            time.sleep(1)
            
            first_store = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".store-list li:first-child")))
            first_store.click()
            time.sleep(1)
            
            confirm_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".confirm-store")))
            confirm_btn.click()
            print("✅ Selected first available store")
            time.sleep(2)
            return True
        except Exception as e:
            print(f"❌ Failed to select store: {str(e)}")
            save_screenshot(driver, "store_selection_fail")
            return False
            
    except Exception as e:
        print(f"❌ Store modal handling failed: {str(e)}")
        save_screenshot(driver, "store_modal_fail")
        return False

def handle_age_verification(driver):
    """Handle the age verification modal shown in the HTML you provided"""
    try:
        # Check for age verification modal
        modal = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".modal-content"))
        )
        
        # Check if it's the age verification modal
        if "Consent" in modal.text or "Disclaimer" in modal.text:
            print("🔞 Age verification modal detected")
            
            # Find and click the 'Yes' button
            yes_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@onclick, 'catConsent') and contains(., 'Yes')]"))
            )
            
            # Scroll to button and click with JavaScript
            driver.execute_script("arguments[0].scrollIntoView();", yes_button)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", yes_button)
            print("✅ Clicked 'Yes' on age verification")
            
            # Wait for modal to disappear
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, ".modal-content"))
            )
            time.sleep(1)
            return True
        else:
            print("ℹ️ Found a modal but not age verification - proceeding")
            return True
            
    except TimeoutException:
        print("ℹ️ No age verification modal found within timeout")
        return True
    except Exception as e:
        print(f"⚠️ Error handling age verification: {str(e)}")
        save_screenshot(driver, "age_verify_error")
        return False

# ======================
# MAIN SCRAPING FUNCTIONS
# ======================
# def scrape_products_page(driver, category_name):
    """Extracts products from current page"""
    products = []
    try:
        # Scroll to load lazy-loaded products
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find all product elements
        product_elements = soup.select(".products.productInfoJs")
        if not product_elements:
            print("⚠️ No products found on page")
            save_screenshot(driver, "no_products_found")
            return products
            
        for product in product_elements:
            try:
                name = product.select_one(".products-title").get_text(strip=True)
                
                # Handle price - try new price first, then old price
                price_elem = product.select_one(".products-price-new") or product.select_one(".products-price-old")
                price = price_elem.get_text(strip=True) if price_elem else "Price not found"
                
                products.append({
                    "Category": category_name,
                    "Product Name": name,
                    "Price": price
                })
            except Exception as e:
                print(f"⚠️ Error parsing a product: {str(e)}")
                continue
                
    except Exception as e:
        print(f"❌ Error scraping page: {str(e)}")
        save_screenshot(driver, "page_scrape_error")
        
    return products


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


def scrape_category(driver, category_name, category_url):
    """Scrape all pages of a category"""
    print(f"\n🌐 Starting category: {category_name}")
    
    try:
        # Navigate to category URL
        driver.get(category_url)
        time.sleep(PAGE_LOAD_DELAY)
        
        # Handle any modals
        if not handle_age_verification(driver):
            print("⚠️ Age verification may have failed - trying to continue anyway")
        
        all_products = []
        page_count = 1
        
        while page_count <= MAX_PAGES:
            print(f"   📖 Processing page {page_count}")
            
            # Scrape current page
            page_products = scrape_products_page(driver, category_name)
            all_products.extend(page_products)
            print(f"   ✔ Found {len(page_products)} products")
            
            # Try to go to next page
            try:
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "li.pagination-item.next > button"))
                )
                driver.execute_script("arguments[0].click();", next_button)
                page_count += 1
                time.sleep(PAGE_LOAD_DELAY)
            except (TimeoutException, NoSuchElementException):
                print("   ⏹ Reached last page")
                break
            except Exception as e:
                print(f"   ❌ Pagination error: {str(e)}")
                save_screenshot(driver, "pagination_error")
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
        # First visit homepage to set cookies/context
        print("🏠 Visiting homepage...")
        driver.get("https://www.quickmart.co.ke")
        time.sleep(3)
        
        # Handle store selection
        if not accept_store_modal(driver):
            print("⚠️ Store selection failed - trying to continue anyway")
        
        # Scrape all categories
        all_products = []
        for cat_name, cat_url in MANUAL_CATEGORIES:
            products = scrape_category(driver, cat_name, cat_url)
            all_products.extend(products)
            print(f"✅ Finished '{cat_name}' with {len(products)} products")
        
        # Save results
        if all_products:
            df = pd.DataFrame(all_products)
            df.to_excel(OUTPUT_FILE, index=False)
            print(f"\n🎉 Success! Saved {len(all_products)} products to {OUTPUT_FILE}")
        else:
            print("😢 No products were scraped")
            
    except Exception as e:
        print(f"💥 Critical error: {str(e)}")
        save_screenshot(driver, "main_error")
    finally:
        driver.quit()
        print("🌐 Browser closed")

if __name__ == "__main__":
    main()