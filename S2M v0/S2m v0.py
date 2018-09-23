#Author-M4nusky
#Description-simplier script to add parametric shaft

import adsk.core as Core
import adsk.fusion as Fusion
import traceback
import math

class internalScriptError(BaseException):
    pass

def run(context):
    ui = None
    try:
        app = Core.Application.get()
        ui  = app.userInterface
        design = Fusion.Design.cast(app.activeProduct)

        if not design:
            raise internalScriptError('No active Fusion design')
        
        rootComp = design.rootComponent;

        # Create a new sketch on the xy plane.	
        sketches = rootComp.sketches;
        
        # create a new occurence of a new component at origin
        newComp = rootComp.occurrences.addNewComponent(Core.Matrix3D.create()).component        
        #newComp.name = "S2M v0"
        
       # xyPlane = newComp.xYConstructionPlane
        sketches = newComp.sketches
        sketch = sketches.add(newComp.xYConstructionPlane, None)        
       
        cp = Core.Point3D.create(0,0,0);
        #dPI = math.pi*2   
        
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
        n = 20   
        t = 0.6
        
        pd2 = (n * pitch / math.pi) / 2
        od2 = pd2 - pitchOffset
        bd2 = od2 - baseOffset

        #halfToothAngle = math.pi / n
        newComp.name = "S2M v0 {}n".format(n)
        
        #OD circle and pulley body
        sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, od2)
        extrudes = newComp.features.extrudeFeatures
        extInput = extrudes.createInput(sketch.profiles.item(0), Fusion.FeatureOperations.NewBodyFeatureOperation)
        distance = Core.ValueInput.createByReal(t)
        extInput.setDistanceExtent(False, distance)
        od_cyl = extrudes.add(extInput)  
        
        #BD and PD circles
        sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, bd2)
        p_circ = sketch.sketchCurves.sketchCircles.addByCenterRadius(cp, pd2)
        p_circ.isConstruction = True
        
        #Involutes
        invOffset = Core.Point3D.create(-invOffsetX, invOffsetY + od2, 0)
        sketch.sketchCurves.sketchCircles.addByCenterRadius(invOffset, invRad)
        invOffset = Core.Point3D.create( invOffsetX, invOffsetY + od2, 0)
        sketch.sketchCurves.sketchCircles.addByCenterRadius(invOffset, invRad)
        
        
        # Sketch Tooth Lines    
        #line1 = sketch.sketchCurves.sketchLines.addByTwoPoints(cp, Core.Point3D.create(0, od2, 0))
        #line2 = sketch.sketchCurves.sketchLines.addByTwoPoints(cp, Core.Point3D.create(0, od2, 0))

        #rot = Core.Matrix3D.create()
        #rot.setToRotation(halfToothAngle, Core.Vector3D.create(0,0,1), cp)
    
        #entities = Core.ObjectCollection.create()
        
        #entities.add(line1)
        #sketch.move(entities, rot)        
        ##entities.clear()
        
        #entities.add(line2)   
        #rot.setToRotation(-halfToothAngle, Core.Vector3D.create(0,0,1), cp)
        #sketch.move(entities, rot)        
        #entities.clear()

        # Get the profile of the inv circles cut
        prof = None;
        for pro in sketch.profiles:
            p_c_y = pro.areaProperties().centroid.y
            p_c_x = pro.areaProperties().centroid.x
            if (p_c_y > bd2) and (p_c_y < od2) and (math.fabs(p_c_x) < 0.0001):
                prof = pro
              
        # Create an extrusion input
        extInput = extrudes.createInput(prof, Fusion.FeatureOperations.NewBodyFeatureOperation)
        
        # Define that the extent is a distance extent of 5 cm.
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
            
        input1 = fillets.createInput()  
        input1.addConstantRadiusEdgeSet(collection, Core.ValueInput.createByReal(filletRad), True)
        input1.isG2 = False
        input1.isRollingBallCorner = False        
        fillets.add(input1)

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
        
        for th in teeth.bodies:
            collection.add(th)
            
        comb = newComp.features.combineFeatures
        combInput = comb.createInput(od_cyl.bodies.item(0), collection)
        combInput.operation = Fusion.FeatureOperations.CutFeatureOperation
        
        res = comb.add(combInput)
        
        toothCutter.dissolve()
        
    except internalScriptError as ise:        
        if ui:
            ui.messageBox(ise, "Internal Script Error")
        else:
            print("Internal Script Error" + ise)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc())) 
        else:
            print('Failed:\n{}'.format(traceback.format_exc()))
