# -*- coding: utf-8 -*-

import codecs
import csv
import os
import sys

import AVFunksjoner as avf
import AVPathsAndSettings as avp
from subprocess import Popen, PIPE


avf.clr_highest_revitapi()
op = os.path.join

from script_util import Output

""" Hent alle baner fra Rserver """
def run_and_get_serverpaths(exe_path, csv_path, refresh_path=False):

    if refresh_path:
        process = Popen([exe_path, "--output", csv_path], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print("Feilmelding ved kjøring av Rserver path-funksjon:\n{}".format(stderr.decode('utf-8')))
            sys.exit()

    pa = []
    with open(csv_path) as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                pa.append(row[0])
    return pa

""" Hent Rserverbaner """
Output("Henter Rserverbaner...")
paths = run_and_get_serverpaths(avp.crawler_exe_path, avp.server_paths_csv, False)


""" Deaktiver alle addins som ikke er batchprocessor eller AVTools """
avf.deactivate_all_addins()

""" Create a file with all the paths to the rvt files in the folder and subfolders. """
Output("Lager filbanefil...")
create_file_paths_file(avp.input_rvt_folder, op(avp.main_config_folder, "rvt_file_list.txt"), ".rvt")

""" Create a file with all the paths to the pset files in the folder and subfolders. """
Output("Lager pset og mappingfil...")
create_file_paths_file(avp.config_pset_folder, op(avp.main_config_folder, "pSets_Paths.txt"), ".txt")

""" Create a file with all the paths to the family mapping files in the folder and subfolders. """
Output("Lager mappingfil...")
create_file_paths_file(avp.mappings_folder, op(avp.main_config_folder, "mapping_paths.txt"), ".txt")

""" Create a CSV file that links the rvt files to the pset and mapping files. """
Output("Lager CSV-fil...")
create_csv_file(avp.rvt_file_list_path, avp.psets_paths_path, avp.mapping_paths_path, avp.generated_paths_and_settings_path)

krasj

