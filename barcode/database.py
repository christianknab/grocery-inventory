import os
from supabase import create_client, Client
from typing import Dict, Optional
from similarity import extract_similar_item

from dotenv import load_dotenv

load_dotenv()

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
        reponse = None
        if id:
            reponse = self.client.table('inventory').select('*').eq('id', id).execute()
        elif name:
            reponse = self.client.table('inventory').select('*').eq('name', name).execute()
        return reponse
    
    def insert_inventory_itme(self, inventory_item: Dict) -> Optional[Dict]:
        try:
            response = self.client.table('inventory').insert(inventory_item).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"db insert error: {e}")
            return None
    
    def get_similar_item(self, product_name: str) -> tuple[str, str]:
        # returns name, anylist_identifier
        def find_similar_item(items):
            # returns the name, anylist_identifier
            names = [item['name'] for item in items]
            best_match = extract_similar_item(product_name, names)

            if best_match:
                matched_name, index = best_match
                identifier = items[index]['id']

                return matched_name, identifier
            return None, None

        def get_inventory_items():
            # return all favorites the name, anylist_identifier
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
        
    # def update_inventory_description(self, id: str, description: str) -> bool:
    #     try:
    #         self.client.table('inventory').update({'description': description}).eq('id', id).execute()
    #         return True
    #     except Exception as e:
    #         print(f"db update error: {e}")
    #         return False

def main():
    database = InventoryDatabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    # product_data = {
    #                     'barcode': '123',
    #                     'product_name': 'test'
    #                 }
    # response = database.insert_barcode_entry(product_data)
    # print(response)

    name, anylist_identifier = database.get_similar_item(" Yamaimo Buckwheat Soba Noodles, with Yam, 10.58 Oz ")
    print(name, anylist_identifier)
    

if __name__ == "__main__":
    main()