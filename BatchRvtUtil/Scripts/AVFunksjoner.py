# -*- coding: utf-8 -*-

import os
import clr
import re

""" Nødvendig for kjøring i pycharm """
# noinspection PyUnresolvedReferences
def clr_batchrvtutil():
    clr.AddReferenceToFileAndPath(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\GitHub\AVRevitBatchProcessor\BatchRvtUtil\bin\x64\Release\BatchRvtUtil.dll")


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
    paths = get_installed_revit_paths()
    revitpath = get_highest_revit_version_path(paths)
    revitapi_path = os.path.join(revitpath, 'revitapi.dll')
    clr.AddReferenceToFileAndPath(revitapi_path)


def get_revit_file_version(path):
    clr_highest_revitapi()
    from Autodesk.Revit import DB

    fileinfo = DB.BasicFileInfo.Extract(path)
    return str(fileinfo.Format)

# def find_newest_revit():
#     current_year = datetime.datetime.now().year
#     search_years = list(range(current_year, current_year + 3))
#     search_years.reverse()
#
#     for year in search_years:
#         revit_path = "C:\\Program Files\\Autodesk\\Revit {0}".format(year)
#         if os.path.exists(revit_path):
#             Output("Found Revit {0} at {1}".format(year, revit_path))
#             return revit_path
#             break
#     else:
#         print("No installed version of Revit found.")
