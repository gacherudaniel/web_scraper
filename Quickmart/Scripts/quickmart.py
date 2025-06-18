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

OUTPUT_FILE = "Quickmart/Quickmart Data/Raw Data/quickmart_products_18-06-2025.xlsx"  # Single output file for all categories
PAGE_LOAD_DELAY = 3  # Seconds to wait between page loads
MAX_PAGES = 150  # Safety limit to prevent infinite loops

# ======================
# SETUP SELENIUM DRIVER
# ======================

def accept_store_modal(driver, location="Nairobi"):
    """Handle the location modal with improved reliability"""
    try:
        # Wait for modal and input field
        modal = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "modal-content"))
        )
        
        if not modal.is_displayed():
            return True
            
        input_box = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.ID, "location_fld_popup"))
        )
        
        # Clear and enter location
        input_box.clear()
        input_box.send_keys(location)
        time.sleep(2)  # Wait for suggestions
        
        # Try clicking first suggestion
        try:
            suggestions = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".pac-item"))
            )
            if suggestions:
                suggestions[0].click()
                print(f"✅ Selected location: {location}")
                time.sleep(2)
                return True
        except:
            # If no suggestions, try Enter key
            input_box.send_keys(Keys.ENTER)
            time.sleep(2)
            print(f"✅ Entered location: {location}")
            return True
            
    except Exception as e:
        print(f"❌ Modal handling error: {str(e)}")
        return False
    
def setup_driver():
    """Setup Chrome driver with enhanced options"""
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Network.setCacheDisabled", {"cacheDisabled": True})
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

    


def handle_pagination(driver, category_name):
    """Handles pagination using the site's JavaScript pagination function"""
    all_products = []
    page = 1
    
    while page <= MAX_PAGES:
        print(f"   📄 Processing page {page}...")
        
        try:
            # Wait for products to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".products.productInfoJs"))
            )
            
            # Get products from current page
            current_products = scrape_products_page(driver, category_name)
            all_products.extend(current_products)
            print(f"   ✔ Found {len(current_products)} products on this page")
            
            # Check if next page exists
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    "li.pagination-item.next button.pagination-link"
                ))
            )
            
            # Store current URL
            current_url = driver.current_url
            
            # Execute the JavaScript pagination function directly
            next_page = page + 1
            driver.execute_script(f"goToProductListingSearchPage({next_page});")
            
            # Wait for page change
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.current_url != current_url
                )
                time.sleep(2)  # Wait for content to load
                page += 1
            except TimeoutException:
                print("   ⏹ Last page reached")
                break
                
        except TimeoutException:
            print("   ⏹ No more pages available")
            break
        except Exception as e:
            print(f"   ❌ Error during pagination: {str(e)}")
            break
    
    return all_products

def scrape_products_page(driver, category_name):
    """Extracts products from current page"""
    products = []
    
    try:
        # Get page source after all products are loaded
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find all product elements
        product_elements = soup.select(".products.productInfoJs")
        
        for product in product_elements:
            try:
                name = product.select_one(".products-title").get_text(strip=True)
                price_elem = (product.select_one(".products-price-new") or 
                            product.select_one(".products-price-old"))
                price = price_elem.get_text(strip=True) if price_elem else "N/A"
                
                products.append({
                    "category": category_name,
                    "name": name,
                    "price": price,
                    "url": driver.current_url  # Add page URL for debugging
                })
            except Exception as e:
                print(f"   ⚠ Error extracting product: {str(e)}")
                continue
                
    except Exception as e:
        print(f"   ❌ Error scraping page: {str(e)}")
    
    return products

def scrape_category(driver, category_name, category_url):
    """Scrape category with improved modal and pagination handling"""
    print(f"\n🔍 Scraping category: {category_name}")
    
    try:
        driver.get(category_url)

        time.sleep(3)
        
        # Handle modal if present
        if accept_store_modal(driver):
            # Wait for page to load after modal
            time.sleep(3)
            driver.refresh()
            time.sleep(3)
        
        # Ensure products are loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".products.productInfoJs"))
        )
        
        return handle_pagination(driver, category_name)
        
    except Exception as e:
        print(f"❌ Error in category {category_name}: {str(e)}")
        return []

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
        for cat_name, category_url in MANUAL_CATEGORIES:
            category_products = scrape_category(driver, cat_name, category_url)
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