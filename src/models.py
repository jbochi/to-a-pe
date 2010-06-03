from google.appengine.ext import db

from aetycoon import DerivedProperty
from geo.geomodel import GeoModel
from glinedec import decode_line
from util import format_timedelta_seconds, get_words
#from django.template.defaultfilters import slugify
from util import slugify

#http://code.google.com/transit/spec/transit_feed_specification.html#agency_txt___Field_Definitions

class Agency(db.Model):
    id = db.StringProperty() #unique, but not required
    name = db.StringProperty(required=True)
    url = db.LinkProperty(required=True)
    timezone = db.StringProperty(required=True)
    lang = db.StringProperty()
    phone = db.PhoneNumberProperty()


class Service(db.Model):
    "From calendar.txt"
    id = db.StringProperty(required=True) #unique
    monday = db.BooleanProperty(required=True)
    tuesday = db.BooleanProperty(required=True)
    wednesday = db.BooleanProperty(required=True)
    thursday = db.BooleanProperty(required=True)
    friday = db.BooleanProperty(required=True)
    saturday = db.BooleanProperty(required=True)
    sunday = db.BooleanProperty(required=True)
    start_date = db.DateProperty(required=True)
    end_date = db.DateProperty(required=True)


class Stop(GeoModel):
    LOCATION_TYPE_CHOICES = (0, # 0  or blank - Stop. A location where passengers board or disembark from a transit vehicle.
                             1,) # 1 - Station. A physical structure or area that contains one or more stop.

    id = db.StringProperty(required=True) #unique
    code = db.StringProperty() #unique, but not required
    name = db.StringProperty(required=True)
    desc = db.StringProperty()
    zone_id = db.StringProperty()
    url = db.LinkProperty()
    location_type = db.IntegerProperty(choices=LOCATION_TYPE_CHOICES)
    parent_station = db.StringProperty()


class Route(db.Model):
    ROUTE_TYPE_CHOICES = (0, #Tram, Streetcar, Light rail. Any light rail or street level system within a metropolitan area.
                          1, #Subway, Metro. Any underground rail system within a metropolitan area.
                          2, #Rail. Used for intercity or long-distance travel.
                          3, #Bus. Used for short- and long-distance bus routes.
                          4, #Ferry. Used for short- and long-distance boat service.
                          5, #Cable car. Used for street-level cable cars where the cable runs beneath the car.
                          6, #Gondola, Suspended cable car. Typically used for aerial cable cars where the car is suspended from the cable.
                          7) #Funicular. Any rail system designed for steep inclines.


    id = db.StringProperty(required=True) #unique
    agency = db.ReferenceProperty(Agency)
    short_name = db.StringProperty(required=True)
    long_name = db.StringProperty(required=True)
    desc = db.StringProperty()
    type = db.IntegerProperty(required=True)
    url = db.LinkProperty()
    color = db.StringProperty()
    text_color = db.StringProperty()

    def get_absolute_url(self):
        return '/%s/%s' % (self.id, slugify(self.long_name))

    def preview_image_url(self):
        return self.trip_set.get().preview_image_url()

    def search_text(self):
        return "%s - %s" % (self.short_name, self.long_name)

    @DerivedProperty
    def searchable_words(self):
        return get_words(self.search_text())

def search_routes(search_string, offset=0, limit=10):
    base_query = Route.all()
    words = get_words(search_string)
    if search_string.endswith(' '):
        #search routes that have all entire words
        for word in words:
            base_query = base_query.filter('searchable_words =', word)
    elif len(words) == 0:
        return []
    elif len(words) == 1:
        #search by routes that have word starting with text
        word = words[0]
        base_query = base_query.filter('searchable_words >=', word)
        base_query = base_query.filter('searchable_words <', word[:-1] + chr(ord(word[-1]) + 1))
    else:
        #search by routes that have all first words complete and a word starting with last word
        for word in words[:-1]:
            base_query = base_query.filter('searchable_words =', word)
        last_word = words[-1]

        #need to order in memory (exploding indexes)
        routes = [route for route in base_query.fetch(1000) if
                  any([word.startswith(last_word) for word in route.searchable_words])]
        return routes[offset:limit]

    return base_query.fetch(offset=offset, limit=limit)

class Trip(db.Model):
    route = db.ReferenceProperty(Route, required=True)
    service = db.ReferenceProperty(Service, required=True)
    id = db.StringProperty() #unique
    headsign = db.StringProperty()
    short_name = db.StringProperty()
    direction_id = db.BooleanProperty()
    block_id = db.StringProperty()
    shape_id = db.StringProperty()

    shape_encoded_polyline = db.TextProperty()
    shape_encoded_levels = db.TextProperty()
    stops = db.StringListProperty() #list of Stop key names

    def get_absolute_url(self):
        return '/%s/%s' % (self.id, slugify(self.route.long_name))

    def get_shape(self):
        return decode_line(self.encoded_polyline)

    def preview_image_url(self):
        url = 'http://maps.google.com/maps/api/staticmap?size=300x300&sensor=false&path=weight:4'
        url += '|color:' + ('0x%s' % self.route.color if self.route.color else 'blue')
        url += '|enc:' + self.shape_encoded_polyline
        return url

class StopTime():
    PICKUP_DROPOFF_CHOICES = (0, # Regularly scheduled pickup/dropoff
                              1, # No pickup/dropoff available
                              2, # Must phone agency to arrange pickup/dropoff
                              3) # Must coordinate with driver to arrange pickup/dropoff

    trip = db.ReferenceProperty(Trip, required=True)
    arrival_time = db.IntegerProperty() #seconds
    departure_time = db.IntegerProperty() #seconds
    stop = db.ReferenceProperty(Stop, required=True)
    stop_sequence = db.IntegerProperty(required=True)
    pickup_type = db.IntegerProperty(required=True, default=0, choices=PICKUP_DROPOFF_CHOICES)
    drop_off_type = db.IntegerProperty(required=True, default=0, choices=PICKUP_DROPOFF_CHOICES)
    shape_dist_traveled = db.FloatProperty()

class Trips(db.Model):
    "Old model for trips. To be deleted"
    trip_id = db.StringProperty()

    route_id = db.StringProperty()
    agency_id = db.StringProperty()
    route_short_name = db.StringProperty()
    route_long_name = db.StringProperty()
    route_type = db.IntegerProperty()

    service_id = db.StringProperty()
    trip_headsign = db.StringProperty()
    direction_id = db.StringProperty()
    shape_id = db.StringProperty()

    encoded_polyline = db.TextProperty()
    encoded_levels = db.TextProperty()

    starts = db.StringListProperty()

    def get_absolute_url(self):
        return '/%s/%s' % (self.trip_id, slugify(self.route_long_name))

    def route(self):
        return decode_line(self.encoded_polyline)


class Frequency(db.Model):
    trip = db.ReferenceProperty(Trip) #
    trip_id = db.ReferenceProperty(Trips) #old property linking to old model
    start_time = db.IntegerProperty() #seconds since midnight
    end_time = db.IntegerProperty() #seconds since midnight
    headway_secs = db.IntegerProperty()

    def human_headway(self):
        return '%i min' % int(self.headway_secs / 60)

    def interval(self):
        return "%s - %s" % (format_timedelta_seconds(self.start_time),
                            format_timedelta_seconds(self.end_time))
