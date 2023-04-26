# -*- coding: utf-16 -*-

import codecs
import csv
import os

import AVFunksjoner as avf
import AVPathsAndSettings as avp
import batch_rvt_config

avf.clr_highest_revitapi()
op = os.path.join

from script_util import Output


def get_outputfolder(full_input_path):
    full_input_path = os.path.dirname(full_input_path)
    # get the relative input folder path
    relative_input_path = os.path.relpath(full_input_path, avp.input_rvt_folder)
    # create the output folder path by joining the output folder with the relative input folder path
    output_folder_path = os.path.join(avp.output_ifc_folder, relative_input_path)
    # create the output folder if it doesn't exist
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    return output_folder_path


def create_file_paths_file(folder_path, output_file, file_ending):
    with open(output_file, 'wb') as fi:
        tofile = []
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                # # todo: Midlertidig ignorerer
                # if "ARK" in filename or "RIB" in filename:
                #     continue
                if filename.endswith(file_ending):
                    file_path = os.path.join(root, filename) + '\n'
                    tofile.append(file_path)

        # for line in tofile[:2]:
        for line in tofile:
            fi.write(line.encode('utf-8'))


def get_lower_fixed_filename(file_path):
    filename = os.path.splitext(os.path.basename(file_path.strip()))[0]
    newname = filename.lower().strip()
    return newname


def create_csv_file(rvt_file_list, pset_file_list, mapping_file_list, output_file):
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(avp.CSWROWS)
        with codecs.open(rvt_file_list, mode='r', encoding='utf-8') as rvt_file_list_file, codecs.open(pset_file_list, mode='r', encoding='utf-8') as pset_file_list_file, codecs.open(mapping_file_list, mode='r', encoding='utf-8') as mapping_file_list_file:

            rvt_files = rvt_file_list_file.readlines()
            pset_files = pset_file_list_file.readlines()
            mapping_files = mapping_file_list_file.readlines()

            for rvt_file in rvt_files:
                rvt_file = os.path.normpath(rvt_file.strip())
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
create_file_paths_file(avp.input_rvt_folder, avp.rvt_file_list_path, ".rvt")

""" Create a file with all the paths to the pset files in the folder and subfolders. """
Output("Lager pset og mappingfil...")
create_file_paths_file(avp.config_pset_folder, avp.psets_paths_path, ".txt")

""" Create a file with all the paths to the family mapping files in the folder and subfolders. """
Output("Lager mappingfil...")
create_file_paths_file(avp.mappings_folder, avp.mapping_paths_path, ".txt")

""" Create a CSV file that links the rvt files to the pset and mapping files. """
Output("Lager CSV-fil...")
# create_csv_file(op(avp.main_config_folder, "rvt_file_list.txt"), op(avp.main_config_folder, "pSets_Paths.txt"), op(avp.main_config_folder, "mapping_paths.txt"), op(avp.main_config_folder, "generated_paths_and_settings.csv"))
create_csv_file(avp.rvt_file_list_path, avp.psets_paths_path, avp.mapping_paths_path, avp.generated_paths_and_settings_path)
