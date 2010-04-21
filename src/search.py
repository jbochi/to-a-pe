import re
from sets import Set
from util import remove_accents

def get_words(text):
    splitter = re.compile(r'[\s|\-|\)|\(|/]+')
    return [s.lower() for s in splitter.split(remove_accents(text)) if s != '']

def get_unique_words(text, min_lenght):
    word_set = Set([word for word in get_words(text) if len(word) >= min_lenght])
    return word_set

def get_starts(text, min_length=3):
    word_set = get_unique_words(text)
    starts = Set()
    for word in word_set:
        for i in range(len(word)):
            starts.add(word[:i + 1])

    return sorted(starts)
