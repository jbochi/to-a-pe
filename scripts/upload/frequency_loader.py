from google.appengine.ext import db
from google.appengine.tools import bulkloader

from src import models

from upload_utils import str2seconds

def getTrip(trip_id):
    result = db.GqlQuery("SELECT * FROM Trip WHERE trip_id = :1 LIMIT 1",
                    trip_id).fetch(1)
    if result:
        return result[0].key()
    else:
        return None #just to keep the loader from importing

class FrequencyLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Frequency',
                                   [('trip_id', getTrip),
                                    ('start_time', str2seconds),
                                    ('end_time', str2seconds),
                                    ('headway_secs', int)
                                   ])

    def generate_key(self, i, values):
        return '_'.join(values[:2])

loaders = [FrequencyLoader]
