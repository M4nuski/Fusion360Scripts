#Author-M4nusky
#Description-S2M type pulley generator script

import adsk.core, adsk.fusion, adsk.cam, traceback
import math

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Hello script')
        
        design = adsk.fusion.Design(app.activeProduct).cast()
        if not design:
            ui.messageBox('No active Fusion 360 design', 'No Design')
            return
        
        # Get the root component of the active design.	
        rootComp = design.rootComponent

# Create a new sketch on the xy plane.	
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)

        # Get the SketchCircles collection from an existing sketch.
        circles = sketch.sketchCurves.sketchCircles

# Call an add method on the collection to create a new circle.
        circle1 = circles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 2)

# Get the SketchLines collection from an existing sketch.
        lines = sketch.sketchCurves.sketchLines

# Call an add method on the collection to create a new line.
        axis = lines.addByTwoPoints(adsk.core.Point3D.create(-1,-4,0), adsk.core.Point3D.create(1,-4,0))
        
        
        
        

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
