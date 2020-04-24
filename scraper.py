import re
import requests
import urllib
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import urllib.robotparser
import tokenizer
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

unique_url = set()  # Question 1: How many unique pages (based on url) ?
longest_page = {'url': 'initial', 'len': 0}  # Question 2: What is the longest page in terms of number of words?
most_common = defaultdict(int)  # Question 3: What are the 50 most common words in the entire set of pages (exclude stop words) ?
sub_domains = defaultdict(int) # Questions 4: How many sub domains did you find in the ics.uci.edu domain?

def scraper(url, resp):

    site = requests.get(url)
    if site.status_code != 200:  # request did not succeed
        return []
    links = extract_next_links(url, resp)

    # need to move on to more URLs
    found = [link for link in links if is_valid(link)]
    #print('final')
    #final = check_similar(found)  # Check for similarities within list of new found links
    #print('done')
    return found


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


        # # checking for large files
        # if is_large(url):
        #     return False

        if url.find('ics.uci.edu') == -1 and url.find('cs.uci.edu') == -1 and url.find('informatics.uci.edu') == -1 and url.find('stat.uci.edu') == -1 and url.find('www.today.uci.edu'):
            return False

        # checking if can crawl
        if not can_crawl(url, parsed):
            return False

        # checking if trap
        if is_trap(parsed):
            return False

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
    # robots
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url("http://" + parsed.netloc + "/robots.txt")
    rp.read()
    return rp.can_fetch("*", url)


def is_trap(parsed) -> bool:
    # was able to identify what causes traps and get regular expressions from:
    # https://support.archive-it.org/hc/en-us/articles/208332943-Identify-and-avoid-crawler-traps-

    # long url traps
    if len(str(parsed.geturl())) > 150:
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

    # no calendars
    if "calendar" in parsed.path:
        return False

    # no event calendars
    if "/event/" in parsed.path or "/events/" in parsed.path:
        return False


def is_large(url) -> bool:
    d = urllib.request.urlopen(url)
    file_size = int(d.getheader('Content-Length'))
    if file_size > 4096:
        return True


'''
This is intended to further filter the results that stem from is_valid(url)
Created to check if there are pairs of similar pages through checking of token overlap and checks if unique by checking
number of unique tokens

Added analysis tools to use when building report

Current Issues: Inefficient
Print statements are commented out for debugging purposes.
'''


def analyze(url): # Checks url for data being asked
    text = get_text(url) # Gathers text found from web page
    parsed = urlparse(url) # Gathers url to be edited
    page = parsed.scheme + "://" + parsed.netloc + parsed.path
    unique_url.add(page)  # Question 1
    if len(text) > longest_page['len']:  # Question 2
        longest_page['len'] = len(text)
        longest_page['url'] = page
    for word in text:      # Question 3
        most_common[word] += 1
    if url.find('ics.uci.edu') > 0:
        sub_domains[page] += 1

def get_text(url):
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    words = soup.get_text(" ", strip=True)
    wordset = tokenizer.tokenize(words)
    return wordset


def check_similar(link_list):

    #print(f'Checking {len(link_list)} new links')

    matched = []
    for link in link_list:
        find_same(link, link_list, matched)

    #print(matched, ' removed ', len(matched))
    link_list = [link for link in link_list if link not in matched]
    #print(f'{len(link_list)} new links have been verified')
    return link_list


def find_same(check, llist, matched): # Determines if check url is similar with another in the new link list
   #print('done', len(matched))
    for others in llist.copy():
        if check != others and others not in matched:
            similarity, percent, unique = tokenizer.intersection(get_text(check), get_text(others))
            if (unique < 150 or percent > 90.0) and others not in matched:
                matched.append(check)
                #print('matched', check, ' with ', others)
                break
