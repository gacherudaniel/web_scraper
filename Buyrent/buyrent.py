import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# Set headers to mimic a browser visit
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def scrape_property_listings(url, max_pages=5):
    properties = []
    
    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        page_url = f"{url}?page={page}" if page > 1 else url
        response = requests.get(page_url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch page {page}. Status code: {response.status_code}")
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('div', class_='listing-card')
        
        for listing in listings:
            try:
                property_info = {
                    'title': extract_title(listing),
                    'price': extract_price(listing),
                    'location': extract_location(listing),
                    'description': extract_description(listing),
                    'features': extract_features(listing),
                    'property_type': extract_property_type(listing),
                    'bedrooms': extract_bedrooms(listing),
                    'bathrooms': extract_bathrooms(listing),
                    'url': extract_url(listing),
                    'agency': extract_agency(listing)
                }
                properties.append(property_info)
            except Exception as e:
                print(f"Error processing a listing: {e}")
                continue
        
        # Random delay to avoid overwhelming the server
        time.sleep(random.uniform(1, 3))
    
    return properties

def extract_title(listing):
    # Try both mobile and desktop title selectors
    title = listing.find('span', class_='text-lg font-semibold leading-6 text-black md:inline')
    if not title:
        title = listing.find('h2', class_='font-semibold md:hidden')
    return title.text.strip() if title else "N/A"

def extract_price(listing):
    price_container = listing.find('div', class_='flex items-center justify-center text-xl font-bold leading-7 text-grey-900')
    if price_container:
        price = price_container.get_text(strip=True)
        # Clean up price text
        price = price.replace('KSh', '').strip()
        return price
    return "N/A"

def extract_location(listing):
    location_div = listing.find('div', class_='flex max-w-full items-center')
    if location_div:
        location = location_div.find('p', class_='ml-1 truncate text-sm font-normal capitalize text-grey-650')
        return location.text.strip() if location else "N/A"
    return "N/A"

def extract_description(listing):
    # Try both description selectors
    desc = listing.find('h5', class_='text-md mb-3 hidden font-normal leading-8 md:block md:text-sm')
    if not desc:
        desc = listing.find('h3', class_='block flex-1 text-sm font-medium leading-5 text-black text-grey-850 md:hidden')
    return desc.text.strip() if desc else "N/A"

def extract_features(listing):
    features = []
    # Extract bedroom and bathroom counts
    bedrooms = extract_bedrooms(listing)
    bathrooms = extract_bathrooms(listing)
    if bedrooms != "N/A":
        features.append(f"{bedrooms} Bedrooms")
    if bathrooms != "N/A":
        features.append(f"{bathrooms} Bathrooms")
    
    # Extract other features from the swiper list
    feature_items = listing.find_all('div', class_='swiper-slide flex h-6 !w-auto items-center rounded-full bg-highlight px-2 py-1 text-sm font-normal leading-4 text-grey-550')
    for item in feature_items:
        features.append(item.text.strip())
    
    return features if features else ["N/A"]

def extract_bedrooms(listing):
    bedroom_tag = listing.find('span', attrs={'data-cy': 'card-bedroom_count'})
    return bedroom_tag.text.strip() if bedroom_tag else "N/A"

def extract_bathrooms(listing):
    bathroom_tag = listing.find('span', attrs={'data-cy': 'card-bathroom_count'})
    return bathroom_tag.text.strip() if bathroom_tag else "N/A"

def extract_property_type(listing):
    # Property type is often in the title or URL
    url = extract_url(listing)
    if "apartment" in url.lower():
        return "Apartment"
    elif "house" in url.lower():
        return "House"
    return "N/A"

def extract_url(listing):
    link = listing.find('a', attrs={'data-cy': 'listing-information-link'})
    if link and link.has_attr('href'):
        return "https://www.buyrentkenya.com" + link['href']
    return "N/A"

def extract_agency(listing):
    agency_logo = listing.find('a', attrs={'data-cy': 'agency-logo'})
    if agency_logo and agency_logo.has_attr('agency-slug'):
        return agency_logo['agency-slug']
    return "N/A"

def save_to_csv(properties, filename='buyrentkenya_properties.csv'):
    # Convert features list to string for CSV
    df = pd.DataFrame(properties)
    df['features'] = df['features'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == "__main__":
    url = "https://www.buyrentkenya.com/property-for-rent"
    properties = scrape_property_listings(url, max_pages=3)  # Scrape 3 pages for demo
    save_to_csv(properties)