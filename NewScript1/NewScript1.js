//Author-moi-même
//Description-Description inline of test script 1

function run(context) {

    "use strict";
    if (adsk.debug === true) {
        /*jslint debug: true*/
        debugger;
        /*jslint debug: false*/
    }
 
    var ui;
    try {
        var app = adsk.core.Application.get();
        ui = app.userInterface;
 
        ui.messageBox('Hello script');        
    } 
    catch (e) {
        if (ui) {
            ui.messageBox('Failed : ' + (e.description ? e.description : e));
        }
    }

    adsk.terminate(); 
}