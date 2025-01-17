# -*- coding: utf-8 -*-

import revit_script_util
from revit_script_util import Output

Output("------------------ RUNNING ACC EXPORT SCRIPT ------------------")
from Autodesk.Revit import DB, UI
import AVIFCExporterLib

import traceback

#############################################
"""
Denne filen er for export av ACC prosjekter
"""
#############################################

for x in revit_script_util.GetAssociatedData():
    Output(x)

SESSIONID = revit_script_util.GetSessionId()
UIAPP = revit_script_util.GetUIApplication()  # type: UI.UIApplication
DOC = revit_script_util.GetScriptDocument()  # type: DB.Document
REVITFILEPATH = revit_script_util.GetRevitFilePath()

ifc_outfolder = revit_script_util.GetAssociatedData()[0]
ifc_psets = revit_script_util.GetAssociatedData()[1]
ifc_mapping = revit_script_util.GetAssociatedData()[2]
ifc_settings = revit_script_util.GetAssociatedData()[3]


def exporter(doc, outfolder, psetfile, mappingfile, ifc_settings_file, output):
    # type: (DB.Document, str, str, str) -> None
    ifcviews = AVIFCExporterLib.samle_3dViews(doc, output)
    Output("Samlet {} 3D Views...".format(str(len(ifcviews))))
    for view in ifcviews:
        AVIFCExporterLib.export_view(view, outfolder, psetfile, mappingfile, ifc_settings_file, output)


TR = None
try:
    Output("Start IFC Export...")
    TR = DB.Transaction(DOC, "IFCExport")
    TR.Start()
    exporter(DOC, ifc_outfolder, ifc_psets, ifc_mapping, ifc_settings, Output)
except Exception as fmeld:
    Output(traceback.format_exc())
finally:
    if TR is not None:
        TR.RollBack()
