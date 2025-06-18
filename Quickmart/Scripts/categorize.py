import pandas as pd
import re

def split_product_details(full_name):
    """Split product name into base name and quantity while preserving original name as description"""
    if not isinstance(full_name, str):
        return pd.Series({'product_name': None, 'quantity': None, 'description': None})
    
    # Store original name as description
    description = full_name
    
    # Pattern to match quantity with units
    quantity_pattern = r'(?i)(\d+(?:\.\d+)?)\s*(ml|l|g|kg|pcs|pack|pieces|grams|kilos)'
    
    # Try to find quantity in the name
    quantity_match = re.search(quantity_pattern, full_name)
    
    if quantity_match:
        # Extract quantity and standardize unit
        qty_value = quantity_match.group(1)
        qty_unit = quantity_match.group(2).upper()
        quantity = f"{qty_value}{qty_unit}"
        
        # Get product name by removing quantity
        product_name = re.split(quantity_pattern, full_name, maxsplit=1, flags=re.IGNORECASE)[0].strip()
    else:
        # If no quantity found
        product_name = full_name
        quantity = None
    
    return pd.Series({
        'product_name': product_name,
        'quantity': quantity,
        'description': description
    })

def categorize_products(input_file):
    """Categorize Quickmart products based on their names and descriptions"""
    try:
        # Read the Excel file
        df = pd.read_excel(input_file)

        # Verify column names in the DataFrame
        print("Available columns:", df.columns.tolist())

        # Rename columns if needed to match expected names
        df_processed = df.copy()
        df_processed.columns = df_processed.columns.str.lower()

        # Create category mapping
        category_mapping = {
            'Beverages': r'(juice|water|soda|tea|coffee|drink|milk|yoghurt)',
            'Snacks': r'(chips|crisps|biscuits|chocolate|candy|sweets|cookies)',
            'Household': r'(cleaner|detergent|soap|tissue|towel|brush)',
            'Personal Care': r'(shampoo|toothpaste|deodorant|lotion|cream)',
            'Fresh Produce': r'(fruits|vegetables|meat|fish|chicken)',
            'Groceries': r'(rice|flour|sugar|oil|pasta|bread)',
            'Electronics': r'(battery|charger|cable|headphone|speaker)',
            'Home Care': r'(mop|broom|bucket|trash|bin|cleaning)'
        }

        # Add new category column
        df_processed['Product_Category'] = 'Other'

        # Categorize products based on name
        for category, pattern in category_mapping.items():
            mask = df_processed['name'].str.lower().str.contains(pattern, regex=True, na=False)
            df_processed.loc[mask, 'Product_Category'] = category

        # Save categorized data
        output_file = input_file.replace('.xlsx', '_categorized.xlsx')
        df_processed.to_excel(output_file, index=False)
        
        # Print summary
        print("\nCategorization Summary:")
        print(df_processed['Product_Category'].value_counts())
        print(f"\n✅ Categorized data saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("DataFrame columns:", df.columns.tolist() if 'df' in locals() else "DataFrame not loaded")

def process_products(input_file):
    """Process Quickmart products to split name components"""
    try:
        # Read the Excel file
        df = pd.read_excel(input_file)
        print("Original columns:", df.columns.tolist())
        
        # Split the name column into components
        split_df = df['name'].apply(split_product_details)
        
        # Combine with original dataframe, excluding original name column
        result_df = pd.concat([df.drop('name', axis=1), split_df], axis=1)
        
        # Reorder columns to put description first
        cols = result_df.columns.tolist()
        cols = ['description', 'product_name', 'quantity'] + [col for col in cols if col not in ['description', 'product_name', 'quantity']]
        result_df = result_df[cols]
        
        # Save processed data
        output_file = 'Quickmart/Quickmart Data/Categorized Data/categorized_products_18-06-2025.xlsx'
        result_df.to_excel(output_file, index=False)
        
        # Print summary with examples
        print("\nProcessing Summary:")
        print(f"Total products processed: {len(result_df)}")
        print(f"Products with quantity: {result_df['quantity'].notna().sum()}")
        
        print("\nExample transformations:")
        sample = result_df[['description', 'product_name', 'quantity']].head(3)
        print(sample.to_string())
        
        print(f"\n✅ Processed data saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    input_file = "Quickmart/Quickmart Data/Raw Data/quickmart_products_18-06-2025.xlsx"
    process_products(input_file)
    categorize_products(input_file)