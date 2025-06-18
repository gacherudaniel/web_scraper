import pandas as pd
import re

# Input and output file paths
INPUT_FILE = "Quickmart/Quickmart Data/Raw Data/quickmart_products_18-06-2025.xlsx"  # Your input Excel file
OUTPUT_FILE = "Quickmart/Quickmart Data/Categorized Data/categorized_products_18-06-2025.xlsx"  # Output Excel file

# Function to extract quantity and clean product name
def extract_quantity_and_name(product_name):
    """
    Extracts quantity (e.g., "500Ml", "1L", "3Pc") and cleans the product name.
    Returns (clean_name, quantity).
    """
    # Common patterns for quantity (case-insensitive)
    patterns = [
        r'(\d+\.?\d*)\s*(ML|Ml|ml|L|Ltr|G|Kg|KG|g|PC|Pc|pc|PCS|Pcs|pcs|Mts|Gms|Gm|Litre|Ltrs)\b',  # 500Ml, 1L, 50G
        r'(\d+)\s*(Pack|Bottle|Can|Jar|Box|Sat|Tray)\b',  # 3 Pack, 1 Bottle
        r'(\d+)\s*-\s*(Pack|Piece|Pc|Pk|Pc)\b',  # 3-Pack, 1-Piece
    ]
    
    for pattern in patterns:
        match = re.search(pattern, product_name, re.IGNORECASE)
        if match:
            quantity = f"{match.group(1)} {match.group(2)}"
            clean_name = re.sub(pattern, '', product_name, flags=re.IGNORECASE).strip()
            return clean_name, quantity
    
    # If no quantity found, return original name and empty string
    return product_name, ""

# Read the entire Excel file (if it fits in memory)
try:
    df = pd.read_excel(INPUT_FILE)
    
    # Apply the extraction function to each product name
    df[['Name', 'Quantity']] = df['name'].apply(
        lambda x: pd.Series(extract_quantity_and_name(x))
    )
    
    # Reorder columns and rename
    df = df.rename(columns={'Product Name': 'Description'})
    df = df[['Category', 'Name', 'Description', 'Quantity', 'Price']]
    
    # Save to Excel
    df.to_excel(OUTPUT_FILE, index=False)
    
    print(f"Processing complete! Output saved to {OUTPUT_FILE}")
    print(f"Total rows processed: {len(df)}")

except MemoryError:
    print("Error: File is too large to load into memory. Try splitting it into smaller files or use a CSV instead.")
except Exception as e:
    print(f"An error occurred: {e}")