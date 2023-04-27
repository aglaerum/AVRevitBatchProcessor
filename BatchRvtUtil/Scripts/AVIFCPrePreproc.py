# -*- coding: utf-8 -*-

import os

import AVFunksjoner as avf
import AVClr
# noinspection PyUnresolvedReferences
import AVImports
import AVPathsAndSettings as avp

avf.clr_highest_revitapi()
op = os.path.join

from script_util import Output

""" GLOBAL VARIABLES """
CSWROWS = ["RVT File Path", "Project Name", "PSet File Path", "Mapping File Path", "IFC Folder Path"]


input_rvt_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656\TESTFOLDER\Input_models"
output_ifc_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656\TESTFOLDER\Output AG"
mappings_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656\TESTFOLDER\FamilymappingFile"
config_pset_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656\TESTFOLDER\Input_configs"

""" Hovedmappen for programmet """
main_config_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656"
# main_config_folder = os.path.dirname(BatchRvtUtil.CommandLineUtil.GetCommandLineOption("settings_file"))
""" Disse mappene blir autogenerert av programmet """
rvt_file_list_path = os.path.join(main_config_folder, "rvt_file_list.txt")
psets_paths_path = os.path.join(main_config_folder, "pSets_Paths.txt")
mapping_paths_path = os.path.join(main_config_folder, "mapping_paths.txt")
generated_paths_and_settings_path = os.path.join(main_config_folder, "generated_paths_and_settings.csv")

""" Midlertidig bane for deaktivering av addins """
addin_deactivate_foldername = "AVDeaktivert"

""" Annet """
crawler_exe_path = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterRServer\RServerCrawler.exe"
server_paths_csv = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterRServer\RserverSQL.csv"

""" Deaktiver alle addins som ikke er batchprocessor eller AVTools """
avf.deactivate_all_addins()

""" Create a file with all the paths to the rvt files in the folder and subfolders. """
Output("Lager filbanefil...")
avf.search_folder_create_file(input_rvt_folder, avp.rvt_file_list_path, ".rvt")

""" Create a file with all the paths to the pset files in the folder and subfolders. """
Output("Lager pset og mappingfil...")
avf.search_folder_create_file(avp.config_pset_folder, avp.psets_paths_path, ".txt")

""" Create a file with all the paths to the family mapping files in the folder and subfolders. """
Output("Lager mappingfil...")
avf.search_folder_create_file(avp.mappings_folder, avp.mapping_paths_path, ".txt")

""" Create a CSV file that links the rvt files to the pset and mapping files. """
Output("Lager CSV-fil...")
# create_csv_file(op(avp.main_config_folder, "rvt_file_list.txt"), op(avp.main_config_folder, "pSets_Paths.txt"), op(avp.main_config_folder, "mapping_paths.txt"), op(avp.main_config_folder, "generated_paths_and_settings.csv"))
avf.create_csv_file(avp.rvt_file_list_path, avp.psets_paths_path, avp.mapping_paths_path, avp.generated_paths_and_settings_path)

