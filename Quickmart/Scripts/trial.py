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
    ("Fresh Produce", "https://www.quickmart.co.ke/fresh")
    # ("Personal Care", "https://www.quickmart.co.ke/personal-care"),
    # # ("Liquor", "https://www.quickmart.co.ke/liquor")
    # ("Household Items", "https://www.quickmart.co.ke/households"), 
    # ("Home Care", "https://www.quickmart.co.ke/homecare"),
    # ("Electronics", "https://www.quickmart.co.ke/electronics"),
    # ("Textile","https://www.quickmart.co.ke/textile")
    
]

OUTPUT_FILE = "quickmart_products_trial_06-2025.xlsx"  # Single output file for all categories
PAGE_LOAD_DELAY = 10  # Seconds to wait between page loads
MAX_PAGES = 150  # Safety limit to prevent infinite loops


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

# def scrape_products_page(driver, category_name):
#     """Extracts products from current page"""
#     products = []
#     try:
#         # Wait for products to be visible
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".products.productInfoJs"))
#         )
        
#         # Scroll to load lazy-loaded products
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)  # Wait for loading
        
#         soup = BeautifulSoup(driver.page_source, "html.parser")
        
#         for product in soup.select(".products.productInfoJs"):
#             try:
#                 name = product.select_one(".products-title").get_text(strip=True)
#                 price_elem = (product.select_one(".products-price-new") or 
#                             product.select_one(".products-price-old"))
#                 price = price_elem.get_text(strip=True) if price_elem else "N/A"
                
#                 products.append({
#                     "category": category_name,
#                     "name": name,
#                     "price": price
#                 })
#             except Exception as e:
#                 print(f"   ⚠ Error extracting product: {str(e)}")
#                 continue
                
#     except Exception as e:
#         print(f"   ❌ Error scraping page: {str(e)}")
    
#     return products

def handle_pagination(driver, category_name):
    """Handles pagination using the site's specific pagination structure"""
    all_products = []
    page = 1
    
    while page <= MAX_PAGES:
        print(f"   📄 Processing page {page}...")
        
        # Wait for products to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".products.productInfoJs"))
            )
            
            # Get products from current page
            current_products = scrape_products_page(driver, category_name)
            all_products.extend(current_products)
            print(f"   ✔ Found {len(current_products)} products on this page")
            
            # Find next button with specific structure
            next_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, 
                    "li.pagination-item.next button.pagination-link"
                ))
            )
            
            # Store current URL for verification
            current_url = driver.current_url
            
            # Execute the JavaScript click function directly
            page_number = page + 1
            driver.execute_script(f"goToProductListingSearchPage({page_number});")
            
            # Wait for URL or content change
            WebDriverWait(driver, 10).until(lambda d: d.current_url != current_url)
            time.sleep(2)  # Additional wait for content to load
            
            page += 1
            
        except TimeoutException:
            print("   ⏹ No more pages available")
            break
        except Exception as e:
            print(f"   ❌ Error during pagination: {str(e)}")
            break
    
    return all_products

# def handle_pagination(driver, category_name):
#     """Handles pagination for a single category"""
#     all_products = []
#     page = 1
#     last_page_products = 0
    
#     while page <= MAX_PAGES:
#         print(f"   📄 Processing page {page}...")
        
#         # Scrape current page
#         current_products = scrape_products_page(driver, category_name)
#         all_products.extend(current_products)
#         print(f"   ✔ Found {len(current_products)} products on this page")
        
#         # Check for duplicate content
#         if len(current_products) == last_page_products and page > 1:
#             print("   ⚠ Duplicate content detected, stopping pagination")
#             break
            
#         last_page_products = len(current_products)
        
#         # Try to go to next page
#         try:
#             next_button = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "a.page-link[rel='next']"))
#             )
#             if not next_button.is_enabled():
#                 print("   ⏹ Next button is disabled")
#                 break
                
#             driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
#             time.sleep(1)  # Brief pause for scrolling
#             next_button.click()
            
#             # Wait for new products to load
#             WebDriverWait(driver, 10).until(
#                 EC.staleness_of(driver.find_element(By.CSS_SELECTOR, ".products.productInfoJs"))
#             )
#             time.sleep(2)  # Additional wait for products to render
#             page += 1
            
#         except TimeoutException:
#             print("   ⏹ No more pages (next button not found or page didn't change)")
#             break
#         except Exception as e:
#             print(f"   ❌ Error navigating to next page: {str(e)}")
#             break
    
#     return all_products

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

def main():
    """Main execution with improved flow control"""
    driver = setup_driver()
    all_products = []
    
    try:
        # Initial setup
        driver.get(MANUAL_CATEGORIES[0][1])
        if accept_store_modal(driver):
            time.sleep(3)
        
        # Process each category
        for category_name, category_url in MANUAL_CATEGORIES:
            products = scrape_category(driver, category_name, category_url)
            all_products.extend(products)
            print(f"✅ Completed category {category_name} with {len(products)} products")
            time.sleep(2)
            
    except Exception as e:
        print(f"❌ Main execution error: {str(e)}")
    finally:
        driver.quit()
        
    # Save results
    if all_products:
        df = pd.DataFrame(all_products)
        df.to_excel(OUTPUT_FILE, index=False)
        print(f"\n✅ Saved {len(all_products)} products to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()