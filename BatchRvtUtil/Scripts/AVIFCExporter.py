# -*- coding: utf-8 -*-

import AVFunksjoner as avf
import os

# avf.clr_batchrvtutil()
# avf.clr_highest_revitapi()

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

csvpath = avf.generated_paths_and_settings_path


def read_csv_file(csv_file_path, search_path):
    # define the row names
    row_names = avf.CSWROWS

    rvt_file_path, project_name, pset_file_path, mapping_file_path, ifc_folder_path = "", "", "", "", ""

    with open(csv_file_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pathincsv = row[row_names[0]]
            if os.path.abspath(pathincsv) == os.path.abspath(search_path):
                # append the values to the corresponding variables
                rvt_file_path = row[row_names[0]]
                project_name = row[row_names[1]]
                pset_file_path = row[row_names[2]]
                mapping_file_path = row[row_names[3]]
                ifc_folder_path = row[row_names[4]]

    return rvt_file_path, project_name, pset_file_path, mapping_file_path, ifc_folder_path


def exporter(doc, outfolder, psetfile, mappingfile):
    # type: (DB.Document, str, str, str) -> None
    ifcviews = AVIFCExporterLib.samle_3dViews(doc)
    Output("Samlet {} 3D Views...".format(str(len(ifcviews))))
    for view in ifcviews:
        AVIFCExporterLib.export_view(view, outfolder, psetfile, mappingfile)


RVT_FILEPATH, PROJECT_NAME, PSETS_FILE, MAPPINGFILE, OUTFOLDER = read_csv_file(csvpath, REVITFILEPATH)

printthis = str([RVT_FILEPATH, PROJECT_NAME, PSETS_FILE, MAPPINGFILE, OUTFOLDER])
Output()
Output(RVT_FILEPATH)
Output(REVITFILEPATH)

TR = None
try:
    Output("Start IFC Export...")
    TR = DB.Transaction(DOC, "IFCExport")
    TR.Start()
    exporter(DOC, OUTFOLDER, PSETS_FILE, MAPPINGFILE)
except Exception as fmeld:
    Output(traceback.format_exc())
finally:
    if TR is not None:
        TR.RollBack()
