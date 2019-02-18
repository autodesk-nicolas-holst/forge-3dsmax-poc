# file for 3ds Max functions


import MaxPlus 
from pymxs import runtime as rt


def add_properties(config):
   # before we upload populate the properties
   # uuid & name
   for c in rt.geometry:
      if rt.getUserPropVal(c,"original_name")==None:
         rt.setUserPropVal(c,"original_name",c.Name)
      if rt.getUserPropVal(c,"uuid")==None:
         rt.setUserPropVal(c,"uuid",uuid.uuid4().hex)
      # then rename the object so it's uuid+name (checking the this hasn't been done already)
      c.Name=rt.getUserPropVal(c,"original_name")+rt.getUserPropVal(c,"uuid")
      
def restore_name(config):
  # todo
