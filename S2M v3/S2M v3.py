#Author-M4nusky
#Description-Updated version of S2M step pulley generator

import adsk.core as Core
import adsk.fusion as Fusion
import adsk as Adsk
import traceback
import math
import time

def run(context):
    print("run")
    try:
        script4()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):  
    print("in main.stop")




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

def inputBoolean(text, ui):
    # Get a string from the user.
    input = ui.messageBox(text, 'S2M Options', Core.MessageBoxButtonTypes.YesNoCancelButtonType, Core.MessageBoxIconTypes.QuestionIconType)
    if input == Core.DialogResults.DialogYes: return (True, False)
    if input == Core.DialogResults.DialogNo: return (False, False)
    return (False, True)

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

    # Base Data
        # Center point
        cp = Core.Point3D.create(0,0,0)
        
        # S2M Standard Parameters
        pitch = 0.2
        edgeRad = 0.019 # outside teeth fillet
        filletRad = 0.01 # inside root fillet
        invRad = 0.1325
        invOffsetX = 0.130 / 2
        invOffsetY = 0.0172
        
        pitchOffset = 0.0254 # pitch radius to outside radius
        baseOffset = 0.076 # outside radius to base radius
        
    # Get Pulley properties from user
        (userInput, cancelled) = inputInt("20", 'Number of teeth', design, ui)
        if cancelled:
            return
        n = int(userInput)

        (userInput, cancelled) = inputLength("6.5 mm", 'Pulley Thickness', design, ui)
        if cancelled:
            return
        t = userInput

        (userInput, cancelled) = inputBoolean("Add Sides?", ui)
        if cancelled:
            return
        addSides = userInput

        if addSides:        
            (userInput, cancelled) = inputLength("2 mm", 'Sides Thickness', design, ui)
            if cancelled:
                return
            st = userInput
            
            (userInput, cancelled) = inputLength("1.5 mm", 'Sides Margin From Outer Radius', design, ui)
            if cancelled:
                return
            sr = userInput
        else:
            st = 0.0
            sr = 0.0
        
        (userInput, cancelled) = inputBoolean("Dimensional Offsets?", ui)
        if cancelled:
            return
        addOffsets = userInput

        if addOffsets:
            (userInput, cancelled) = inputLength("0.0 mm", '"Involute" Shape Radius Offset', design, ui)
            if cancelled:
                return
            sro = userInput

            (userInput, cancelled) = inputLength("0.0 mm", 'Root Radius Offset', design, ui)
            if cancelled:
                return
            rro = userInput

            (userInput, cancelled) = inputLength("0.0 mm", 'Teeth Radius Offset', design, ui)
            if cancelled:
                return
            tro = userInput
        else:
            sro = 0.0
            rro = 0.0
            tro = 0.0


        print("invRad offset ", sro)
        print("root offset ", rro)
        print("teeth offset ", tro)

        startTime = time.time()
    
    # Calculate parameters
        
        pitchRadius = (n * pitch / math.pi) / 2
        print ("pitch dia ", pitchRadius * 2)
        outsideRadius  = pitchRadius - pitchOffset
        offsetOutsideRadius = pitchRadius - pitchOffset + tro
        rootRadius = outsideRadius - baseOffset + rro
        invRad = invRad + sro
        
        print("outside dia ", outsideRadius * 2)
        print("root dia ", rootRadius * 2)
        print("invRad ", invRad)
        
        midPt = (outsideRadius + rootRadius)/2
        #midPtSq = midPt * midPt
        
        toothAngle = 2 * math.pi / n
        halfAngle = math.pi / n

    # Create Sketch
        
        # Setup arcs        
        left_pt = Core.Point3D.create(-invOffsetX, invOffsetY + outsideRadius, 0)
        left_arc = Core.Point3D.create(-invOffsetX + invRad, invOffsetY + outsideRadius, 0)
   
        right_pt = Core.Point3D.create( invOffsetX, invOffsetY + outsideRadius, 0)
        right_arc = Core.Point3D.create( invOffsetX - invRad, invOffsetY + outsideRadius, 0)
        
        od_arc = Core.Point3D.create(0, offsetOutsideRadius, 0)
        bd_arc = Core.Point3D.create(0, rootRadius, 0)
        
        setRotate(halfAngle)           
        rotateZ(od_arc)
        rotateZ(bd_arc)

        rotateZ(left_pt)
        rotateZ(left_arc)  
        
        setRotate(-halfAngle)   
        rotateZ(right_pt)
        rotateZ(right_arc)

        # Validate teeth offset limit
        if offsetOutsideRadius > dist2D(left_arc, cp):
            raise BaseException("Teeth offset too big: teeth radius is greater than outside circle")

        # Validate root offset limit
        if dist2D(left_pt, bd_arc) > invRad - filletRad:
            raise BaseException("Root offset too small: would create root diameter smaller than base circle")
            
        # create a new occurence of a new component at origin
        newComp = design.rootComponent.occurrences.addNewComponent(Core.Matrix3D.create()).component        
    
        # Create a new sketch on the xy plane.
        sketch = newComp.sketches.add(newComp.xYConstructionPlane)   
        sketch.name = "InvoluteShapeSketch"

        newComp.name = "S2M v3, n={}".format(n)        
            
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(left_pt,  left_arc, -1.5)
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(right_pt, right_arc, 1.5)
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(cp, od_arc, -toothAngle)
        sketch.sketchCurves.sketchArcs.addByCenterStartSweep(cp, bd_arc, -toothAngle)
        
        sketch.sketchCurves.sketchLines.addByTwoPoints(cp, bd_arc)
        bd_arc2 = Core.Point3D.create(-bd_arc.x, bd_arc.y, bd_arc.z)
        sketch.sketchCurves.sketchLines.addByTwoPoints(cp, bd_arc2)

    
    # Add Construction Data to Sketch using standard spec
        # PD circle
        p_circ = sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, pitchRadius)
        p_circ.isConstruction = True

        # BD circle
        tempCC = sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, rootRadius - rro)
        tempCC.isConstruction = True

        # OD circle
        tempCC = sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, outsideRadius)
        tempCC.isConstruction = True 

        # Involute circle
        tempCC = sketch.sketchCurves.sketchCircles.addByCenterRadius(left_pt, invRad - sro)
        tempCC.isConstruction = True 

        # Involute circle
        tempCC = sketch.sketchCurves.sketchCircles.addByCenterRadius(right_pt, invRad - sro)
        tempCC.isConstruction = True 

    # Add parameters to Sketch
        sketchTexts = sketch.sketchTexts
        textPoint = Core.Point3D.create(pitchRadius, pitchRadius, 0.0)
        dataString = "n={}\nthickness={:.4f}".format(n, t)
        if addSides:
            dataString += "\nsides thickness={:.4f}\nsides margin={:.4f}".format(st, sr)
        if addOffsets:
            dataString += "\nshape radius offset={:.6f}\nroot radius offset={:.6f}\nteeth radius offset={:.6f}".format(sro, rro, tro)
        sketchTextInput = sketchTexts.createInput(dataString, 0.2, textPoint)   
        sketchTexts.add(sketchTextInput)


    # Create Solid
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
                    (math.fabs(len2D(edge.endVertex.geometry) - rootRadius) < 0.01):  
                        collection.add(edge)
                    
        filletInput = fillets.createInput()  
        filletInput.addConstantRadiusEdgeSet(collection, Core.ValueInput.createByReal(filletRad), False)
        filletInput.isG2 = False
        filletInput.isRollingBallCorner = False
        try:
            fillets.add(filletInput)
        except:
            ui.messageBox('Failed to create root fillets:\n{}'.format(traceback.format_exc()), "Script Exception (S2M)",
                          Core.MessageBoxButtonTypes.OKButtonType,
                          Core.MessageBoxIconTypes.CriticalIconType) 
    
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

        try:
            fillets.add(filletInput)
        except:
            ui.messageBox('Failed to create teeth fillets:\n{}'.format(traceback.format_exc()), "Script Exception (S2M)",
                          Core.MessageBoxButtonTypes.OKButtonType,
                          Core.MessageBoxIconTypes.CriticalIconType) 

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
        if addSides and (st != 0.0) and (sr > 0):
            sketch2 = newComp.sketches.add(newComp.xYConstructionPlane)
            sketch2.name = "SidesSketch"

            sketch2.sketchCurves.sketchCircles.addByCenterRadius(cp, outsideRadius + sr)
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
        print("Elapsed time: " + str(endTime - startTime))
        

    except BaseException as ise:      
        print("Internal Script Error {}".format(ise))
        #if ui:
        ui.messageBox(ise.args[0], "Internal Script Error",
                          Core.MessageBoxButtonTypes.OKButtonType, 
                          Core.MessageBoxIconTypes.CriticalIconType)
    except:
        print('Failed:\n{}'.format(traceback.format_exc()))
        #if ui:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), "Script Exception (S2M)",
                          Core.MessageBoxButtonTypes.OKButtonType,
                          Core.MessageBoxIconTypes.CriticalIconType) 