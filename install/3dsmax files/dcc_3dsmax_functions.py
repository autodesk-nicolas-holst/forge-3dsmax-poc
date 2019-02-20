# file for 3ds Max functions

global config

import MaxPlus 
from pymxs import runtime as rt

import uuid,os


def store_widget_3dsmax(self):
   MaxPlus.AttachQWidgetToMax(self)

def add_properties():
	global config
	# before we upload populate the properties
	# uuid & name
	for c in rt.geometry:
		if rt.getUserPropVal(c,"original_name")==None:
			rt.setUserPropVal(c,"original_name",c.Name)
		if rt.getUserPropVal(c,"uuid")==None:
			rt.setUserPropVal(c,"uuid",uuid.uuid4().hex)
		# then rename the object so it's uuid+name (checking the this hasn't been done already)
		c.Name=rt.getUserPropVal(c,"original_name")+"UUID"+rt.getUserPropVal(c,"uuid")
      
def  restore_original_objectnames():
	global config
	# restore the object so it's name again (stripping off the uuid if it's at the beginning of the name)
	for c in rt.geometry:
		c.Name=str(rt.getUserPropVal(c,"original_name"))

def open_local_temp_file(config):
	# open the scene without user interaction
	if os.path.exists(config["temp_folder"]+config["temp_dcc_filename"]):
		rt.loadmaxfile(config["temp_folder"]+config["temp_dcc_filename"],useFileUnits=True,quiet=True)
		
def save_current_scene_to_temp_filename(config):
	# save the current scene to a temp file
	rt.saveMaxFile(config["temp_folder"]+config["temp_dcc_filename"],clearNeedSaveFlag=False,useNewFile=False,quiet=True)
	
def processmessages():
	rt.windows.processPostedMessages()
