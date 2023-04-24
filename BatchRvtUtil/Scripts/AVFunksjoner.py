# -*- coding: utf-8 -*-

import os
import clr
import re
from System import Environment
import shutil

""" Nødvendig for kjøring i pycharm """

def runnin_in_pycharm():
    return 'PYCHARM_HOSTED' in os.environ

# noinspection PyUnresolvedReferences
def clr_batchrvtutil():
    if runnin_in_pycharm():
        # clr.AddReferenceToFileAndPath(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\GitHub\AVRevitBatchProcessor\BatchRvtUtil\bin\x64\Release\BatchRvtUtil.dll")
        clr.AddReferenceToFileAndPath(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\GitHub\AVRevitBatchProcessor\BatchRvtUtil\BatchRvtUtil.dll")
        print ("Script is running in PyCharm")
    else:
        print("Script is not running in PyCharm")


CSWROWS = ["RVT File Path", "Project Name", "PSet File Path", "Mapping File Path", "IFC Folder Path"]

op = os.path.join
main_volo_volder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656\TESTFOLDER"
input_rvt_folder = op(main_volo_volder, r"Input_models\524 Myrane IS")
output_ifc_folder = op(main_volo_volder, "Output AG")
mappings_folder = op(main_volo_volder, "FamilymappingFile")
config_pset_folder = op(main_volo_volder, "Input_configs")
main_config_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656"

# file paths to various configuration files
rvt_file_list_path = op(main_config_folder, "rvt_file_list.txt")
psets_paths_path = op(main_config_folder, "pSets_Paths.txt")
mapping_paths_path = op(main_config_folder, "mapping_paths.txt")
generated_paths_and_settings_path = op(main_config_folder, "generated_paths_and_settings.csv")

""" Midlertidig bane for deaktivering av addins """
addin_deactivate_foldername = "AVDeaktivert"


def get_installed_revit_paths():
    clr_batchrvtutil()
    import BatchRvtUtil
    installed_versions = BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()
    paths = []
    for version in installed_versions:
        path = BatchRvtUtil.RevitVersion.GetRevitExecutableFolderPath(version)
        paths.append(path)
    return paths


def get_highest_revit_version_path(paths):
    highest_version = None
    highest_version_path = None
    for path in paths:
        match = re.search(r'Revit (\d+)', path)
        if match:
            version = int(match.group(1))
            if highest_version is None or version > highest_version:
                highest_version = version
                highest_version_path = path
    return highest_version_path


def clr_highest_revitapi():
    if runnin_in_pycharm():
        paths = get_installed_revit_paths()
        revitpath = get_highest_revit_version_path(paths)
        revitapi_path = os.path.join(revitpath, 'revitapi.dll')
        clr.AddReferenceToFileAndPath(revitapi_path)


def get_revit_file_version(path):
    clr_highest_revitapi()
    from Autodesk.Revit import DB

    fileinfo = DB.BasicFileInfo.Extract(path)
    return str(fileinfo.Format)


def deactivate_all_addins(deactivatefoldername=None, Output=None):
    """ Deactivate all addins in Revit. """
    if Output is not None:
        Output("Deaktiverer alle addins...")

    if deactivatefoldername is None:
        deactivatefoldername = addin_deactivate_foldername

    clr_batchrvtutil()
    import BatchRvtUtil
    allrevitversions = BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()
    print allrevitversions
    folderpaths = []
    for version in allrevitversions:
        for addinsfolder in [Environment.SpecialFolder.CommonApplicationData, Environment.SpecialFolder.ApplicationData]:
            folderpath = BatchRvtUtil.RevitVersion.GetRevitAddinsFolderPath(version, addinsfolder)
            folderpaths.append(folderpath)

            addin_files = [f for f in os.listdir(folderpath) if f.endswith('.addin')]
            subfolderpath = os.path.join(folderpath, deactivatefoldername)

            if addin_files:
                if not os.path.exists(subfolderpath):
                    os.makedirs(subfolderpath)
                for addin_file in addin_files:
                    if addin_file.startswith("AVToolsRevit") or addin_file.startswith("BatchRvtAddin"):
                        continue
                    addin_file_path = os.path.join(folderpath, addin_file)
                    shutil.move(addin_file_path, subfolderpath)

    return folderpaths


def reactivate_all_addins(deactivatefoldername=None, Output=None):
    """ Reactivate all addins in Revit. """
    if Output is not None:
        Output("Reactivering av addins...")

    if deactivatefoldername is None:
        deactivatefoldername = addin_deactivate_foldername

    clr_batchrvtutil()
    import BatchRvtUtil
    allrevitversions = BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()

    for version in allrevitversions:
        for addinsfolder in [Environment.SpecialFolder.CommonApplicationData, Environment.SpecialFolder.ApplicationData]:
            folderpath = BatchRvtUtil.RevitVersion.GetRevitAddinsFolderPath(version, addinsfolder)
            subfolderpath = os.path.join(folderpath, deactivatefoldername)

            if os.path.exists(subfolderpath):
                addin_files = [f for f in os.listdir(subfolderpath) if f.endswith('.addin')]
                for addin_file in addin_files:
                    addin_file_path = os.path.join(subfolderpath, addin_file)
                    shutil.move(addin_file_path, folderpath)

                os.rmdir(subfolderpath)

    return True
