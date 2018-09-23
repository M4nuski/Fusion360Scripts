#Author-M4nusky
#Description-input test

import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        isValid = False
        defaultValue = '1 in' #  // The initial default value.
        realValue = ""
        while not isValid:
           #    // Get a string from the user.

            realValue = ui.inputBox('Enter a distance', 'Distance', defaultValue)
           #     // Exit the program if the dialog was cancelled.
            if realValue[1]: #tuple (resultstr, cancelledbool)
                adsk.terminate()
                return

           # // Check that a valid length was entered.
            design = adsk.fusion.Design.cast(app.activeProduct)
            unitsMgr = design.unitsManager
            try:
                realValue = unitsMgr.evaluateExpression(realValue[0], unitsMgr.defaultLengthUnits)
                isValid = True

            except Exception as e:
        #// Invalid expression so display an error and set the flag to allow them
       # // to enter a value again.
                ui.messageBox('"' + realValue[0] + '" is not a valid length expression.', 'Invalid entry',  adsk.core.MessageBoxButtonTypes.OKButtonType, adsk.core.MessageBoxIconTypes.CriticalIconType);
                isValid = False
    
    #// Use the value for something.
        displayLength = unitsMgr.formatInternalValue(realValue, unitsMgr.defaultLengthUnits, True);  
        ui.messageBox('result: ' + realValue.__repr__() + " cm (default system units) " + displayLength + " default units")

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
            
            


