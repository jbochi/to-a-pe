import csv
from upload_utils import unicode_str

def get_stops(path):
    "Returns a dict of lists: trip_id -> [stop_key_names]"

    i = open(path)
    r = csv.reader(i)
    r.next() #skips header

    last_trip = None
    path = []
    stops = {}

    for row in r:
        if row[0] != last_trip:
            if last_trip != None:
                stops[unicode_str(last_trip)] = path[:]
            last_trip = row[0]
            path = []
        else:
            path.append(get_stop_key_name(row[3])) #stop_id

    stops[unicode_str(last_trip)] = path[:]

    return stops

def get_stop_key_name(stop_id):
    return str(stop_id)
