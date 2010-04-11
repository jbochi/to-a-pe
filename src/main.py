import os
from urllib2 import unquote
import wsgiref.handlers

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models import Trips
from models import slugify

from django.utils import simplejson
from search import get_unique_words

PAGESIZE = 25

class List(webapp.RequestHandler):
    def get(self):
        next = None
        bookmark = self.request.get('bookmark')

        if bookmark:
            trips = Trips.all().order("route_id").filter('route_id >=', bookmark).fetch(PAGESIZE + 1)
        else:
            trips = Trips.all().order("route_id").fetch(PAGESIZE + 1)

        if len(trips) == PAGESIZE + 1:
            next = trips[-1].route_id
            trips = trips[:PAGESIZE]

        template_values = {
            'trips': trips,
            'next': next,
            'ida': "1", #1 = ida (going); 2 = volta (returning)
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
        self.response.out.write(template.render(path, template_values))

class Search(webapp.RequestHandler):
    def get(self, bookmark=None):
        next = None
        search_string = self.request.get('q')
        offset = self.request.get('offset')

        if offset.isdigit():
            offset = int(offset)
            previous = max(offset - PAGESIZE, -1)
        else:
            previous = -1
            offset = 0

        words = get_unique_words(search_string)
        where = 'AND'.join([" starts = '%s' " % word for word in words])

        query = db.GqlQuery("SELECT * FROM Trips WHERE %s" % where)
        trips = query.fetch(PAGESIZE + 1, offset)

        if len(trips) == PAGESIZE + 1:
            next = offset + PAGESIZE
            trips = trips[:PAGESIZE]

        template_values = {
            'search': search_string.encode('utf-8'),
            'trips': trips,
            'next': next,
            'previous': previous
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/search_results.html')
        self.response.out.write(template.render(path, template_values))

class Autocomplete(webapp.RequestHandler):
    def get(self, bookmark=None):
        search_string = self.request.get('q')
        limit = self.request.get('limit')

        words = get_unique_words(search_string)
        where = 'AND'.join([" starts = '%s' " % word for word in words])
        query = db.GqlQuery("SELECT * FROM Trips WHERE %s" % where)

        trips = query.fetch(int(limit))

        def format(trip):
            return "%s - %s - Sentido: %s|/%s/%s" % (trip.route_id, trip.route_long_name, trip.trip_headsign,
                                                     trip.trip_id, trip.route_long_name.replace('/', '-').replace(' ', '-'))

        text = '\n'.join([format(trip) for trip in trips])
        self.response.out.write(text)

class Trip(webapp.RequestHandler):
    def get(self, trip_id=None, description=None):
        trip_id = unquote(trip_id)

        if description != None:
            #redirect old links that were not slugfied (SEO)
            slug = slugify(unquote(description))
            if slug != description:
                self.redirect("/%s/%s" % (trip_id, slug), permanent=True)

        trip = Trips.all().filter("trip_id =", trip_id).get()
        frequencies = trip.frequency_set
        template_values = {
            'trip': trip,
            'frequencies': frequencies,
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/trip.html')
        self.response.out.write(template.render(path, template_values))

class GetPoly(webapp.RequestHandler):
    def get(self, trip_id):
        "Returns encoded polyline path from trip_id"

        trip_id = unquote(trip_id)
        trip = Trips.all().filter("trip_id =", trip_id).get()
        if trip:
            data = {'points': trip.encoded_polyline, 'levels': trip.encoded_levels}
            self.response.out.write(simplejson.dumps(data))

class KML(webapp.RequestHandler):
    def get(self, trip_id, file):
        trip_id = unquote(trip_id)
        path = os.path.join(os.path.dirname(__file__), 'templates/trip.kml')
        trip = Trips.all().filter("trip_id =", trip_id).get()
        template_values = {
            'trip': trip,
        }

        self.response.headers['Content-Type'] = 'application/vnd.google-earth.kml+xml'
        self.response.out.write(template.render(path, template_values))


def main():
    application = webapp.WSGIApplication([('/', List),
                                        ('/lista', List),
                                        ('/busca', Search),
                                        ('/ajax/get_poly/(.*)', GetPoly),
                                        ('/ajax/autocomplete', Autocomplete),
                                        ('/(.*)/(.*).kml', KML),
                                        ('/(.*)/(.*)', Trip), ],
                                       debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
