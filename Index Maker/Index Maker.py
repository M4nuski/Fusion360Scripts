#Author-M4nusky
#Description-Create a series of circle following a specific formula for diameter and stride

import adsk.core as Core
import adsk.fusion as Fusion
import adsk as Adsk
import traceback
#import math

from . import transaction
#import time

# Entry points

def run(context):
    print("in main.run")
    transaction.setup(script1, "IndexMaker1")
    
def stop(context):  
    print("in main.stop")
    transaction.cleanup()
    
    
# Some helpers


def inputLength(default, text, design, ui):
    # Prompt the user for a string and validate it's valid.
    isValid = False
    isCancelled = False
    
    while (not isValid) and (not isCancelled):
        # Get a string from the user.
        (input, isCancelled) = ui.inputBox(text, 'Distance', default)
      
        # Exit the program if the dialog was cancelled.
        if isCancelled:
            return (default, isCancelled)
        
        # Check that a valid length description was entered.
        unitsMgr = design.unitsManager
        try:
            realValue = unitsMgr.evaluateExpression(input, unitsMgr.defaultLengthUnits)
            isValid = True
            input = realValue
        except:
            # Invalid expression so display an error and set the flag to allow them
            # to enter a value again.
            ui.messageBox('"' + input + '" is not a valid length expression.', 'Invalid entry', 
                          Core.MessageBoxButtonTypes.OKButtonType, 
                          Core.MessageBoxIconTypes.CriticalIconType)
            isValid = False
    
    return (input, isCancelled)
    
    
def inputInt(default, text, design, ui):
    # Prompt the user for a string and validate it's valid.
    isValid = False
    isCancelled = False
    
    while (not isValid) and (not isCancelled):
        # Get a string from the user.
        (input, isCancelled) = ui.inputBox(text, 'Integer', default)
      
        # Exit the program if the dialog was cancelled.
        if isCancelled:
            return (default, isCancelled)
        
        # Check that a valid length description was entered.

        if str.isdigit(input):
            isValid = True
        else:
            # Invalid expression so display an error and set the flag to allow them
            # to enter a value again.
            ui.messageBox('"' + input + '" is not a valid integer expression.', 'Invalid entry', 
                          Core.MessageBoxButtonTypes.OKButtonType, 
                          Core.MessageBoxIconTypes.CriticalIconType)
            isValid = False
    
    return (input, isCancelled)
    

# Main scripts

            
def script1():
    print("in main.script")
    ui = None
    try:
        app = Core.Application.get()
        ui  = app.userInterface
        design = Fusion.Design.cast(app.activeProduct)       
    
        if not design:
            raise BaseException('No active Fusion design')
    
        design.designType = Fusion.DesignTypes.ParametricDesignType

        
        # Properties
        (userInput, cancelled) = inputInt("10", 'Number of circles', design, ui)
        if cancelled:
            return
        n = int(userInput)
        
        (userInput, cancelled) = inputLength("10 mm", 'Starting Diameter', design, ui)
        if cancelled:
            return
        sd = userInput
        
        (userInput, cancelled) = inputLength("1 mm", 'Diameter incrase per circle', design, ui)
        if cancelled:
            return
        di = userInput
        
        (userInput, cancelled) = inputLength("15 mm", 'Basic Offset between circles', design, ui)
        if cancelled:
            return
        so = userInput
        
        (userInput, cancelled) = inputLength("1 mm", 'Offset incrase per circle\n(Equal to dia incrase for constant gap)', design, ui)
        if cancelled:
            return
        oi = userInput
        
        #todo add multiline

       
        # Get current component
        comp = design.rootComponent        
    
        # Create a new sketch on the xy plane of the current component	
        sketch = comp.sketches.add(comp.xYConstructionPlane, None)   
    
        sketch.name = "Index, num:{}, Bdia: {} +by {}, Offset: {} +by{}".format(n, sd, di, so, oi)        
        
        
        # Setup
        # (Convert to radius)
        sd = sd /2
        di = di /2
        
        offset = 0
        
        # Loop and add circles to sketch
        for i in range(n):
            sketch.sketchCurves.sketchCircles.addByCenterRadius(Core.Point3D.create(offset , 0, 0), sd + (di*i))
            offset = offset + so + (oi * i)



    except BaseException as ise:      
        print("Internal Script Error {}".format(ise))
    #    if ui:
     #       ui.messageBox(ise, "Internal Script Error",
      #                    Core.MessageBoxButtonTypes.OKButtonType, 
       #                   Core.MessageBoxIconTypes.CriticalIconType)
    except:
      #  if ui:
       #     ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), "Script Exception (S2M)") 
      #  else:
            print('Failed:\n{}'.format(traceback.format_exc()))



