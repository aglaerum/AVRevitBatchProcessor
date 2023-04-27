# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
import AVClr
import os
from System import Environment
import shutil
import codecs
import AVServerFuncs as avs
import BatchRvtUtil
import AVPathsAndSettings as avps
# CSWROWS = ["RVT File Path", "Project Name", "PSet File Path", "Mapping File Path", "IFC Folder Path"]


def deactivate_all_addins(deactivatefoldername=None, Output=None):
    """ Deactivate all addins in Revit. """
    if Output is not None:
        Output("Deaktiverer alle addins...")

    if deactivatefoldername is None:
        deactivatefoldername = avps.addin_deactivate_foldername

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


def reactivate_all_addins(deactivatefoldername=None, Output=None):
    """ Reactivate all addins in Revit. """
    if Output is not None:
        Output("Reactivering av addins...")

    if deactivatefoldername is None:
        deactivatefoldername = avps.addin_deactivate_foldername

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


def search_folder_create_file(folder_path, output_file, file_ending):
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


def get_lower_fixed_filename(file_path):
    filename = os.path.splitext(os.path.basename(file_path.strip()))[0]
    newname = filename.lower().strip()
    return newname


# def create_csv_file(csv_file_path, rvt_file_list, pset_file_list, mapping_file_list, ifc_folder, output):
#     with codecs.open(csv_file_path, 'w', encoding="utf-8") as f:
#         writer = csv.writer(f)
#         writer.writerow(CSWROWS)
#         with codecs.open(rvt_file_list, mode='r', encoding='utf-8') as rvt_file_list_file,\
#                 codecs.open(pset_file_list, mode='r', encoding='utf-8') as pset_file_list_file,\
#                 codecs.open(mapping_file_list, mode='r', encoding='utf-8') as mapping_file_list_file:
#
#             rvt_files = rvt_file_list_file.readlines()
#             pset_files = pset_file_list_file.readlines()
#             mapping_files = mapping_file_list_file.readlines()
#
#             for rvt_file in rvt_files:
#                 rvt_file = os.path.normpath(rvt_file.strip())
#                 project_name = os.path.basename(os.path.dirname(rvt_file))
#                 rvt_path = rvt_file
#                 pset_path = ""
#                 mapping_path = ""
#
#                 for pset_file in pset_files:
#                     if get_lower_fixed_filename(rvt_file) in get_lower_fixed_filename(pset_file):
#                         pset_path = pset_file.strip()
#                         break
#
#                 for mapping_file in mapping_files:
#                     if get_lower_fixed_filename(rvt_file) in get_lower_fixed_filename(mapping_file):
#                         mapping_path = mapping_file.strip()
#                         break
#                 rows = [rvt_path, project_name, pset_path, mapping_path, ifc_path]
#                 # Output(str(rows))
#                 writer.writerow(rows)

class LocalPath(object):
    def __init__(self, path):
        super(LocalPath, self).__init__()
        self.path = os.path.normpath(unicode(path).strip())

    def get_ifc_psets_file(self, psets_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0] # fjern .rvt
        the_file = os.path.join(psets_folder, my_basename + ".txt")
        if not os.path.exists(the_file):
            the_file = os.path.join(psets_folder, "default.txt")
        if not os.path.exists(the_file):
            the_file = None
        return the_file

    def get_ifc_mappings_file(self, mappings_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0] # fjern .rvt
        the_file = os.path.join(mappings_folder, my_basename + ".txt")
        if not os.path.exists(the_file):
            the_file = os.path.join(mappings_folder, "default.txt")
        if not os.path.exists(the_file):
            the_file = None
        return the_file

    def get_ifc_settings_file(self, ifc_settings_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0] # fjern .rvt
        the_file = os.path.join(ifc_settings_folder, my_basename + ".json")
        if not os.path.exists(the_file):
            the_file = os.path.join(ifc_settings_folder, "default.json")
        if not os.path.exists(the_file):
            the_file = None
        return the_file