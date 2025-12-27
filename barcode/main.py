import logging
import logging.handlers
import os
import signal
import sys
import time
from barcode_api import BarcodeAPI
from barcode_scanner import BarcodeScanner
from database import InventoryDatabase
from anylist_updater_queue import AnylistUpdaterQueue
from led_controller import LEDController
from display_controller import DisplayController
from operation import Operation
from dotenv import load_dotenv

# Setup logging
LOG_DIR = '/home/knab-server/grocery-inventory/logs'
LOG_FILE_NAME = 'application.log'
RETENTION_DAYS = 7
os.makedirs(LOG_DIR, exist_ok=True)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_file_path = os.path.join(LOG_DIR, LOG_FILE_NAME)
file_handler = logging.handlers.TimedRotatingFileHandler(
    log_file_path, when='midnight', interval=1, backupCount=RETENTION_DAYS
)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger = logging.getLogger('barcode_app')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

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
    logger.info("Initializing application")
    led = LEDController(insert_pin=16, remove_pin=26)
    display = DisplayController()
    scanner = BarcodeScanner(led_controller=led)
    api_client = BarcodeAPI(api_key=RAPIDAPI_KEY, api_host=RAPIDAPI_HOST)
    database = InventoryDatabase(url=SUPABASE_URL, key=SUPABASE_KEY)
    anylist_updater_queue = AnylistUpdaterQueue(display, logger, led)

    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup_and_exit)
    signal.signal(signal.SIGTERM, cleanup_and_exit)

    # Set initial display
    display.draw_image()
    logger.info("Application started and waiting for barcode scan")

    try:
        while True:
            # Scan barcode
            barcode = scanner.scan_barcode()
            # print(barcode)
            logger.debug(f"Scanned barcode: {barcode}")

            # Check if setup barcode
            if barcode in ['000000000000', '111111111111']:
                display.draw_image(scanner.operation, body="Please Scan Item")
                continue

            # Validate barcode
            if not scanner.validate_barcode(barcode):
                display.draw_image(scanner.operation, body=f"Invalid: {barcode}\nPlease try again.")
                # print("Invalid barcode. Please try again.")
                logger.warning(f"Invalid barcode: {barcode}")
                continue

            display.draw_image(body=f"Searching for barcode: {barcode}")
            try:
                # Check if barcode exists in database
                start = time.time()
                existing_product = database.get_barcode_entry(barcode)
                item_id = None
                product_name = None

                if existing_product:
                    # Barcode exists, update description or handle as needed
                    item_id = existing_product['item_id']
                    # print(f"Product found: {existing_product}")
                    logger.info(f"Product found in database: {existing_product}")
                else:
                    # Barcode not in database, fetch from API
                    product_name = api_client.get_product_name(barcode)
                    if product_name:
                        product_data = {
                            'barcode': barcode,
                            'product_name': product_name,
                        }
                        
                        # Check if the item is in the list
                        name, item_id = database.get_similar_item(product_name)

                        if item_id:
                            product_data['item_id'] = item_id
                        
                        # Insert new product into database
                        inserted_product = database.insert_barcode_entry(product_data)
                        logger.info(f"Inserted new product: {product_data}")
                    else:
                        logger.error(f"Could not retrieve product information. {barcode}")
                        display.draw_image(scanner.operation, body=f"Product Data\nNot Found:\n-> {barcode}")
                        continue
                # get anylist identifier and call js function
                if item_id:
                    item = database.get_inventory_item(id=item_id)
                    # Skip if we are to ignore the item
                    if item['ignore']:
                        logger.info(f"Ignoring item: {item['name']}")
                        display.draw_image(scanner.operation, body=f"{item['name']}\n-> Update Manually!")
                        continue
                    display.draw_image(scanner.operation, item['name'] + '\nUpdating Quantity...')
                    anylist_updater_queue.add_to_queue(item['anylist_identifier'], 1 if scanner.operation == Operation.INSERT else -1)
                # No item id found
                else:
                    existing = 'NONE'
                    if product_name:
                        existing = product_name
                    elif existing_product:
                        existing = existing_product
                    logger.error(f"No item id found. Existing product: {existing}")
                    display.draw_image(scanner.operation, body=f"No anylist id linked\nUpdate db manually\n-> {barcode}\n{existing}")
            except Exception as e:
                # print(f"Error during barcode processing: {e}")
                logger.error(f"Error during barcode processing: {e}", exc_info=True)
                display.draw_image(scanner.operation, body=f"Error:\n{e}")
                continue
    finally:
        if led:
            led.cleanup()
        if display:
            display.clear()
        # print("LEDs turned off. Exiting...")
        logger.info("LEDs turned off. Exiting...")

if __name__ == "__main__":
    main()
