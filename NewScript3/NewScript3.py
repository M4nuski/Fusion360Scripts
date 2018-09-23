#Author-M4nusky
#Description-simplier script to add parametric shaft

import adsk.core, adsk.fusion, adsk.cam, traceback

class internalScriptError(BaseException):
    pass

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        ui.messageBox('Hello script Test 3')
        print("test script 3 log")
        
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            raise internalScriptError('No active Fusion design')

        ui.messageBox(design.rootComponent.partNumber, 'Desing part number?')   
        
        rootComp = design.rootComponent;

        # Create a new sketch on the xy plane.	
        sketches = rootComp.sketches;
        print("number of sketches in rootcomponent:", sketches.count)
        
        # create a new occurence of a new component at origin
        newComp = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
        
        newComp.name = "Script 3 Geneated Extrusion"
        
        xyPlane = newComp.xYConstructionPlane
        sketches = newComp.sketches
        sketch = sketches.add(xyPlane, None)
        
        print(design.unitsManager.evaluateExpression("5mm"), "units evaluated")
        #dim1 = adsk.core.ValueInput.stringValue("5 mm")
        sketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 0.5)
        
        
        #Create an extrusion.	
       #newComp.features.extrudeFeatures.
        
        extInput = newComp.features.extrudeFeatures.createInput(sketch.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation);
        distance = adsk.core.ValueInput.createByString("1.234 in")
        extInput.setDistanceExtent(False, distance)
        newComp.features.extrudeFeatures.add(extInput)

        #Create a new occurrence for the component, offset by 15 cm in the X direction.	
        #trans.setCell(0, 3, 15.0);
       # newOcc = rootComp.occurrences.addExistingComponent(newComp, trans);

    except internalScriptError as ise:        
        if ui:
            ui.messageBox(ise, "Internal Script Error")
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            
def stop(context):
    print("stop")
