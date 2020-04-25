import re
import requests
import urllib
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import urllib.robotparser
from collections import defaultdict


stopwords = ["a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as",
             "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
             "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
             "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't",
             "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself",
             "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
             "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of",
             "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
             "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
             "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
             "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
             "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
             "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
             "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
             "yourself", "yourselves"]

# Question 1: How many unique pages (based on url) ?
unique_url = set()

# Question 2: What is the longest page in terms of number of words?
longest_page = {'url': 'initial', 'len': 0}

# Question 3: What are the 50 most common words in the entire set of pages (exclude stop words) ?
most_common = defaultdict(int)

# Questions 4: How many sub domains did you find in the ics.uci.edu domain?
sub_domains = defaultdict(int)


def scraper(url, resp):
    site = requests.get(url)

    # request did not succeed
    if site.status_code != 200:
        return []

    # find links of current url
    links = extract_next_links(url, resp)
    found = [link for link in links if is_valid(link)]
    return found


def extract_next_links(url, resp):
    linked_pages = set()
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    # finds all html link tags
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        linked_pages.add(href)
    return linked_pages


def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in {'http', 'https'}:
            return False

        # checking for quality
        if not is_high_quality(url):
            return False

        # checking if right domain/subdomain
        if url.find('ics.uci.edu') == -1 and url.find('cs.uci.edu') == -1 \
                and url.find('informatics.uci.edu') == -1 and url.find('stat.uci.edu') == -1 \
                and url.find('www.today.uci.edu'):
            return False

        # checking if can crawl
        if not can_crawl(url, parsed):
            return False

        # checking if trap
        if is_trap(parsed):
            return False

        # answering deliverables
        analyze(url)

        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|thmx|mso|arff|rtf|jar|csv|thesis"
            + r"|z|aspx|mpg|mat|pps|bam|ppsx"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz|war|apk)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise


def can_crawl(url, parsed) -> bool:
    # checking robots.txt
    site = requests.get("http://" + parsed.netloc + "/robots.txt")
    if site.status_code != 200:
        return False
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url("http://" + parsed.netloc + "/robots.txt")
    rp.read()
    return rp.can_fetch("*", url)


def is_trap(parsed) -> bool:
    # was able to identify what causes traps and get regular expressions from:
    # https://support.archive-it.org/hc/en-us/articles/208332943-Identify-and-avoid-crawler-traps-

    # long url traps
    if len(str(parsed.geturl())) > 200:
        return True

    # anchor traps
    if "#" in parsed.geturl():
        return True

    # repeating directories
    if re.match("^.*?(/.+?/).*?\1.*$|^.*?/(.+?/)\2.*$", parsed.path):
        return True

    # extra directories
    if re.match("^.*(/misc|/sites|/all|/themes|/modules|/profiles|/css|/field|/node|/theme){3}.*$", parsed.path):
        return True

    # empty
    if parsed is None:
        return False

    if re.match(r".*(calendar|date|gallery|image|wp-content|pdf|img_).*?$", parsed.path.lower()):
        return False

    # no event calendars
    if "/event/" in parsed.path or "/events/" in parsed.path:
        return False


def is_high_quality(url) -> bool:
    # checks if high quality by amount of text
    soup = BeautifulSoup(requests.get(url).content, 'html.parser')
    amount_of_text = len(get_text(url))
    if amount_of_text > 100:
        return True
    return False


def analyze(url):
    text = get_text(url)
    parsed = urlparse(url)
    page = parsed.scheme + "://" + parsed.netloc + parsed.path
    # increments unique urls to find total
    unique_url.add(page)

    # compares for longest page
    if len(text) > longest_page['len']:
        longest_page['len'] = len(text)
        longest_page['url'] = page

    # finds most common word
    for word in text:
        most_common[word] += 1
    if url.find('ics.uci.edu') > 0:
        sub_domains[page] += 1


def get_text(url):
    # scraps entire webpage's text and tokenizes
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    words = soup.get_text(" ", strip=True)
    words = words.lower()
    words = re.sub('[^A-Za-z0-9]+', ' ', words)

    # takes all duplicates out
    word_list = words.split()
    word_set = set(word_list)
    copy_set = word_set

    # removes words that aren't
    for word in copy_set:
        if len(word) < 3:
            word_set.remove(word)
    return word_set
