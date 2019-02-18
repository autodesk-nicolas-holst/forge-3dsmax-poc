# TODO code to import 

# in maxscript you do:
# importfile "c:/temp/test.fbx" #noPrompt using:FBXIMP

# and to make sure we're not adding it to the current scene you would do:
# resetMaxFile #noprompt


# So now for the python equivalents:
from pymxs import runtime as rt
rt.resetMaxFile(rt.Name("noPrompt"))
rt.exportFile("c:/temp/test3.fbx",rt.Name("noPrompt"),using="FBXEXP")

# yeah, so you might have guessed the using parameter, but to go from #noprompt to rt.Name("noPrompt") was non-trivial...
