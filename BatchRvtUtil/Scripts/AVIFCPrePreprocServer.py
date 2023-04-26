# -*- coding: utf-8 -*-

import codecs
import csv
import os
import sys

import AVFunksjoner as avf
import AVPathsAndSettings as avp
import AVServerFuncs as avs
import subprocess as SU
import time


avf.clr_highest_revitapi()
op = os.path.join
from Autodesk.Revit import DB

from script_util import Output

""" Hent alle baner fra Rserver """
def run_and_get_serverpaths(exe_path, csv_path, force_refresh=False):
    if force_refresh or (time.time() - os.path.getmtime(csv_path)) > 8 * 3600:
        Output("Baner må hentes på nytt fordi CSV er gammel eller force er satt til True...")
        process = SU.Popen([exe_path, "--output", csv_path], creationflags=SU.CREATE_NEW_CONSOLE)
        process.wait()
        # if process.returncode != 0:
        #     error = process.stderr.readline()
        #     print("Feilmelding ved kjøring av Rserver path-funksjon:\n{}".format(error.decode('utf-8')))
        #     sys.exit()

    pa = []
    with open(csv_path) as f:
        reader = csv.reader(f)
        next(reader) # skip header
        for row in reader:
            if row:
                pa.append(row[0])
    return pa

def filter_new_paths(all_paths):
    new_paths = [avs.ServerPath(path) for path in all_paths if avs.get_RserverVersion(path) == str(2022)]
    new_paths = new_paths[0:50]
    # new_paths = [avs.ServerPath(path) for path in all_paths]

    for path in new_paths:
        Output("----------------------------------------")
        Output("Path: {}".format(path.path))
        # Output("Server: {}".format(path.rsn_path))
        Output(path.server_node)
    return new_paths

""" Hent Rserverbaner """
Output("Henter Rserverbaner...")
paths = run_and_get_serverpaths(avp.crawler_exe_path, avp.server_paths_csv, False)
# paths = paths[1000:1008]
paths = filter_new_paths(paths)
Output("Hentet {} baner fra Rserver.".format(len(paths)))

# """ Deaktiver alle addins som ikke er batchprocessor eller AVTools """
# avf.deactivate_all_addins()
#
# """ Create a file with all the paths to the rvt files in the folder and subfolders. """
# Output("Lager filbanefil...")
# avf.create_file_paths_file(avp.input_rvt_folder, op(avp.main_config_folder, "rvt_file_list.txt"), ".rvt")
#
# """ Create a file with all the paths to the pset files in the folder and subfolders. """
# Output("Lager pset og mappingfil...")
# avf.create_file_paths_file(avp.config_pset_folder, op(avp.main_config_folder, "pSets_Paths.txt"), ".txt")
#
# """ Create a file with all the paths to the family mapping files in the folder and subfolders. """
# Output("Lager mappingfil...")
# avf.create_file_paths_file(avp.mappings_folder, op(avp.main_config_folder, "mapping_paths.txt"), ".txt")
#
# """ Create a CSV file that links the rvt files to the pset and mapping files. """
# Output("Lager CSV-fil...")
# avf.create_csv_file(avp.rvt_file_list_path, avp.psets_paths_path, avp.mapping_paths_path, avp.generated_paths_and_settings_path)

krasj

