import csv
from glineenc import encode_pairs

def get_polys(path):
    "Returns a dict of tuples: shape_id -> (encoded polyline, encoded levels)"

    i = open(path)
    r = csv.reader(i)
    r.next() #skips header

    last_shape = None
    points = []
    polys = {}

    for row in r:
        if row[0] != last_shape:
            if last_shape != None:
                polys[last_shape] = encode_pairs(coords)
            last_shape = row[0]
            coords = []
        else:
            coords.append((float(row[1]), float(row[2])))

    polys[last_shape] = encode_pairs(coords)

    return polys
