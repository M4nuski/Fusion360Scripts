#Author-M4nusky
#Description-Script Test 2 in python (?)

import adsk.core, adsk.fusion, adsk.cam, traceback

_handlers = []

def run(context):
    ui = None
    try:
        global _handlers
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Hello script Test 2\n Python because ... anime')
        
        #product = app.activeProduct;
        design = adsk.fusion.Design.cast(app.activeProduct);

        if not design:
            ui.messageBox('No active Fusion design', 'No Design');
        else:
            ui.messageBox(design.rootComponent.partNumber, 'Desing part number?')   
        
        cmdDef = ui.commandDefinitions.itemById('M4nuskyTestScript2')
        if not cmdDef:
            # Create a command definition.
            cmdDef = ui.commandDefinitions.addButtonDefinition('M4nuskyTestScript2', 'No Idea', 'Creates whatever, it\'s a test script', '') 
        
        # Connect to the command created event.
        onCommandCreated = TS2CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        
        # Execute the command.
        cmdDef.execute()
        

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class TS2CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
        adsk.core.Application.get().userInterface.messageBox('Command Created Handler')
        
    def notify(self):
        adsk.core.Application.get().userInterface.messageBox("Command Created Handler Notify")
        
    # assign subsequent handlers 
      
def stop(context):
    adsk.core.Application.get().userInterface.messageBox('Script Stop Command Handler')
    
