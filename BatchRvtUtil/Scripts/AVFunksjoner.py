# -*- coding: utf-16 -*-

import os
import clr
import re
from System import Environment
import shutil
import AVPathsAndSettings as avp

""" Nødvendig for kjøring i pycharm """

def runnin_in_pycharm():
    if 'PYCHARM_HOSTED' in os.environ:
        print ("Script is running in PyCharm")
        return True
    else:
        print("Script is not running in PyCharm")
        return False


# noinspection PyUnresolvedReferences
def clr_batchrvtutil():
    if runnin_in_pycharm():
        # clr.AddReferenceToFileAndPath(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\GitHub\AVRevitBatchProcessor\BatchRvtUtil\bin\x64\Release\BatchRvtUtil.dll")
        clr.AddReferenceToFileAndPath(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\GitHub\AVRevitBatchProcessor\BatchRvtUtil\BatchRvtUtil.dll")
        print "BatchRvtUtil assembly reference added."




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

def clr_spesific_revitapi(version):
    if runnin_in_pycharm():
        clr_batchrvtutil()
        import BatchRvtUtil
        version = BatchRvtUtil.RevitVersion.GetSupportedRevitVersion(version)
        revitpath = BatchRvtUtil.RevitVersion.GetRevitExecutableFolderPath(version)
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
        deactivatefoldername = avp.addin_deactivate_foldername

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
                    target_file_path = os.path.join(subfolderpath, addin_file)
                    shutil.copy2(addin_file_path, target_file_path)
                    if os.path.exists(addin_file_path) and os.path.exists(target_file_path):
                        os.remove(addin_file_path)
    return folderpaths


def reactivate_all_addins(deactivatefoldername=None, Output=None):
    """ Reactivate all addins in Revit. """
    if Output is not None:
        Output("Reactivering av addins...")

    if deactivatefoldername is None:
        deactivatefoldername = avp.addin_deactivate_foldername

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
