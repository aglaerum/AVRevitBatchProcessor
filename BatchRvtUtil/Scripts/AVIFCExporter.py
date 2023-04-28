# -*- coding: utf-8 -*-

import os
import revit_script_util
from revit_script_util import Output
Output("------------------ RUNNING ACC EXPORT SCRIPT ------------------")
from Autodesk.Revit import DB
import AVIFCExporterLib
import AVFunksjoner as avf

import csv
import traceback
import codecs

#############################################
"""
Denne filen er for export av ACC prosjekter
"""
#############################################

SESSIONID = revit_script_util.GetSessionId()
UIAPP = revit_script_util.GetUIApplication()  # type: UI.UIApplication
DOC = revit_script_util.GetScriptDocument()  # type: DB.Document
REVITFILEPATH = revit_script_util.GetRevitFilePath()

"""" CSV file with list of rvt files to process """
my_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterACC"  # Midlertidige filer for programmet
rvt_csv_file_list_path = os.path.join(my_folder, "rvt_csv_file_list.csv")

""" Hent riktig rvt fil fra csv filen """
def open_csv_file(csv_file_path):
    # type: (str) -> avf.PathFromCSVACC
    with codecs.open(csv_file_path, "r", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        # "LocalPath", "IFCPath", "IFCpSets", "IFCMapping", "IFCSettings"
        for row in csv_reader:
            if os.path.normpath(row[0]) == os.path.normpath(REVITFILEPATH):
                return avf.PathFromCSVACC(*row)

""" Match denne .rvt fil med en rad i csv fil """
rvt_path_class = open_csv_file(rvt_csv_file_list_path)
if rvt_path_class is None:
    raise Exception("Could not find rvt file: {} in csv file: {}".format(REVITFILEPATH, rvt_csv_file_list_path))

Output("Start IFC Export...")
for x, y in rvt_path_class.__dict__.items():
    Output("{}: {}".format(x, y))

def exporter(doc, outfolder, psetfile, mappingfile, ifc_settings, output):
    # type: (DB.Document, str, str, str) -> None
    ifcviews = AVIFCExporterLib.samle_3dViews(doc, output)
    Output("Samlet {} 3D Views...".format(str(len(ifcviews))))
    for view in ifcviews:
        AVIFCExporterLib.export_view(view, outfolder, psetfile, mappingfile, ifc_settings, output)


TR = None
try:
    Output("Start IFC Export...")
    TR = DB.Transaction(DOC, "IFCExport")
    TR.Start()
    exporter(DOC,
            rvt_path_class.ifc_outfolder,
            rvt_path_class.psets_file,
            rvt_path_class.mappings_file,
            rvt_path_class.ifc_export_settings,
            Output)

except Exception as fmeld:
    Output(traceback.format_exc())
finally:
    if TR is not None:
        TR.RollBack()
