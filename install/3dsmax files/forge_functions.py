# file for forge functions

# log in and get a token
def log_in_and_get_a_token(config):
	scope="data:read data:write data:create data:search bucket:create bucket:read bucket:update bucket:delete viewables:read"
	#self.scope=scope
		
	# make sure the following files contain the app data or else the login will fail
	client_id=""
	if os.path.exists("d:/d/forge2018/client_id.txt"): 
		f=open("d:/d/forge2018/client_id.txt","r")
		client_id=f.read()
		f.close()
	#self.client_id=client_id
		
	client_secret=""
	if os.path.exists("d:/d/forge2018/client_secret.txt"):
		f=open("d:/d/forge2018/client_secret.txt","r")
		client_secret=f.read()
		f.close()
	#self.client_secret=client_secret
		
		
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
	#self.token=token

    	# should we also pass all the self.* stuff we used to store??
    
	return token
  
  
  
def get_all_files(config):
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
        
   return files
    

	
def upload_a_file(config):
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

			
			
def delete_+selected_files(config,files_to_delete):
	# delete the selected file(s)

	h={"Authorization": self.token,"Content-Type": "application/json", "x-ads-region": self.bucket_region}
	d={}
	r=requests.get("https://developer.api.autodesk.com/oss/v2/buckets/%s/details"%(self.bucket_name), headers=h)
	#print r
	#print r.json()
 
	if "bucketKey" in r.json() and r.json()["bucketKey"]==self.bucket_name:
		# if we get here we have access to the bucket

		for i in files_to_delete:
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
				
				
				
				

