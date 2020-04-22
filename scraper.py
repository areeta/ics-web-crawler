import re
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup


def scraper(url, resp):
    site = requests.get(url)

    if site.status_code != 200:  # request did not succeed
        return []
    links = extract_next_links(url, resp)

    # need to move on to more URLs
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):
    linked_pages = set()

    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    for a_tag in soup.findAll("a"):  # html link tags
        href = a_tag.attrs.get("href")  # url
        linked_pages.add(href)

    return linked_pages


def is_valid(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme not in {'http', 'https'}:
            return False

        # checking for subdomains
        parsed_copy = urlparse(url)
        subdomain_split = parsed_copy.netloc.split('.')

        # has a subdomain
        if len(subdomain_split) > 4:
            if subdomain_split[-2] != 'uci' and subdomain_split[-1] != 'edu':
                return False

            if subdomain_split[-3] not in {'ics', 'cs', 'informatics', 'stat', 'today'}:
                return False

        # does not have a subdomain
        else:
            if parsed.scheme not in {"http", "https"} \
                    or parsed.netloc not in {'www.ics.uci.edu', 'www.cs.uci.edu', 'www.informatics.uci.edu',
                                             'www.stat.uci.edu',
                                             'www.today.uci.edu'}:
                return False

            # special case: today.uci.edu
            if parsed.netloc == 'www.today.uci.edu':
                if '/department/information_computer_sciences' not in parsed.path:
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
        print("TypeError for ", parsed)
        raise

