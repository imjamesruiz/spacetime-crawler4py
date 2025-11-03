import re
import json
from urllib.parse import urlparse, urljoin, urldefrag
from bs4 import BeautifulSoup
from collections import Counter
from utils.response import Response


IGNORED_EXTENSIONS = [
    # Document/Media files
    'pdf', 'docx', 'doc', 'ppt', 'pptx', 'xls', 'xlsx', 'csv', 'rar', 'zip',
    # Images/Audio/Video
    'jpg', 'jpeg', 'png', 'gif', 'tif', 'tiff', 'bmp', 'webp', 'ico', 
    'mp3', 'wav', 'ogg', 'mp4', 'webm', 'avi', 'mov', 'flv', 
    # Scripts/Styles
    'css', 'js', 'xml', 'json', 'py', 'java', 'c', 'cpp', 'h', 'hpp', 
    # Other common non-HTML
    'txt', 'rss', 'atom', 'php', 
]


unique_urls = set()
word_counts = Counter()
subdomain_counts = Counter()
longest_page = {"url": None, "word_count": 0}

# Load stopwords
STOPWORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "as", "at", "be", "because", "been", "before",
    "being", "below", "between", "both", "but", "by", "could", "did", "do",
    "does", "doing", "down", "during", "each", "few", "for", "from", "further",
    "had", "has", "have", "having", "he", "her", "here", "hers", "herself",
    "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it",
    "its", "itself", "just", "me", "more", "most", "my", "myself", "no",
    "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other",
    "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should",
    "so", "some", "such", "than", "that", "the", "their", "theirs", "them",
    "themselves", "then", "there", "these", "they", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "we", "were", "what",
    "when", "where", "which", "while", "who", "whom", "why", "with", "you",
    "your", "yours", "yourself", "yourselves"
])


def scraper(url, resp):
    """
    Main scraper function called by the crawler.
    Returns a list of valid links to crawl next.
    Also updates analytics structures.
    """
    links = extract_next_links(url, resp)
    valid_links = [link for link in links if is_valid(link)]

    # save progress every 50
    if len(unique_urls) % 50 == 0 and len(unique_urls) > 0:
        save_progress()

    return valid_links


def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    next_links = []

    if resp.status != 200 or resp.raw_response is None:
        return []

    try:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

        for s in soup(["script", "style", "noscript"]):
            s.decompose()

        text = soup.get_text(separator=' ')
        words = re.findall(r"[A-Za-z]+", text.lower())
        words = [w for w in words if w not in STOPWORDS]

        defragged_url, _ = urldefrag(url)
        if defragged_url not in unique_urls:
            unique_urls.add(defragged_url)

            word_counts.update(words)

            wc = len(words)
            if wc > longest_page["word_count"]:
                longest_page.update({"url": defragged_url, "word_count": wc})

            hostname = (urlparse(url).hostname or "").lower()
            if hostname.endswith(".uci.edu"):
                subdomain_counts[hostname] += 1

        for tag in soup.find_all('a', href=True):
            href = tag.get('href')
            if not href:
                continue
            defragged, _ = urldefrag(href)
            absolute = urljoin(url, defragged)
            next_links.append(absolute)

    except Exception as e:
        print(f"[extract_next_links] Error parsing {url}: {e}")

    return next_links


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        url, _ = urldefrag(url)
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return False

        domain = parsed.netloc.lower()
        allowed_domains = (
            ".ics.uci.edu",
            ".cs.uci.edu",
            ".informatics.uci.edu",
            ".stat.uci.edu",
        )
        if not any(domain.endswith(d) for d in allowed_domains):
            return False

        path = parsed.path.lower()
        if any(path.endswith(f".{ext}") for ext in IGNORED_EXTENSIONS):
            return False

        # avoid the calendar, etc
        query = (parsed.query or "").lower()
        if any(keyword in query for keyword in [
            "tribe-bar-date", "ical", "outlook-ical",
            "eventdisplay", "calendar", "date=",
            "sort=", "session", "replytocom", "share="
        ]):
            return False

        return True

    except Exception as e:
        print(f"[is_valid] Error validating {url}: {e}")
        return False


def save_progress():
    """
    Save crawler analytics periodically to a JSON file.
    """
    try:
        data = {
            "unique_pages": len(unique_urls),
            "longest_page": longest_page,
            "top_50_words": word_counts.most_common(50),
            "subdomains": dict(sorted(subdomain_counts.items()))
        }
        with open("crawler_stats.json", "w") as f:
            json.dump(data, f, indent=2)
        print(f"[save_progress] Saved {len(unique_urls)} pages so far.")
    except Exception as e:
        print(f"[save_progress] Error saving stats: {e}")
