
from typing import Dict, Optional
import requests

class BarcodeAPI:
    def __init__(self, api_key: str, api_host: str):
        self.api_key = api_key
        self.api_host = api_host

    def get_product_name(self, barcode: str) -> Optional[str]:
        try:
            url = f"https://big-product-data.p.rapidapi.com/gtin/{barcode}"
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": self.api_host
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            product_info = response.json()
            title_data = product_info.get('properties', {}).get('title', None)
            if title_data is None:
                return self.get_product_name_fallback(barcode)
            return title_data[0] if isinstance(title_data, list) else title_data
        except requests.RequestException as e:
            print(f"API Request Error: {e}")
            return None
    
    def get_product_name_fallback(self, barcode: str):
    # https://www.postman.com/cs-demo/public-rest-apis/request/zgtahxr/barcode-lookup?tab=overview
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
            print(url)
            response = requests.get(url)
            response.raise_for_status()
            product_info = response.json()
            title_data = product_info.get('product', {}).get('generic_name', None)
            if title_data is None or title_data == "":
                title_data = product_info.get('product', {}).get('product_name', None)
            return title_data if title_data != "" else None
        except requests.RequestException as e:
            print(f"API Request Error: {e}")
            return None

# api = BarcodeAPI("", "")
# print(api.get_product_name_fallback("021130308552"))