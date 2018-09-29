#Author-M4nusky
#Description-S2M pulley generator

import adsk.core as Core
import adsk.fusion as Fusion
import adsk as Adsk
import traceback
import math

from . import transaction
import time


# Entry points

def run(context):
    print("in main.run")
    transaction.setup(script4, "S2Mv2")
    
def stop(context):  
    print("in main.stop")
    transaction.cleanup()
    
    
# Some helpers
    
def len2D(pt):
    return math.sqrt( (pt.x*pt.x) + (pt.y*pt.y) )
    
def len2DSq(pt):
    return (pt.x*pt.x) + (pt.y*pt.y)
    
def dist2D(pt1, pt2):
    dx = pt2.x - pt1.x
    dy = pt2.y - pt1.y
    return math.sqrt((dx * dx) + (dy * dy))
    
def dist2DSq(pt1, pt2):
    dx = pt2.x - pt1.x
    dy = pt2.y - pt1.y
    return (dx * dx) + (dy * dy)

def vertical(pt1, pt2):
    return (pt1.geometry.z != pt2.geometry.z) and (pt1.geometry.x == pt2.geometry.x) and (pt1.geometry.y == pt2.geometry.y)
         
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
    
_s = 1
_c = 1

def setRotate(a):
    global _s
    global _c
    _s = math.sin(a)
    _c = math.cos(a)

def rotateZ(pt): 
    x = (pt.x * _c) - (pt.y * _s)
    y = (pt.x * _s) + (pt.y * _c)    
    pt.x = x
    pt.y = y    
    
    
# Main scripts
            
def script4():
    print("in main.script")
    ui = None
    try:
        app = Core.Application.get()
        ui  = app.userInterface
        design = Fusion.Design.cast(app.activeProduct)       
    
        if not design:
            raise BaseException('No active Fusion design')
    
        design.designType = Fusion.DesignTypes.ParametricDesignType
       
        # Center point
        cp = Core.Point3D.create(0,0,0)
        
        # S2M Standard Parameters
        pitch = 0.2
        edgeRad = 0.019
        filletRad = 0.01
        invRad = 0.1325
        invOffsetX = 0.130 / 2
        invOffsetY = 0.0172
        
        pitchOffset = 0.0254
        baseOffset = 0.076
        
        # Pulley properties
        (userInput, cancelled) = inputInt("20", 'Number of teeth', design, ui)
        if cancelled:
            return
        n = int(userInput)
        
        (userInput, cancelled) = inputLength("2 mm", 'Sides Thickness', design, ui)
        if cancelled:
            return
        st = userInput
        
        (userInput, cancelled) = inputLength("1.5 mm", 'Sides Radius Margin', design, ui)
        if cancelled:
            return
        sr = userInput
        
        (userInput, cancelled) = inputLength("6.5 mm", 'Pulley Thickness', design, ui)
        if cancelled:
            return
        t = userInput


        
        startTime = time.time()
        
        pd2 = (n * pitch / math.pi) / 2
        od2 = pd2 - pitchOffset
        bd2 = od2 - baseOffset
        
        midPt = (od2 + bd2)/2
        #midPtSq = midPt * midPt
        
        toothAngle = 2 * math.pi / n
        halfAngle = math.pi / n
        
        # create a new occurence of a new component at origin
        newComp = design.rootComponent.occurrences.addNewComponent(Core.Matrix3D.create()).component        
    
        # Create a new sketch on the xy plane.	
        sketch = newComp.sketches.add(newComp.xYConstructionPlane, None)   
        sketch2 = newComp.sketches.add(newComp.xYConstructionPlane, None)  
    
        newComp.name = "S2M v2, n={}".format(n)
        
        
        
        # Setup arcs        
        left_pt = Core.Point3D.create(-invOffsetX, invOffsetY + od2, 0)
        left_arc = Core.Point3D.create(-invOffsetX + invRad, invOffsetY + od2, 0)
        
        right_pt = Core.Point3D.create( invOffsetX, invOffsetY + od2, 0)
        right_arc = Core.Point3D.create( invOffsetX - invRad, invOffsetY + od2, 0)
        
        od_arc = Core.Point3D.create(0, od2, 0)
        bd_arc = Core.Point3D.create(0, bd2, 0)     
        
        setRotate(halfAngle)           
        rotateZ(od_arc)
        rotateZ(bd_arc)
        
        rotateZ(left_pt)
        rotateZ(left_arc)  
        
        setRotate(-halfAngle)   
        rotateZ(right_pt)
        rotateZ(right_arc)   
            
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(left_pt,  left_arc, -1.5)
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(right_pt, right_arc, 1.5)
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(cp, od_arc, -toothAngle)
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(cp, bd_arc, -toothAngle)
        
        sketch.sketchCurves.sketchLines.addByTwoPoints(cp, bd_arc)
        bd_arc2 = Core.Point3D.create(-bd_arc.x, bd_arc.y, bd_arc.z)
        sketch.sketchCurves.sketchLines.addByTwoPoints(cp, bd_arc2)

    
        # PD circle
        p_circ = sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, pd2)
        p_circ.isConstruction = True
        

        # Get all the profiles
        collection = Core.ObjectCollection.create()    
        for prof in sketch.profiles:
            collection.add(prof)
              
        # Create an extrusion input
        extrudes = newComp.features.extrudeFeatures
        extInput = extrudes.createInput(collection, Fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = Core.ValueInput.createByReal(t)
        extInput.setDistanceExtent(False, distance)
    
        # Create the extrusion.
        pulleyTooth = extrudes.add(extInput)
       
  
        # Add base fillets        
        fillets = newComp.features.filletFeatures
        collection.clear()
     
        # Get the straight edges closest to midpoint
        for face in pulleyTooth.sideFaces:
            for edge in face.edges:
                if edge.geometry.curveType == Core.Curve3DTypes.Line3DCurveType:
                    if vertical(edge.endVertex, edge.startVertex) and \
                    dist2DSq(bd_arc, edge.endVertex.geometry) > 0.00001 and \
                    dist2DSq(bd_arc2, edge.endVertex.geometry) > 0.00001 and \
                    (math.fabs(len2D(edge.endVertex.geometry) - bd2) < 0.01):  
                        collection.add(edge)
                    
        filletInput = fillets.createInput()  
        filletInput.addConstantRadiusEdgeSet(collection, Core.ValueInput.createByReal(filletRad), False)
        filletInput.isG2 = False
        filletInput.isRollingBallCorner = False        
        fillets.add(filletInput)
    
    
        # Add edge fillets  
        collection.clear()
     
        # Get the straight edges fartest from midpoint
        for face in pulleyTooth.sideFaces:
            for edge in face.edges:
                if (edge.geometry.curveType == Core.Curve3DTypes.Line3DCurveType):
                    if (edge.pointOnEdge.y > midPt) :
                        collection.add(edge)
            
        filletInput = fillets.createInput()  
        filletInput.addConstantRadiusEdgeSet(collection, Core.ValueInput.createByReal(edgeRad), False) 
        fillets.add(filletInput)
    
        # Circular pattern for each teeth
        collection.clear()
        collection.add(pulleyTooth.bodies.item(0))
    
        # Create the input for circular pattern
        circularFeats = newComp.features.circularPatternFeatures
        circularFeatInput = circularFeats.createInput(collection, newComp.zConstructionAxis)
        circularFeatInput.quantity = Core.ValueInput.createByReal(n)
        circularFeatInput.totalAngle = Core.ValueInput.createByString('360 deg')
        circularFeatInput.isSymmetric = False
        
        # Create the circular pattern
        allTeeth = circularFeats.add(circularFeatInput)
        

        # Add sides
        if (st != 0.0) and (sr > 0):
            sketch2.sketchCurves.sketchCircles.addByCenterRadius(cp, od2 + sr)
            collection.clear()
            collection.add(sketch2.profiles.item(0))
            extInput = extrudes.createInput(collection, Fusion.FeatureOperations.NewBodyFeatureOperation)
            extInput.setDistanceExtent(False, Core.ValueInput.createByReal(-st))
            bottomSide = extrudes.add(extInput)
            topSide = extrudes.add(extInput)
            
                        
            collection.clear()
            collection.add(bottomSide.bodies.item(0))
            
            vector = Core.Vector3D.create(0.0, 0.0, t+st)
            transform = Core.Matrix3D.create()
            transform.translation = vector

            moveFeats = newComp.features.moveFeatures
            moveFeatureInput = moveFeats.createInput(collection, transform)
            moveFeats.add(moveFeatureInput)

            collection.clear()
            collection.add(bottomSide.bodies.item(0))
            collection.add(topSide.bodies.item(0))
            
        else:
            collection.clear()
            
        # Combine bodies from circula pattern with base tooth
        for th in allTeeth.bodies:
            collection.add(th)
            
        comb = newComp.features.combineFeatures
        combInput = comb.createInput(pulleyTooth.bodies.item(0), collection)
        combInput.operation = Fusion.FeatureOperations.JoinFeatureOperation        
        
        # Combine
        pulley = comb.add(combInput)
        pulley.bodies.item(0).name = "S2M " + str(n)
        
        endTime = time.time()
        ui.messageBox(str(endTime - startTime), "Elapsed Time")
        

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



