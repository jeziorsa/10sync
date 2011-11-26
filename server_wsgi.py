from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server
import settings

# A relatively simple WSGI application. It's going to print out the
# environment dictionary after being updated by setup_testing_defaults


def server_wsgi_func(environ, start_response):
    setup_testing_defaults(environ)

    status = '200 OK'
    headers = [('Content-type', 'text/plain')]

    start_response(status, headers)

    ret = ["%s: %s\n" % (key, value)
           for key, value in environ.iteritems()]

    ret ='<html><head><title>Sync monitor</title>\n<meta http-equiv=\"refresh\" content=\"1\"></head>\n<body><h2>Sync Monitor</h2><p>Current sync status:</p><p></p></body></html>    '
    return ret
