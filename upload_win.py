#!/usr/bin/env python3

import json
import requests
import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox


class Application(tk.Tk):

    def __init__(self):

        super().__init__()

        self.createWidgets()

    def createWidgets(self):

        self.title('Upload Tool')
        self.columnconfigure(0, minsize=50)

        # define variable
        self.entryvar = tk.StringVar()
        self.selectpath = False
        #self.keyvar = tk.StringVar()
        #self.keyvar.set('keyword')
        #items = ['BufferPool','Close','Data Capture','Compress','Pqty','Sqty']

        # define Top and Botton Frame
        topframe = tk.Frame(self, height=80)
        contentframe = tk.Frame(self)
        topframe.pack(side=tk.TOP)
        contentframe.pack(side=tk.TOP)

        # Top
        # 
        glabel = tk.Label(topframe, text='Current directory:')
        gentry = tk.Entry(topframe, textvariable=self.entryvar)
        #gbutton = tk.Button(topframe, command=self.opendir, text='Select directory')
        guploadbutton = tk.Button(topframe, command=self.__uploadfw, text='Upload image')
        glistbutton = tk.Button(topframe, command=self.__listfw, text='List firmware')
        #gcombobox = ttk.Combobox(topframe, values=items, textvariable=self.keyvar)
        # -- bind
        gentry.bind('<Return>', func=self.__refresh)
        #gcombobox.bind('<ComboboxSelected>', func=self.__refresh) # bind <ComboboxSelected>
        # -- location
        glabel.grid(row=0, column=0, sticky=tk.W)
        gentry.grid(row=0, column=1)
        #gbutton.grid(row=0, column=2)
        guploadbutton.grid(row=0, column=3)
        glistbutton.grid(row=0, column=4)
        #gcombobox.grid(row=0, column=3)

        # content area
        # -- two scrollbar
        rightbar = tk.Scrollbar(contentframe, orient=tk.VERTICAL)
        bottombar = tk.Scrollbar(contentframe, orient=tk.HORIZONTAL)
        self.textbox = tk.Text(contentframe, yscrollcommand=rightbar.set, xscrollcommand=bottombar.set)
        # -- location
        rightbar.pack(side =tk.RIGHT, fill=tk.Y)
        bottombar.pack(side=tk.BOTTOM, fill=tk.X)
        self.textbox.pack(side=tk.LEFT, fill=tk.BOTH)
        # -- config
        rightbar.config(command=self.textbox.yview)
        bottombar.config(command=self.textbox.xview)


    def opendir(self):
        ''''''
        self.textbox.delete('1.0', tk.END) # delete all

        self.dirname = filedialog.askdirectory() # open dialog
        self.entryvar.set(self.dirname) # set entryvar

        if not self.dirname:
            messagebox.showwarning('Warning', message='You do not choose anyfile!')  # show messagebox
        else:
            self.selectpath = True
            self.dirlist = os.listdir(self.entryvar.get())
            for eachdir in self.dirlist:
                self.textbox.insert(tk.END, eachdir+'\n')
            ####
            #self.textbox.insert(tk.END, self.dirname+'\r\n')
            self.needfile = open(self.dirname+'/'+'ota_upload_info')
            #self.filename = self.needfile.readline().strip('\n')
            self.md5_name_raw = self.needfile.readline().strip('\n')
            self.md5_name = self.md5_name_raw.split('  ')
            self.md5 = self.md5_name[0]
            self.filename = self.md5_name[1]
            self.ver = self.needfile.readline().strip('\n')
            self.textbox.insert(tk.END, '\n\n----Image Information----\n')
            self.textbox.insert(tk.END, 'file name: '+self.filename+'\n')
            self.textbox.insert(tk.END, 'version: '+self.ver+'\n')
            self.textbox.insert(tk.END, 'md5: '+self.md5+'\n')
            ####
            self.textbox.update()


    def __refresh(self, event=None):
        ''''''
        self.textbox.delete('1.0', tk.END) # delete all

        self.dirlist = os.listdir(self.entryvar.get())
        for eachdir in self.dirlist:
            self.textbox.insert(tk.END, eachdir+'\n')

        self.textbox.update()


    def addmenu(self, Menu):
        ''''''
        Menu(self)


    def __uploadfw(self):
        if self.selectpath:
            self.url="http://scienvet.southeastasia.cloudapp.azure.com:7120/firmware/firmware_helper"
            #self.post_para = {"filename":self.filename,'version':self.ver}
            self.post_para = {"filename":self.filename,'version':self.ver,'md5chksum':self.md5}
            self.file_para = {'file':open(self.dirname+'/'+self.filename,'rb')}
            self.result = requests.post(self.url,files=self.file_para,data=self.post_para)

            if (200 == self.result.status_code):
                self.textbox.insert(tk.END, '\n\nUpload Success\n')
            elif (400 == self.result.status_code):
                self.textbox.insert(tk.END, '\n\nBad Request(parameter error)\n')
            elif (500 == self.result.status_code):
                self.textbox.insert(tk.END, '\n\nInternal Server Error\n')
            else:
                self.textbox.insert(tk.END, '\n\nUnknown Error\n')
            self.textbox.update()
        else:
            messagebox.showwarning('Warning', message='You do not choose anyfile!')


    def __listfw(self):
        self.textbox.delete('1.0', tk.END) # delete all

        self.r = requests.get('http://scienvet.southeastasia.cloudapp.azure.com:7120/firmware/firmware_list')
        if (200 == self.r.status_code):
            self.textbox.insert(tk.END, 'Get Firmware List Success\n')
            self.firmware_dict = json.loads(self.r.text)
            self.firm_list = self.firmware_dict['firmware_list']
            for i in self.firm_list:
                self.textbox.insert(tk.END, '\nFilename:')
                self.textbox.insert(tk.END, i['name'])
                self.textbox.insert(tk.END, '\n')
                self.ver = i['version_list']
                for j in self.ver:
                    self.textbox.insert(tk.END, 'Version:')
                    self.textbox.insert(tk.END, j)
                    self.textbox.insert(tk.END, '\n')
                
        elif (400 == self.r.status_code):
            self.textbox.insert(tk.END, '\n\nBad Request(parameter error)\n')
        elif (500 == self.r.status_code):
            self.textbox.insert(tk.END, '\n\nInternal Server Error\n')
        else:
            self.textbox.insert(tk.END, '\n\nUnknown Error\n')

        self.textbox.update()





class MyMenu():
    ''''''

    def __init__(self, root):
        ''''''
        self.menubar = tk.Menu(root) # 

        # 
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="OPEN", command=self.file_open)
        #filemenu.add_command(label="NEW", command=self.file_new)
        #filemenu.add_command(label="SAVE", command=self.file_save)
        filemenu.add_separator()
        filemenu.add_command(label="EXIT", command=root.quit)

        # 
        #editmenu = tk.Menu(self.menubar, tearoff=0)
        #editmenu.add_command(label="CUT", command=self.edit_cut)
        #editmenu.add_command(label="COPY", command=self.edit_copy)
        #editmenu.add_command(label="PASTE", command=self.edit_paste)

        # 
        #helpmenu = tk.Menu(self.menubar, tearoff=0)
        #helpmenu.add_command(label="ABOUT", command=self.help_about)

        # 
        self.menubar.add_cascade(label="FILE", menu=filemenu)

        #self.menubar.add_cascade(label="EDIT", menu=editmenu)
        #self.menubar.add_cascade(label="HELP", menu=helpmenu)


        # 
        root.config(menu=self.menubar)

    def file_open(self):
        #messagebox.showinfo('Open', 'File-Open!')  # 
        app.opendir()
        #root.textbox.delete('1.0', tk.END) # delete all
        pass

    def file_new(self):
        messagebox.showinfo('New', 'File-New!')  # 
        pass

    def file_save(self):
        messagebox.showinfo('Save', 'File-Save!')  # 
        pass

    def edit_cut(self):
        messagebox.showinfo('Cut', 'Edit-Cut!')  # 
        pass

    def edit_copy(self):
        messagebox.showinfo('Copy', 'Edit-Copy!')  # 
        pass

    def edit_paste(self):
        messagebox.showinfo('Paste', 'Edit-Paste!')  # 
        pass

    def help_about(self):
        messagebox.showinfo('About', 'Author:kinfinger \n verion 1.0 \n Thanks! \n kinfinge@gmail.com ')  # show messagebox



if __name__ == '__main__':
    # create Application
    app = Application()

    # add menu:
    app.addmenu(MyMenu)

    # loop:
    app.mainloop()

