# -*- coding: utf-8 -*-
from System import AppDomain
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
        clr.AddReferenceToFileAndPath(r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\Documents\GitHub\AVRevitBatchProcessor\BatchRvtUtil\BatchRvtUtil.dll")

def get_highest_revit_version_path():
    clr_batchrvtutil()
    import BatchRvtUtil
    installed_revits = BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()
    installed_revits = sorted(installed_revits, key=lambda x: x.ToString(), reverse=True)
    latest_revit = installed_revits[0]
    revit_folder = BatchRvtUtil.RevitVersion.GetRevitExecutableFolderPath(latest_revit)
    # print("Highest Revit version found: " + revit_folder)
    return revit_folder

def clr_revitapi(force=False):
    if runnin_in_pycharm() or force:
        # print("Adding reference to revitapi...")
        clr.AddReference("RevitAPI")

def clr_highest_revitapi(force=False):
    if runnin_in_pycharm() or force:
        revitpath = get_highest_revit_version_path()
        revitapi_path = os.path.join(revitpath, 'revitapi.dll')
        clr.AddReferenceToFileAndPath(revitapi_path)

def clr_from_currentdomain(theassname):
    toclr = None
    listen = sorted(list(AppDomain.CurrentDomain.GetAssemblies()))
    for assembly in listen:
        assname = str(assembly.FullName)
        if theassname in assname:
            toclr = assname
    if toclr is not None:
        clr.AddReference(toclr)
        return toclr
    if toclr is None:
        return None

def clr_IFCExportUIOverride():
    result = clr_from_currentdomain("IFCExportUIOverride")
    if result is None:
        result = clr_from_currentdomain("IFCExporterUIOverride")
    assert result is not None

def clr_from_ifcaddin(version, assemblyname):
    path = r"C:\ProgramData\Autodesk\ApplicationPlugins\IFC {}.bundle\Contents\{}".format(str(version), str(version))
    clr.AddReferenceToFileAndPath(os.path.join(path, assemblyname))