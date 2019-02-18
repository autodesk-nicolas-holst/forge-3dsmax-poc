import os, sys, time,uuid,string

import MaxPlus 
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QTableWidgetItem

import requests # http://requests.readthedocs.org/en/latest/
import uuid,json,base64,webbrowser

from pymxs import runtime as rt

# import forge_fucntions
import forge_functions

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
		
		
		
		# log in and get a token

		scope="data:read data:write data:create data:search bucket:create bucket:read bucket:update bucket:delete viewables:read"
		self.scope=scope
		
		# make sure the following files contain the app data or else the login will fail
		client_id=""
		if os.path.exists("d:/d/forge2018/client_id.txt"): 
			f=open("d:/d/forge2018/client_id.txt","r")
			client_id=f.read()
			f.close()
		self.client_id=client_id
		
		client_secret=""
		if os.path.exists("d:/d/forge2018/client_secret.txt"):
			f=open("d:/d/forge2018/client_secret.txt","r")
			client_secret=f.read()
			f.close()
		self.client_secret=client_secret
		
		
		d={'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'client_credentials', 'scope': scope}
		t=requests.post("https://developer.api.autodesk.com/authentication/v1/authenticate", data=d)

		if t.status_code==200:
			#print t
			#print t.json()
			token="%s %s"%(t.json()['token_type'],t.json()['access_token'])
		else:
			print client_id,client_secret,scope
			print t
			print t.status_code
			print "failed to log in"
			token="" # set token to blank so that the rest of the code doesn't try to use it
		self.token=token
 
 
		# check to see if the bucket already exists

		bucket_type="persistent" #  transient, temporary, persistent
		bucket_region="EMEA" # US or EMEA
		
		if bucket_region=="EMEA":
			bucket_name="nh"+"20181227-104400"+"testbucket1" # made to be globally unique!!!
		if bucket_region=="US":
			bucket_name="nh"+"20181227-104400"+"testbucket2" # made to be globally unique!!!

		self.bucket_name=bucket_name
		self.bucket_region=bucket_region
		
		# first get all buckets
		r={}
		r['status_code']="-1"

		buckets=[]
		if token!="":
			h={"Authorization": token,"Content-Type": "application/json", "x-ads-region":  bucket_region}
			next_url="https://developer.api.autodesk.com/oss/v2/buckets"
			while next_url!="":
				t=requests.get(next_url, headers=h)
				#print t
				#print t.json()
				if t.status_code==200:
					x=t.json()["items"]
					if len(x)==0:
						pass
						#print "no buckets found"
					else:
						#print "found the following buckets in region %s"%(bucket_region)
						for i in x:
							#print i
							buckets.append((i))
					if "next" in t.json():
						next_url=t.json()["next"]
					else:
						next_url=""

			#r['status_code']=t.status_code
			#r['buckets']=buckets

		# we now have all the buckets, check the one we're looking for is present
		f=0
		for i in buckets:
			if i["bucketKey"]==bucket_name:
				f=1
				#print "found bucket"
				break
		
		# and if not create it
		if (token!="")and(f==0):
			h={"Authorization": token,"Content-Type": "application/json", "x-ads-region":  bucket_region}
			d={"bucketKey": bucket_name, "policyKey": bucket_type}
			r=requests.post("https://developer.api.autodesk.com/oss/v2/buckets", headers=h, data=json.dumps(d))
			#print r
			#print r.json()
			if r.status_code==200:
				#print "successfully created bucket: %s"%(bucket_name)
				pass
			else:
				print "failed to created bucket: %s"%(bucket_name)

		if (token!=""):
			# now get a list of all the objects in the bucket
			h={"Authorization": token,"Content-Type": "application/json", "x-ads-region":  bucket_region}
			d={}
			r=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/details"%(bucket_name), headers=h)

			if "bucketKey" in r.json() and r.json()["bucketKey"]==bucket_name:
				# if we get here we have access to the bucket
				r=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/objects"%(bucket_name), headers=h)

				#print r
				#print r.json()
  
				if r.status_code==200:
					x=r.json()["items"]
					if len(x)==0:
						#print  "no items found"
						pass
					else:
						#print "found the following objects in bucket %s"%(bucket_name)
						for i in x:
							#print i
							# stip the first n characters off and use those as the date and time stamp
							t1=""
							t2=i["objectKey"]
							if len(t2)>14:
								t1=t2[:15]
								t2=t2[15:]
							self.files.append((t1,t2,i["objectId"],i["size"]))
			else:
				print "something went wrong retrieving the objects from the bucket"
		
		
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
		h={"Authorization": self.token,"Content-Type": "application/json", "x-ads-region": self.bucket_region}
		d={}
		r=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/details"%(self.bucket_name), headers=h)
		#print r
		#print r.json()
 
		if "bucketKey" in r.json() and r.json()["bucketKey"]==self.bucket_name:
			# if we get here we have access to the bucket

			# save the current scene to a temp file
			##t=MaxPlus.Core.EvalMAXScript("saveMaxFile \"d:/d/forge2018/temp.max\" clearNeedSaveFlag:False useNewFile:False quiet:true")
			rt.saveMaxFile("d:/d/forge2018/temp.max",clearNeedSaveFlag=False,useNewFile=False,quiet=True)
	
			file_to_upload="d:/d/forge2018/temp.max" 
			# read the file in
			f=open(file_to_upload,"rb")	
			d=f.read()
			f.close()

			# build the object name
			object_name=t1+t2+".max"

			headers={"Authorization": self.token, "x-ads-region":  self.bucket_region, "Content-Type": "text/plain; charset=UTF-8", "Content-Disposition": file_to_upload, "Content-Length": "%s"%(len(d))}
			r=requests.put("https://developer.api.autodesk.com/oss/v2/buckets/%s/objects/%s"%(self.bucket_name,object_name), headers=h, data=d)

			if r.status_code==200:
				#print "uploaded %s to bucket %s"%(file_to_upload,self.bucket_name)
				# delete the temp file
				if os.path.exists("d:/d/forge2018/temp.max"):
					os.unlink("d:/d/forge2018/temp.max")
			else:
				print "failed to upload file %s to bucket %s, %s"%(file_to_upload,self.bucket_name,r.status_code)



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
		# delete the selected file(s)

		h={"Authorization": self.token,"Content-Type": "application/json", "x-ads-region": self.bucket_region}
		d={}
		r=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/details"%(self.bucket_name), headers=h)
		#print r
		#print r.json()
 
		if "bucketKey" in r.json() and r.json()["bucketKey"]==self.bucket_name:
			# if we get here we have access to the bucket
			
			# build a list of items to delete
			todelete=[]
			for i in self.t_files.selectionModel().selectedRows():
				todelete.append((i.row()))

			todelete.reverse()
			for i in todelete:
				object_name=self.files[i][0]+self.files[i][1]

				t=requests.delete("https://developer.api.autodesk.com/oss/v2/buckets/%s/objects/%s"%(self.bucket_name,object_name), headers=h)
				#print t
				if t.status_code==200:
					#print "deleted object %s from bucket %s"%(object_name,self.bucket_name)
					# remove entry from the tablewidget
					self.t_files.removeRow(i)
					del self.files[i]
				else:
					print "failed to delete object %s from bucket %s"%(object_name,self.bucket_name)
		
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
		temp_name="d:/d/forge2018/temp.max"
		# make sure there isn't a temp file
		if os.path.exists(temp_name):
			os.unlink(temp_name)
			
		# grab the object from the cloud and save it locally
		h={"Authorization": self.token,"Content-Type": "application/json", "x-ads-region":  self.bucket_region}
		d={}
		r=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/details"%(self.bucket_name), headers=h)
		#print r
		#print r.json()
 
		if "bucketKey" in r.json() and r.json()["bucketKey"]==self.bucket_name:
			# if we get here we have access to the bucket

			t=""
			for i in self.t_files.selectionModel().selectedRows():
				t=i.row()
				break

			if t!="":
				object_name=self.files[t][0]+self.files[t][1]

				t=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/objects/%s"%(self.bucket_name,object_name), headers=h)
				print t
				if t.status_code==200:
					f=open(temp_name,"wb")
					f.write(t.content)
					f.close()
					print "downloaded object %s to %s from bucket %s"%(object_name,temp_name,self.bucket_name)
				else:
					print "failed to download object %s from bucket %s"%(object_name,self.bucket_name)
		
		# open the scene without user interaction
		if os.path.exists(temp_name):
			##t=MaxPlus.Core.EvalMAXScript("loadMaxFile \"%s\" useFileUnits:true quiet:true"%(temp_name))
			rt.loadmaxfile(temp_name,useFileUnits=True,quiet=True)

		for c in rt.geometry:
			print rt.getUserPropVal(c,"original_name")
			c.Name=str(rt.getUserPropVal(c,"original_name"))

		# remove the temp file
		if os.path.exists(temp_name):
			os.unlink(temp_name)


	def b_web_clicked(self):
		# https://forge.autodesk.com/en/docs/model-derivative/v2/tutorials/prepare-file-for-viewer/
		# Step 1: Convert the source URN into a Base64-Encoded URN
		t=""
		b64=""
		for i in self.t_files.selectionModel().selectedRows():
			t=i.row()
			break
		#print t
		if t!="":
			#print self.files[t][2]
			urn=self.files[t][2]
			if urn!="":
				b64=base64.urlsafe_b64encode(urn)

				#print urn
				# strip off any padding, because forge expects RFC 6920
				while b64[-1]=="=":
					b64=b64[:-1]
				#print b64
			
			
		if b64!="":
			# Step 2: Translate the Source File into SVF Format
			h={"Authorization": self.token,"Content-Type": "application/json",  "x-ads-region":  self.bucket_region}
			i={"urn": b64}
			o={"formats": [{"type": "svf","views":["2d","3d"]}]}
			
			d={"input": i, "output": o}
			r=requests.post("https://developer.api.autodesk.com/modelderivative/v2/designdata/job", headers=h, data=json.dumps(d))
			#print r
			#print r.json()	
			
			viewerurn=""
			if r.status_code==200:
				# Step 3: Verify the Job is Complete
				x="pending"
				y=200
				tm=0
				while (y==200)and((x=="pending")or(x=="inprogress")):
					h={"Authorization": self.token,"Content-Type": "application/json",  "x-ads-region":  self.bucket_region}
					t=requests.get("https://developer.api.autodesk.com/modelderivative/v2/designdata/%s/manifest"%(b64), headers=h)
					#print t
					y=t.status_code
					if y==200:
						x=t.json()["status"]
						print tm,t,x
						# pending, inprogress, success, failed, timeout
						time.sleep(5)
						tm=tm+5
						##MaxPlus.Core.EvalMAXScript("windows.processPostedMessages()")
						rt.windows.processPostedMessages()
					if t.json()["status"]=="success":
						viewerurn=r.json()["urn"]
						
			if 	 r.status_code==201:
				#print r
				if r.json()["result"]=="created":
					print "this file already has svg files"
					viewerurn=r.json()["urn"]
				# it seems there is already a translated item avaivalable when you get a 201 and result of created
				
		# Step 4: Embed the Source File URN into the Viewer
		# https://forge.autodesk.com/en/docs/viewer/v5/tutorials/basic-viewer/
		# 1 get a new viewer token
		
		viewerscope="viewables:read"
		d={'client_id': self.client_id, 'client_secret': self.client_secret, 'grant_type': 'client_credentials', 'scope': viewerscope}
		t=requests.post("https://developer.api.autodesk.com/authentication/v1/authenticate", data=d)
		if t.status_code==200:
			viewertoken=t.json()['access_token'] # would be nice if someone had mentioned that you shouldn't include the "Bearer: " part...
		else:
			print t
			print t.status_code
			print "failed to obtain a viewer token"
			viewertoken="" # set token to blank so that the rest of the code doesn't try to use it
		
		if (viewertoken!="")and(viewerurn!=""):
			# 2 read in the html file
			f=open("d:/d/forge2018/forge_html.txt","r")
			d=f.read()
			f.close()
			
			html_location="d:/d/forge2018/forge_viewer.html"
			html_location="c:/wamp64/www/forge_viewer.html"
			html_url="http://localhost:81/forge_viewer.html"
			
			viewerurn=b64
			# 3 replace the token and the urn, the urn doesn't seem to have trailing equal signs
			d=string.replace(d, '<YOUR_APPLICATION_TOKEN>', viewertoken)
			d=string.replace(d, '<YOUR_URN_ID>', viewerurn)
			
			# 4 save the html
			f=open(html_location,"w")
			f.write(d)
			f.close()
		
			# 5 fire up a browser with the page we just created 
			webbrowser.open_new(html_url)
		else:
			print "couldn't get token (%s) or urn (%s)"%(viewertoken,viewerurn)



w=ForgeWidget()
w.show()
