from omega import *
from cyclops import *
from omegaToolkit import *

currentObject = None

interactor = ToolkitUtils.setupInteractor('config/interactor')

#--------------------------------------------------------------------------------------------------
def onObjectSelected(node, distance):
	global currentObject
	print("CUrrent object: " + str(node))
	# If no object has ben selected and the context menu is open, close it.
	currentObject = node
	interactor.setSceneNode(currentObject)
		
#--------------------------------------------------------------------------------------------------
def onEvent(e):
	#if(e.getType() != EventType.Update): print(e.getType() )
	if(e.getServiceType() == ServiceType.Pointer or e.getServiceType() == ServiceType.Wand):
		# Button mappings are different when using wand or mouse
		confirmButton = EventFlags.Button1
		if(e.getServiceType() == ServiceType.Wand): confirmButton = EventFlags.Button5
		
		r = getRayFromEvent(e)
		
		# When the confirm button is pressed:
		if(e.isButtonDown(confirmButton)):
			if(r[0]): querySceneRay(r[1], r[2], onObjectSelected)

