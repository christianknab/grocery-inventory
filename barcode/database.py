import os
from supabase import create_client, Client
from typing import Dict, Optional
from similarity import extract_similar_item

class InventoryDatabase:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    def get_barcode_entry(self, barcode: str) -> Optional[Dict]:
        try:
            response = self.client.table('barcodes').select('*').eq('barcode', barcode).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"db select error: {e}")
            return None

    def insert_barcode_entry(self, product_data: Dict) -> Optional[Dict]:
        try:
            response = self.client.table('barcodes').insert(product_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"db insert error: {e}")
            return None
    
    def get_inventory_item(self, id: str = None, name: str = None):
        response = ''
        if id:
            response = self.client.table('inventory').select('*').eq('id', id).execute()
        elif name:
            response = self.client.table('inventory').select('*').eq('name', name).execute()
        if response:
            return response.data[0] if response.data else None
        return None
    
    def insert_inventory_item(self, inventory_item: Dict) -> Optional[Dict]:
        try:
            response = self.client.table('inventory').insert(inventory_item).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"db insert error: {e}")
            return None
    
    def get_similar_item(self, product_name: str) -> tuple[str, str]:
        '''returns name, inventory_identifier'''
        def find_similar_item(items):
            # returns the name, inventory_identifier
            names = [item['name'] for item in items]
            best_match = extract_similar_item(product_name, names)

            if best_match:
                matched_name, index = best_match
                if index < 0:
                    return None, None
                identifier = items[index]['id']

                return matched_name, identifier
            return None, None

        def get_inventory_items():
            '''return all favorites the name, inventory_identifier'''
            try:
                response = self.client.table('inventory').select('name, id').execute()
                return response.data
            except Exception as e:
                print(f'db select all name error {e}')
                return None
        
        items = get_inventory_items()
        if items is None:
            return None, None
        return find_similar_item(items)

    def update_quantity(self, item_id, amount):
        '''increment or decrement the quantity'''
        try:
            response = self.client.rpc('update_quantity', {'item_id': item_id, 'amount': amount}).execute()
            print(f'changed quantity: {item_id}')
        except Exception as e:
            print(f'inventory quantity update error {e}')


# from barcode_api import BarcodeAPI
# from dotenv import load_dotenv
# load_dotenv()

# test product
# SUPABASE_URL = os.getenv("SUPABASE_URL")
# SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
# RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
# barcode = "022000159342"

# database = InventoryDatabase(url=SUPABASE_URL, key=SUPABASE_KEY)

# api_client = BarcodeAPI(api_key=RAPIDAPI_KEY, api_host=RAPIDAPI_HOST)
# product_info = api_client.get_product_info("022000159342")

# # Extract relevant product details
# product_name = 'ttt'

# product_data = {
#     'barcode': barcode,
#     'product_name': product_name,
# }

# # Check if the item is in the list
# # probably log the name somewhere for ease of debugging
# name, item_id = database.get_similar_item(product_name)

# if item_id:
#     product_data['item_id'] = item_id

# # Insert new product into database
# inserted_product = database.insert_barcode_entry(product_data)

# if inserted_product:
#     print(f"New product added: {product_data}")
#     # update product quantity. this will trigger a function to update the anylist item
#     # updated_product = database.update_quantity(1 if operation == 1 else -1)
#     # if updated_product:
#     #     print(f"Product modified {1 if operation == 1 else -1}: {updated_product}")