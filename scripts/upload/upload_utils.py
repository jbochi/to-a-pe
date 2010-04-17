from google.appengine.ext import db
from datetime import date
from time import strptime

import models

class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.

    WARNING! Uses canonical string representation of the args as cache key
    to make it possible to cache almost anything.

    Addapted from http://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        try:
            key = args
            return self.cache[key]
        except KeyError:
            self.cache[key] = value = self.func(*args)
            return value
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

dummy = lambda x: None

def str2seconds(string):
    t = strptime(string, "%H:%M:%S")
    return t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec

def str2date(string):
    year, month, day = map(int, [string[:4], string[4:6], string[6:]])
    return date(year, month, day)

def unicode_str(string):
    return string.decode('windows-1252')

def lat_lon(s):
    lat, lon = [float(v) for v in s.split(',')]
    return db.GeoPt(lat, lon)

@memoized
def get_agency(agency_id):
    return models.Agency.get_by_key_name('agency_%s' % agency_id)

@memoized
def get_service(service_id):
    return models.Service.get_by_key_name(service_id)

@memoized
def get_route(route_id):
    return models.Route.get_by_key_name(route_id)
