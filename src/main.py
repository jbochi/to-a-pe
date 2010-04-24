import os
from urllib2 import unquote
import wsgiref.handlers

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext import db

from models import Route, Stop, Trip, Trips
from util import slugify

from django.utils import simplejson
from search import get_unique_words

PAGESIZE = 20

class List(webapp.RequestHandler):
    def get(self):
        base_query = Route.all().order("id")
        page = int(self.request.get('pagina', default_value=1))
        n_pages = base_query.count()
        routes = base_query.fetch(PAGESIZE, offset=(page - 1) * PAGESIZE)
        template_values = {
            'routes': routes,
            'page': page,
            'back_url': '/?pagina=%d' % (page - 1) if page > 1 else None,
            'next_url': '/?pagina=%d' % (page + 1) if page < n_pages else None,
            'n_pages': n_pages
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
        self.response.out.write(template.render(path, template_values))

class ListByType(webapp.RequestHandler):
    def get(self, route_type, description):
        routes = Route.all().filter('type =', int(route_type)).order("id").fetch(PAGESIZE + 1)
        template_values = {
            'routes': routes,
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
        limit = int(self.request.get('limit'))

        words = get_unique_words(search_string)
        query = Trips.all()
        for word in words:
            query = query.filter('starts =', word)
        trips = query.fetch(limit=limit)

        def format(trip):
            return "%s - %s - Sentido: %s|/%s/%s" % (trip.route_id, trip.route_long_name, trip.trip_headsign,
                                                     trip.trip_id, trip.route_long_name.replace('/', '-').replace(' ', '-'))

        text = '\n'.join([format(trip) for trip in trips])
        self.response.out.write(text)

class RouteHandler(webapp.RequestHandler):
    def get(self, route_id=None, description=None):
        route = Route.get_by_key_name(unquote(route_id))
        if not route: #redirect old links that were not slugfied (SEO)
            trip_id = route_id
            trip = Trips.all().filter("trip_id =", unquote(trip_id)).get()

            if not trip:
                self.error(404)
                self.response.out.write('404 - Pagina nao encontrada')
            else:
                #redirect old links that were not slugfied (SEO)
                if description != slugify(trip.route_long_name):
                    self.redirect(trip.get_absolute_url(), permanent=True)
                else:
                    template_values = {'trip': trip,
                                       'frequencies': trip.frequency_set, }
                    path = os.path.join(os.path.dirname(__file__), 'old_templates/trip.html')
                    self.response.out.write(template.render(path, template_values))
        else:
            template_values = {'route': route,
                               'trips': route.trip_set.fetch(1000), }
            path = os.path.join(os.path.dirname(__file__), 'templates/route.html')
            self.response.out.write(template.render(path, template_values))

class GetPoly(webapp.RequestHandler):
    def get(self, trip_id):
        "Returns encoded polyline path from trip_id"

        trip_id = unquote(trip_id)
        trip = Trip.get_by_key_name('trip_' + trip_id)
        stops = Stop.get_by_key_name(trip.stops)
        stops = filter(lambda s: s is not None, stops)
        stops = filter(lambda s: s.location is not None, stops)
        def serializable_stop(stop):
            return (stop.id,
                    stop.location.lat,
                    stop.location.lon,
                    stop.name)

        stop_locations = [serializable_stop(stop) for stop in stops]

        if trip:
            data = {'points': trip.shape_encoded_polyline,
                    'levels': trip.shape_encoded_levels,
                    'color': trip.route.color,
                    'stops': stop_locations}
            self.response.out.write(simplejson.dumps(data))

class GetStopDetails(webapp.RequestHandler):
    def get(self, stop_id):
        stop_id = unicode(unquote(stop_id))
        stop = Stop.get_by_key_name(stop_id)
        trips = Trip.all().filter('stops =', stop_id).fetch(1000)
        if stop:
            template_values = {'stop': stop, 'trips': trips}
            path = os.path.join(os.path.dirname(__file__), 'templates/stop_details.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.error(404)
            return self.response.out.write('Erro')


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
                                        ('/lista/(\d+)/(.*)', ListByType),
                                        ('/busca', Search),
                                        ('/ajax/stop_details/(.*)/', GetStopDetails),
                                        ('/ajax/get_poly/(.*)', GetPoly),
                                        ('/ajax/autocomplete', Autocomplete),
                                        ('/(.*)/(.*).kml', KML),
                                        ('/(.*)/(.*)', RouteHandler), ],
                                       debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
