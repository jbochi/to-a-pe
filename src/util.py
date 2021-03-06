from datetime import timedelta
import re
import unicodedata
from google.appengine.ext import db

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

#http://blog.notdot.net/2010/01/ReferenceProperty-prefetching-in-App-Engine
def prefetch_refprop(entities, prop):
    ref_keys = [prop.get_value_for_datastore(x) for x in entities]
    ref_entities = dict((x.key(), x) for x in db.get(set(ref_keys)))
    for entity, ref_key in zip(entities, ref_keys):
        prop.__set__(entity, ref_entities[ref_key])
    return entities
