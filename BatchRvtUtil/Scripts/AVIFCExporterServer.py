# -*- coding: utf-8 -*-

import traceback

import AVIFCExporterLib
import revit_script_util
from Autodesk.Revit import DB
from revit_script_util import Output

#############################################
"""
Denne filen er for export av Rserver prosjekter
"""
#############################################

SESSIONID = revit_script_util.GetSessionId()
UIAPP = revit_script_util.GetUIApplication()  # type: UI.UIApplication
DOC = revit_script_util.GetScriptDocument()  # type: DB.Document
REVITFILEPATH = revit_script_util.GetRevitFilePath()

rvt_server_path = revit_script_util.GetAssociatedData()[0]
ifc_outfolder = revit_script_util.GetAssociatedData()[1]
ifc_psets = revit_script_util.GetAssociatedData()[2]
ifc_mapping = revit_script_util.GetAssociatedData()[3]
ifc_settings = revit_script_util.GetAssociatedData()[4]


def exporter(doc, outfolder, psetfile, mappingfile, ifc_settings, output):
    # type: (DB.Document, str, str, str) -> None
    ifcviews = AVIFCExporterLib.samle_3dViews(doc, output)
    Output("Samlet {} 3D Views...".format(str(len(ifcviews))))
    for view in ifcviews:
        AVIFCExporterLib.export_view(view, outfolder, psetfile, mappingfile, ifc_settings, output)


TR = None
try:
    Output("Start IFC Export fra Rserver...")
    TR = DB.Transaction(DOC, "IFCExport")
    TR.Start()
    exporter(DOC, ifc_outfolder, ifc_psets, ifc_mapping, ifc_settings, Output)

except Exception as fmeld:
    Output(traceback.format_exc())
finally:
    if TR is not None:
        TR.RollBack()
