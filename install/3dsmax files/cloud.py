import os,sys, time,string

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QTableWidgetItem


# there must be a better way...
sys.path.append("D:\\d\\_forge_testing\\20190218\\forge-3dsmax-poc-master\\install\\3dsmax files\\")
# import logic_fucntions which in turn will call forge and dcc functions
import logic_functions
# making sure it reads the file again as I'm modifying it all the time...
reload(logic_functions)


fname = "d:/d/forge2018/qt-cloud_3dsmax.ui"
ui_type, base_type=MaxPlus.LoadUiType(fname)






class ForgeWidget(base_type,ui_type):
	# thinking of removing these and putting them all in config
	files=[]
	config={}
	
	# utility functions
	def set_button_status(self):
		# if there are files active the buttons, otherwise disable them
		if len(self.files)!=0:
			self.b_open.setEnabled(True)
			self.b_delete.setEnabled(True)
			self.b_web.setEnabled(True)
		else:
			self.b_open.setEnabled(False)
			self.b_delete.setEnabled(False)
			self.b_web.setEnabled(False)
	
	def __init__(self, parent = None):
		self.config["temp_folder"]="c:/temp/"
		self.config["temp_dcc_filename"]="temp_open.max"


		base_type.__init__(self)
		ui_type.__init__(self)
		self.setupUi(self)
		logic_functions.store_widget_dcc(self)
				
		# set up the table widget
		self.t_files.setRowCount(0)
		self.t_files.setColumnCount(3)
		self.t_files.setHorizontalHeaderLabels(['timestamp','description',"size"])
		h=self.t_files.horizontalHeader()
		h.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
		h.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
		h.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
		self.t_files.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows);
		
		# hook up all the buttons to the respective functions
		self.b_upload.clicked.connect(self.b_upload_clicked)
		self.b_open.clicked.connect(self.b_open_clicked)
		self.b_web.clicked.connect(self.b_web_clicked)
		self.b_delete.clicked.connect(self.b_delete_clicked)
		#self.t_files
		#self.e_description

		# disable the delete button
		self.b_delete.setEnabled(False)
		
		# connect to the cloud service
		config=logic_functions.connect_to_cloud(self.config)

		# get all the files that are currently stored on the cloud
		self.files=logic_functions.get_cloud_files(self.config)
		self.files.sort()
		
		# populate the files list with these files
		self.t_files.setRowCount(len(self.files))
		for i in range(len(self.files)):
			self.t_files.setItem(i,0, QTableWidgetItem(self.files[i][0]))
			self.t_files.setItem(i,1, QTableWidgetItem(self.files[i][1]))
			self.t_files.setItem(i,2, QTableWidgetItem(self.files[i][3]))

		self.set_button_status()

		
		
	def b_upload_clicked(self):
		# add the uuid to the object names and add original name and uuid as properties in the dcc
		logic_functions.add_properties()
		
		self.t_files.clearSelection()
		
		t1=timestamp=time.strftime("%Y%m%d_%H%M%S",time.gmtime())
		t2=name=self.e_description.text()

		# upload the file, using the timestamp and description
		logic_functions.upload_a_file(self.config,timestamp,name)
		self.files.append((timestamp,name+".max","",-1))
							
		#populate the file list with this new name
		self.t_files.setRowCount(len(self.files))
		self.t_files.setItem(len(self.files)-1,0, QTableWidgetItem(self.files[-1][0]))
		self.t_files.setItem(len(self.files)-1,1, QTableWidgetItem(self.files[-1][1]))
		
		self.set_button_status()

		# blank the description field as we've used that when uploading the file
		self.e_description.setText("")
		
		# restore the object names in the dcc
		logic_functions.restore_original_objectnames()
		
		
	def b_delete_clicked(self):
		# build a list of items to delete
		todelete=[]
		for i in self.t_files.selectionModel().selectedRows():
			todelete.append((i.row()))

		# reverse the array so the indices into the self.files renmain valid
		todelete.reverse()
		
		# one ny one delete the files from the cloud
		for i in todelete:
			object_name=self.files[i][0]+self.files[i][1]
			logic_functions.delete_cloud_file(self.config,object_name)

			# remove entry from the tablewidget
			self.t_files.removeRow(i)
			del self.files[i]
			
		# deselect all as we've just deleted the entries
		self.t_files.clearSelection()
		
		self.set_button_status()

		self.e_description.setText("")



	def b_open_clicked(self):
		# find which file is selected
		t=""
		for i in self.t_files.selectionModel().selectedRows():
			t=i.row()
			break

		# don't do it unless there was a file selected
		if t!="":
			object_name=self.files[t][0]+self.files[t][1]
			
		logic_functions.open_file_dcc(self.config,object_name)


	def b_web_clicked(self):
		t=""
		for i in self.t_files.selectionModel().selectedRows():
			t=i.row()
			break
		if t!="":
			logic_functions.open_file_web(self.config,self.files[t][2])
			
			
		


w=ForgeWidget()
w.show()
