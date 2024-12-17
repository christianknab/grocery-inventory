
from typing import Dict, Optional
import requests

class BarcodeAPI:
    def __init__(self, api_key: str, api_host: str):
        self.api_key = api_key
        self.api_host = api_host

    def get_product_info(self, barcode: str) -> Optional[Dict]:
        try:
            url = f"https://big-product-data.p.rapidapi.com/gtin/{barcode}"
            headers = {
                "x-rapidapi-key": self.api_key,
                "x-rapidapi-host": self.api_host
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API Request Error: {e}")
            return None