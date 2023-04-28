# -*- coding: utf-8 -*-
import System
import clr
import os

def runnin_in_pycharm():
    if 'PYCHARM_HOSTED' in os.environ:
        # print ("Script is running in PyCharm")
        return True
    else:
        # print("Script is not running in PyCharm")
        return False

def clr_batchrvtutil():
    if runnin_in_pycharm():
        # clr.AddReferenceToFileAndPath(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\GitHub\AVRevitBatchProcessor\BatchRvtUtil\bin\x64\Release\BatchRvtUtil.dll")
        clr.AddReferenceToFileAndPath(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\GitHub\AVRevitBatchProcessor\BatchRvtUtil\BatchRvtUtil.dll")
        # print "BatchRvtUtil assembly reference added."
        # System.AppDomain.Unload(System.AppDomain.CurrentDomain)


# def get_installed_revit_paths():
#     installed_versions = BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()
#     paths = []
#     for version in installed_versions:
#         path = BatchRvtUtil.RevitVersion.GetRevitExecutableFolderPath(version)
#         paths.append(path)
#     return paths
#
def get_highest_revit_version_path():
    clr_batchrvtutil()
    import BatchRvtUtil
    installed_revits = BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()
    installed_revits = sorted(installed_revits, key=lambda x: x.ToString(), reverse=True)
    latest_revit = installed_revits[0]
    revit_folder = BatchRvtUtil.RevitVersion.GetRevitExecutableFolderPath(latest_revit)
    # print("Highest Revit version found: " + revit_folder)
    return revit_folder

def clr_revitapi():
    if runnin_in_pycharm():
        # print("Adding reference to revitapi...")
        clr.AddReference("RevitAPI")

def clr_highest_revitapi():
    if runnin_in_pycharm():
        revitpath = get_highest_revit_version_path()
        revitapi_path = os.path.join(revitpath, 'revitapi.dll')
        # print("Adding reference to highest revitapi.dll: " + revitapi_path)
        clr.AddReferenceToFileAndPath(revitapi_path)
#
# def clr_spesific_revitapi(version):
#     version = str(version)
#     if runnin_in_pycharm():
#         return
#         version = BatchRvtUtil.RevitVersion.GetSupportedRevitVersion(version)
#         revitpath = BatchRvtUtil.RevitVersion.GetRevitExecutableFolderPath(version)
#         revitapi_path = os.path.join(revitpath, 'revitapi.dll')
#         print("Adding reference to spesific revitapi.dll: " + revitapi_path)
#         clr.AddReferenceToFileAndPath(revitapi_path)