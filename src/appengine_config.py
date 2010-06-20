import re

def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
    return app

def appstats_normalize_path(path):
    if path.startswith('/ajax/stop_details/'):
        return '/ajax/stop_details/<stop_id>/'
    elif path.startswith('/ajax/get_poly/'):
        return '/ajax/get_poly/<trip_id>/'
    elif path.startswith('/lista') or path.startswith('/busca') or path.startswith('/ajax'):
        return path
    elif re.match('/[^/]+/[^/]+\.kml', path):
        return '/<route_id>/<route_slug>.kml'
    elif re.match('/[^/]+/[^/]+', path):
        return '/<route_id>/<route_slug>/'
    else:
        return path
