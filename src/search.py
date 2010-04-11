import unicodedata
import re
from sets import Set

def remove_accents(text):
    nkfd_form = unicodedata.normalize('NFKD', unicode(text))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def get_words(text):
    splitter = re.compile(r'[\s|\-|\)|\(|/]+')
    return [s.lower() for s in splitter.split(remove_accents(text)) if s!= '']

def get_unique_words(text):
    word_set = Set(get_words(text))
    return word_set

def get_starts(text):
    word_set = get_unique_words(text)
    starts = Set()
    for word in word_set:
        for i in range(len(word)):
            starts.add(word[:i+1])

    return sorted(starts)