import sys
sys.path.append('C:/USERS/personal/to-a-pe/src')
sys.path.append('C:/USERS/personal/to-a-pe/scripts/upload')

from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models
from upload_utils import unicode_str, lat_lon, dummy

class StopLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Stop',
                                   [('id', unicode_str),
                                    ('name', unicode_str),
                                    ('desc', unicode_str),
                                    ('location', lat_lon), # set lat and lon 
                                    ('_dummy', dummy), #skip longitude
                                   ])

    def create_entity(self, values, key_name=None, parent=None):
        # Set the 4th column as the 4th,5th column (lat/lon)
        # so that we can set one property (location:GeoPt) from two
        # CSV columns.
        values[3] = values[3] + ',' + values[4]
        return super(StopLoader, self).create_entity(values, key_name)

    def generate_key(self, i, values):
        return values[0]

loaders = [StopLoader]
