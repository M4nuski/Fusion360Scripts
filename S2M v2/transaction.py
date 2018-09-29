#Author-M4nusky
#Description-Fusion360 Script Transaction Wrapper

import adsk as Adsk
import adsk.core as Core

import traceback

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []

_script_to_run = None
_script_name = ""

def setup(target_script, script_name):
    
    global _script_to_run
    _script_to_run = target_script
    global _script_name
    _script_name = script_name
    
    ui = None
    try:
        print("in transaction.setup")
        app = Core.Application.get()
        ui  = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        if cmdDefs.itemById(script_name):
            cmdDefs.itemById(script_name).deleteMe()
            
        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition(script_name, script_name, "")
        
        # Connect to the command created event.
        sampleCommandCreated = SampleCommandCreatedEventHandler()
        buttonSample.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)
        
        # Execute the command.
        buttonSample.execute()
        
        # Keep the script running.
        #Adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), "Script Exception (S2M)") 


    
    
# Event handler for the commandCreated event.
class SampleCommandCreatedEventHandler(Core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        print("in transaction.SampleCommandCreatedEventHandler")
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
        
        global _script_to_run
        print("in transaction.SampleCommandExecuteHandler")

        # Code to react to the event.  
        _script_to_run()
        
        # Force the termination of the command.
        Adsk.terminate()  


def cleanup(context):    
    print("in transaction.cleanup")
    try:
        app = Core.Application.get()
        ui  = app.userInterface
        
        global _script_name
        
        # Delete the command definition.
        cmdDef = ui.commandDefinitions.itemById(_script_name)
        if cmdDef:
            cmdDef.deleteMe()            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()), "Script Exception (S2M)") 
    