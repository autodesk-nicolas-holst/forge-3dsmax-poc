# file to contain the logic functions, which in turn can call forge or dcc specific functions

def open_file():
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
