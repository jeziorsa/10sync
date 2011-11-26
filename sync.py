import datetime
import threading 
import os
import time
import socket
import sys
import BaseHTTPServer
import re
import settings
import server_wsgi
import re

# ===================================================
# Connection class used manage basic socket connection

#TODO: 
# 1. serwerek
# 2. string > data
# 3. porownywanie i logika wysylania
# 4. obsluga bledow

class File_and_data(object):

    def __init__(self, file_name_external, file_data_external):
        self.file_name = file_name_external
        self.file_data = file_data_external



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
	print ">>> " + cmd
        msg = self.receive()
        print "<<< " + msg
        return msg

    def storbinary(self, fp):
	blocksize = 8192
        while True:
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

    def ftp_parse227(self, message):
        kompil = re.compile(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)')
        m = kompil.search(message)
        numbers = m.groups()
        host = '.'.join(numbers[:4])
        port = (int(numbers[4]) << 8) + int(numbers[5])
        return host, port

    def ftp_login(self, conn):
        msg = conn.receive()
        msg = conn.send_cmd('USER ' + settings.FTP_LOGIN )
        msg = conn.send_cmd('PASS ' + settings.FTP_PASSWORD )
        msg = conn.send_cmd('SYST')
        msg = conn.send_cmd('PWD')
        return msg
    
    def ftp_makepasv(self, conn):
        host, port = self.ftp_parse227(conn.send_cmd('PASV'))
        return host, port

    def ftp_list_directory(self, conn):
        msg = conn.send_cmd('TYPE I')
        pasv_host, pasv_port = self.ftp_makepasv(conn)
        conn_pasv = Connection(pasv_host, pasv_port)
        msg = conn.send_cmd('LIST')
        msg2 = conn_pasv.receive()
        msg = conn.receive()
        conn_pasv.close()
        return msg2

    def ftp_upload_file(self, conn, f):
        #TODO: change to variable and find better way to add file name to string
        filename = 'pyftp_upload/'+f
        command = 'STOR '+f
        f = open(filename,"rb")
        msg = conn.send_cmd('TYPE A')
        pasv_host, pasv_port = self.ftp_makepasv(conn)
        conn_pasv = Connection(pasv_host, pasv_port)
        msg = conn.send_cmd(command)
        msg2 = conn_pasv.storbinary(f)
        conn_pasv.close()
        #TODO: check os "close" is good way to close file
        f.close()
        return msg2

    def ftp_download_file(self, conn, f):
        filename = f
        command = 'RETR '+f
        f = open(filename,"wb")   
        msg = conn.send_cmd('TYPE A')
        pasv_host, pasv_port = self.ftp_makepasv(conn)
        conn_pasv = Connection(pasv_host, pasv_port)
        msg = conn.send_cmd(command)
        data = conn_pasv.retrbinary(f)
        conn_pasv.close()
        return msg

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    #httpd = server_class((settings.HOST_NAME, settings.HOST_PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (settings.HOST_NAME, settings.HOST_PORT_NUMBER)
    
    conn = Connection(settings.FTP_HOST, settings.FTP_PORT)
    msg = conn.ftp_login(conn)
    msg_list_remote_files = conn.ftp_list_directory(conn)
    #msg = names_dates(msg)
    #msg = conn.send_cmd('MDTM putty.exe')
    #print msg
    #msg = month_to_numer('Nfv')
    #print msg

    list_local_files = os.listdir(settings.uploadDirectory)
    files_local = []

    for i in range(len(list_local_files)):
        pathname = os.path.join(settings.uploadDirectory, list_local_files[i])
        filename = list_local_files[i]
        mtime = os.stat(pathname).st_mtime
        filedata =  datetime.datetime.fromtimestamp(mtime)
        #print filedata
        pliczorek = File_and_data(filename, filedata)
        files_local.append(pliczorek)
        del pliczorek

    #print files_local

    files_remote = []
    
    list_remote_files = msg_list_remote_files.splitlines()
    
    for i in range(len(list_remote_files)):
        #print list_remote_files[i]
        #filename = list_remote_files[i]
        splittedline = list_remote_files[i].split()
        #print splittedline[8]
        command_msg = 'MDTM '+ splittedline[8]
        filename = splittedline[8]
        msg = conn.send_cmd(command_msg)
        try:
            str_dt = '%s %s %s %s %s' % (msg[4:8], msg[8:10], msg[10:12], msg[12:14], msg[14:16])
            dt = datetime.datetime.strptime(str_dt, '%Y %m %d %H %M')
            #print dt
        except ValueError:
            print 'wywalenie spodowal' 
        pliczorek = File_and_data(filename, dt)
        files_remote.append(pliczorek)
        del pliczorek

    #print files_remote[0].file_name
    print '======\n\n'

    for i in range(len(files_local)):
        for j in range(len(files_remote)):
            print files_local[i].file_name
            print files_remote[j].file_name
            if files_remote[j].file_name==files_local[i].file_name:
                print files_remote[j].file_name + ' jest lokalnie i na serwerze'
                print files_remote[j].file_data
                print files_local[i].file_data
                if files_remote[j].file_data>files_local[i].file_data:
                    print 'plik na serwerze jest nowszy'
        print '\n'
    
    #print pliczorek
    #msg = conn.ftp_upload_file(conn,"putty.exe")
    #msg = conn.ftp_download_file(conn,"readme.txt")

    #MyHttpServer = MyHttpServer()
    #MyHttpServer.start()
    
    conn.close()
