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
        from urllib.parse import urlparse
        import re

        while True:
            url = self.frontier.get_tbd_url()
            if not url:
                print(f"[Worker-{self.worker_id}] No more URLs to crawl.")
                break

            ext = urlparse(url).path.lower().split('.')[-1]
            if re.match(r'^(img|apk|sql|zip|tar|gz|bz2|7z|mp4|mp3|pdf|docx?|pptx?|xlsx?|bin|exe|dmg|iso)$', ext):
                print(f"[Worker-{self.worker_id}] [SKIP LARGE FILE] {url}")
                self.frontier.mark_url_complete(url)
                continue

            print(f"[Worker-{self.worker_id}] Downloading: {url}")
            resp = download(url, self.config)

            if resp and resp.raw_response:
                ctype = resp.raw_response.headers.get("Content-Type", "").lower()
                clen = int(resp.raw_response.headers.get("Content-Length", 0))
                
            if not ctype.startswith("text/html"):
                print(f"[Worker-{self.worker_id}] [SKIP NON-HTML] {url} ({ctype})")
                self.frontier.mark_url_complete(url)
                continue
            if clen > 5_000_000:
                print(f"[Worker-{self.worker_id}] [SKIP LARGE CONTENT >5MB] {url}")
                self.frontier.mark_url_complete(url)
                continue

            next_links = scraper(url, resp)
            for link in next_links:
                self.frontier.add_url(link)

            self.frontier.mark_url_complete(url)
            self.frontier.save_state()
            time.sleep(self.config.time_delay)
