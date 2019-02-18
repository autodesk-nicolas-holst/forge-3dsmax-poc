import os, sys, time,uuid,string

import MaxPlus 
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QTableWidgetItem

import requests # http://requests.readthedocs.org/en/latest/
import uuid,json,base64,webbrowser

from pymxs import runtime as rt

# import logic_fucntions which in turn will call forge and dcc functions
import logic_functions

sys.path.append("d:/d/forge2018/")

fname = "d:/d/forge2018/qt-cloud_3dsmax.ui"
ui_type, base_type=MaxPlus.LoadUiType(fname)


class ForgeWidget(base_type,ui_type):
	token=""
	files=[]
	client_id=""
	client_secret=""
	scope=""
	bucket_name=""
	bucket_region=""
	
	def __init__(self, parent = None):
		base_type.__init__(self)
		ui_type.__init__(self)
		self.setupUi(self)
		MaxPlus.AttachQWidgetToMax(self)
				
		# set up the table widget
		self.t_files.setRowCount(0)
		self.t_files.setColumnCount(3)
		self.t_files.setHorizontalHeaderLabels(['timestamp','description',"size"])
		h=self.t_files.horizontalHeader()
		h.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
		h.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
		h.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
		self.t_files.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows);
		
		self.b_upload.clicked.connect(self.b_upload_clicked)
		self.b_open.clicked.connect(self.b_open_clicked)
		self.b_web.clicked.connect(self.b_web_clicked)
		self.b_delete.clicked.connect(self.b_delete_clicked)
		#self.t_files
		#self.e_description

		self.b_delete.setEnabled(False)
		
		
		
		config=logic_functions.connect_to_cloud(config)
		
		#populate the file list with these names
		self.files.sort()
		
		
		self.t_files.setRowCount(len(self.files))
		for i in range(len(self.files)):
			self.t_files.setItem(i,0, QTableWidgetItem(self.files[i][0]))
			self.t_files.setItem(i,1, QTableWidgetItem(self.files[i][1]))
			self.t_files.setItem(i,2, QTableWidgetItem(self.files[i][3]))

		if len(self.files)!=0:
			self.b_open.setEnabled(True)
			self.b_delete.setEnabled(True)
			self.b_web.setEnabled(True)
		else:
			self.b_open.setEnabled(False)
			self.b_delete.setEnabled(False)
			self.b_web.setEnabled(False)

		
		
	def b_upload_clicked(self):
		# before we upload populate the properties
		# uuid & name
		for c in rt.geometry:
			if rt.getUserPropVal(c,"original_name")==None:
				rt.setUserPropVal(c,"original_name",c.Name)
			if rt.getUserPropVal(c,"uuid")==None:
				rt.setUserPropVal(c,"uuid",uuid.uuid4().hex)
			# then rename the object so it's uuid+name (checking the this hasn't been done already)
			c.Name=rt.getUserPropVal(c,"original_name")+rt.getUserPropVal(c,"uuid")
		
		self.t_files.clearSelection()
		
		t1=time.strftime("%Y%m%d_%H%M%S",time.gmtime())
		t2=self.e_description.text()

		# upload the file, using the timestamp and description
		forge_functions.upload_a_file(config,t1,t2)
		self.files.append((t1,t2+".max","",-1))
							
		#populate the file list with these names
		self.t_files.setRowCount(len(self.files))
		self.t_files.setItem(len(self.files)-1,0, QTableWidgetItem(self.files[-1][0]))
		self.t_files.setItem(len(self.files)-1,1, QTableWidgetItem(self.files[-1][1]))
		
		if len(self.files)!=0:
			self.b_open.setEnabled(True)
			self.b_delete.setEnabled(True)
			self.b_web.setEnabled(True)
		else:
			self.b_open.setEnabled(False)
			self.b_delete.setEnabled(False)
			self.b_web.setEnabled(False)

		self.e_description.setText("")
		
		# restore the object so it's name again (stripping off the uuid if it's at the beginning of the name)
		for c in rt.geometry:
			c.Name=str(rt.getUserPropVal(c,"original_name"))
		
	def b_delete_clicked(self):
		# build a list of items to delete
		todelete=[]
		for i in self.t_files.selectionModel().selectedRows():
			todelete.append((i.row()))

		todelete.reverse()
		for i in todelete:
			object_name=self.files[i][0]+self.files[i][1]
			forge_functions.delete_file(config.object_name)
		
		self.t_files.clearSelection()
		
		if len(self.files)!=0:
			self.b_open.setEnabled(True)
			self.b_delete.setEnabled(True)
			self.b_web.setEnabled(True)
		else:
			self.b_open.setEnabled(False)
			self.b_delete.setEnabled(False)
			self.b_web.setEnabled(False)

		self.e_description.setText("")



	def b_open_clicked(self):
		logic_functions.open_file()


	def b_web_clicked(self):
		t=""
		for i in self.t_files.selectionModel().selectedRows():
			t=i.row()
			break
		if t!="":
			logic_functions.open_file_web(self.files[t][2])
			
			
		


w=ForgeWidget()
w.show()
