# -*- coding: utf-8 -*-

import os
import csv
import datetime
import struct
import sys
import traceback
import codecs

import clr
import System

# def Output(inp=None):
#     if inp is not None:
#         print(inp)
#     else:
#         print("")

op = os.path.join

# main_volo_volder = r"C:\AVIFCExporter"
main_volo_volder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656"
input_rvt_folder = op(main_volo_volder, "Input_models")
output_ifc_folder = op(main_volo_volder, "Output AG")
mappings_folder = op(main_volo_volder, "FamilymappingFile")
config_pset_folder = op(main_volo_volder, "Input_configs")

main_config_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656"

""" Fra BatchRvtUtil """
clr.AddReferenceToFileAndPath(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\GitHub\AVRevitBatchProcessor\BatchRvtUtil\bin\x64\Release\BatchRvtUtil.dll")
import BatchRvtUtil
""" Fra BatchRvtUtil """""


from script_util import Output

print BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()


def find_newest_revit():
    current_year = datetime.datetime.now().year
    search_years = list(range(current_year, current_year + 3))
    search_years.reverse()

    for year in search_years:
        revit_path = "C:\\Program Files\\Autodesk\\Revit {0}".format(year)
        if os.path.exists(revit_path):
            Output("Found Revit {0} at {1}".format(year, revit_path))
            return revit_path
            break
    else:
        print("No installed version of Revit found.")

clr.AddReferenceToFileAndPath(op(find_newest_revit(), "RevitAPI.dll"))
from Autodesk.Revit import DB

def create_file_paths_file(folder_path, output_file, file_ending):
    with open(output_file, 'wb') as fi:
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename.endswith(file_ending):
                    file_path = os.path.join(root, filename) + '\n'
                    fi.write(file_path.encode('utf-8'))

def create_csv_file(rvt_file_list, pset_file_list, mapping_file_list, output_file):
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Version", "Project Name", "RVT File Path", "PSet File Path", "Mapping File Path"])
        with \
                codecs.open(rvt_file_list, mode='r', encoding='utf-8')as rvt_file_list,\
                codecs.open(pset_file_list, mode='r', encoding='utf-8') as pset_file_list,\
                codecs.open(mapping_file_list, mode='r', encoding='utf-8') as mapping_file_list:

            rvt_files = rvt_file_list.readlines()
            pset_files = pset_file_list.readlines()
            mapping_files = mapping_file_list.readlines()

            for rvt_file in rvt_files:
                Output("Henter fil: {0}".format(rvt_file))
                rvt_file = rvt_file.strip()
                project_name = os.path.basename(os.path.dirname(rvt_file))
                rvt_path = rvt_file
                pset_path = ""
                mapping_path = ""
                version = get_revit_version(rvt_file)

                for pset_file in pset_files:
                    if os.path.basename(pset_file.strip()).lower() in os.path.basename(rvt_file).lower():
                        pset_path = pset_file.strip()
                        break

                for mapping_file in mapping_files:
                    if os.path.basename(mapping_file.strip()).lower() in os.path.basename(rvt_file).lower():
                        mapping_path = mapping_file.strip()
                        break

                writer.writerow([version, project_name, rvt_path, pset_path, mapping_path])

def get_revit_version(revit_path):
    revit_version = DB.BasicFileInfo.Extract(revit_path)
    return str(revit_version.Format)

try:
    """ Create a file with all the paths to the rvt files in the folder and subfolders. """
    Output("Lager filbanefil...")
    create_file_paths_file(input_rvt_folder, op(main_config_folder, "rvt_file_list.txt"), ".rvt")

    """ Create a file with all the paths to the pset files in the folder and subfolders. """
    Output("Lager pset og mappingfil...")
    create_file_paths_file(config_pset_folder, op(main_config_folder, "pSets_Paths.txt"), "pset.txt")

    """ Create a file with all the paths to the family mapping files in the folder and subfolders. """
    Output("Lager mappingfil...")
    create_file_paths_file(mappings_folder, op(main_config_folder, "mapping_paths.txt"), ".txt")

    """ Create a CSV file that links the rvt files to the pset and mapping files. """
    Output("Lager CSV-fil...")
    create_csv_file(op(main_config_folder, "rvt_file_list.txt"), op(main_config_folder, "pSets_Paths.txt"), op(main_config_folder, "mapping_paths.txt"), op(main_config_folder, "generated_paths_and_settings.csv"))

    # print get_revit_version(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\VERSIONTEST.rvt")
except Exception as e:
    Output("Error: {0}".format(e))
    Output(traceback.format_exc())
    raise e