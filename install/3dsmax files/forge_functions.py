# file for forge functions
import os,sys, time,string
import requests # http://requests.readthedocs.org/en/latest/
import json,base64,webbrowser

# log in and get a token
def log_in_and_get_a_token(config):
	scope="data:read data:write data:create data:search bucket:create bucket:read bucket:update bucket:delete viewables:read"
	config["scope"]=scope
		
	# make sure the following files contain the app data or else the login will fail
	client_id=""
	if os.path.exists("d:/d/forge2018/client_id.txt"): 
		f=open("d:/d/forge2018/client_id.txt","r")
		client_id=f.read()
		f.close()
	config["client_id"]=client_id
		
	client_secret=""
	if os.path.exists("d:/d/forge2018/client_secret.txt"):
		f=open("d:/d/forge2018/client_secret.txt","r")
		client_secret=f.read()
		f.close()
	config["client_secret"]=client_secret
		
		
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
	config["token"]=token

    	# should we also pass all the self.* stuff we used to store??
	return config
  
  
  
def get_all_files(config):
	
	# check to see if the bucket already exists
	files=[]
	bucket_type="persistent" #  transient, temporary, persistent
	bucket_region="EMEA" # US or EMEA
		
	if bucket_region=="EMEA":
		bucket_name="nh"+"20181227-104400"+"testbucket1" # made to be globally unique!!!
	if bucket_region=="US":
		bucket_name="nh"+"20181227-104400"+"testbucket2" # made to be globally unique!!!

	config["bucket_name"]=bucket_name
	config["bucket_region"]=bucket_region
	
	# first get all buckets
	r={}
	r['status_code']="-1"

	buckets=[]
	if config["token"]!="":
		h={"Authorization": config["token"],"Content-Type": "application/json", "x-ads-region":  config["bucket_region"]}
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
	if (config["token"]!="")and(f==0):
		h={"Authorization": config["token"],"Content-Type": "application/json", "x-ads-region": config["bucket_region"]}
		d={"bucketKey": config["bucket_name"], "policyKey": config["bucket_type"]}
		r=requests.post("https://developer.api.autodesk.com/oss/v2/buckets", headers=h, data=json.dumps(d))
		#print r
		#print r.json()
		if r.status_code==200:
			#print "successfully created bucket: %s"%(bucket_name)
			pass
		else:
			print "failed to created bucket: %s"%(config["bucket_name"])

	if (config["token"]!=""):
		# now get a list of all the objects in the bucket
		h={"Authorization": config["token"],"Content-Type": "application/json", "x-ads-region":  config["bucket_region"]}
		d={}
		r=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/details"%(config["bucket_name"]), headers=h)

		if "bucketKey" in r.json() and r.json()["bucketKey"]==config["bucket_name"]:
			# if we get here we have access to the bucket
			r=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/objects"%(config["bucket_name"]), headers=h)
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
						files.append((t1,t2,i["objectId"],i["size"]))
		else:
			print "something went wrong retrieving the objects from the bucket"
        
	return files
    

	
def upload_a_file(config,t1,t2):
	# upload the file, using the timestamp and description
	h={"Authorization": config["token"],"Content-Type": "application/json", "x-ads-region": config["bucket_region"]}
	d={}
	r=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/details"%(config["bucket_name"]), headers=h)
	#print r
	#print r.json()
 
	if "bucketKey" in r.json() and r.json()["bucketKey"]==config["bucket_name"]:
		# if we get here we have access to the bucket
	
		file_to_upload=config["temp_folder"]+config["temp_dcc_filename"]
		# read the file in
		f=open(file_to_upload,"rb")	
		d=f.read()
		f.close()

		# build the object name
		object_name=t1+t2+".max"

		headers={"Authorization": config["token"], "x-ads-region":  config["bucket_region"], "Content-Type": "text/plain; charset=UTF-8", "Content-Disposition": file_to_upload, "Content-Length": "%s"%(len(d))}
		r=requests.put("https://developer.api.autodesk.com/oss/v2/buckets/%s/objects/%s"%(config["bucket_name"],object_name), headers=h, data=d)

		if r.status_code==200:
			# delete the temp file
			if os.path.exists("d:/d/forge2018/temp.max"):
				os.unlink("d:/d/forge2018/temp.max")
		else:
			print "failed to upload file %s to bucket %s, %s"%(file_to_upload,config["bucket_name"],r.status_code)

			
			
def delete_file(config,file_to_delete):
	# delete the selected file(s)

	h={"Authorization": config["token"],"Content-Type": "application/json", "x-ads-region": config["bucket_region"]}
	d={}
	r=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/details"%(config["bucket_name"]), headers=h)
	#print r
	#print r.json()
 
	if "bucketKey" in r.json() and r.json()["bucketKey"]==config["bucket_name"]:
		# if we get here we have access to the bucket

		object_name=file_to_delete
		t=requests.delete("https://developer.api.autodesk.com/oss/v2/buckets/%s/objects/%s"%(config["bucket_name"],object_name), headers=h)
		#print t
		if t.status_code==200:
			pass
		else:
			print "failed to delete object %s from bucket %s"%(object_name,config["bucket_name"])
				
def open_file_dcc(config,object_name):
	# grab the object from the cloud and save it locally
	h={"Authorization": config["token"],"Content-Type": "application/json", "x-ads-region":  config["bucket_region"]}
	d={}
	r=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/details"%(config["bucket_name"]), headers=h)
	#print r
	#print r.json()
 
	if "bucketKey" in r.json() and r.json()["bucketKey"]==config["bucket_name"]:
		# if we get here we have access to the bucket

		#object_name=self.files[t][0]+self.files[t][1]

		t=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/objects/%s"%(config["bucket_name"],object_name), headers=h)
		print t
		if t.status_code==200:
			f=open(config["temp_folder"]+config["temp_dcc_filename"],"wb")
			f.write(t.content)
			f.close()
			#print "downloaded object %s to %s from bucket %s"%(object_name,config["temp_name"],config["bucket_name"])
		#else:
			#print "failed to download object %s from bucket %s"%(object_name,config["bucket_name"])
				
				
def open_file_web(config,f):
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
		h={"Authorization": config["token"],"Content-Type": "application/json",  "x-ads-region":  config["bucket_region"]}
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
				h={"Authorization": config["token"],"Content-Type": "application/json",  "x-ads-region":  config["bucket_region"]}
				t=requests.get("https://developer.api.autodesk.com/modelderivative/v2/designdata/%s/manifest"%(b64), headers=h)
				#print t
				y=t.status_code
				if y==200:
					x=t.json()["status"]
					print tm,t,x
					# pending, inprogress, success, failed, timeout
					time.sleep(5)
					tm=tm+5

					# I'd like to call this to ensure 3ds Max prints the message, but I don't want to call the dcc functions from here...
					#rt.windows.processPostedMessages()
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
	d={'client_id': config["client_id"], 'client_secret': config["client_secret"], 'grant_type': 'client_credentials', 'scope': viewerscope}
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

