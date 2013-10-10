import sys,os,ftplib,socket
import time
import ttk
from tkFileDialog import askopenfilename
import pika
import yaml


host_ip = '140.114.91.91'
user_name =
user_pwd =
temp_buffer = 8192
rabbitmq_host = '140.114.XX.XX'
key = 'db_update'

class FTP_upload():

    def __init__(self):
        print 'Start uploading'

    def ftp_connection(self):
        try :
            connection = ftplib.FTP(host_ip)
            print 'connection access'
        except :
            print 'Connection failed'
            return (0,'Connection failed')
        else :
            try :
                connection.login(user_name, user_pwd)
                print 'Login access'
            except :
                print 'Login failed'
                return (0,'Login failed')
            else :
                return (1,connection)

    def ftp_disconnection(self, connection):
        connection.quit()

    def upload_image(self, f_path, pass_data, message = None, root = None):
        status, connection = self.ftp_connection()
        global stop_signal
        stop_signal = 0

        if status != 1:
            self.ftp_disconnection(connection)
            return connection

        if not os.path.exists(f_path):
            print 'No file'
            return 'No file'


        #get file name from path
        file_name = self.get_file_name(f_path)
        print file_name

        #set the remote path
        connection.cwd('/var/lib/libvirt/ftp-image')
        #get remote file size
        try :
            ftp_file_size = connection.size(file_name)
            print 'get file size %s' % ftp_file_size
            get_size = True
        except :
            print 'No file in this path'
            get_size = False

        if get_size == False :
            ftp_file_size = 0

        #get local file size
        local_file_size = os.stat(f_path).st_size
        print "local  size : %s  \nremote size : %s" % (local_file_size, ftp_file_size)

        if local_file_size == ftp_file_size :
            print 'Already having same file.'
            return 'Already having same file.'

        elif ftp_file_size < local_file_size :
            all_data = open(f_path, 'rb')
            all_data.seek(ftp_file_size)
            connection.voidcmd('TYPE I')
            print '123'
            data_socket,chechsize = connection.ntransfercmd("STOR "+file_name, ftp_file_size)

            cont_size = ftp_file_size
            i = 0
            while True :
                if stop_signal == 1:
                    break
                try :
                    temp_buffer = all_data.read(4*1024)
                    i = i + 1
                    print "%s : %s" % (i, len(temp_buffer))
                    if len(temp_buffer) == 0 :
                        print 'finish'
                        print pass_data
                        self.send_update_info(pass_data)
                        break
                    data_socket.sendall(temp_buffer)
                    cont_size = cont_size + len(temp_buffer)
                    print 'uploading %.2f%%' % (float(cont_size)/local_file_size*100)
                    temp_num = int(float(cont_size)/local_file_size*36)
                    temp_num_2 = int(90 - temp_num*2.5)
                    progress = "%5.2f%%|" % (float(cont_size)/local_file_size*100) + '>'*temp_num + ' '*temp_num_2   + '|'
                    if message != None:
                        message.set(progress)
                        #root.update_idletasks()
                except KeyboardInterrupt :
                    print 'Interrupt'
                    data_socket.close()
                    self.ftp_disconnection(connection)
                    all_data.close()
                    return 'Interrupt'


        data_socket.close()
        self.ftp_disconnection(connection)
        all_data.close()
        if stop_signal == 0:
            return (0,'uploading ok')
        else:
            return (1,'uploading suspend')

    def get_file_name(self, path):
        position = path.rfind('/')
        return path[position+1:]

    def change_stop_signal(self):
          global stop_signal
          stop_signal = 1

    def conn_server(self):
        conn_param = pika.ConnectionParameters(host=rabbitmq_host)
        connect = pika.BlockingConnection(conn_param)
        channel = connect.channel()
        return channel,connect

    def send_update_info(self, msg):
        channel,connect = self.conn_server()
        msg = yaml.dump(msg)
        channel.basic_publish( exchange='db_client', routing_key= key, body= msg )


if __name__ == '__main__':
    start = FTP_upload()
    print start.upload_image('/Users/dosa/Desktop/test.png')



