import pandas as pd

# Load both datasets
products_df = pd.read_excel("categorized_products.xlsx")  # Your product data
cpi_basket_df = pd.read_excel("CPI basket.xlsx", sheet_name="Basket")  # CPI basket

# Get the list of CPI basket items (convert to lowercase for case-insensitive matching)
cpi_items = cpi_basket_df["Elementary aggregate"].str.lower().tolist()

def is_in_cpi_basket(product_name):
    """Check if any CPI basket item appears in the product name (case-insensitive)"""
    product_lower = str(product_name).lower()
    return any(cpi_item in product_lower for cpi_item in cpi_items)

# Filter products to only those matching CPI basket items
filtered_products = products_df[products_df["Name"].apply(is_in_cpi_basket)].copy()

# Save the filtered results
filtered_products.to_excel("cpi_filtered_products.xlsx", index=False)

print(f"Filtered {len(filtered_products)}/{len(products_df)} products matching CPI basket")
print("Saved to 'cpi_filtered_products.xlsx'")