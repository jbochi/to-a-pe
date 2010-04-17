import sys
sys.path.append('C:/USERS/personal/to-a-pe/src')
sys.path.append('C:/USERS/personal/to-a-pe/scripts/upload')

from google.appengine.ext import db
from google.appengine.tools import bulkloader
import models
from upload_utils import unicode_str

class AgencyLoader(bulkloader.Loader):
    def __init__(self):
        bulkloader.Loader.__init__(self, 'Agency',
                                   [('id', unicode_str),
                                    ('name', unicode_str),
                                    ('url', str),
                                    ('timezone', unicode_str)
                                   ])

    def generate_key(self, i, values):
        return 'agency_%s' % values[0]

loaders = [AgencyLoader]
