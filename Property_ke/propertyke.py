from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from urllib.parse import urlparse, urljoin

def configure_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def is_url_allowed(url):
    """Check if URL is allowed by robots.txt"""
    parsed = urlparse(url)
    disallowed_paths = [
        '/admin', '/backend', '/property-search',
        '/links', '/property-for-rent?search=',
        '/property-for-rent?max_price=',
        '/property-for-rent?min_price=',
        '/property-for-rent?sort=',
        '/property-for-rent?order='
    ]
    return not any(parsed.path.startswith(path) for path in disallowed_paths)

# [Previous code remains the same until...]

def extract_property_features(features_container):
    """Extract bedroom, bathroom, and toilet counts from features container"""
    features = {
        'bedrooms': 'N/A',
        'bathrooms': 'N/A',
        'toilets': 'N/A'
    }
    
    if not features_container:
        return features
    
    # Extract all feature spans
    for span in features_container.find_all('span'):
        text = span.get_text(strip=True)
        img = span.find('img')
        
        if img:
            alt = img.get('alt', '').lower()
            if 'bed' in alt:
                features['bedrooms'] = text.split()[0]  # Extract just the number
            elif 'bath' in alt:
                features['bathrooms'] = text.split()[0]  # Extract just the number
            elif 'toilet' in alt:
                features['toilets'] = text.split()[0]  # Extract just the number
    
    return features

# def extract_property_data(listing, base_url):
#     """Extract detailed data from a single property listing"""
#     property_data = {}
    
    # [Keep all your existing extraction code...]
    
    # # Property features - ADD THIS SECTION:
    # features_container = listing.find('div', class_='fur-areea')
    # features = extract_property_features(features_container)
    # property_data.update(features)
    
    # [Rest of your existing extract_property_data function...]

# [Rest of your script remains the same...]

# def extract_property_data(listing, base_url):
    """Extract detailed data from a single property listing"""
    property_data = {}
    
    # Title and URL
    title_element = listing.find('h2', class_='listings-property-title')
    property_data['title'] = title_element.get_text(strip=True) if title_element else 'N/A'
    
    link_element = listing.find('a', href=True)
    if link_element and is_url_allowed(link_element['href']):
        property_data['url'] = urljoin(base_url, link_element['href'])
    else:
        property_data['url'] = 'N/A'
    
    # Location
    location_element = listing.find('h4')
    property_data['location'] = location_element.get_text(strip=True).replace('\n', ' ') if location_element else 'N/A'
    
    # Property Type
    type_element = listing.find('h3', class_='listings-property-title2')
    property_data['property_type'] = type_element.get_text(strip=True) if type_element else 'N/A'
    
    # Price details
    price_container = listing.find('div', class_='n50')
    if price_container:
        price_element = price_container.find('h3', class_='listings-price')
        if price_element:
            currency = price_element.find('span', {'itemprop': 'priceCurrency'})
            amount = price_element.find('span', {'itemprop': 'price'})
            property_data['price_currency'] = currency.get_text(strip=True) if currency else 'N/A'
            property_data['price_amount'] = amount.get_text(strip=True) if amount else 'N/A'
        
        premium_element = price_container.find('h4')
        property_data['premium_status'] = premium_element.get_text(strip=True) if premium_element else 'N/A'
    
    # Date information
    date_element = listing.find('h5')
    if date_element:
        date_text = date_element.get_text(strip=True)
        property_data['dates_info'] = ' '.join(date_text.split())
    else:
        property_data['dates_info'] = 'N/A'
    
    # PID (Property ID)
    pid_element = listing.find('h2', string=lambda text: text and 'PID:' in text)
    property_data['pid'] = pid_element.get_text(strip=True).replace('PID:', '').strip() if pid_element else 'N/A'
    
    # Serviced status
    serviced_element = listing.find('div', class_='furnished-btn')
    property_data['serviced'] = serviced_element.get_text(strip=True) if serviced_element else 'No'
    
    # Description
    desc_element = listing.find('p', class_='d-none d-sm-block')
    property_data['description'] = desc_element.get_text(" ", strip=True) if desc_element else 'N/A'
    
    # # Property features
    # features_container = listing.find('div', class_='fur-areea')
    # if features_container:
    #     beds = features_container.find('span', string=lambda text: text and 'beds' in text.lower())
    #     baths = features_container.find('span', string=lambda text: text and 'baths' in text.lower())
    #     toilets = features_container.find('span', string=lambda text: text and 'toilets' in text.lower())
        
    #     property_data['bedrooms'] = beds.get_text(strip=True) if beds else 'N/A'
    #     property_data['bathrooms'] = baths.get_text(strip=True) if baths else 'N/A'
    #     property_data['toilets'] = toilets.get_text(strip=True) if toilets else 'N/A'

    # Property features - ADD THIS SECTION:
    features_container = listing.find('div', class_='fur-areea')
    features = extract_property_features(features_container)
    property_data.update(features)
    

    
    # Agent information
    agent_element = listing.find('div', class_='elite-icon')
    if agent_element:
        agent_img = agent_element.find('img')
        property_data['agent_image'] = agent_img['src'] if agent_img and 'src' in agent_img.attrs else 'N/A'
    
    return propert
    property_data = {}

    # Title
    title_element = listing.find('h4')
    property_data['title'] = title_element.get_text(strip=True) if title_element else 'N/A'

    # Price
    price_element = listing.find('h2')
    property_data['price'] = price_element.get_text(strip=True) if price_element else 'N/A'

    # Location
    location_element = listing.find('p')
    property_data['location'] = location_element.get_text(strip=True) if location_element else 'N/A'

    # URL
    link_element = listing.find_parent('a', href=True)
    if link_element:
        property_data['url'] = urljoin(base_url, link_element['href'])
    else:
        property_data['url'] = 'N/A'

    # Image
    img_element = listing.find('img')
    property_data['image_url'] = img_element['src'] if img_element and 'src' in img_element.attrs else 'N/A'

    return property_data


def extract_property_data(listing, base_url):
    property_data = {}

    # Title
    title_element = listing.find('h4')
    property_data['title'] = title_element.get_text(strip=True) if title_element else 'N/A'

    # Price
    price_element = listing.find('h2')
    property_data['price'] = price_element.get_text(strip=True) if price_element else 'N/A'

    # Location
    location_element = listing.find('p')
    property_data['location'] = location_element.get_text(strip=True) if location_element else 'N/A'

    # URL
    link_element = listing.find_parent('a', href=True)
    if link_element:
        property_data['url'] = urljoin(base_url, link_element['href'])
    else:
        property_data['url'] = 'N/A'

    # Image
    img_element = listing.find('img')
    property_data['image_url'] = img_element['src'] if img_element and 'src' in img_element.attrs else 'N/A'

    return property_data

def scrape_property_listings(max_pages=100, delay_range=(5, 10)):
    driver = configure_driver()
    all_properties = []
    base_url = "https://www.propertypro.co.ke"
    
    try:
        for page in range(1, max_pages + 1):
            # Construct URL
            if page == 1:
                url = f"{base_url}/property-for-rent"
            else:
                url = f"{base_url}/property-for-rent/?page={page}"
            
            if not is_url_allowed(url):
                print(f"Skipping potentially disallowed URL: {url}")
                continue
            
            print(f"Scraping page {page}...")
            driver.get(url)
            
            # Wait for listings to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "popular-block")))
            
            # Respectful delay
            delay = random.uniform(*delay_range)
            print(f"Waiting {delay:.1f} seconds to be polite...")
            time.sleep(delay)
            
            # Parse page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            listings = soup.find_all('div', class_='popular-block')
            
            for listing in listings:
                property_data = extract_property_data(listing, base_url)
                all_properties.append(property_data)
            
            print(f"Found {len(listings)} listings on page {page}")
            
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
    
    return all_properties

# Execute scraping
properties = scrape_property_listings(max_pages=100, delay_range=(5, 10))

# Process and save results
if properties:
    df = pd.DataFrame(properties)
    
    # Clean data
    for col in ['location', 'description', 'dates_info']:
        if col in df.columns:
            df[col] = df[col].str.replace('\s+', ' ', regex=True)
    
    print(f"\nTotal properties scraped: {len(df)}")
    print("\nSample data:")
    print(df.head(3).to_markdown(index=False))
    
    # Save to CSV
    df.to_csv('propertypro_detailed_listings.csv', index=False)
    print("\nData saved to propertypro_detailed_listings.csv")
else:
    print("No properties were scraped.")