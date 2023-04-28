# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
import AVClr

import os
import shutil
import codecs
import AVServerFuncs as avs
import AVPathsAndSettings as avps
from System import Environment


def deactivate_all_addins(deactivatefoldername=None, output=None):
    AVClr.clr_batchrvtutil()
    import BatchRvtUtil
    """ Deactivate all addins in Revit. """
    if output is not None:
        output("Deaktiverer alle addins...")

    if deactivatefoldername is None:
        deactivatefoldername = avps.addin_deactivate_foldername

    """ Deaktiver application plugins """
    # application_plugins = os.path.normpath(r"C:\ProgramData\Autodesk\ApplicationPlugins")
    # deactivate_folder = os.path.join(application_plugins, deactivatefoldername)
    # for plugin_folder in os.listdir(application_plugins):
    #     if plugin_folder.endswith(".bundle"):
    #         if not "ifc" in plugin_folder.lower() or "avtools" in plugin_folder.lower():
    #             full_path = os.path.join(application_plugins, plugin_folder)
    #             shutil.copy2(full_path, deactivate_folder)
    #             if os.path.exists(full_path) and os.path.exists(deactivate_folder):
    #                 os.remove(full_path)

    allrevitversions = BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()
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


# def reactivate_all_addins(deactivatefoldername=None, Output=None):
#     """ Reactivate all addins in Revit. """
#     if Output is not None:
#         Output("Reactivering av addins...")
#
#     if deactivatefoldername is None:
#         deactivatefoldername = avps.addin_deactivate_foldername
#
#     allrevitversions = BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()
#
#     for version in allrevitversions:
#         for addinsfolder in [Environment.SpecialFolder.CommonApplicationData, Environment.SpecialFolder.ApplicationData]:
#             folderpath = BatchRvtUtil.RevitVersion.GetRevitAddinsFolderPath(version, addinsfolder)
#             subfolderpath = os.path.join(folderpath, deactivatefoldername)
#
#             if os.path.exists(subfolderpath):
#                 addin_files = [f for f in os.listdir(subfolderpath) if f.endswith('.addin')]
#                 for addin_file in addin_files:
#                     addin_file_path = os.path.join(subfolderpath, addin_file)
#                     shutil.move(addin_file_path, folderpath)
#
#                 os.rmdir(subfolderpath)
#
#     return True


def search_folder_create_file(folder_path, output_file, file_ending):
    # For Rserver
    with open(output_file, 'wb') as fi:
        tofile = []
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                if filename.endswith(file_ending):
                    file_path = os.path.join(root, filename) + '\n'
                    tofile.append(file_path)

        for line in tofile:
            fi.write(line.encode('utf-8'))

def create_paths_file(rvt_paths, output_file, output):
    with open(output_file, 'wb') as fi:
        tofile = []
        for rvt_path in rvt_paths:
            if os.path.exists(rvt_path):
                file_path = rvt_path + '\n'
                tofile.append(file_path)
            else:
                output("Filen eksisterer ikke: " + rvt_path)

        for line in tofile:
            fi.write(line.encode('utf-8'))

def get_paths_from_file(file_path):
    with codecs.open(file_path, 'r', encoding="utf-8") as fi:
        rvt_paths = fi.readlines()
        rvt_paths = [avs.ServerPath(x) for x in rvt_paths]
    return rvt_paths


# def get_lower_fixed_filename(file_path):
#     filename = os.path.splitext(os.path.basename(file_path.strip()))[0]
#     newname = filename.lower().strip()
#     return newname

class LocalFileACC(object):

    def __init__(self, local_path):
        super(LocalFileACC, self).__init__()
        self.local_path = os.path.normpath(unicode(local_path).strip())

    def get_ifc_psets_file(self, psets_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
        the_file = os.path.join(psets_folder, my_basename + ".txt")
        if not os.path.exists(the_file):
            the_file = os.path.join(psets_folder, "default.txt")
        if not os.path.exists(the_file):
            the_file = None
        return the_file

    def get_ifc_mappings_file(self, mappings_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
        the_file = os.path.join(mappings_folder, my_basename + ".txt")
        if not os.path.exists(the_file):
            the_file = os.path.join(mappings_folder, "default.txt")
        if not os.path.exists(the_file):
            the_file = None
        return the_file

    def get_ifc_settings_file(self, ifc_settings_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
        the_file = os.path.join(ifc_settings_folder, my_basename + ".json")
        if not os.path.exists(the_file):
            the_file = os.path.join(ifc_settings_folder, "default.json")
        if not os.path.exists(the_file):
            the_file = None
        return the_file

class LocalPath(object):
    def __init__(self, local_path, ServerPath, Date, IFCPath, IFCpSets, IFCMapping, IFCSettings, Version):
        super(LocalPath, self).__init__()

        self.local_path = os.path.normpath(unicode(local_path).strip())
        self.server_path = ServerPath
        self.date = Date
        self.ifc_outfolder = IFCPath
        self.psets_file = IFCpSets
        self.mappings_file = IFCMapping
        self.ifc_export_settings = IFCSettings
        self.version = Version


    # def get_ifc_psets_file(self, psets_folder):
    #     my_basename = os.path.basename(self.path)
    #     my_basename = os.path.splitext(my_basename)[0] # fjern .rvt
    #     the_file = os.path.join(psets_folder, my_basename + ".txt")
    #     if not os.path.exists(the_file):
    #         the_file = os.path.join(psets_folder, "default.txt")
    #     if not os.path.exists(the_file):
    #         the_file = None
    #     return the_file
    #
    # def get_ifc_mappings_file(self, mappings_folder):
    #     my_basename = os.path.basename(self.path)
    #     my_basename = os.path.splitext(my_basename)[0] # fjern .rvt
    #     the_file = os.path.join(mappings_folder, my_basename + ".txt")
    #     if not os.path.exists(the_file):
    #         the_file = os.path.join(mappings_folder, "default.txt")
    #     if not os.path.exists(the_file):
    #         the_file = None
    #     return the_file
    #
    # def get_ifc_settings_file(self, ifc_settings_folder):
    #     my_basename = os.path.basename(self.path)
    #     my_basename = os.path.splitext(my_basename)[0] # fjern .rvt
    #     the_file = os.path.join(ifc_settings_folder, my_basename + ".json")
    #     if not os.path.exists(the_file):
    #         the_file = os.path.join(ifc_settings_folder, "default.json")
    #     if not os.path.exists(the_file):
    #         the_file = None
    #     return the_file
