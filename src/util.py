from datetime import timedelta
import re
import unicodedata

def slugify(text):
    text = remove_accents(text)
    #replace disallowed chars by spaces
    text = text.replace("'", "")
    text = re.subn(r'(\s|\.|\(|\)|\/|\\)', ' ', text)[0]
    text = text.strip().lower()
    #replaces group of dashes or spaces to one dash
    text = re.subn(r'(-|\s)+', '-', text)[0]
    return text

def format_timedelta_seconds(timedelta_seconds):
    return str(timedelta(seconds=timedelta_seconds))[:-3]

def remove_accents(text):
    nkfd_form = unicodedata.normalize('NFKD', unicode(text))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def get_words(text):
    list = remove_accents(text).strip().lower().split(' ')
    list = [word for word in list if word != '']
    return make_unique(list)

def make_unique(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]
