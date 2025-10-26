import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag
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


def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

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
    
    if resp.status != 200:
        return []
    
    if resp.raw_response and resp.raw_response.content:
        soup = BeautifulSoup(resp.raw_response.content, 'lxml')
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            defragmented_URL, _ = urldefrag(href)
            absolute_URL = urljoin(url, defragmented_URL)
            
            if is_valid(absolute_URL):
                next_links.append(absolute_URL)
                

    return next_links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        
        if not re.match(r".*\.ics\.uci\.edu$", parsed.netloc.lower()):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise

