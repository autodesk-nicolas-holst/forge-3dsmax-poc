# TODO: code to save the current 3ds Max scene as fbx

# so in maxscript you do 
# exportFile "c:/temp/test.fbx" #noPrompt using:FBXEXP

# the python equivalent is:
from pymxs import runtime as rt
rt.exportFile("c:/temp/test.fbx", rt.Name("noPrompt"),using="FBXEXP")
