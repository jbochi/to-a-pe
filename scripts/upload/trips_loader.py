from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models

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

class TripsLoader(bulkloader.Loader):
  def __init__(self):
    bulkloader.Loader.__init__(self, 'Trips',
                               [('trip_id', str),
								('route_id', str),
								('agency_id', str),
								('route_short_name', str),
								('route_long_name', str),
								('route_type', int),
								('service_id', str),
								('trip_headsign', str),
								('direction_id', str),
								('shape_id', str),
								('encoded_polyline', str),
								('encoded_levels', str),
								('starts', get_starts)
                               ])

loaders = [TripsLoader]