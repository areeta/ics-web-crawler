import re
import requests
from urllib.parse import urlparse

def scraper(url, resp):
    html = requests.get(url)  #status code
    decoded_html = html.content.decode('latin-1')

    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"  # the base url
    page_links = re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', decoded_html)  # links on pages

    for link in page_links:
        print(link)

    #links = extract_next_links(url, resp)
    return [link for link in page_links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    return list()

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
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

