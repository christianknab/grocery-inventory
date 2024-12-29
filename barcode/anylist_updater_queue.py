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
        self.lock = threading.Lock()
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
            with self.lock:
                self._call_js_script(item_id, quantity)
                self.task_queue.task_done()

    def _call_js_script(self, item_id, quantity):
        # Run Node.js script
        command = [self.NODE_PATH, self.ANYLIST_PACKAGE_PATH, str(item_id), str(quantity)]
        print("THREAD LAUNCHING:::", item_id, quantity)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Wait for process to finish before proceeding
        stdout, stderr = process.communicate()
        if stderr:
            print(f"[JS ERROR] {stderr.strip()}")
        else:
            print(f"[JS OUTPUT] {stdout.strip()}")
        
# queue = AnylistUpdaterQueue()
# queue.add_to_queue("c9bd57c0bee24caeb5bfbde5241831ce", 1)
# time.sleep(3)