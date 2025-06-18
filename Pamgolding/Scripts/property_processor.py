import pandas as pd
import re

def extract_prices(price_str):
    """Extract main price and bracketed price from string"""
    if not isinstance(price_str, str):
        return None, None
        
    # Extract main Rand price
    rand_match = re.search(r'R([\d,]+)', price_str)
    main_price = float(rand_match.group(1).replace(',', '')) if rand_match else None
    
    # Extract bracketed price
    # First check for KSH amount
    ksh_match = re.search(r'KSH([\d,]+)', price_str)
    if ksh_match:
        bracket_price = float(ksh_match.group(1).replace(',', ''))
    else:
        # If no KSH, check for USD and convert
        usd_match = re.search(r'\$\s*([\d,]+)', price_str)
        if usd_match:
            usd_amount = float(usd_match.group(1).replace(',', ''))
            # Using current exchange rate (1 USD = 142.6 KSH)
            bracket_price = usd_amount * 142.6
        else:
            bracket_price = None
    
    return main_price, bracket_price

def extract_location(title):
    """Extract location from title"""
    if not isinstance(title, str):
        return None, None, None
    
    # Get text in parentheses at the end
    location_match = re.search(r'in\s+([^()]+)\s*\(([^)]+)\)$', title)
    if location_match:
        area = location_match.group(1).strip()
        country = location_match.group(2).strip()
        full_location = f"{area}, {country}"
        return full_location, area, country
    return None, None, None

def process_properties(input_file, output_file):
    """Process both prices and locations"""
    try:
        # Read CSV file
        df = pd.read_csv(input_file)
        
        # Add new columns
        df['Price_Rand'] = None
        df['Price_KSH'] = None
        df['Location'] = None
        df['Area'] = None
        df['Country'] = None
        
        # Process each row
        for idx, row in df.iterrows():
            # Process prices
            rand_price, ksh_price = extract_prices(row['price'])
            df.at[idx, 'Price_Rand'] = rand_price
            df.at[idx, 'Price_KSH'] = ksh_price
            
            # Process location - now unpacking three values
            full_location, area, country = extract_location(row['title'])
            df.at[idx, 'Location'] = full_location
            df.at[idx, 'Area'] = area
            df.at[idx, 'Country'] = country
        
        # Save processed data
        df.to_csv(output_file, index=False)
        
        print(f"✅ Processing complete! Results saved to {output_file}")
        print("\nSummary:")
        print(f"Total properties processed: {len(df)}")
        print(f"Properties with Rand prices: {df['Price_Rand'].notna().sum()}")
        print(f"Properties with KSH prices: {df['Price_KSH'].notna().sum()}")
        
    except Exception as e:
        print(f"❌ Error processing data: {str(e)}")

if __name__ == "__main__":
    input_file = "pam_golding_properties_all_pages.csv"
    output_file = "processed_properties.csv"
    process_properties(input_file, output_file)