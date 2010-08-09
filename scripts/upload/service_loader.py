import sys
sys.path.append('d:/juadasil/personal/to-a-pe/src')
sys.path.append('d:/juadasil/personal/to-a-pe/scripts/upload')

from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models
from upload_utils import str2date, unicode_str

class ServiceLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Service',
                                   [('id', unicode_str),
                                    ('monday', bool),
                                    ('tuesday', bool),
                                    ('wednesday', bool),
                                    ('thursday', bool),
                                    ('friday', bool),
                                    ('saturday', bool),
                                    ('sunday', bool),
                                    ('start_date', str2date),
                                    ('end_date', str2date),
                                   ])

    def generate_key(self, i, values):
        return values[0]

loaders = [ServiceLoader]
