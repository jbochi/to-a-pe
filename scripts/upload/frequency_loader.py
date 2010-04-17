from time import strptime
from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models

def getTrip(trip_id):
    result = db.GqlQuery("SELECT * FROM Trips WHERE trip_id = :1 LIMIT 1",
                    trip_id).fetch(1)
    if result:
        return result[0].key()
    else:
        return None #just to keep the loader from importing

def str2time(string):
    t = strptime(string, "%H:%M:%S")
    return t.tm_hour * 3600 + t.tm_min * 60 + t.tm_sec

class FrequencyLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Frequency',
                                   [('trip_id', getTrip),
                                    ('start_time', str2time),
                                    ('end_time', str2time),
                                    ('headway_secs', int)
                                   ])
        
    def generate_key(self, i, values):
        return '_'.join(values[:2])

loaders = [FrequencyLoader]
