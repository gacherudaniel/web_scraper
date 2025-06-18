# Real Estate and Retail Web Scrapers

A comprehensive web scraping solution for extracting and processing data from multiple sources including Quickmart retail store and real estate platforms (Pam Golding and Property.ke).

## Project Structure

```
Web Scraping/
├── Quickmart/
│   ├── Scripts/
│   │   ├── quickmart.py        # Main scraping script
│   │   ├── categorize.py       # Product categorization
│   │   ├── basket_items.py     # CPI basket matching
│   │   └── liquor.py          # Liquor category scraper
│   │
│   └── Quickmart Data/
│       ├── Raw Data/          # Initial scraped data
│       ├── Categorized Data/  # Processed and categorized products
│       └── Filtered Data/     # CPI basket matched items
│
├── Pamgolding/
│   ├── Scripts/
│   │   ├── pamgolding.py      # Property scraping script
│   │   └── price_processor.py # Price and location processor
│   │
│   └── Data/
│       ├── pam_golding_properties_all_pages.csv
│       └── processed_properties.csv
│
└── Property_ke/
    └── propertyke.py         # PropertyKE scraping script
```

## Features

### Quickmart Scraper

- **Product Data Collection:**

  - Multiple category support
  - Pagination handling
  - Price extraction
  - Location-based store selection

- **Data Processing:**
  - Product categorization
  - Quantity extraction
  - CPI basket item matching
  - Price standardization

### Real Estate Scrapers

- **Pam Golding:**

  - Property listing extraction
  - Price conversion (USD/KSH)
  - Location processing
  - Multiple page handling

- **Property.ke:**
  - Detailed property information
  - Feature extraction
  - Agent information
  - Respectful scraping with delays

## Prerequisites

- Python 3.12+
- Chrome Browser
- ChromeDriver matching your Chrome version

## Required Packages

```bash
pip install selenium
pip install beautifulsoup4
pip install pandas
pip install openpyxl
pip install fuzzywuzzy
pip install webdriver_manager
```

## Usage

### Quickmart Scraper

```bash
# Run main scraper
python Quickmart/Scripts/quickmart.py

# Process and categorize products
python Quickmart/Scripts/categorize.py

# Match with CPI basket items
python Quickmart/Scripts/basket_items.py
```

### Real Estate Scrapers

```bash
# Pam Golding Properties
python Pamgolding/Scripts/pamgolding.py
python Pamgolding/Scripts/price_processor.py

# Property.ke
python Property_ke/propertyke.py
```

## Output Files

### Quickmart

- `quickmart_products_[date].xlsx`: Raw scraped data
- `categorized_products_[date].xlsx`: Processed products
- `cpi_matched_products_[date].xlsx`: CPI basket matches

### Real Estate

- `pam_golding_properties_all_pages.csv`: Raw property data
- `processed_properties.csv`: Processed property data
- `propertypro_detailed_listings.csv`: Property.ke listings

## Features by Platform

### Quickmart

- Product name and price extraction
- Category-based scraping
- Quantity standardization
- Price formatting
- CPI basket matching

### Pam Golding

- Property details extraction
- Price conversion (USD to KSH)
- Location parsing
- Multi-page support

### Property.ke

- Detailed property features
- Agent information
- Location data
- Pricing details
- Respectful scraping practices

## Development

### Branching Strategy

- `main`: Production-ready code
- Feature branches for new functionality

### Contributing

1. Create a feature branch
2. Implement changes
3. Test thoroughly
4. Create pull request

## Error Handling

- Robust exception handling
- Screenshot capture for debugging
- Detailed error logging
- Graceful failure recovery

## License

[Your chosen license]

## Authors

[Your name]

## Acknowledgments

- Quickmart Kenya
- Pam Golding Properties
- Property.ke
- Selenium and BeautifulSoup4 documentation
