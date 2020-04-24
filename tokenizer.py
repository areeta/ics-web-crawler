"""
Summary of my tokenizer:
    * A sequence is composed of 2 or more alphanumeric characters.
    * A space indicates the end of the token.
    * All characters have been converted to lowercase.
    * Punctuation-handling: words are split at the punctuation and counted separately (if they make a sequence).
        - Handles hyphens, apostrophes, and end punctuation (periods, commas,
        exclamations, question marks, colons, and semicolons)
"""
import re


def tokenize(wordlist) -> list:
    tokens = []  # Return this for final tokens found in file

    for text in wordlist:
        found = re.findall(r"[a-z0-9A-Z]{2,}", text)
        tokens = tokens + found

    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()

    return tokens

"""
EXPLANATION:
This intersection method demonstrates liner O(N) time. The larger
the word lists of files 1 and 2, the more loops executed to add each word to the
similar words list. Because of the use of the keyword "in", I avoided a
double loop that would iterate through both word lists.
"""


def intersection(file1_words, file2_words):
    """ Word lists are casted to sets in order to remove duplicates. """
    file1_words = set(file1_words)
    file2_words = set(file2_words)

    similar_words = []
    for word in file1_words:
        """ Conditional to avoid counting duplicates """
        if (word in file2_words) and (word not in similar_words):
            similar_words.append(word)

    return len(similar_words), len(similar_words)/ len(file1_words)*100, len(file1_words)


def compare(text1, text2):
    list1 = tokenize(text1)
    list2 = tokenize(text2)

    similarity, percent, unique = intersection(list1, list2)

    return similarity, percent, unique
