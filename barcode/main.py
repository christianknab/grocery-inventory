import barcode_handler as b
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

def main():
    # Initialize objects
    scanner = b.BarcodeScanner()
    api_client = b.APIClient(api_host=RAPIDAPI_HOST, api_key=RAPIDAPI_KEY)
    # db = b.Database(connection_string="database connection string")
    
    while True:
        # Scan and validate barcode
        barcode = scanner.scan_barcode()
        
        if not scanner.validate_barcode(barcode):
            print("Invalid barcode. Please try again.")
            continue
        
        try:
            # Call API to get product info
            product_data = api_client.get_product_info(barcode)
            
            # Parse product data
            product = b.Product(product_data)
            
            # Save product to the database
            # product.save_to_db(db)
            
            print(f"Product name: {product.product_name}")
        
        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Ask if the user wants to continue or exit
        should_continue = input("Scan another barcode? (y/n): ").lower()
        if should_continue != 'y':
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
