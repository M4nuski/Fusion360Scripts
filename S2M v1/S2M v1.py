#Author-M4nusky
#Description-S2M pulley generator

import adsk.core as Core
import adsk.fusion as Fusion
import traceback
import math

from . import transaction
import time

def run(context):
    print("in main.run")
    transaction.setup(script, "S2Mv1")
    
def stop(context):  
    print("in main.stop")
    transaction.cleanup()
    
def len2D(pt):
    return math.sqrt( (pt.x*pt.x) + (pt.y*pt.y) )

def script():
    print("in main.script")
    ui = None
    try:
        app = Core.Application.get()
        ui  = app.userInterface
        design = Fusion.Design.cast(app.activeProduct)       
    
        if not design:
            raise BaseException('No active Fusion design')
    
        design.designType = Fusion.DesignTypes.ParametricDesignType
       
        # create a new occurence of a new component at origin
        newComp = design.rootComponent.occurrences.addNewComponent(Core.Matrix3D.create()).component        
    
        # Create a new sketch on the xy plane.	
        sketch = newComp.sketches.add(newComp.xYConstructionPlane, None)        
       
        # Center point
        cp = Core.Point3D.create(0,0,0);
        
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
        (userInput, cancelled) = inputInt("20", design, ui)
        if cancelled:
            return
        n = int(userInput)
        #n = 20
        
        (userInput, cancelled) = inputLength("6 mm", design, ui)
        if cancelled:
            return
        t = userInput
        #t = 0.6
        
        startTime = time.time()
        
        pd2 = (n * pitch / math.pi) / 2
        od2 = pd2 - pitchOffset
        bd2 = od2 - baseOffset
    
        newComp.name = "S2M v1, n={}".format(n)
        #
        # OD circle and pulley body
        sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, od2)
        extrudes = newComp.features.extrudeFeatures
        extInput = extrudes.createInput(sketch.profiles.item(0), Fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = Core.ValueInput.createByReal(t)
        extInput.setDistanceExtent(False, distance)
        od_cyl = extrudes.add(extInput)  
        
        # BD and PD circles
        sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, bd2)
        p_circ = sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, pd2)
        p_circ.isConstruction = True
        
        # "Involutes"
        invOffset = Core.Point3D.create(-invOffsetX, invOffsetY + od2, 0)
        sketch.sketchCurves.sketchCircles.addByCenterRadius(invOffset, invRad)
        invOffset = Core.Point3D.create( invOffsetX, invOffsetY + od2, 0)
        sketch.sketchCurves.sketchCircles.addByCenterRadius(invOffset, invRad)
      
      
        # Get the profile of the involute circles cut
        prof = None;
        for pro in sketch.profiles:
            p_c_y = pro.areaProperties().centroid.y
            p_c_x = pro.areaProperties().centroid.x
            if (p_c_y > bd2) and (p_c_y < od2) and (math.fabs(p_c_x) < 0.0001):
                prof = pro
              
              
        # Create an extrusion input
        extInput = extrudes.createInput(prof, Fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = Core.ValueInput.createByReal(t)
        extInput.setDistanceExtent(False, distance)
    
        # Create the extrusion.
        toothCutter = extrudes.add(extInput)
            
        # Add base fillets to cutter        
        fillets = newComp.features.filletFeatures
        collection = Core.ObjectCollection.create()
     
        # Get the straight edges closest to center
        for face in toothCutter.sideFaces:
            for edge in face.edges:
                if (edge.geometry.curveType == Core.Curve3DTypes.Line3DCurveType):
                    if (edge.pointOnEdge.y < (od2 + bd2)/2) :
                        collection.add(edge)
            
        filletInput = fillets.createInput()  
        filletInput.addConstantRadiusEdgeSet(collection, Core.ValueInput.createByReal(filletRad), True)
        filletInput.isG2 = False
        filletInput.isRollingBallCorner = False        
        fillets.add(filletInput)
    
    
        # Circular pattern for each teeth
        collection.clear()
        collection.add(toothCutter.bodies.item(0))
    
        # Create the input for circular pattern
        circularFeats = newComp.features.circularPatternFeatures
        circularFeatInput = circularFeats.createInput(collection, newComp.zConstructionAxis)
        circularFeatInput.quantity = Core.ValueInput.createByReal(n)
        circularFeatInput.totalAngle = Core.ValueInput.createByString('360 deg')
        circularFeatInput.isSymmetric = False
        
        # Create the circular pattern
        teeth = circularFeats.add(circularFeatInput)
           
           
        # Cut the base cylinder with the teeth
        collection.clear()        
        collection.add(toothCutter.bodies.item(0))
        
        for th in teeth.bodies:
            collection.add(th)
            
        comb = newComp.features.combineFeatures
        combInput = comb.createInput(od_cyl.bodies.item(0), collection)
        combInput.operation = Fusion.FeatureOperations.CutFeatureOperation
        
        # Combine
        pulley = comb.add(combInput)

        
        # Add edge fillets to pulley
        collection.clear()
     
        # Get the straight edges fartest from center
        for face in pulley.faces:
            for edge in face.edges:
                if (edge.geometry.curveType == Core.Curve3DTypes.Line3DCurveType):
                    if (len2D(edge.pointOnEdge) > ( (od2 + bd2)/2 ) ) :
                        collection.add(edge)
         
    
        filletInput.addConstantRadiusEdgeSet(collection, Core.ValueInput.createByReal(edgeRad), True)
        fillets.add(filletInput)     
        
        endTime = time.time()
        ui.messageBox(str(endTime - startTime), "Elapsed Time");
        
                
    except BaseException as ise:        
        if ui:
            ui.messageBox(ise, "Internal Script Error")
        else:
            print("Internal Script Error" + ise)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc())) 
        else:
            print('Failed:\n{}'.format(traceback.format_exc()))
           
def inputLength(default, design, ui):
    # Prompt the user for a string and validate it's valid.
    isValid = False
    isCancelled = False
    
    while (not isValid) and (not isCancelled):
        # Get a string from the user.
        (input, isCancelled) = ui.inputBox('Pulley Thickness', 'Distance', default)
      
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
    
    
def inputInt(default, design, ui):
    # Prompt the user for a string and validate it's valid.
    isValid = False
    isCancelled = False
    
    while (not isValid) and (not isCancelled):
        # Get a string from the user.
        (input, isCancelled) = ui.inputBox('Number of teeth', 'Integer', default)
      
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
    
    
    
def script2(): # Test 2 with sketch drawn completly and extrude all , then fillet 
    print("in main.script")
    ui = None
    try:
        app = Core.Application.get()
        ui  = app.userInterface
        design = Fusion.Design.cast(app.activeProduct)       
    
        if not design:
            raise BaseException('No active Fusion design')
    
        design.designType = Fusion.DesignTypes.ParametricDesignType
       
        # create a new occurence of a new component at origin
        newComp = design.rootComponent.occurrences.addNewComponent(Core.Matrix3D.create()).component        
    
        # Create a new sketch on the xy plane.	
        sketch = newComp.sketches.add(newComp.xYConstructionPlane, None)        
       
        # Center point
        cp = Core.Point3D.create(0,0,0);
        
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
        (userInput, cancelled) = inputInt("20", design, ui)
        if cancelled:
            return
        n = int(userInput)
        #n = 20
        
        (userInput, cancelled) = inputLength("6 mm", design, ui)
        if cancelled:
            return
        t = userInput
        #t = 0.6
        
        startTime = time.time()
        
        pd2 = (n * pitch / math.pi) / 2
        od2 = pd2 - pitchOffset
        bd2 = od2 - baseOffset
    
        newComp.name = "S2M v1b, n={}".format(n)
        #
        # OD circle and pulley body
        #sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, od2)
        #extrudes = newComp.features.extrudeFeatures
        #extInput = extrudes.createInput(sketch.profiles.item(0), Fusion.FeatureOperations.NewBodyFeatureOperation)
        #distance = Core.ValueInput.createByReal(t)
        #extInput.setDistanceExtent(False, distance)
        #od_cyl = extrudes.add(extInput)  
        
        # BD and PD circles
        sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, bd2)
        p_circ = sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, pd2)
        p_circ.isConstruction = True
        
        # "Involutes"
        #create list of Point3D for center, radius and end point, for both side arc
        #create Point3D for OD that dosent completly close the outer circle
        #create rotation matrix
        #add and rotate the 3 arcs to sketch
        #extrude all
        #add fillets
        invOffset = Core.Point3D.create(-invOffsetX, invOffsetY + od2, 0)
        sketch.sketchCurves.sketchCircles.addByCenterRadius(invOffset, invRad)
        invOffset = Core.Point3D.create( invOffsetX, invOffsetY + od2, 0)
        sketch.sketchCurves.sketchCircles.addByCenterRadius(invOffset, invRad)
      
      
        # Get the profile of the involute circles cut
        prof = None;
        for pro in sketch.profiles:
            p_c_y = pro.areaProperties().centroid.y
            p_c_x = pro.areaProperties().centroid.x
            if (p_c_y > bd2) and (p_c_y < od2) and (math.fabs(p_c_x) < 0.0001):
                prof = pro
              
              
        # Create an extrusion input
        extInput = extrudes.createInput(prof, Fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = Core.ValueInput.createByReal(t)
        extInput.setDistanceExtent(False, distance)
    
        # Create the extrusion.
        toothCutter = extrudes.add(extInput)
            
        collection = Core.ObjectCollection.create()

    
  #      # Circular pattern for each teeth
  #      collection.clear()
  #      collection.add(toothCutter.bodies.item(0))
  #  
  #      # Create the input for circular pattern
  #      circularFeats = newComp.features.circularPatternFeatures
  #      circularFeatInput = circularFeats.createInput(collection, newComp.zConstructionAxis)
  #      circularFeatInput.quantity = Core.ValueInput.createByReal(n)
  #      circularFeatInput.totalAngle = Core.ValueInput.createByString('360 deg')
  #      circularFeatInput.isSymmetric = False
  #      
  #      # Create the circular pattern
  #      teeth = circularFeats.add(circularFeatInput)
           
           
        # Cut the base cylinder with the teeth
#        collection.clear()        
#        collection.add(toothCutter.bodies.item(0))
#        
#        for th in teeth.bodies:
#            collection.add(th)
#            
#        comb = newComp.features.combineFeatures
#        combInput = comb.createInput(od_cyl.bodies.item(0), collection)
#        combInput.operation = Fusion.FeatureOperations.CutFeatureOperation
 #       
#        # Combine
#        pulley = comb.add(combInput)
#        
        

        collection = Core.ObjectCollection.create()
        
        # Add base fillets to cutter        
        fillets = newComp.features.filletFeatures
        
        # Get the straight edges away from mid teeth
        for face in pulley.faces:
            for edge in face.edges:
                if (edge.geometry.curveType == Core.Curve3DTypes.Line3DCurveType):
                    if (len2D(edge.pointOnEdge) < ( (od2 + bd2)/2 ) ) :
                        collection.add(edge)    
            
        filletInput = fillets.createInput()  
        filletInput.addConstantRadiusEdgeSet(collection, Core.ValueInput.createByReal(filletRad), True)
        filletInput.isG2 = False
        filletInput.isRollingBallCorner = False        
        fillets.add(filletInput)
     
        collection.clear()
        # Get the straight edges inward from mid teeth
        for face in pulley.faces:
            for edge in face.edges:
                if (edge.geometry.curveType == Core.Curve3DTypes.Line3DCurveType):
                    if (len2D(edge.pointOnEdge) > ( (od2 + bd2)/2 ) ) :
                        collection.add(edge)         
    
        filletInput.addConstantRadiusEdgeSet(collection, Core.ValueInput.createByReal(edgeRad), True)
        fillets.add(filletInput)     
        
        endTime = time.time()
        ui.messageBox(str(endTime - startTime), "Elapsed Time");
        
                
    except BaseException as ise:        
        if ui:
            ui.messageBox(ise, "Internal Script Error")
        else:
            print("Internal Script Error" + ise)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc())) 
        else:
            print('Failed:\n{}'.format(traceback.format_exc()))