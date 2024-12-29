import time
import subprocess
import threading
import queue

import os
from dotenv import load_dotenv
load_dotenv()

class AnylistUpdaterQueue:
    def __init__(self):
        self.task_queue = queue.Queue()
        self.NODE_PATH = os.getenv("NODE_PATH")
        self.ANYLIST_PACKAGE_PATH = os.getenv("ANYLIST_PACKAGE_PATH")
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()

    def add_to_queue(self, item_id, quantity):
        # Add task to queue
        self.task_queue.put((item_id, quantity))
        print(f"Added to queue: item_id={item_id}, quantity={quantity}")

    def _worker(self):
        # Worker function -> process queue items
        while True:
            item_id, quantity = self.task_queue.get()
            self._call_js_script(item_id, quantity)
            self.task_queue.task_done()

    def _call_js_script(self, item_id, quantity):
        # Run Node.js script
        command = [self.NODE_PATH, self.ANYLIST_PACKAGE_PATH, str(item_id), str(quantity)]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Handle errors in a separate thread
        threading.Thread(target=self._log_errors, args=(process,), daemon=True).start()

    def _log_errors(self, process):
        for line in iter(process.stderr.readline, ''):
            print(f"[JS ERROR] {line.strip()}")
            # self._handle_js_error(line.strip())

    # def _handle_js_error(self, error_message):
    #     print(error_message)

# queue = AnylistUpdaterQueue()
# queue.add_to_queue("c9bd57c0bee24caeb5bfbde5241831ce", 1)
# time.sleep(3)