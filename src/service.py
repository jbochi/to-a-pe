"""Service /s/* request handlers."""

import os
import sys
import wsgiref.handlers

from django.utils import simplejson

from google.appengine.ext import webapp
from geo import geotypes

from models import Stop

def _merge_dicts(*args):
    """Merges dictionaries right to left. Has side effects for each argument."""
    return reduce(lambda d, s: d.update(s) or d, args)


class SearchService(webapp.RequestHandler):
    """Handler for public school search requests."""
    def get(self):
        def _simple_error(message, code=400):
            self.error(code)
            self.response.out.write(simplejson.dumps({
                'status': 'error',
                'error': { 'message': message },
                'results': []
            }))
            return None

        self.response.headers['Content-Type'] = 'application/json'
        query_type = self.request.get('type')

        if not query_type in ['proximity', 'bounds']:
            return _simple_error('type parameter must be '
                                 'one of "proximity", "bounds".',
                                 code=400)

        if query_type == 'proximity':
            try:
                center = geotypes.Point(float(self.request.get('lat')),
                                        float(self.request.get('lon')))
            except ValueError:
                return _simple_error('lat and lon parameters must be valid latitude '
                                     'and longitude values.')
        elif query_type == 'bounds':
            try:
                bounds = geotypes.Box(float(self.request.get('north')),
                                    float(self.request.get('east')),
                                    float(self.request.get('south')),
                                    float(self.request.get('west')))
            except ValueError:
                return _simple_error('north, south, east, and west parameters must be '
                                 'valid latitude/longitude values.')

        max_results = 100
        if self.request.get('maxresults'):
            max_results = int(self.request.get('maxresults'))

        max_distance = 80000 # 80 km ~ 50 mi
        if self.request.get('maxdistance'):
            max_distance = float(self.request.get('maxdistance'))


        try:
            # Can't provide an ordering here in case inequality filters are used.
            base_query = Stop.all()

            # Perform proximity or bounds fetch.
            if query_type == 'proximity':
                results = Stop.proximity_fetch(
                    base_query,
                    center, max_results=max_results, max_distance=max_distance)
            elif query_type == 'bounds':
                results = Stop.bounding_box_fetch(
                    base_query,
                    bounds, max_results=max_results)

            results_obj = [
                {
                    'lat': result.location.lat,
                    'lng': result.location.lon,
                }
                for result in results
            ]

            self.response.out.write(simplejson.dumps({
                'status': 'success',
                'results': results_obj
            }))
        except:
            return _simple_error(str(sys.exc_info()[1]), code=500)

def main():
    application = webapp.WSGIApplication([
          ('/s/search', SearchService),
        ],
          debug=('Development' in os.environ['SERVER_SOFTWARE']))
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
