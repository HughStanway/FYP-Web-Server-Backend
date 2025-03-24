import hashlib
import logging
import queue
import shutil
import subprocess
import tempfile
import threading
from exceptions import ProcessInsertError
from pathlib import Path

from java_parser import extract_methods_from_java

logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:     [LOGGING]: %(message)s"
)


class ProcessInsert:
    def __init__(self, embedding_client, database_client, redis_client):
        self.embedding_client = embedding_client
        self.database_client = database_client
        self.redis_client = redis_client

        self._initialized = False
        self.running = True
        self.task_queue = queue.Queue()

    def is_running(self):
        return self._initialized

    def _process_queue(self) -> None:
        """Background worker that processes the in-memory queue"""
        while self.running:
            try:
                data = self.task_queue.get(timeout=1)
                logging.info(f"data {data}")
                # Make a temporary clone of the repository and checkout
                # the corresponding commit
                collection_name = data["collectionName"]
                repositories = data["repositories"]
                for repo in repositories:
                    repo_name, commit_hash = repo["repoName"], repo["commitHash"]
                    temp_clone = self.clone_and_checkout(repo_name, commit_hash)
                    self.process_repo_files(temp_clone, collection_name)
                    self.cleanup_temp_directory(temp_clone)

                continue
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error inserting new query. Skipping: {e}")

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
        temp_dir = Path(tempfile.mkdtemp())
        clone_path = temp_dir / repo_name

        try:
            # Ensure the repo is accessible
            subprocess.run(
                ["git", "config", "--global", "--add", "safe.directory", repo_path],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Clone the repo into the temp directory
            logging.info(f"Cloning {repo_path} into {clone_path}...")
            subprocess.run(
                ["git", "clone", str(repo_path), str(clone_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Create and checkout a new branch pointing to the commit
            logging.info(f"Checking out commit {commit_hash}...")
            subprocess.run(
                ["git", "-C", str(clone_path), "checkout", "-b", "tmp", commit_hash],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return clone_path
        except subprocess.SubprocessError as e:
            logging.info(f"error: {e}")
            raise ProcessInsertError("Error cloning input repository", 0)

    def process_repo_files(self, repo_path, collection_name):
        # Find all .java files in the repository
        files = list(repo_path.glob("**/*.java"))
        logging.info(f"Found {len(files)} .java files.")

        # Process each file
        for file in files:
            with open(file, "r") as f:
                content = f.read()

                java_methods = extract_methods_from_java(content)
                for java_method in java_methods:
                    logging.info(f"Extracted method: {java_method}")
                    hashed_text = self.compute_hash(java_method)
                    embedded_text = self.embedding_client.compute_embedding(java_method)

                    # Insert into databases
                    if not self.redis_client.exists(hashed_text):
                        self.redis_client.put(hashed_text, content)

                        # Insert into vector dataabse
                        self.database_client.insert(
                            {"hash": hashed_text, "embedding": embedded_text},
                            collection_name,
                        )

                        logging.info("Method inserted successfully.")

        logging.info("Successfully inserted into database")

    def compute_hash(self, filetext: str):
        return hashlib.sha256(filetext.encode()).hexdigest()

    def cleanup_temp_directory(self, temp_dir):
        shutil.rmtree(temp_dir)
        logging.info("Temp directory removed")
