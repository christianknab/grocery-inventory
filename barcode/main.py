import signal
import sys
from barcode_api import BarcodeAPI
from barcode_scanner import BarcodeScanner
from database import InventoryDatabase
from anylist_updater_queue import AnylistUpdaterQueue
from led_controller import LEDController
from display_controller import DisplayController
from operation import Operation
import os
from dotenv import load_dotenv

load_dotenv()

led = None

def cleanup_and_exit(signum, frame):
    global led
    global display
    if led:
        led.cleanup()
    if display:
        display.clear()
    print("Exiting gracefully...")
    sys.exit(0)

def main():
    global led
    global display

    # Load envs
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Initialize
    led = LEDController(insert_pin=16, remove_pin=26)
    display = DisplayController()
    scanner = BarcodeScanner(led_controller=led)
    api_client = BarcodeAPI(api_key=RAPIDAPI_KEY, api_host=RAPIDAPI_HOST)
    database = InventoryDatabase(url=SUPABASE_URL, key=SUPABASE_KEY)
    anylist_updater_queue = AnylistUpdaterQueue(display)

    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    # Set initial display
    display.draw_image()

    try:
        while True:
            # Scan barcode
            barcode = scanner.scan_barcode()
            print(barcode)
            # Check if setup barcode
            if barcode in ['000000000000', '111111111111']:
                display.draw_image(scanner.operation, body="Please Scan Item")
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
                    else:
                        print("Could not retrieve product information.")
                # get anylist identifier and call js function
                if item_id:
                    item = database.get_inventory_item(id=item_id)
                    display.draw_image(scanner.operation, item['name'] + '\nUpdating Quantity...')
                    anylist_updater_queue.add_to_queue(item['anylist_identifier'], 1 if scanner.operation == Operation.INSERT else -1)
            except Exception as e:
                print(f"Error during barcode processing: {e}")
                break
    finally:
        if led:
            led.cleanup()
        if display:
            display.clear()
        print("LEDs turned off. Exiting...")

if __name__ == "__main__":
    main()