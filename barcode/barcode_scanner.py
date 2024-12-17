class BarcodeScanner:
    def __init__(self):
        # possible inits for an actual barcode scanner???
        pass

    def scan_barcode(self) -> str:
        barcode = input("Scan or enter barcode: ").strip()
        return barcode

    def validate_barcode(self, barcode: str) -> bool:
        return barcode.isdigit() and len(barcode) == 12