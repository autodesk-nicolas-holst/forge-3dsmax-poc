# file to contain the logic functions, which in turn can call forge or dcc specific functions

global config

# TODO auto-detect if we're running in a dcc or standalone and also set functions pointers based on dcc/standalone
import os,sys, time,string

import dcc_3dsmax_functions
import forge_functions
# making sure it reads the file again as I'm modifying it all the time...
reload(dcc_3dsmax_functions)
reload(forge_functions)


def store_widget_dcc(self):
	dcc_3dsmax_functions.store_widget_3dsmax(self)

def connect_to_cloud(config):
	return forge_functions.log_in_and_get_a_token(config)

def get_cloud_files(config):
	return forge_functions.get_all_files(config)

def add_properties():
	dcc_3dsmax_functions.add_properties()

def restore_original_objectnames():
	dcc_3dsmax_functions.restore_original_objectnames()

def delete_cloud_file(config,file_to_delete):
	forge_functions.delete_file(config,file_to_delete)

def upload_a_file(config,timestamp,name):
	dcc_3dsmax_functions.save_current_scene_to_temp_filename(config)
	forge_functions.upload_a_file(config,timestamp,name)

def open_file_dcc(config,object_name):
	#config["temp_name"]="d:/d/forge2018/temp.max"
	# make sure there isn't a temp file
	if os.path.exists(config["temp_folder"]+config["temp_dcc_filename"]):
		os.unlink(config["temp_folder"]+config["temp_dcc_filename"])
	
	# download a copy to the temp folder/temp name
	forge_functions.open_file_dcc(config,object_name)
	# open the temp file in the dcc
	dcc_3dsmax_functions.open_local_temp_file(config)
	# restore the object 
	dcc_3dsmax_functions.restore_original_objectnames()

	# remove the temp file
	if os.path.exists(config["temp_folder"]+config["temp_dcc_filename"]):
		os.unlink(config["temp_folder"]+config["temp_dcc_filename"])


def open_file_web(config,f):
	forge_functions.open_file_web(config,f)
