import RPi.GPIO as GPIO
import time
from operation import Operation

class LEDController:
    def __init__(self, insert_pin, remove_pin):
        self.insert_pin = insert_pin
        self.remove_pin = remove_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.insert_pin, GPIO.OUT)
        GPIO.setup(self.remove_pin, GPIO.OUT)
        self.off()

    def on(self, pin):
        GPIO.output(pin, GPIO.HIGH)

    def off(self, pin=None):
        if pin:
            GPIO.output(pin, GPIO.LOW)
        else:
            GPIO.output(self.insert_pin, GPIO.LOW)
            GPIO.output(self.remove_pin, GPIO.LOW)

    def update_leds(self, operation):
        self.off()
        if operation == Operation.INSERT:
            self.on(self.insert_pin)
        elif operation == Operation.REMOVE:
            self.on(self.remove_pin)

    def cleanup(self):
        GPIO.cleanup()