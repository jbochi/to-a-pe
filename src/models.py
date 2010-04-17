from datetime import timedelta
import re
from google.appengine.ext import db
from glinedec import decode_line

class Trips(db.Model):
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

    def url(self):
        return '/%s/%s' % (self.trip_id, slugify(self.route_long_name))

    def route(self):
        return decode_line(self.encoded_polyline)


class Frequency(db.Model):
    trip_id = db.ReferenceProperty(Trips)
    start_time = db.IntegerProperty() #seconds since midnight
    end_time = db.IntegerProperty() #seconds since midnight
    headway_secs = db.IntegerProperty()

    def human_headway(self):
        return '%i min' % int(self.headway_secs / 60)

    def interval(self):
        return "%s - %s" % (format_timedelta_seconds(self.start_time),
                            format_timedelta_seconds(self.end_time))


def slugify(text):
    text = text.replace("'", "")
    text = re.subn(r'(\s|\.|\(|\)|\/|\\)', ' ', text)[0]
    text = text.strip().lower()
    text = re.subn(r'(-|\s)+', '-', text)[0]
    return text

def format_timedelta_seconds(timedelta_seconds):
    return str(timedelta(seconds=timedelta_seconds))[:-3]
