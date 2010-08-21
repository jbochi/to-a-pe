import re
from sets import Set

from django.utils import simplejson
from google.appengine.api import memcache

from util import remove_accents
from models import Route


def search_routes(search_string, offset=0, limit=10):
    base_query = Route.all()
    words = get_words(search_string)
    if search_string.endswith(' '):
        #search routes that have all entire words
        for word in words:
            base_query = base_query.filter('searchable_words =', word)
    elif len(words) == 0:
        return []
    elif len(words) == 1:
        #search by routes that have word starting with text
        word = words[0]
        base_query = base_query.filter('searchable_words >=', word)
        base_query = base_query.filter('searchable_words <', word[:-1] + chr(ord(word[-1]) + 1))
    else:
        #search by routes that have all first words complete and a word starting with last word
        for word in words[:-1]:
            base_query = base_query.filter('searchable_words =', word)
        last_word = words[-1]

        #need to order in memory (exploding indexes)
        routes = [route for route in base_query.fetch(1000) if
                  any([word.startswith(last_word) for word in route.searchable_words])]
        return routes[offset:limit]

    return base_query.fetch(offset=offset, limit=limit)

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
