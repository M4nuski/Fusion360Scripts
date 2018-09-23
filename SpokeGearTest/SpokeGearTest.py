#Author-M4nusky
#Description- Spoked Gear Generator

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

# Globals
_app = adsk.core.Application.cast(None)
_ui = adsk.core.UserInterface.cast(None)
_units = ''

# Command inputs
_baseDia = adsk.core.ValueCommandInput.cast(None)
_topDia = adsk.core.ValueCommandInput.cast(None)
_height = adsk.core.ValueCommandInput.cast(None)
_numTeeth = adsk.core.StringValueCommandInput.cast(None)
_filletRadius = adsk.core.ValueCommandInput.cast(None)

#_baseEndC = adsk.core.DropDownCommandInput.cast(None)
#_topEndC = adsk.core.DropDownCommandInput.cast(None)
#_baseEndP = adsk.core.DropDownCommandInput.cast(None)
#_topEndP = adsk.core.DropDownCommandInput.cast(None)

_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_handlers = []

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        # Create a command definition and add a button to the CREATE panel. # EC
        cmdDef = _ui.commandDefinitions.addButtonDefinition('SpokedGearPythonAddIn', 'Spoked Gear', 'Creates a spoked gear component')
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        createPanel.controls.addCommand(cmdDef)

        # Connect to the command created event.
        onCommandCreated = GearCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        if context['IsApplicationStartup'] == False:
            _ui.messageBox('The "Spoked Gear" command has been added\nto the CREATE panel of the MODEL workspace.')
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        gearButton = createPanel.controls.itemById('SpokedGearPythonAddIn')  # EC
        if gearButton:
            gearButton.deleteMe()

        cmdDef = _ui.commandDefinitions.itemById('SpokedGearPythonAddIn') # EC
        if cmdDef:
            cmdDef.deleteMe()
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Verfies that a value command input has a valid expression and returns the
# value if it does.  Otherwise it returns False.  This works around a
# problem where when you get the value from a ValueCommandInput it causes the
# current expression to be evaluated and updates the display.  Some new functionality
# is being added in the future to the ValueCommandInput object that will make
# this easier and should make this function obsolete.
def getCommandInputValue(commandInput, unitType):
    try:
        valCommandInput = adsk.core.ValueCommandInput.cast(commandInput)
        if not valCommandInput:
            return (False, 0)

        # Verify that the expression is valid.
        des = adsk.fusion.Design.cast(_app.activeProduct)
        unitsMgr = des.unitsManager

        if unitsMgr.isValidExpression(valCommandInput.expression, unitType):
            value = unitsMgr.evaluateExpression(valCommandInput.expression, unitType)
            return (True, value)
        else:
            return (False, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class GearCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)

            # Verify that a Fusion design is active.
            des = adsk.fusion.Design.cast(_app.activeProduct)
            if not des:
                _ui.messageBox('A Fusion design must be active when invoking this command.')
                return()

            defaultUnits = des.unitsManager.defaultLengthUnits

            baseDia = "5.0"

            topDia = "10.0"

            height = "2.0"

            numTeeth = "10"

            filletRadius = "0.0"

            global _baseDia, _topDia, _height, _numTeeth, _filletRadius

            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            _baseDia = inputs.addValueInput('baseDia', 'Base Diameter', defaultUnits, adsk.core.ValueInput.createByReal(float(baseDia)))

            _topDia = inputs.addValueInput('topDia', 'Top Diameter', defaultUnits, adsk.core.ValueInput.createByReal(float(topDia)))

            _numTeeth = inputs.addStringValueInput("numTeeth", 'Number of teeth', numTeeth)

            _filletRadius = inputs.addValueInput('filletRadius', 'Fillet Radius', defaultUnits, adsk.core.ValueInput.createByReal(float(filletRadius)))

            _height = inputs.addValueInput('height', 'Height', defaultUnits, adsk.core.ValueInput.createByReal(float(height)))

            # Connect to the command related events.
            onExecute = GearCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)

            onInputChanged = GearCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            onValidateInputs = GearCommandValidateInputsHandler()
            cmd.validateInputs.add(onValidateInputs)
            _handlers.append(onValidateInputs)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the execute event.
class GearCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            adsk.core.CommandEventArgs.cast(args)

            baseDia = _baseDia.value
            topDia = _topDia.value
            height = _height.value
            numTeeth = int(_numTeeth.value)
            filletRadius = _filletRadius.value

            CreateSpokedGear(baseDia, topDia, height, numTeeth, filletRadius)

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



# Event handler for the inputChanged event.
class GearCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input
#            print(changedInput.id)
#            if changedInput.id == "baseDia":
#                if float(_baseDia.value) > 0:
#                    _baseEndC.isVisible = True
#                    _baseEndP.isVisible = False
#                else:
#                    _baseEndC.isVisible = False
#                    _baseEndP.isVisible = True
#
#            if changedInput.id == "topDia":
#                if float(_topDia.value) > 0:
#                    _topEndC.isVisible = True
#                    _topEndP.isVisible = False
#                else:
#                    _topEndC.isVisible = False
#                    _topEndP.isVisible = True

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the validateInputs event.
class GearCommandValidateInputsHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.ValidateInputsEventArgs.cast(args)

            if (_topDia.value < 0) or (_baseDia.value < 0):
                _errMessage.text = "Diameters must be greater or equal to 0"
                eventArgs.areInputsValid = False
                return                

            if _topDia.value < _baseDia.value:
                _errMessage.text = "Top diameter must be larger than the base diameter"
                eventArgs.areInputsValid = False
                return

            if int(_numTeeth.value) < 1:
                _errMessage.text = "Number of Teeth must be greater than 0"
                eventArgs.areInputsValid = False
                return
                
            if _topDia.value - _baseDia.value < _filletRadius.value:
                _errMessage.text = "Fillet too large"
                eventArgs.areInputsValid = False
                return                

            pitchCir = (_baseDia.value * math.pi)
            filletsLength = _filletRadius.value * 2 * int(_numTeeth.value)
            
            if pitchCir < filletsLength:
                _errMessage.text = "Fillet too large"
                eventArgs.areInputsValid = False
                return       

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def CreateSpokedGear(baseDia, topDia, height, numTeeth, filletRadius):
    design = adsk.fusion.Design.cast(_app.activeProduct)

    # Create a new component by creating an occurrence.
    occs = design.rootComponent.occurrences
    mat = adsk.core.Matrix3D.create()
    newOcc = occs.addNewComponent(mat)
    newComp = adsk.fusion.Component.cast(newOcc.component)

    newComp.name = "SpokedGear;" + str(numTeeth)

    # Create a new sketch.
    sketches = newComp.sketches
    xyPlane = newComp.xYConstructionPlane
    baseSketch = sketches.add(xyPlane)

    baseSketch.name = "Spoked Gear Generator Sketch"

    # Sketch Construction Circles    

    circ = baseSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), baseDia / 2.0)
    #circ.isConstruction = True
    circ = baseSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), topDia / 2.0)
    #circ.isConstruction = True


    
    ext = newComp.features.extrudeFeatures
    extInp = ext.createInput(baseSketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    distance = adsk.core.ValueInput.createByReal(height)
    extInp.setDistanceExtent(False, distance)

    cExt = ext.add(extInp)
    
    
    # Sketch Tooth Lines    
    line1 = baseSketch.sketchCurves.sketchLines.addByTwoPoints(adsk.core.Point3D.create(baseDia/2.0,0,0), adsk.core.Point3D.create(topDia/2.0,0,0))
    line2 = baseSketch.sketchCurves.sketchLines.addByTwoPoints(adsk.core.Point3D.create(baseDia/2.0,0,0), adsk.core.Point3D.create(topDia/2.0,0,0))

    rot = adsk.core.Matrix3D.create()
    rot.setToRotation(math.pi/numTeeth, adsk.core.Vector3D.create(0,0,1), adsk.core.Point3D.create(0,0,0))
    
    #baseSketch.move(line2, rot)


    
    entities = adsk.core.ObjectCollection.create()
    #entities.add(line1)
    entities.add(line2)    

    baseSketch.move(entities, rot)
    
    entities.clear()
    
    
    print("num profiles:", baseSketch.profiles.count)
    middlePoint = adsk.core.Point3D.create((baseDia + topDia) /4.0, 0.0, 0.0)

    tProf = baseSketch.profiles.item(0)
    tDist = tProf.areaProperties().centroid.distanceTo(middlePoint)

    for prof in baseSketch.profiles:
        profCenter = prof.areaProperties().centroid.distanceTo(middlePoint)
        if profCenter < tDist:
            tDist = profCenter
            tProf = prof
 
           
    ext = newComp.features.extrudeFeatures
    extInp = ext.createInput(tProf, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    
    distance = adsk.core.ValueInput.createByReal(height)
    extInp.setDistanceExtent(False, distance)

    tExt = ext.add(extInp)
   
    entities.add(tExt)   
   
    #entities.add(baseFillet)
    #cylFace = baseExtrude.sideFaces.item(0)  

    #cAxis =  adsk.core.Vector3D.create(0,0,1)
        # Make the pattern
    circularPatterns = newComp.features.circularPatternFeatures
    patternInput = circularPatterns.createInput(entities, cExt.sideFaces.item(0)) 
    nti = adsk.core.ValueInput.createByReal(numTeeth)
    patternInput.quantity = nti
    pattern = circularPatterns.add(patternInput)  
    
    

