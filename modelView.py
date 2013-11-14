from math import *
from euclid import *
from omega import *
from cyclops import *
from omegaToolkit import *

import os

import skyboxSwitcher
import objectManipulator

#------------------------------------------------------------------------------
# configuration
modelHome = "/data/evl/omegalib-user/usb/models"

scene = getSceneManager()

# dictionary of loaded models. will be filled up by the onModelLoaded function
loadedModels = {}
modelButtons = {}

#------------------------------------------------------------------------------
light = Light.create()
light.setColor(Color("#807070"))
light.setAmbient(Color("#202020"))
light.setEnabled(True)
getDefaultCamera().addChild(light)

light2 = Light.create()
light2.setColor(Color("#707090"))
light2.setPosition(Vector3(0, -20, -5))
light2.setEnabled(True)

# setup menu
mm = MenuManager.createAndInitialize()
menu = mm.getMainMenu()
skyboxSwitcher.setupSkyboxSwitcher(menu)

# When set to true, scales loaded objects to 1 meter and centers them. Enabled by default
autoScaleCenter = True
scbtn = menu.addButton("Auto Scale / Center", "autoScaleCenter = %value%")
scbtn.getButton().setCheckable(True)
scbtn.getButton().setChecked(True)

selLabel = menu.addLabel("SelectedObject")
selLabel.getWidget().setStyleValue('border-top', '1 white')
menu.addButton("Reset Scale", "onResetScaleButtonClicked()")
menu.addButton("Scale to 1 Meter", "onFixedScaleButtonClicked()")
pinnedCheck = menu.addButton("Static", "onPinnedButtonClicked(%value%)")
pinnedCheck.getButton().setCheckable(True)
ab = menu.addButton("Animate", "onAnimationToggleButtonClicked(%value%)")
ab.getButton().setCheckable(True)

vsmnu = menu.addSubMenu("Visual Options")
vsmnu.addLabel("Transparency")
alphaSlider = vsmnu.addSlider(10, "onAlphaSliderChanged(%value%)")
alphaSlider.getSlider().setValue(0)
alphaSlider.getWidget().setWidth(200)

vl = vsmnu.addLabel("Effects")
vl.getWidget().setStyleValue('border-top', '1 white')
vsmnu.addButton("Textured", "setObjectEffect('textured')")
vsmnu.addButton("Colored Matte", "setObjectEffect('colored')")
vsmnu.addButton("Colored Plastic", "setObjectEffect('colored -g 1.0 -s 30')")
vsmnu.addButton("Additive", "setObjectEffect('colored -a -t -C')")
vsmnu.addButton("Blue Haze", "setObjectEffect('colored -e #303060 -a -t -C -D')")

vl = menu.addLabel("Visible Objects")
vl.getWidget().setStyleValue('border-top', '1 white')

# create the default interactor
interactor = ToolkitUtils.setupInteractor("config/interactor")

# enable wand
scene.displayWand(0, 1)

selectedObject = None

#------------------------------------------------------------------------------
# Function called when a model with the specified name has finished loading.
def onModelLoaded(name):
	#m = models[name]
	#if(m.animated == False): model = StaticObject.create(m.name)
	#else: model = AnimatedObject.create(m.name)
	model = AnimatedObject.create(name)
	model.setName(os.path.basename(name))
	model.setVisible(False)
	
	#default placement in front of camera.
	cam = getDefaultCamera()
	#defaultPos = cam.getPosition() + cam.getHeadOffset() + Vector3(0, 0, -model.getBoundRadius() - 3)
	defaultPos = Vector3(0, 1.5, -3)
	
	pivot = SceneNode.create(name + "_pivot")
	pivot.addChild(model)
	pivot.setPosition(defaultPos)

	if(autoScaleCenter):
		model.setPosition(-model.getBoundCenter())
		s = 1.0 / model.getBoundRadius()
		pivot.setScale(Vector3(s, s, s))
	else:
		pivot.setPosition(pivot.getPosition() - Vector3(0, 0, model.getBoundRadius()))
	
	#model.setBoundingBoxVisible(True)
	#model.setPosition(m.defaultPosition)
	# model displayed as colored by default
	model.setEffect("textured - g 1.0 -s 30")
	model.setSelectable(True)
	model.setVisible(False)
	loadedModels[name] = model
	btn = menu.addButton(os.path.basename(name), "onModelButtonClicked('" + name + "', %value%)")
	btn.setText(os.path.basename(name))
	btn.getButton().setCheckable(True)
	btn.getButton().setChecked(True)
	onModelButtonClicked(name, True)

#------------------------------------------------------------------------------
# Event handler for model button click
def onModelButtonClicked(name, value):
	global curModel
	curModel = loadedModels[name]
	curModel.setVisible(value)
	# If the model has been set to visible, set it as the selected object
	if(value): objectManipulator.currentObject = curModel

#------------------------------------------------------------------------------
def onPinnedButtonClicked(value):
	global selectedObject
	if(selectedObject != None):
		selectedObject.setSelectable(not value)

#------------------------------------------------------------------------------
def onResetScaleButtonClicked():
	global selectedObject
	if(selectedObject != None):
		selectedObject.setScale(Vector3(1, 1, 1))

#--------------------------------------------------------------------------------------------------
def onFixedScaleButtonClicked():
	global selectedObject
	if(selectedObject != None):
		# Scale the object to be 1 meter big.
		factor = 1.0 / selectedObject.getBoundRadius()
		curScale = selectedObject.getScale()
		selectedObject.setScale(curScale * factor)
		
#------------------------------------------------------------------------------
def onAnimationToggleButtonClicked(value):
	global selectedObject
	if(selectedObject != None):
		if(selectedObject.hasAnimations()):
			if(value):
				curModel.loopAnimation(0)
			else:
				curModel.stopAllAnimations()
	
#------------------------------------------------------------------------------
def onAlphaSliderChanged(value):
	global selectedObject
	if(selectedObject != None):
		alpha = 1.0 - value / 10.0
		if(alpha != 1.0): selectedObject.getMaterial().setTransparent(True)
		else: selectedObject.getMaterial().setTransparent(False)
		selectedObject.getMaterial().setAlpha(alpha)

#------------------------------------------------------------------------------
def setObjectEffect(value):
	global selectedObject
	if(selectedObject != None):
			selectedObject.setEffect(value)
			
#------------------------------------------------------------------------------
def createFilesystemMenu(mnu, dir):
	global modelButtons
	for filename in os.listdir(dir):
		filePath = dir + "/" + filename
		# Skip hidden files and directories
		if(not filename.startswith('.')):
			fl = filename.lower()
			if(fl.endswith('.fbx') or fl.endswith('.obj') or fl.endswith('.iv') or fl.endswith('.ply') or fl.endswith('.stl')):
				modelButtons[filePath] = mnu.addButton(os.path.basename(filename), "queueModelLoad('" + filePath + "')")
			elif(os.path.isdir(filePath)):
				createFilesystemMenu(mnu.addSubMenu(os.path.basename(filename)), filePath)

createFilesystemMenu(menu.addSubMenu('Load'), modelHome)

#------------------------------------------------------------------------------
def queueModelLoad(modelPath):
	global modelButtons
	modelName = os.path.basename(modelPath)
	mi = ModelInfo()
	mi.name = modelPath
	mi.path = modelPath
	#mi.size = 2
	mi.optimize = True
	scene.loadModelAsync(mi, "onModelLoaded('" + modelPath + "')")
	modelButtons[modelPath].setText(modelButtons[modelPath].getText() + " <<")
	modelButtons[modelPath].setCommand("")

#------------------------------------------------------------------------------
def updateSelectedObject(selObj):
	global selectedObject
	selectedObject = selObj
	if(selectedObject != None):
		selLabel.setText("Selected Object: " + selectedObject.getName())
		pinnedCheck.getButton().setChecked(not selectedObject.isSelectable())
		alpha = 9 - selectedObject.getMaterial().getAlpha() * 9;
		alphaSlider.getSlider().setValue(int(alpha))
	else:
		selLabel.setText("Selected Object: None")

#------------------------------------------------------------------------------
def onUpdate(frame, t, dt):
	global selectedObject
	cam = getDefaultCamera()
	light.setPosition(cam.getHeadOffset())
	if(objectManipulator.currentObject != selectedObject):
		updateSelectedObject(objectManipulator.currentObject)

#------------------------------------------------------------------------------
def onEvent():
	e = getEvent()
	if(not e.isProcessed()):
		objectManipulator.onEvent(e)
	
setEventFunction(onEvent)
setUpdateFunction(onUpdate)
