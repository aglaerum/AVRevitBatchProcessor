# -*- coding: utf-8 -*-

import AVPathsAndSettings as avp
import AVFunksjoner as avf

from Autodesk.Revit import DB
import revit_script_util
from revit_script_util import Output
import AVIFCExporterLib

import csv
import traceback


SESSIONID = revit_script_util.GetSessionId()
UIAPP = revit_script_util.GetUIApplication()  # type: UI.UIApplication
DOC = revit_script_util.GetScriptDocument()  # type: DB.Document
REVITFILEPATH = revit_script_util.GetRevitFilePath()

Output(REVITFILEPATH)
rvt_path_class = avf.LocalPath(REVITFILEPATH)

Output("Start IFC Export...")
Output(rvt_path_class.path)
Output(rvt_path_class.get_ifc_psets_file(avp.config_pset_folder))
Output(rvt_path_class.get_ifc_mappings_file(avp.mappings_folder))
Output(rvt_path_class.get_ifc_settings_file(avp.config_ifcsettings_folder))

def exporter(doc, outfolder, psetfile, mappingfile):
    # type: (DB.Document, str, str, str) -> None
    ifcviews = AVIFCExporterLib.samle_3dViews(doc)
    Output("Samlet {} 3D Views...".format(str(len(ifcviews))))
    for view in ifcviews:
        AVIFCExporterLib.export_view(view, outfolder, psetfile, mappingfile)



# TR = None
# try:
#     Output("Start IFC Export...")
#     TR = DB.Transaction(DOC, "IFCExport")
#     TR.Start()
#     exporter(DOC, OUTFOLDER, PSETS_FILE, MAPPINGFILE)
# except Exception as fmeld:
#     Output(traceback.format_exc())
# finally:
#     if TR is not None:
#         TR.RollBack()
