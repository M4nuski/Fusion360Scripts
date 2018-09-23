#Author-M4nusky
#Description- Conical shape generator

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

_baseEndC = adsk.core.DropDownCommandInput.cast(None)
_topEndC = adsk.core.DropDownCommandInput.cast(None)
_baseEndP = adsk.core.DropDownCommandInput.cast(None)
_topEndP = adsk.core.DropDownCommandInput.cast(None)

_errMessage = adsk.core.TextBoxCommandInput.cast(None)

_handlers = []

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui  = _app.userInterface

        # Create a command definition and add a button to the CREATE panel. # EC
        cmdDef = _ui.commandDefinitions.addButtonDefinition('ConicalShaftPythonAddIn', 'Conical Shaft', 'Creates a conical shaft component')        
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        gearButton = createPanel.controls.addCommand(cmdDef)
        
        # Connect to the command created event.
        onCommandCreated = GearCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        if context['IsApplicationStartup'] == False:
            _ui.messageBox('The "Conical Shape" command has been added\nto the CREATE panel of the MODEL workspace.') 
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        createPanel = _ui.allToolbarPanels.itemById('SolidCreatePanel')
        gearButton = createPanel.controls.itemById('ConicalShaftPythonAddIn')  # EC      
        if gearButton:
            gearButton.deleteMe()
        
        cmdDef = _ui.commandDefinitions.itemById('ConicalShaftPythonAddIn') # EC
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

            baseDia = "1.0"
                
            topDia = "0.5"            
               
            height = "2.0"

            global _baseDia, _topDia, _height, _baseEndC, _baseEndP, _topEndC, _topEndP
            
            cmd = eventArgs.command
            cmd.isExecutedWhenPreEmpted = False
            inputs = cmd.commandInputs

            _baseDia = inputs.addValueInput('baseDia', 'Base Diameter', defaultUnits, adsk.core.ValueInput.createByReal(float(baseDia)))

            _baseEndC = inputs.addDropDownCommandInput('baseEndC', 'Base End Condition', adsk.core.DropDownStyles.TextListDropDownStyle)
            _baseEndC.listItems.add('Free', True)
            _baseEndC.listItems.add('Direction', False)        
            
            _baseEndP = inputs.addDropDownCommandInput('baseEndP', 'Base End Condition', adsk.core.DropDownStyles.TextListDropDownStyle)
            _baseEndP.listItems.add('Sharp', True)
            _baseEndP.listItems.add('Tangent', False)   
            _baseEndP.isVisible = False;
            
            _topDia = inputs.addValueInput('topDia', 'Top Diameter', defaultUnits, adsk.core.ValueInput.createByReal(float(topDia)))

            _topEndC = inputs.addDropDownCommandInput('topEndC', 'Top End Condition', adsk.core.DropDownStyles.TextListDropDownStyle)
            _topEndC.listItems.add('Free', True)
            _topEndC.listItems.add('Direction', False)    
            
            _topEndP = inputs.addDropDownCommandInput('topEndP', 'Base End Condition', adsk.core.DropDownStyles.TextListDropDownStyle)
            _topEndP.listItems.add('Sharp', True)
            _topEndP.listItems.add('Tangent', False)   
            _topEndP.isVisible = False;
            
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
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            baseDia = _baseDia.value
            topDia = _topDia.value
            height = _height.value
            
            if float(baseDia) > 0:
                baseEnd = _baseEndC.selectedItem.name
            else:
                baseEnd = _baseEndP.selectedItem.name
                
            if float(topDia) > 0:
                topEnd = _topEndC.selectedItem.name
            else:
                topEnd = _topEndP.selectedItem.name              
                
            CreateConicalShape(baseDia, topDia, height, baseEnd, topEnd)
            
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
            print(changedInput.id)
            if changedInput.id == "baseDia":
                if float(_baseDia.value) > 0:
                    _baseEndC.isVisible = True
                    _baseEndP.isVisible = False
                else:
                    _baseEndC.isVisible = False
                    _baseEndP.isVisible = True                    
                
            if changedInput.id == "topDia":
                if float(_topDia.value) > 0:
                    _topEndC.isVisible = True
                    _topEndP.isVisible = False
                else:
                    _topEndC.isVisible = False
                    _topEndP.isVisible = True               

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
                
            #ba = int(_bevelAngle.value ) # EC
            #if (ba > 89) or (ba < 0):
            #    _errMessage.text = 'The bevel angle must be between 0 and 89 degrees.'
            #    eventArgs.areInputsValid = False
            #    return       

        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
                
def CreateConicalShape(base, top, height, baseEnd, topEnd):
    design = adsk.fusion.Design.cast(_app.activeProduct)
    
    # Create a new component by creating an occurrence.
    occs = design.rootComponent.occurrences
    mat = adsk.core.Matrix3D.create()
    newOcc = occs.addNewComponent(mat)        
    newComp = adsk.fusion.Component.cast(newOcc.component)
    
    newComp.name = "Conical Shaft;" + str(base) + ":" + str(top) + ":" + str(height);
    
    # Create a new sketch.
    sketches = newComp.sketches
    xyPlane = newComp.xYConstructionPlane
    baseSketch = sketches.add(xyPlane)
            
    baseSketch.name = "Conical Shape Generator Sketch"
    
    lofts = newComp.features.loftFeatures
    loftInput = lofts.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            
    # Base feature
    if base > 0:                
        baseSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), base)
        loftInput.loftSections.add(baseSketch.profiles.item(baseSketch.profiles.count-1))
    else:
        baseSketch.sketchPoints.add(adsk.core.Point3D.create(0,0,0))
        loftInput.loftSections.add(baseSketch.sketchPoints.item(baseSketch.sketchPoints.count-1))
        
    # Top feature
    if top > 0:
        baseSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,height), top)
        loftInput.loftSections.add(baseSketch.profiles.item(baseSketch.profiles.count-1))
    else:
        baseSketch.sketchPoints.add(adsk.core.Point3D.create(0,0,height))
        loftInput.loftSections.add(baseSketch.sketchPoints.item(baseSketch.sketchPoints.count-1))
    # create construction plane
      #  planes = newComp.constructionPlanes
    # Create construction plane input
      #  planeInput = planes.createInput()
      #  offset = adsk.core.ValueInput.createByReal(height)
      #  planeInput.setByOffset(xyPlane, offset)
      #  newPlane = planes.add(planeInput)
    
      #  secondSketch = sketches.add(newPlane)
       # secondSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,height), top)
    
    
    #baseSect = loftInput.loftSections.add(baseSketch.profiles.item(0)) 
    #topSect = loftInput.loftSections.add(baseSketch.profiles.item(1))
    
    setEndSection(loftInput.loftSections.item(0), baseEnd)    
    setEndSection(loftInput.loftSections.item(1), topEnd)           
    # Create loft feature
    lofts.add(loftInput)
        
        
        
def setEndSection(sect, endName):
    if endName == "Free":
        sect.setFreeEndCondition()
    if endName == "Direction":
        sect.setDirectionEndCondition(adsk.core.ValueInput.createByReal(0.0), adsk.core.ValueInput.createByReal(1.0))
    if endName == "Sharp":
        sect.setPointSharpEndCondition()
    if endName == "Tangent":
        sect.setPointTangentEndCondition(adsk.core.ValueInput.createByReal(1.0))
        
        
