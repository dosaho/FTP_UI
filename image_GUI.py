from Tkinter import *
from tkFileDialog import askopenfilename
import ImageTk
import ttk
from image_ftp_upload import FTP_upload
import thread
import pika
import yaml

rabbitmq_host = '140.114.91.91'
key = 'db_client'

class GUIDemo(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        self.temp_path = None

        self.bg = ImageTk.PhotoImage(file='SSLab.png')
        self.bgText = Label(self, image=self.bg, )
        self.bgText.grid(row=0, column=2, rowspan=8, columnspan=2, sticky=W+E+S+N)

        self.UserText = Label(self)
        self.UserText["text"] = "User: "
        self.UserText.grid(row=0, column=0, sticky=W)
        self.UserField = Entry(self)
        self.UserField["width"] = 20
        self.UserField.grid(row=0, column=1, sticky=W)

        self.PasswdText = Label(self)
        self.PasswdText["text"] = "Passwd:"
        self.PasswdText.grid(row=1, column=0, sticky=W)
        self.PasswdField = Entry(self)
        self.PasswdField["show"] = '*'
        self.PasswdField["width"] = 20
        self.PasswdField.grid(row=1, column=1, sticky=W)

        #self.ImageText = Label(self)
        #self.ImageText["text"] = "Image Name: "
        #self.ImageText.grid(row=2, column=0, sticky=W)
        #self.ImageField = Entry(self)
        #self.ImageField["width"] = 20
        #self.ImageField.grid(row=2, column=1, sticky=W)

        self.osText = Label(self)
        self.osText["text"] = "OS Version:"
        self.osText.grid(row=3, column=0, sticky=W)
        self.oscombobox = ttk.Combobox(self)
        self.oscombobox['state']='readonly'
        self.oscombobox.set('What OS...?')
        self.oscombobox.grid(row=3, column=1, sticky=W)
        self.oscombobox['values'] = ['Windows_XP', 'Windows_7', 'Windows_8', 'Ubuntu', 'CentOS', 'Other..']
        self.oscombobox['width'] = 15

        self.typeText = Label(self)
        self.typeText["text"] = "Image Type:"
        self.typeText.grid(row=4, column=0, sticky=W)
        self.typecombobox = ttk.Combobox(self)
        self.typecombobox['state']='readonly'
        self.typecombobox.set('What Type...?')
        self.typecombobox.grid(row=4, column=1, sticky=W)
        self.typecombobox['values'] = ['raw', 'qcow2']
        self.typecombobox['width'] = 15

        self.privateText = Label(self)
        self.privateText["text"] = "Is Private:"
        self.privateText.grid(row=5, column=0, sticky=W)
        self.privatecombobox = ttk.Combobox(self)
        self.privatecombobox['state']='readonly'
        self.privatecombobox.set('public')
        self.privatecombobox.grid(row=5, column=1, sticky=W)
        self.privatecombobox['values'] = ['private', 'public']
        self.privatecombobox['width'] = 15

        self.accountText = Label(self)
        self.accountText["text"] = "default account:"
        self.accountText.grid(row=6, column=0, sticky=W)
        self.accountField = Entry(self)
        self.accountField["width"] = 20
        self.accountField.grid(row=6, column=1, sticky=W)

        self.dpasswdText = Label(self)
        self.dpasswdText["text"] = "default passwd:"
        self.dpasswdText.grid(row=7, column=0, sticky=W)
        self.dpasswdField = Entry(self)
        self.dpasswdField["width"] = 20
        self.dpasswdField.grid(row=7, column=1, sticky=W)

        self.file_path=StringVar()

        self.pathText = Label(self)
        self.pathText["text"] = "Image Path:"
        self.pathText.grid(row=8, column=0, sticky=W)        
        self.pathField = Entry(self,textvariable=self.file_path)
        self.pathField["width"] = 35
        self.pathField.grid(row=8, column=1, columnspan=2, sticky=W)
        self.pathbutton=Button(self, command= self.getpath)
        self.pathbutton['text']='path...'
        self.pathbutton.grid(row=8, column=3, sticky=W, pady=5, padx=5)

        self.message=StringVar()
        progress = "%5.2f%%|" % 0 + '>'*0 + ' '*90 + '|'
        self.message.set(progress)
        self.printMessage= Message(self, relief=RAISED, justify=LEFT, width=500,textvariable=self.message)
        self.printMessage.grid(row=9, columnspan=3, sticky=W)
        
        self.printbutton=Button(self, command=self.printall)
        self.printbutton['text']='Upload'
        self.printbutton.grid(row=10, columnspan=1, rowspan=2, sticky=W, pady=5, padx=5)

        self.printbutton=Button(self, command=self.default_info)
        self.printbutton['text']='Default'
        self.printbutton.grid(row=10, column=1, columnspan=1, rowspan=2, sticky=W, pady=5, padx=5)

        self.printbutton=Button(self, command=self.pass_stop_signal)
        self.printbutton['text']='Stop'
        self.printbutton.grid(row=10, column=2, columnspan=1, rowspan=2, sticky=W, pady=5, padx=5)
        
    def printall(self):
        
        all_data = {'User':self.UserField.get(),
                    'Passwd':self.PasswdField.get(),
                    'os_version':self.oscombobox.get(),
                    'image_type':self.typecombobox.get(),
                    'private':self.privatecombobox.get(),
                    'd_account':self.accountField.get(),
                    'd_passwd':self.dpasswdField.get(),
                    'path':self.temp_path}
                    #'image_name':self.ImageField.get(),

        if self.UserField.get() == '':
            self.message.set("Please input your User Name.")
        elif self.PasswdField.get() == '':
            self.message.set("Please input your User Password.")
        #elif self.ImageField.get() == '':
        #    self.message.set("Please input your Image Name.")
        elif self.oscombobox.get() == 'What OS...?':
            self.message.set("Please choose your Image OS Version.")
        elif self.typecombobox.get() == 'What Type...?':
            self.message.set("Please choose your Image Type .")
        elif self.accountField.get() == '':
            self.message.set("Please input your Image default account.")
        elif self.dpasswdField.get() == '':
            self.message.set("Please input your Image default password.")
        elif self.temp_path == None:
            self.message.set("Please Choose an image file.")
        else:
            #self.message.set(yaml.dump(all_data))

            #mysql_status, mysql_message = image_db.write_db(all_data)
            mysql_status, mysql_message= self.send_data_info(all_data)
            if mysql_status == 1:
                print mysql_message
                return
            else:
                start = FTP_upload()
                print mysql_message
                thread.start_new_thread(start.upload_image, (all_data['path'], all_data, self.message, self))
                
    def default_info(self):
        self.UserField.insert(0,'Test_1')
        self.PasswdField.insert(0,'Pass_1')
        self.oscombobox.set('Win7')
        self.typecombobox.set('raw')
        self.accountField.insert(0, 'root')
        self.dpasswdField.insert(0, 'root')    

    def getpath(self):
        self.temp_path = askopenfilename(filetypes=[("allfiles","*"),("pythonfiles","*.py"),('pngfiles','*.png')])
        self.file_path.set(self.temp_path)
        print self.temp_path

    def pass_stop_signal(self):
        test = FTP_upload()
        test.change_stop_signal()


    def conn_server(self):
        conn_param = pika.ConnectionParameters(host=rabbitmq_host)
        connect = pika.BlockingConnection(conn_param)
        channel = connect.channel()
        return channel,connect

    def send_data_info(self, msg):
        channel,connect = self.conn_server()
        msg = yaml.dump(msg)
        channel.basic_publish( exchange='db_client', routing_key= key, body= msg )
        response = self.return_info(channel, connect)
        return (response['mysql_status'], response['mysql_message'])

    def return_info(self, channel, connect):
        global response
        response = None
        channel.queue_declare( queue='db_callback' )
        channel.exchange_declare( exchange='return_db', type='direct' )

        channel.queue_bind( exchange='return_db', queue='db_callback', routing_key='return_db')
        channel.basic_consume(self.on_return, no_ack=True, queue='db_callback')
        while response is None :
            connect.process_data_events()
        print response
        response = yaml.load(response)
        print response
        connect.close()
        return response
    def on_return (self, ch, method, props, body):
        global response
        response = body
        


if __name__ == '__main__':
    root = Tk()
    root.title('Image Uploader')
    app = GUIDemo(master=root)
    app.mainloop()

