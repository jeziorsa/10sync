import datetime
import threading 
import os
import time
import socket
import sys
import BaseHTTPServer
import re
import settings

# ===================================================
# Cleaning

def deletefile(fs):
    try:
        os.remove(fs)
    except:
        print 'Nie ma takiego pliku '.join(fs)


# ===================================================
# simple http server in thread based on BaseHTTPServer module

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("<html><head><title>Sync monitor[%s]</title>" %sync_counter)
        s.wfile.write("<meta http-equiv=\"refresh\" content=\"1\"></head>")
        s.wfile.write("<body><h2>Sync Monitor</h2><p>Current sync status:</p><p>%s</p>" %sync_status)
        s.wfile.write("<p>You accessed path: %s</p>" % s.path)
        s.wfile.write("<p>Licznik: %s</p>" % sync_counter)
        s.wfile.write("</body></html>")

# ===================================================
# Connection class used manage basic socket connection

class Connection(object):

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send(self, message, endwith='\r\n'):
        return self.socket.sendall(message + endwith)

    def receive(self):
        chunks = []
        while True:
            chunk = self.socket.recv(1024)
            chunks.append(chunk)
            if chunk.endswith('\r\n'):
                break
        return ''.join(chunks)

    def send_cmd(self, cmd):
        self.send(cmd)
	print cmd
        return self.receive()

    def storbinary(self, fp):
	blocksize=8192
        while 1:
            buf = fp.read(blocksize)
            if not buf: break
            self.socket.sendall(buf)

    def retrbinary(self, fp):
        while True:
            data = self.socket.recv(8192)
            if not data:
                break
            fp.write(data)
        return data

    def close(self):
        self.socket.close()

class MyHttpServer(threading.Thread):
    def run(self):
        while True:
            httpd.serve_forever()

def parse227(message):
    import re
    kompil = re.compile(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)')
    m = kompil.search(message)
    numbers = m.groups()
    host = '.'.join(numbers[:4])
    port = (int(numbers[4]) << 8) + int(numbers[5])
    return host,port

def login(conn):
    msg = conn.receive()
    print msg
    msg = conn.send_cmd('USER ' + settings.FTP_LOGIN )
    print msg
    msg = conn.send_cmd('PASS ' + settings.FTP_PASSWORD )
    print msg
    msg = conn.send_cmd('SYST')
    print msg
    msg = conn.send_cmd('PWD')
    print msg
    
def makepasv(conn):
    host, port = parse227(conn.send_cmd('PASV'))
    return host, port

def listdirectory(conn):
    msg = conn.send_cmd('TYPE I')
    print msg
    pasv_host, pasv_port = makepasv(conn)
    conn_pasv = Connection(pasv_host, pasv_port)
    msg = conn.send_cmd('LIST')
    print msg
    msg2 = conn_pasv.receive()
    print msg2
    msg = conn.receive()
    print msg
    conn_pasv.close()
    return msg2

def uploadfile(conn, f):
    filename = 'pyftp_upload/'+f
    command = 'STOR '+f
    f = open(filename,"rb")
    msg = conn.send_cmd('TYPE A')
    print msg
    pasv_host, pasv_port = makepasv(conn)
    conn_pasv = Connection(pasv_host, pasv_port)
    msg = conn.send_cmd(command)
    print msg
    msg2 = conn_pasv.storbinary(f)
    print msg2
    conn_pasv.close()
    return msg2

def downloadfile(conn, f):
    filename = f
    command = 'RETR '+f
    f = open(filename,"wb")   
    msg = conn.send_cmd('TYPE A')
    print msg
    pasv_host, pasv_port = makepasv(conn)
    conn_pasv = Connection(pasv_host, pasv_port)
    msg = conn.send_cmd(command)
    print msg
    data = conn_pasv.retrbinary(f)
    conn_pasv.close()
    return msg2

def syncandprint(msg):
    print msg
    return sync_status.join(msg)
    
if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((settings.HOST_NAME, settings.HOST_PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (settings.HOST_NAME, settings.HOST_PORT_NUMBER)
    
    conn = Connection(settings.FTP_HOST, settings.FTP_PORT)
    login(conn)
    msg2 = listdirectory(conn)

    uploadfile(conn,"putty.exe")
    downloadfile(conn,"readme.txt")

    #MyHttpServer = MyHttpServer()
    #MyHttpServer.start()
    
    conn.close()

"""
    lines = msg2.splitlines()

    while True:
        sync_counter=sync_counter+1
        time.sleep(1)

    print "status: "+ sync_status


for n in lines:
    print re.findall(r'\d+', n)
    split = n.split()
    print split[8]

filesLocal = os.listdir(uploadDirectory)
fileLocalDate = []
filesLocal2 = []

for i in range(len(filesLocal)):
    pathname = os.path.join(uploadDirectory, filesLocal[i])
    mtime = os.stat(pathname).st_mtime
    print filesLocal[i]
    print datetime.datetime.fromtimestamp(mtime)
    fileLocalDate.append(time.asctime(time.localtime(mtime)))
    filesLocal2.append((filesLocal[i], datetime.datetime.fromtimestamp(mtime)))
"""
