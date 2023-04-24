# -*- coding: utf-8 -*-

import AVFunksjoner as avf
import os

avf.clr_batchrvtutil()
avf.clr_highest_revitapi()

from Autodesk.Revit import DB
import revit_script_util
from revit_script_util import Output
import AVIFCExporterLib

import csv
import traceback

SESSIONID = None
UIAPP = None
DOC = None
REVITFILEPATH = None

if not avf.runnin_in_pycharm():
    SESSIONID = revit_script_util.GetSessionId()
    UIAPP = revit_script_util.GetUIApplication()  # type: UI.UIApplication
    DOC = revit_script_util.GetScriptDocument()  # type: DB.Document
    REVITFILEPATH = revit_script_util.GetRevitFilePath()

csvpath = avf.generated_paths_and_settings_path


def read_csv_file(csv_file_path, search_path):
    # define the row names
    row_names = avf.CSWROWS

    rvt_file_path, project_name, pset_file_path, mapping_file_path, ifc_folder_path = "", "", "", "", ""

    with open(csv_file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pathincsv = row[row_names[0]]

            if os.path.is
                # todo: Sjekk om filbanene peker på samme fil uansett hvilken vei man kommer fra
            if row[row_names[0]] == search_path:
                # append the values to the corresponding variables
                rvt_file_path = row[row_names[0]]
                project_name = row[row_names[1]]
                pset_file_path = row[row_names[2]]
                mapping_file_path = row[row_names[3]]
                ifc_folder_path = row[row_names[4]]

    return rvt_file_path, project_name, pset_file_path, mapping_file_path, ifc_folder_path


def exporter(doc, outfolder, psetfile):
    # type: (DB.Document, str) -> None
    ifcviews = AVIFCExporterLib.samle_3dViews(doc)
    Output("Samlet {} 3D Views...".format(str(len(ifcviews))))
    for view in ifcviews:
        AVIFCExporterLib.export_view(view, outfolder, psetfile)


values = read_csv_file(csvpath, REVITFILEPATH)
print values

# TR = None
# try:
#     Output("Start IFC Export...")
#     TR = DB.Transaction(DOC, "IFCExport")
#     TR.Start()
#     exporter(DOC, IFCOUT, PSETS_FILE)
# except Exception as fmeld:
#     Output(traceback.format_exc())
# finally:
#     if TR is not None:
#         TR.RollBack()
