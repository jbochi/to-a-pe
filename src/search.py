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


#############
from django.utils import simplejson
from google.appengine.api import memcache
from models import Route

def create_search_list():
    def route_dict(route):
        return {'url': route.get_absolute_url(),
                'text': "%s - %s" % (route.short_name, route.long_name)}

    routes = Route.all().fetch(2000)
    data = [route_dict(route) for route in routes]
    return simplejson.dumps(data)

def get_search_list(force_update=False):
    memcache_key = "search_list"
    if not force_update:
        list = memcache.get(memcache_key)
        if list is not None:
            return list

    list = create_search_list()
    memcache.add(memcache_key, list)
    return list
