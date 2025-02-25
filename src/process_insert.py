import logging
import queue
import subprocess
import tempfile
import threading
from exceptions import ProcessInsertError
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:     [LOGGING]: %(message)s"
)

class ProcessInsert:
    def __init__(self):
        self._initialized = False
        self.running = True
        self.task_queue = queue.Queue()

    def is_running(self):
        return self._initialized
    
    def _process_queue(self) -> None:
        """Background worker that processes the in-memory queue"""
        while self.running:
            try:
                logging.info("PING")
                data = self.task_queue.get(timeout=1)

                logging.info(data)
                logging.info(type(data))

                continue
            except queue.Empty:
                continue
            except Exception:
                logging.error("Error inserting new query. Skipping")

    def start_worker(self):
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        logging.info("Database updater worker thread started")

    def stop_worker(self):
        if self.running:
            self.running = False
            self.worker_thread.join()

    def add_to_queue(self, items):
        self.task_queue.put(items)

    def clone_and_checkout(self, repo_name, commit_hash):
        # Calculate full git path
        repo_path = "/srv/git/" + repo_name
 
        # Create a temporary directory for the repository
        # to be cloned into
        temp_dir = Path(tempfile.mkdtemp())
        clone_path = temp_dir / repo_name
        
        try:
            # Clone the repo into the temp directory
            logging.info(f"Cloning {repo_path} into {clone_path}...")
            subprocess.run(["git", "clone", str(repo_path), str(clone_path)], check=True)

            # Checkout the specific commit
            logging.info(f"Checking out commit {commit_hash}...")
            subprocess.run(["git", "-C", str(clone_path), "checkout", commit_hash], check=True)
            
            return clone_path
        except subprocess.SubprocessError as e:
            raise ProcessInsertError("Error cloning input repository", 0)

data =  {
    "data": []
}

instance = ProcessInsert()
instance.clone_and_checkout("input-data.git", "abc")