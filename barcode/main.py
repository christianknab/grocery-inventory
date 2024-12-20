from barcode_api import BarcodeAPI
from barcode_scanner import BarcodeScanner
from database import InventoryDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    # Load envs
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Initialize
    scanner = BarcodeScanner()
    api_client = BarcodeAPI(api_key=RAPIDAPI_KEY, api_host=RAPIDAPI_HOST)
    database = InventoryDatabase(url=SUPABASE_URL, key=SUPABASE_KEY)

    while True:
        # Scan barcode
        operation = scanner.choose_operation()
        barcode = scanner.scan_barcode()

        # Validate barcode
        if not scanner.validate_barcode(barcode):
            print("Invalid barcode. Please try again.")
            continue

        try:
            # Check if barcode exists in database
            existing_product = database.get_barcode_entry(barcode)

            if existing_product:
                # Barcode exists, update description or handle as needed
                print(f"Product found: {existing_product}")
                
            else:
                # Barcode not in database, fetch from API
                product_info = api_client.get_product_info(barcode)
                
                if product_info:
                    # Extract relevant product details
                    product_name = product_info.get('properties', {}).get('title', ['Unknown Product'])[0]

                    product_data = {
                        'barcode': barcode,
                        'product_name': product_name,
                    }

                    # Check if the item is in the list
                    # probably log the name somewhere for ease of debugging
                    name, item_id = database.get_similar_item(product_name)

                    if item_id:
                        product_data['item_id'] = item_id
                    
                    # Insert new product into database
                    inserted_product = database.insert_barcode_entry(product_data)
                    
                    if inserted_product:
                        print(f"New product added: {product_data}")
                        # update product quantity. this will trigger a function to update the anylist item
                        updated_product = database.update_quantity(1 if operation == 1 else -1)
                        if updated_product:
                            print(f"Product modified {1 if operation == 1 else -1}: {updated_product}")
                else:
                    print("Could not retrieve product information.")

        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        # Ask user to continue or exit
        should_continue = input("Scan another barcode? (y/n): ").lower()
        if should_continue != 'y':
            print("Exiting...")
            break

if __name__ == "__main__":
    main()