from google.appengine.ext import db

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
  
  
class Frequency(db.Model):
    trip_id = db.ReferenceProperty(Trips)
    start_time = db.IntegerProperty()
    end_time = db.IntegerProperty()
    headway_secs = db.IntegerProperty()


  