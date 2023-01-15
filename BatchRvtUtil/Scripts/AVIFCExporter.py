# -*- coding: utf-8 -*-

import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
clr.AddReference("RevitAPIIFC")

from Autodesk.Revit import DB, UI
import sys
import os
import AVIFCExporterLib
import revit_script_util
from revit_script_util import Output
from revit_file_util import RelinquishAll, SynchronizeWithCentral
import traceback


opdir = os.path.dirname
# HOMEPATH = opdir(opdir(opdir(sys.argv[0])))  # Hvorfor fungerer ikke dette??!
# HOME_DIR = opdir(opdir(opdir(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\GitHub\AVTools.Revit\site-packages\AutoIFCLibrary\IFCExportRBP.py")))
HOME_DIR = opdir(opdir(opdir(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ACCAutoExporter\AutoIFCExporter\AVExporter.py")))
PROGDATA_DIR = os.path.join(HOME_DIR, "ACCAutoExporter\AutoIFCExporter\progdata")
IFCOUT_DIR = os.path.join(HOME_DIR, "IFCOut")
PSETS_FILE = os.path.join(PROGDATA_DIR, "AVPropertySets.txt")

####### Setup Logging #########

def log(logitem=None):
    if logitem is None:
        logitem = ""
    Output("AVLog: {}".format(str(logitem)))

# for VARITEM in list(vars()):
#     log(VARITEM)


####### Globale #########

SESSIONID = revit_script_util.GetSessionId()
UIAPP = revit_script_util.GetUIApplication()  # type: UI.UIApplication
# UIDOC = UIAPP.ActiveUIDocument  # type: UI.UIDocument

DOC = revit_script_util.GetScriptDocument()  # type: DB.Document
REVITFILEPATH = revit_script_util.GetRevitFilePath()

IFCOUT = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ACCAutoExporter\IFCOut"

####### Defs #########

def exporter(doc, outfolder, psetfile):
    # type: (DB.Document, str) -> None
    ifcviews = AVIFCExporterLib.samle_3dViews(doc)
    log("Samlet {} 3D Views...".format(str(len(ifcviews))))
    for view in ifcviews:
        # uidoc.ActiveView = view
        AVIFCExporterLib.export_view(view, outfolder, psetfile)


######################### Sjekk Grunnleggende ####################

log("IFCOut mappe:")
log(IFCOUT)
log("Sys Paths:")
for alog in sys.path:
    log(alog)

log("Revit filbane:")
log(REVITFILEPATH)
log("Starter IFC Export!")

TR = None
try:
    # open_worksets(DOC)
    TR = DB.Transaction(DOC, "IFCExport")
    TR.Start()
    exporter(DOC, IFCOUT, PSETS_FILE)
except Exception as fmeld:
    log(traceback.format_exc())
finally:
    if TR is not None:
        TR.RollBack()

SynchronizeWithCentral(DOC, "AutoIFCExport")
RelinquishAll(DOC)

