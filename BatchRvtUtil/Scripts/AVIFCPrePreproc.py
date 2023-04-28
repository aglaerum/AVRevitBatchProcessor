# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
# import AVClr
# AVClr.clr_batchrvtutil()
import AVFunksjoner as avf
import AVServerFuncs as avs
import codecs
import csv
import os
from script_util import Output

#############################################
"""
Denne filen er for export av ACC prosjekter
"""
#############################################

""" Input\Output """
input_rvt_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\IFCWorkfolder\RVTLokalfiler2"  # .rvt filer
output_ifc_folder = r"\\trondheim\AVTools\AutoIFC\IFCOutACC"  # .ifc filer

""" IFC innstillinger """
mappings_folder = r"\\trondheim\AVTools\AutoIFC\IFCMapping" # .txt filer
config_pset_folder = r"\\trondheim\AVTools\AutoIFC\IFCPsets" # .txt filer
config_ifcsettings_folder = r"\\trondheim\AVTools\AutoIFC\IFCSettings" # Json filer

""" Hovedmappen for programmet """
main_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterACC"
rvt_csv_file_list_path = os.path.join(main_folder, "rvt_csv_file_list.csv")

""" Deaktiver alle addins som ikke er batchprocessor eller AVTools """
avf.deactivate_all_addins()

""" Henter lokale filer """
def create_local_paths(folder_path, file_ending):
    # For ACC
    local_paths = []
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(file_ending):
                file_path = os.path.join(root, filename)
                local_paths.append(avf.LocalFileACC(file_path))
    return local_paths

def create_csv_file(csv_path, local_paths):
    # type: (str, list[avf.LocalFileACC]) -> None
    with codecs.open(csv_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        # writer.writerow(["LocalPath", "ServerPath", "Date", "IFCPath", "IFCpSets", "IFCMapping", "IFCSettings", "Version"])
        for pa in local_paths:
            writer.writerow([pa.local_path,
                             pa.get_ifc_folder(output_ifc_folder),
                             pa.get_ifc_psets_file(config_pset_folder),
                             pa.get_ifc_mappings_file(mappings_folder),
                             pa.get_ifc_settings_file(config_ifcsettings_folder)])

paths = create_local_paths(input_rvt_folder, ".rvt")
create_csv_file(rvt_csv_file_list_path, paths)
Output("Csv fil for ACC laget: {}".format(rvt_csv_file_list_path))