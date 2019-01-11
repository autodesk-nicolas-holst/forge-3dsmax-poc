import os,sys,time,uuid,string

import MaxPlus 
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QTableWidgetItem

import requests
from pymxs import runtime as rt


sys.path.append("d:/d/forge2018/")

fname = "d:/d/forge2018/qt-edit_data_3dsmax.ui"
ui_type, base_type=MaxPlus.LoadUiType(fname)

#save_mode="local_file"
save_mode="web"


class ForgeWidget(base_type,ui_type):
	current_object=""
	data=[]
	
	def __init__(self, parent = None):
		base_type.__init__(self)
		ui_type.__init__(self)
		self.setupUi(self)
		MaxPlus.AttachQWidgetToMax(self)
				
		# set up the table widget
		self.t_data.setRowCount(0)
		self.t_data.setColumnCount(3)
		self.t_data.setHorizontalHeaderLabels(['timestamp','data','status'])
		h=self.t_data.horizontalHeader()
		h.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
		h.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
		h.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
		self.t_data.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows);
		
		self.b_select.clicked.connect(self.b_select_clicked)
		self.b_delete.clicked.connect(self.b_delete_clicked)
		self.b_add.clicked.connect(self.add_clicked)
		#self.e_data
		#self.e_object
		#self.t_data	

		self.b_delete.setEnabled(False)
		
						
	def b_select_clicked(self):
		self.t_data.clearSelection()
		
		# let the user select an object
		# maxscript:
		##t=pickObject message:"select an object"
		# maxscript from python
		##t=MaxPlus.Core.EvalMAXScript("(pickObject message:\"select an object\") as string")
		##print t.Get()
		##o=t.Get()
		# python
		o=rt.pickObject(message="select an object")
		# check if there is a uuid property on the object, if not create it
		if rt.getUserPropVal(o,"original_name")==None:
			rt.setUserPropVal(o,"original_name",o.Name)
			#print rt.getUserPropVal(o,"original_name")
		if rt.getUserPropVal(o,"uuid")==None:
			rt.setUserPropVal(o,"uuid",uuid.uuid4().hex)
			#print rt.getUserPropVal(o,"uuid")

		self.current_object=rt.getUserPropVal(o,"uuid")
		#print self.current_object
		
		# put the object name in e_object
		# strip off everything before the " @ " bit
		o=str(o)
		pos1=string.find(o," @ ")
		if pos1!=-1:
			o=o[:pos1]

		self.e_object.setText(o)

		self.data=[]
		t1=[]
		t2=[]
		if save_mode=="local_file":
			# check if we have data for this object display
			if os.path.exists("d:/d/forge2018/data.txt"):
				f=open("d:/d/forge2018/data.txt","r")
				t1=f.read()
				f.close()
			# end of save_mode==local_file
		if save_mode=="web":
			r=requests.get("http://localhost:81/read_data.php")
			#print r.status_code
			if r.status_code==200:
				t1=r.text

		if len(t1)>10:
			t1=string.split(t1,"\n")
		else:
			t1=[]
		
		for i in t1:
			l=i.split("|") 
			# i=only get complete records and ones for the matching uuid
			if (len(l)==4)and(l[0]==self.current_object):
				# first get all the records
				t=[]
				t.append((l[1]))
				t.append((l[2]))
				# overwrite it if it's marked as deleted
				if l[3]=="deleted":
					t.append(("deleted"))
				else:
					t.append(("from file"))
					
				t2.append((t))

		
		# remove the ones marked deleted and the ones with the matching time stamp
		keep=[]
		for i in t2:
			keep.append((1))
				
		for i in range(len(t2)-1,-1,-1):
			#print "i=",i
			if t2[i][2]=="deleted":
				for j in range(i-1,-1,-1):
					#print i,j,t2[j],keep[j]
					if t2[i][0]==t2[j][0]:
						#print "j=",j
						keep[j]=0
			
		for i in range(len(t2)):
			if len(t2[i])!=3:
				keep[i]=0
		for i in range(len(t2)-1,-1,-1):
			if keep[i]==0:
				del t2[i]
		
		# add values to the data array
		for i in t2:
			if i[2]!="deleted":
				self.data.append((i))
			
		# add values to the table
		#print len(self.data),self.data
		self.t_data.setRowCount(len(self.data))
		for i in range(len(self.data)):
			self.t_data.setItem(i,0, QTableWidgetItem(self.data[i][0]))
			self.t_data.setItem(i,1, QTableWidgetItem(self.data[i][1]))
			self.t_data.setItem(i,2, QTableWidgetItem(self.data[i][2]))

		if len(self.data)!=0:
			self.b_delete.setEnabled(True)
		else:
			self.b_delete.setEnabled(False)
		
	def b_delete_clicked(self):
		# change the type of the data to deleted
		# update the info in the text file

		for i in self.t_data.selectionModel().selectedRows():
			self.t_data.setItem(i.row(),2, QTableWidgetItem("deleted"))
			
			tm=self.data[i.row()][0]
			tx=self.data[i.row()][1]
			tp="deleted"
			if save_mode=="local_file":
				# add record to the file
				f=open("d:/d/forge2018/data.txt","a")
				f.write("%s|%s|%s|%s\n"%(self.current_object,tm,tx,tp))
				f.close()
			if save_mode=="web":
				r=requests.get("http://localhost:81/write_data.php?o=%s|%s|%s|%s\n"%(self.current_object,tm,tx,tp))
		
		self.t_data.clearSelection()
		
		if len(self.data)!=0:
			self.b_delete.setEnabled(True)
		else:
			self.b_delete.setEnabled(False)


	def add_clicked(self):
		# add the data to the give object
		# figure out how many items we already have
		t=[]
		tm=time.strftime("%Y%m%d_%H%M%S",time.gmtime())
		tx=self.e_data.text()
		tp="new"
		t.append(tm)
		t.append(tx)
		t.append(tp)
		self.data.append(t)
		
		self.t_data.clearSelection()
		
		i=len(self.data)
		self.t_data.setRowCount(i)

		self.t_data.setItem(i-1,0, QTableWidgetItem(tm))
		self.t_data.setItem(i-1,1, QTableWidgetItem(tx))
		self.t_data.setItem(i-1,2, QTableWidgetItem(tp))


		if len(self.data)!=0:
			self.b_delete.setEnabled(True)
		else:
			self.b_delete.setEnabled(False)

		if save_mode=="local_file":
			f=open("d:/d/forge2018/data.txt","a")
			f.write("%s|%s|%s|%s\n"%(self.current_object,tm,tx,tp))
			f.close()
		if save_mode=="web":
			r=requests.get("http://localhost:81/write_data.php?o=%s|%s|%s|%s\n"%(self.current_object,tm,tx,tp))

		self.e_data.setText("")

w=ForgeWidget()
w.show()
