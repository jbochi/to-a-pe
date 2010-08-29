import os
from urllib2 import unquote

from django.utils import simplejson
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from models import Route, Stop, Trip, Trips
from search import get_search_list, search_routes
from util import prefetch_refprop

PAGESIZE = 20


class List(webapp.RequestHandler):
    def get(self, route_type=None, route_type_description=None):
        base_query = Route.all().order("id")
        if route_type:
            base_query = base_query.filter('type =', int(route_type))

        page = int(self.request.get('pagina', default_value=1))
        routes = base_query.fetch(PAGESIZE + 1, offset=(page - 1) * PAGESIZE)

        has_next = len(routes) > PAGESIZE

        for route in routes:
            if route.preview_image_url is None:
                route.set_preview_image_url()

        if route_type:
            base_url = '/lista/%s/%s' % (route_type, route_type_description)
        else:
            base_url = '/'

        template_values = {
            'routes': routes,
            'route_type': route_type_description,
            'page': page,
            'back_url': '%s?pagina=%d' % (base_url, page - 1) if page > 1 else None,
            'next_url': '%s?pagina=%d' % (base_url, page + 1) if has_next else None,
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
        self.response.out.write(template.render(path, template_values))


class Search(webapp.RequestHandler):
    def get(self, bookmark=None):
        search_string = self.request.get('q')
        routes = search_routes(search_string, limit=PAGESIZE)

        for route in routes:
            if route.preview_image_url is None:
                route.set_preview_image_url()

        template_values = {
            'search': search_string.encode('utf-8'),
            'routes': routes,
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/search_results.html')
        self.response.out.write(template.render(path, template_values))


class AutoCompleteData(webapp.RequestHandler):
    def get(self, bookmark=None):
        self.response.out.write(get_search_list())


class RouteHandler(webapp.RequestHandler):
    def get(self, route_id=None, description=None):
        route = Route.get_by_key_name(unquote(route_id))
        if route:
            trips = route.trip_set.fetch(1000)
            trip_id = self.request.get('trip') or trips[0].id

            trip = None
            for trip_loop in trips:
                if trip_loop.id == trip_id:
                    trip = trip_loop
                    break

            if trip is None:
                trip = trips[0]

            similars = Trip.get_by_key_name(trip.similars)

            template_values = {'route': route,
                               'trip': trip,
                               'trips': trips,
                               'similars': similars }
            path = os.path.join(os.path.dirname(__file__), 'templates/route.html')
            self.response.out.write(template.render(path, template_values))
        else:
            #Old urls used trip id. If this is the case, redirect
            trip_id = route_id
            trip = Trips.all().filter("trip_id =", unquote(trip_id)).get()

            if trip:
                route = Route.get_by_key_name(trip.route_id)
                if route:
                    self.redirect(route.get_absolute_url(), permanent=True)
                    return

            #Not found
            self.error(404)
            self.response.out.write('404 - Pagina nao encontrada')


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
        if stop:
            trips = Trip.all().filter('stops =', stop_id).fetch(1000)
            prefetch_refprop(trips, Trip.route)
            template_values = {'stop': stop, 'trips': trips}
            path = os.path.join(os.path.dirname(__file__), 'templates/stop_details.html')
            self.response.out.write(template.render(path, template_values))
        else:
            self.error(404)
            return self.response.out.write('Erro - Pagina nao encontrada')


class KML(webapp.RequestHandler):
    def get(self, trip_id, trip_headsign):
        trip_id = unquote(trip_id)
        trip = Trip.get_by_key_name('trip_' + trip_id)
        if trip:
            path = os.path.join(os.path.dirname(__file__), 'templates/trip.kml')
            template_values = {
                'trip': trip,
            }
            self.response.headers['Content-Type'] = 'application/vnd.google-earth.kml+xml'
            self.response.out.write(template.render(path, template_values))
        else:
            self.error(404)
            return self.response.out.write('Erro - Pagina nao encontrada')

class Sitemap(webapp.RequestHandler):
    def get(self):
        from util import slugify

        def absolute_url(route):
            return 'http://www.toape.com.br/%s/%s' % (route.id, slugify(route.long_name))

        routes = Route.all().fetch(2000)
        urls = ['http://www.toape.com.br']
        urls += [absolute_url(route) for route in routes]

        self.response.headers['Content-Type'] = "text/plain"
        self.response.out.write('\n'.join(urls))

application = webapp.WSGIApplication([('/', List),
                                    ('/sitemap.txt', Sitemap),
                                    ('/lista', List),
                                    ('/lista/(\d+)/(.*)', List),
                                    ('/busca', Search),
                                    ('/ajax/stop_details/(.*)/', GetStopDetails),
                                    ('/ajax/get_poly/(.*)', GetPoly),
                                    ('/ajax/autocomplete', AutoCompleteData),
                                    ('/(.*)/(.*).kml', KML),
                                    ('/(.*)/(.*)', RouteHandler), ],
                                   debug=True)

def main():
    run_wsgi_app(application)

if __name__ == '__main__':
    main()
