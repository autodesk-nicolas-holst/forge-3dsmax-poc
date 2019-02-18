# file to contain the logic functions, which in turn can call forge or dcc specific functions

# TODO auto-detect if we're running in a dcc or standalone and also set functions pointers based on dcc/standalone

import 3dsmax_functions
import forge_functions

def store_widget_dcc(self):
	store_widget_3dsmax(self)

def connect_to_cloud(config):
	return forge_functions.log_in_and_get_a_token(config)

def get_cloud_files(config):
	return forge_functions.get_all_files(config)

def add_properties(config):
	return 3dsmax_functions.add_properties(config)

def restore_original_filenames(config):
	return 3dsmax_functions.restore_original_filenames(config)

def open_file_dcc():
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
		
def open_fille_web(f):
	# https://forge.autodesk.com/en/docs/model-derivative/v2/tutorials/prepare-file-for-viewer/
	# Step 1: Convert the source URN into a Base64-Encoded URN

	urn=""
	b64=""
	
	if f!="":
		b64=base64.urlsafe_b64encode(f)
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

