# -*- coding: utf-8 -*-

import codecs
import csv
import os
import traceback

import AVFunksjoner as avf

op = os.path.join

from script_util import Output


def get_outputfolder(full_input_path):
    # get the relative input folder path
    relative_input_path = os.path.relpath(full_input_path, avf.input_rvt_folder)
    # create the output folder path by joining the output folder with the relative input folder path
    output_folder_path = os.path.join(avf.output_ifc_folder, relative_input_path)
    # create the output folder if it doesn't exist
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    return output_folder_path


def create_file_paths_file(folder_path, output_file, file_ending):
    with open(output_file, 'wb') as fi:
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename.endswith(file_ending):
                    file_path = os.path.join(root, filename) + '\n'
                    fi.write(file_path.encode('utf-8'))

def get_lower_fixed_filename(file_path):
    filename = os.path.splitext(os.path.basename(file_path.strip()))[0]
    newname = filename.lower().strip()
    return newname

def create_csv_file(rvt_file_list, pset_file_list, mapping_file_list, output_file):
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(avf.CSWROWS)
        with \
                codecs.open(rvt_file_list, mode='r', encoding='utf-8') as rvt_file_list, codecs.open(pset_file_list, mode='r', encoding='utf-8') as pset_file_list, codecs.open(mapping_file_list, mode='r', encoding='utf-8') as mapping_file_list:

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
                ifc_path = get_outputfolder(rvt_file)

                for pset_file in pset_files:
                    if get_lower_fixed_filename(rvt_file) in get_lower_fixed_filename(pset_file):
                        pset_path = pset_file.strip()
                        break

                for mapping_file in mapping_files:
                    if get_lower_fixed_filename(rvt_file) in get_lower_fixed_filename(mapping_file):
                        mapping_path = mapping_file.strip()
                        break
                rows = [rvt_path, project_name, pset_path, mapping_path, ifc_path]
                # Output(str(rows))
                writer.writerow(rows)


""" Deaktiver alle addins som ikke er batchprocessor eller AVTools """
avf.deactivate_all_addins()

""" Create a file with all the paths to the rvt files in the folder and subfolders. """
Output("Lager filbanefil...")
create_file_paths_file(avf.input_rvt_folder, op(avf.main_config_folder, "rvt_file_list.txt"), ".rvt")

""" Create a file with all the paths to the pset files in the folder and subfolders. """
Output("Lager pset og mappingfil...")
create_file_paths_file(avf.config_pset_folder, op(avf.main_config_folder, "pSets_Paths.txt"), ".txt")

""" Create a file with all the paths to the family mapping files in the folder and subfolders. """
Output("Lager mappingfil...")
create_file_paths_file(avf.mappings_folder, op(avf.main_config_folder, "mapping_paths.txt"), ".txt")

""" Create a CSV file that links the rvt files to the pset and mapping files. """
Output("Lager CSV-fil...")
# create_csv_file(op(avf.main_config_folder, "rvt_file_list.txt"), op(avf.main_config_folder, "pSets_Paths.txt"), op(avf.main_config_folder, "mapping_paths.txt"), op(avf.main_config_folder, "generated_paths_and_settings.csv"))
create_csv_file(avf.rvt_file_list_path, avf.psets_paths_path, avf.mapping_paths_path, avf.generated_paths_and_settings_path)


# try:
#     """ Create a file with all the paths to the rvt files in the folder and subfolders. """
#     Output("Lager filbanefil...")
#     create_file_paths_file(input_rvt_folder, op(main_config_folder, "rvt_file_list.txt"), ".rvt")
#
#     """ Create a file with all the paths to the pset files in the folder and subfolders. """
#     Output("Lager pset og mappingfil...")
#     create_file_paths_file(config_pset_folder, op(main_config_folder, "pSets_Paths.txt"), ".txt")
#
#     """ Create a file with all the paths to the family mapping files in the folder and subfolders. """
#     Output("Lager mappingfil...")
#     create_file_paths_file(mappings_folder, op(main_config_folder, "mapping_paths.txt"), ".txt")
#
#     """ Create a CSV file that links the rvt files to the pset and mapping files. """
#     Output("Lager CSV-fil...")
#     create_csv_file(op(main_config_folder, "rvt_file_list.txt"), op(main_config_folder, "pSets_Paths.txt"), op(main_config_folder, "mapping_paths.txt"), op(main_config_folder, "generated_paths_and_settings.csv"))
#
#     # print get_revit_version(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\VERSIONTEST.rvt")
# except Exception as e:
#     Output("Error: {0}".format(e))
#     Output(traceback.format_exc())
#     raise e
