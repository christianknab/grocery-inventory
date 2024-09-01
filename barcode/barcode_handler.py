import requests

class BarcodeScanner:
    def __init__(self):
        # Initialize scanner, settings, etc.
        pass
    
    def scan_barcode(self) -> str:
        # Change to scanner input, for now, testing with stdin
        barcode = input("Enter the barcode: ")
        return barcode
    
    def validate_barcode(self, barcode: str) -> bool:
        return True if len(barcode) == 12 else False

class APIClient:
    def __init__(self, api_key, api_host):
        self.api_key = api_key
        self.api_host = api_host

    def get_product_info(self, barcode):
        response = self._make_api_call(barcode)
        return response.json()

    def _make_api_call(self, barcode) -> requests.Response:
        # API call logic with error handling
        url = "https://big-product-data.p.rapidapi.com/gtin/" + barcode

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host
        }

        response = requests.get(url, headers=headers)
        
        return response

class Product:
    def __init__(self, product_data):
        self.product_name = product_data.get("properties").get("title")[0]
        # parse anything else here?
    
    def save_to_db(self, db):
        db.insert_product(self)

class Database:
    def __init__(self, connection_string):
        self.connection = self._connect_to_db(connection_string)
    
    def _connect_to_db(self, connection_string):
        # Connect to the database (e.g., using psycopg2 or SQLAlchemy)
        pass
    
    def insert_product(self, product):
        # Insert product into the database
        pass
