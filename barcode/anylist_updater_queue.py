import time
import subprocess
import threading
import queue
import json
import re

import os
from dotenv import load_dotenv
load_dotenv()

class AnylistUpdaterQueue:
    def __init__(self, display, logger, led_controller):
        self.task_queue = queue.Queue()
        self.NODE_PATH = os.getenv("NODE_PATH")
        self.ANYLIST_PACKAGE_PATH = os.getenv("ANYLIST_PACKAGE_PATH")
        self.lock = threading.Lock()
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        self.led_controller = led_controller
        self.display = display
        self.logger = logger
        self.logger.info("AnylistUpdaterQueue initialized")

    def add_to_queue(self, item_id, quantity):
        # Add task to queue
        self.task_queue.put((item_id, quantity, self.led_controller.insert_pin if quantity == 1 else self.led_controller.remove_pin))
        # print(f"Added to queue: item_id={item_id}, quantity={quantity}")
        self.logger.debug(f"Added to queue: item_id={item_id}, quantity={quantity}")

    def _worker(self):
        # Worker function -> process queue items
        while True:
            item_id, quantity, led = self.task_queue.get()
            with self.lock:
                self._call_js_script(item_id, quantity, led)
                self.task_queue.task_done()
    
    def _decode_json(self, stdout):
        response = json.loads(stdout)
        if response['status'] == 'success':
            self.logger.info(f"[JS OUTPUT] Item: {response['itemName']} | Old Qty: {response['oldQuantity']} | New Qty: {response['newQuantity']} | Old Details: {response['oldDetails']} | New Details: {response['newDetails']}")
            self.display.draw_image(body=f"{response['itemName']}\n{response['oldQuantity']} -> {response['newQuantity']}")
        else:
            self.logger.error(f"[JS ERROR] {response['message']}")
            self.display.draw_image(body=response['message'])

    def _call_js_script(self, item_id, quantity, led):
        # Run Node.js script
        command = [self.NODE_PATH, self.ANYLIST_PACKAGE_PATH, str(item_id), str(quantity)]
        # print("THREAD LAUNCHING:::", item_id, quantity)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Wait for process to finish before proceeding
        stdout, stderr = process.communicate()

        if stderr:
            # print(f"[JS ERROR] {stderr.strip()}")
            self.logger.error(f"[JS ERROR] {stderr.strip()}")
            self.display.draw_image(body=f"JS Error: {stderr.strip()}")
            return
        
        match = re.search(r'\{.*\}', stdout)
        if match:
            parsed = match.group(0)
            self.logger.info(f"[THREAD STDOUT] parsed: {parsed}")
            try:
                response = json.loads(parsed)
                if response['status'] == 'success':
                    self.logger.info(f"[JS OUTPUT] Item: {response['itemName']} | Old Qty: {response['oldQuantity']} | New Qty: {response['newQuantity']} | Old Details: {response['oldDetails']} | New Details: {response['newDetails']}")
                    self.display.draw_image(body=f"{response['itemName']}\n{response['oldQuantity']} -> {response['newQuantity']}")
                    self.led_controller.blink(led, 2, 0.5)
                else:
                    self.logger.error(f"[JS ERROR] {response['message']}")
                    self.display.draw_image(body=response['message'])
            except json.JSONDecodeError:
                self.display.draw_image(body="Error:" + f"Failed to parse JS output.\n{stdout}")
                self.logger.error(f"[THREAD ERROR] stdout: {stdout}")

# queue = AnylistUpdaterQueue()
# queue.add_to_queue("c9bd57c0bee24caeb5bfbde5241831ce", 1)
# time.sleep(3)