from datetime import timedelta
import re
import unicodedata

def slugify(text):
    text = remove_accents(text)
    text = text.replace("'", "")
    text = re.subn(r'(\s|\.|\(|\)|\/|\\)', ' ', text)[0]
    text = text.strip().lower()
    text = re.subn(r'(-|\s)+', '-', text)[0]
    return text

def format_timedelta_seconds(timedelta_seconds):
    return str(timedelta(seconds=timedelta_seconds))[:-3]

def remove_accents(text):
    nkfd_form = unicodedata.normalize('NFKD', unicode(text))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
