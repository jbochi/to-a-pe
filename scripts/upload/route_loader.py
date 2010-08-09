import sys
sys.path.append('d:/juadasil/personal/to-a-pe/src')
sys.path.append('d:/juadasil/personal/to-a-pe/scripts/upload')

from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models
from upload_utils import unicode_str, get_agency

class RouteLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Route',
                                   [('id', unicode_str),
                                    ('agency', get_agency),
                                    ('short_name', unicode_str),
                                    ('long_name', unicode_str),
                                    ('type', int),
                                    ('color', str),
                                   ])

    def generate_key(self, i, values):
        return values[0]

loaders = [RouteLoader]
