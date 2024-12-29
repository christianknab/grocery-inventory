from barcode_api import BarcodeAPI
from barcode_scanner import BarcodeScanner, Operation
from database import InventoryDatabase
from anylist_updater_queue import AnylistUpdaterQueue
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
    anylist_updater_queue = AnylistUpdaterQueue()

    while True:
        # Scan barcode
        # operation = scanner.choose_operation()
        barcode = scanner.scan_barcode()
        print(barcode)
        # Check if setup barcode
        if barcode == '000000000000' or barcode == '111111111111':
            continue
        
        # Validate barcode
        if not scanner.validate_barcode(barcode):
            print("Invalid barcode. Please try again.")
            continue

        try:
            # Check if barcode exists in database
            existing_product = database.get_barcode_entry(barcode)
            item_id = None

            if existing_product:
                # Barcode exists, update description or handle as needed
                item_id = existing_product['item_id']
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
                    
                    # if inserted_product:
                    #     print(f"New product added: {product_data}")
                    #     # update product quantity. this will trigger a function to update the anylist item
                        
                    #     updated_product = database.update_quantity(1 if operation == 1 else -1)
                    #     if updated_product:
                    #         print(f"Product modified {1 if operation == 1 else -1}: {updated_product}")
                else:
                    print("Could not retrieve product information.")
            
            # get anylist identifier and call js function
            if item_id:
                print(scanner.operation)
                item = database.get_inventory_item(id=item_id)
                anylist_updater_queue.add_to_queue(item['anylist_identifier'], 1 if scanner.operation == Operation.INSERT else -1)
            
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        # Ask user to continue or exit
        # should_continue = input("Scan another barcode? (y/n): ").lower()
        # if should_continue != 'y':
        #     print("Exiting...")
        #     break

if __name__ == "__main__":
    main()