# utils/worker.py
import time
from threading import Thread
from utils.download import download
from scraper import scraper

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.config = config
        self.frontier = frontier

    def run(self):
        while True:
            url = self.frontier.get_tbd_url()
            if not url:
                print(f"[Worker-{self.worker_id}] No more URLs to crawl.")
                break

            print(f"[Worker-{self.worker_id}] Downloading: {url}")
            resp = download(url, self.config)
            next_links = scraper(url, resp)
            for link in next_links:
                self.frontier.add_url(link)

            self.frontier.mark_url_complete(url)
            self.frontier.save_state()
            time.sleep(self.config.time_delay)
