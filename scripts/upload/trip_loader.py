import sys
sys.path.append('C:/USERS/personal/to-a-pe/src')
sys.path.append('C:/USERS/personal/to-a-pe/scripts/upload')

from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models
from upload_utils import unicode_str, get_service, get_route
from get_polylines import get_polys

class TripLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Trip',
                                   [('route', get_route),
                                    ('service', get_service),
                                    ('id', unicode_str),
                                    ('headsign', unicode_str),
                                    ('direction_id', bool), #skip longitude
                                    ('shape_id', unicode_str),
                                   ])

    def handle_entity(self, entity):
        poly, levels = polys[entity.shape_id]
        entity.shape_encoded_polyline = poly
        entity.shape_encoded_levels = levels
        return entity

    def generate_key(self, i, values):
        return 'trip_%s' % values[2] #trip_id

loaders = [TripLoader]
polys = get_polys('C:/USERS/personal/offline_toape/transit/google_transit_20100417/shapes.txt')