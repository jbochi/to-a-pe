import csv
from glineenc import encode_pairs

def main():
    i = open("shapes.txt")
    
    r = csv.reader(i)
    r.next()

    o = open("polylines.txt", "w")

    w = csv.writer(o, dialect='excel', quoting=csv.QUOTE_ALL, lineterminator='\n')
    w.writerow(['shape_id', 'encoded_polyline', 'encoded_levels'])
    
    last_shape = None
    points = []
    polys = {}

    for row in r:
        if row[0] != last_shape:
            if last_shape != None:
                writeRow(w, last_shape, coords)
            last_shape = row[0]
            coords = []
        else:
            coords.append((float(row[1]), float(row[2])))
            
    writeRow(w, last_shape, coords)

def writeRow(writer, shape, coords):
    poly = encode_pairs(coords)
    writer.writerow([shape, poly[0], poly[1]])
    return

main()
