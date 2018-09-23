#Author-M4nusky
#Description-S2M pulley generator script

import adsk as Adsk
import adsk.core as Core
import adsk.fusion as Fusion
import traceback
import math

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []

class internalScriptError(BaseException):
    pass

def run(context):
    ui = None
    try:
        app = Core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('S2MScriptId', 
                                                   'Python S2M generator', 
                                                   'Generate S2M pulley')
        
        # Connect to the command created event.
        sampleCommandCreated = SampleCommandCreatedEventHandler()
        buttonSample.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)
        
        # Execute the command.
        buttonSample.execute()
        
        # Keep the script running.
        Adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def len2D(pt):
    return math.sqrt( (pt.x*pt.x) + (pt.y*pt.y) )
    
    
# Event handler for the commandCreated event.
class SampleCommandCreatedEventHandler(Core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        eventArgs = Core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command

        # Connect to the execute event.
        onExecute = SampleCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)
    
# Event handler for the execute event.
class SampleCommandExecuteHandler(Core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        #eventArgs = Core.CommandEventArgs.cast(args)

        # Code to react to the event.
        #app = adsk.core.Application.get()
        #des = adsk.fusion.Design.cast(app.activeProduct)        
        
        
        ui = None
        try:
            app = Core.Application.get()
            ui  = app.userInterface
            design = Fusion.Design.cast(app.activeProduct)       
        
            if not design:
                raise internalScriptError('No active Fusion design')
        
            design.designType = Fusion.DesignTypes.ParametricDesignType
           
            # create a new occurence of a new component at origin
            newComp = design.rootComponent.occurrences.addNewComponent(Core.Matrix3D.create()).component        
        
            #sketches = newComp.sketches
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
            n = 20   
            t = 0.6
            
            pd2 = (n * pitch / math.pi) / 2
            od2 = pd2 - pitchOffset
            bd2 = od2 - baseOffset
        
            newComp.name = "S2M v0 {}n".format(n)
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
        


        # Force the termination of the command.
        Adsk.terminate()  


def stop(context):    
    try:
        app = Core.Application.get()
        ui  = app.userInterface
        
        # Delete the command definition.
        cmdDef = ui.commandDefinitions.itemById('S2MScriptId')
        if cmdDef:
            cmdDef.deleteMe()            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    