import csv
import numpy
import matplotlib.pyplot as plt

from matplotlib import colors, ticker

def read_points(path='stops.txt', lat='stop_lat', lon='stop_lon'):
    f = open(path)
    reader = csv.DictReader(f)
    points = []
    for row in reader:
        points.append((float(row[lat]), float(row[lon])))
    f.close()
    return points

def split(a):
    return [ax.flatten() for ax in numpy.hsplit(a, 2)]

def histogram(a, bins=100):
    lat, lon = split(a)
    return numpy.histogram2d(lat, lon, normed=True, bins=bins)

def plot_histogram(a, bins=100):
    H, xedges, yedges = histogram(a, bins)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]

    H = H.transpose()[::-1] #histogram does not follow the Cartesian convention
    fig = plt.figure()
    ax = fig.add_subplot(111, frameon=False, xticks=[], yticks=[])
    plt.imsave(arr=H, fname='paths3.png', cmap=plt.cm.hot)
    
    #ax.imshow(H, extent=extent, cmap=plt.cm.hot)    
    #z = numpy.ma.masked_where(H<= 0, H)
    #cs = plt.contourf(xedges[:-1], yedges[:-1], z, locator=ticker.LogLocator())
    #plt.show()
    #plt.savefig('paths3.png')
       
def plot_points(a):
    plt.close()
    lat, lon = split(a)
    plt.plot(lat, lon, 'ro')
    plt.show()

#points = read_points('shapes.txt', 'shape_pt_lat', 'shape_pt_lon')
points = read_points()
a = numpy.array(points)
fig = plt.figure(num=None, figsize=(8, 6), dpi=500, facecolor='w', edgecolor='k') 
ax = fig.add_subplot(111, frameon=False, xticks=[], yticks=[])
x, y = split(a)
plt.plot(x, y, 'ro', [-24.0, -23.0, -23.0], [-47.0, -47.0, -46.0], markersize=2)
plt.axis([-24.0, -23.0, -47.0, -46.0])
plt.savefig('points.png')
#plot_histogram(a, 300)
