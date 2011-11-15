from wsgiref.util import setup_testing_defaults
from wsgiref.simple_server import make_server

# A relatively simple WSGI application. It's going to print out the
# environment dictionary after being updated by setup_testing_defaults

"""
def server_wsgi(environ, start_response)
    setup_testing_defaults(environ)
    status = '200 OK'


        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("<html><head><title>Sync monitor[%s]</title>" %sync_counter)
        s.wfile.write("<meta http-equiv=\"refresh\" content=\"1\"></head>")
        s.wfile.write("<body><h2>Sync Monitor</h2><p>Current sync status:</p><p>%s</p>" % sync_status)
        s.wfile.write("<p>You accessed path: %s</p>" % s.path)
        s.wfile.write("<p>Licznik: %s</p>" % sync_counter)
        s.wfile.write("</body></html>")


    headers = [('Content-type', 'textplain')]

    start_response(status, headers)

    ret = [%s %sn % (key, value)
           for key, value in environ.iteritems()]
    return ret

httpd = make_server('', 80, server_wsgi)
#print Serving on port 80...
#httpd.serve_forever()

"""

