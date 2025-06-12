import pandas as pd
from fuzzywuzzy import fuzz

# Load datasets
products_df = pd.read_excel("categorized_products_11-06-2025.xlsx")
cpi_basket_df = pd.read_excel("CPI basket.xlsx", sheet_name="Basket")

# Preprocess CPI basket items
cpi_items = cpi_basket_df["Elementary aggregate"].str.lower().unique().tolist()

# Common brand names to ignore (add more as needed)
brands_to_ignore = ['copia', 'mika', 'nestle', 'brookside', 'tusker', 'guinness', 'pishori', 'basmati']

def clean_text(text):
    """Remove brands and special characters for better matching"""
    text = str(text).lower()
    for brand in brands_to_ignore:
        text = text.replace(brand, '')
    return ''.join(c for c in text if c.isalnum() or c.isspace())

def is_likely_match(product_name, threshold=65):
    """Check if product likely matches any CPI item using fuzzy matching"""
    cleaned_product = clean_text(product_name)
    for cpi_item in cpi_items:
        if fuzz.token_set_ratio(cleaned_product, clean_text(cpi_item)) >= threshold:
            return True
    return False

# Apply filtering
filtered_df = products_df[products_df["Name"].apply(is_likely_match)].copy()

# Add matched CPI item for verification
def get_matched_item(product_name, threshold=65):
    cleaned_product = clean_text(product_name)
    matches = []
    for cpi_item in cpi_items:
        score = fuzz.token_set_ratio(cleaned_product, clean_text(cpi_item))
        if score >= threshold:
            matches.append((cpi_item, score))
    return max(matches, key=lambda x: x[1])[0] if matches else "No clear match"

filtered_df["Matched CPI Item"] = filtered_df["Name"].apply(get_matched_item)

# Save results
filtered_df.to_excel("cpi_matched_liquor_products_11-06-2025.xlsx", index=False)

print(f"Filtered {len(filtered_df)}/{len(products_df)} products likely in CPI basket")
print("Results saved to 'cpi_matchedl_products.xlsx'")