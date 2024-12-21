class BarcodeScanner:
    def __init__(self):
        # possible inits for an actual barcode scanner???
        self.operation = Operation.INSERT
        pass

    def scan_barcode(self) -> str:
        barcode = input("Scan or enter barcode: ").strip()
        return barcode
    
    def choose_operation(self):
        op = input("Choose operation - 0 (DELETE), 1 (REMOVE): ").strip()
        self.operation = Operation.INSERT if op == '1' else Operation.REMOVE
        return self.operation.value

    def validate_barcode(self, barcode: str) -> bool:
        return barcode.isdigit() and len(barcode) == 12
    
from enum import Enum

class Operation(Enum):
    INSERT = 1
    REMOVE = 0