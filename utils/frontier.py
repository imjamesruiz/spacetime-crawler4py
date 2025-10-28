# utils/frontier.py
from collections import deque
import os
import pickle

class Frontier:
    def __init__(self, config, restart):
        self.save_file = config.save_file
        self.to_visit = deque()
        self.visited = set()

        if restart or not os.path.exists(self.save_file):
            print("[Frontier] Starting fresh crawl.")
            for seed in config.seed_urls:
                self.to_visit.append(seed)
        else:
            print("[Frontier] Loading existing frontier state...")
            with open(self.save_file, 'rb') as f:
                self.to_visit, self.visited = pickle.load(f)

    def get_tbd_url(self):
        """Get one URL to be downloaded."""
        return self.to_visit.popleft() if self.to_visit else None

    def add_url(self, url):
        """Add one URL if not already visited or queued."""
        if url not in self.visited and url not in self.to_visit:
            self.to_visit.append(url)

    def mark_url_complete(self, url):
        """Mark a URL as completed."""
        self.visited.add(url)

    def save_state(self):
        """Persist the current frontier to disk."""
        with open(self.save_file, 'wb') as f:
            pickle.dump((self.to_visit, self.visited), f)
