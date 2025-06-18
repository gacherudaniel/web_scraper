from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import random

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # Uncomment for headless mode
    # options.add_argument('--headless')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_single_page(driver):
    properties = []
    
    try:
        # Wait for properties to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "pgp-property-content"))
        )
        
        # Get all property listings
        listings = driver.find_elements(By.CLASS_NAME, "pgp-property-content")
        
        for listing in listings:
            try:
                property_data = {}
                
                # Extract title
                title = listing.find_element(By.CLASS_NAME, "pgp-description")
                property_data['title'] = title.text if title else None
                
                # Extract price
                price = listing.find_element(By.CLASS_NAME, "pgp-price")
                property_data['price'] = price.text if price else None
                
                # Extract description
                description = listing.find_element(By.CLASS_NAME, "pgp-details")
                property_data['description'] = description.get_attribute('textContent').strip() if description else None
                
                # Extract features
                features = listing.find_elements(By.CSS_SELECTOR, ".pgp-features > div")
                for feature in features:
                    text = feature.text.strip()
                    if "bedroom" in feature.get_attribute('innerHTML').lower():
                        property_data['bedrooms'] = text
                    elif "bath" in feature.get_attribute('innerHTML').lower():
                        property_data['bathrooms'] = text
                    elif "parking" in feature.get_attribute('innerHTML').lower():
                        property_data['parking'] = text
                
                # Extract property URL
                link = listing.find_element(By.TAG_NAME, "a")
                if link:
                    href = link.get_attribute('href')
                    property_data['url'] = f"https://www.pamgolding.co.za{href}" if href.startswith('/') else href
                
                properties.append(property_data)
                
            except Exception as e:
                print(f"Error processing a listing: {e}")
                continue
                
    except Exception as e:
        print(f"Error scraping page: {e}")
    
    return properties

def handle_pagination(driver):
    try:
        # Wait for pagination to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".pagination"))
        )
        
        # Try to find the last page number
        page_links = driver.find_elements(By.CSS_SELECTOR, ".pagination a.pageNumber")
        if page_links:
            last_page = page_links[-1].get_attribute('data-pagenumber')
            return int(last_page)
        
        # Alternative method: Check if next button exists
        next_button = driver.find_elements(By.CSS_SELECTOR, ".pagination .next")
        if next_button:
            # If next button exists but we can't find page numbers, we'll use incremental navigation
            return None
        
    except Exception as e:
        print(f"Couldn't determine total pages: {e}")
        return 1
    
    return 1

def scrape_all_pages(base_url, max_pages=40):
    driver = setup_driver()
    all_properties = []
    
    try:
        driver.get(base_url)
        time.sleep(3)  # Initial load wait
        
        # Get total pages if possible
        total_pages = handle_pagination(driver)
        
        if total_pages is None:
            # Use incremental navigation if we couldn't determine total pages
            print("Using incremental page navigation")
            current_page = 1
            while True:
                print(f"Scraping page {current_page}")
                page_properties = scrape_single_page(driver)
                all_properties.extend(page_properties)
                
                # Try to find and click next button
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, ".pagination .next")
                    if "disabled" in next_button.get_attribute("class"):
                        break
                    next_button.click()
                    time.sleep(random.uniform(2, 4))
                    current_page += 1
                    
                    if current_page > max_pages:
                        print(f"Reached maximum page limit of {max_pages}")
                        break
                except:
                    print("No more pages found")
                    break
        else:
            print(f"Found {total_pages} pages to scrape")
            for page_num in range(1, min(total_pages, max_pages) + 1):
                if page_num > 1:
                    page_url = f"{base_url}/page{page_num}"
                    driver.get(page_url)
                    time.sleep(random.uniform(2, 4))
                
                print(f"Scraping page {page_num} of {total_pages}")
                page_properties = scrape_single_page(driver)
                all_properties.extend(page_properties)
                time.sleep(random.uniform(1, 3))
                
    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()
    
    return all_properties

def main():
    base_url = "https://www.pamgolding.co.za/property-search/apartments-to-rent-kenya/119"
    
    print(f"Starting scraping of Pam Golding properties from: {base_url}")
    properties = scrape_all_pages(base_url, max_pages=40)  # Set max_pages as needed
    
    if properties:
        df = pd.DataFrame(properties)
        
        # Save to CSV
        csv_file = 'pam_golding_properties_all_pages.csv'
        df.to_csv(csv_file, index=False)
        
        print(f"\nSuccessfully scraped {len(properties)} properties from all pages.")
        print(f"Data saved to {csv_file}")
        
        # Print summary
        print("\nSample data:")
        print(df.head())
    else:
        print("No properties were scraped.")

if __name__ == "__main__":
    main()