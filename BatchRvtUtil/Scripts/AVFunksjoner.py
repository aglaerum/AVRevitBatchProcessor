# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
import AVClr

import os
import shutil
import codecs
import AVServerFuncs as avs
import AVPathsAndSettings as avps
from System import Environment
import json

from batch_rvt_util import CommandSettings, BatchRvtSettings, RevitVersion

def get_installed_revit_versions():
    """ Hent alle installerte Revit versjoner """
    from batch_rvt_util import RevitVersion
    versions = RevitVersion.GetInstalledRevitVersions()
    return [int(str(x)[-4:]) for x in versions]

class AVAutoExporterSettings(object):
    def __init__(self, output):
        # type: (callable) -> object
        self._home_folder = None
        output("Scriptet kjøres fra: " + self.home_folder)
        output("Innstillingene for Exporter hentes fra: " + self.av_autoexporter_settings_path)
        output("Innstillingene for BatchRvt hentes fra: " + self.batch_rvt_settings_path)

        self.config_ifcsettings_folder = None
        self.config_pset_folder = None
        self.output_ifc_folder = None
        self.mappings_folder = None
        self.input_rvt_folder = None

        """ For bruk med RServer"""
        self.crawler_exe_path = None # Henter alle baner fra Rserver og lagerr til self.server_paths_csv
        self.server_paths_csv = None # CSV fil som inneholder alle baner fra Rserver
        self.temp_folder = None # Mappe med bufferfiler slik at man ikke trenger å oppdatere server_paths_csv hver gang
        self.rvt_temp_server_paths = None # Bufferfil som er filtrert på version og oppdatert for 24 timer siden
        self.force_refresh = None # Brukes for å tvinge oppdatering av server_paths_csv og nedlasting av nye modeller

        """ Default innstillinger """
        # Rserver
        self._default_crawler_exe_path = os.path.join(self.home_folder, "RServerCrawler.exe") # Denne henter alle baner fra Rserver og lagrer til RserverSQL.csv i samme mappe som exe
        self._default_server_paths_csv = os.path.join(self.home_folder, "RserverSQL.csv") # Generert av RServerCrawler.exe
        self._default_temp_folder = os.path.join(self.home_folder, "Temp")
        self._default_rvt_temp_server_paths = os.path.join(self._default_temp_folder, "rvt_temp_server_paths.txt")
        self._default_force_refresh = False

        # Alle
        self._rvt_csv_file_list_path = None # listen over alle rvt filer som skal eksporteres
        self._default_input_rvt_folder = os.path.join(self.home_folder, "Input_models")
        self._default_output_ifc_folder = os.path.join(self.home_folder, "Output")
        self._default_mappings_folder = os.path.join(self.home_folder, "IFCMapping")
        self._default_config_pset_folder = os.path.join(self.home_folder, "IFCPsets")
        self._default_config_ifcsettings_folder = os.path.join(self.home_folder, "IFCSettings")



        self.load_settings()
        self.create_folders()

        output("Input_rvt_folder: " + self.input_rvt_folder)
        output("Output_ifc_folder: " + self.output_ifc_folder)
        output("Mappings_folder: " + self.mappings_folder)
        output("Config_pset_folder: " + self.config_pset_folder)
        output("Config_ifcsettings_folder: " + self.config_ifcsettings_folder)

    @property
    def av_autoexporter_settings_path(self):
        return os.path.join(self.home_folder, "AVAutoExporterSettings.json")

    @property
    def home_folder(self):
        if self._home_folder is None:
            self._home_folder = get_home_folder()
        return self._home_folder

    @property
    def batch_rvt_settings_path(self):
        return get_commanline_option("settings_file")

    @property
    def rvt_csv_file_list_path(self):
        if self._rvt_csv_file_list_path is None:
            self._rvt_csv_file_list_path = get_rvt_file_list_path()
        return self._rvt_csv_file_list_path

    def load_settings(self):
        if not os.path.exists(self.av_autoexporter_settings_path):
            self.create_default_settings()
        else:
            with codecs.open(self.av_autoexporter_settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
                self.input_rvt_folder = settings.get("input_rvt_folder", self._default_input_rvt_folder)
                self.output_ifc_folder = settings.get("output_ifc_folder", self._default_output_ifc_folder)
                self.mappings_folder = settings.get("mappings_folder", self._default_mappings_folder)
                self.config_pset_folder = settings.get("config_pset_folder", self._default_config_pset_folder)
                self.config_ifcsettings_folder = settings.get("config_ifcsettings_folder", self._default_config_ifcsettings_folder)
                self.server_paths_csv = settings.get("server_paths_csv", self._default_server_paths_csv)
                self.crawler_exe_path = settings.get("crawler_exe_path", self._default_crawler_exe_path)
                self.temp_folder = settings.get("temp_folder", self._default_temp_folder)
                self.rvt_temp_server_paths = settings.get("rvt_temp_server_paths", self._default_rvt_temp_server_paths)
                self.force_refresh = settings.get("force_refresh", self._default_force_refresh)

    def create_default_settings(self):
        settings = {
            "input_rvt_folder": self._default_input_rvt_folder,
            "output_ifc_folder": self._default_output_ifc_folder,
            "mappings_folder": self._default_mappings_folder,
            "config_pset_folder": self._default_config_pset_folder,
            "config_ifcsettings_folder": self._default_config_ifcsettings_folder,
            "server_paths_csv": self._default_server_paths_csv,
            "crawler_exe_path": self._default_crawler_exe_path,
            "temp_folder": self._default_temp_folder,
            "rvt_temp_server_paths": self._default_rvt_temp_server_paths,
            "force_refresh": self._default_force_refresh
            }
        with codecs.open(self.av_autoexporter_settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)

        self.load_settings()
        self.create_folders()
        self.crate_default_setting_files()

    def create_folders(self):
        if not os.path.exists(self.input_rvt_folder):
            os.makedirs(self.input_rvt_folder)

        if not os.path.exists(self.output_ifc_folder):
            os.makedirs(self.output_ifc_folder)

        if not os.path.exists(self.mappings_folder):
            os.makedirs(self.mappings_folder)

        if not os.path.exists(self.config_pset_folder):
            os.makedirs(self.config_pset_folder)

        if not os.path.exists(self.config_ifcsettings_folder):
            os.makedirs(self.config_ifcsettings_folder)

        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

    def crate_default_setting_files(self):
        default_path = os.path.join(self.mappings_folder, "default.txt")
        if not os.path.exists(default_path):
            with codecs.open(default_path, "w", encoding="utf-8") as f:
                f.write("KOPIER INN MAPPING HER")

        default_path = os.path.join(self.config_pset_folder, "default.txt")
        if not os.path.exists(default_path):
            with codecs.open(default_path, "w", encoding="utf-8") as f:
                f.write("KOPIER INN PSET HER")

        default_path = os.path.join(self.config_ifcsettings_folder, "default.txt")
        if not os.path.exists(default_path):
            with codecs.open(default_path, "w", encoding="utf-8") as f:
                f.write("KOPIER INN IFCSETTINGS HER")


def get_rvt_file_list_path():
    # type: () -> str
    batch_rvt_config = get_new_batch_rvt_config()
    return batch_rvt_config.RevitFileListFilePath.GetValue()

def get_home_folder():
    # type: () -> str
    settings_file = get_commanline_option("settings_file")
    home_folder = os.path.dirname(settings_file)
    return home_folder

def get_new_batch_rvt_config():
    batch_rvt_config = BatchRvtSettings()
    batch_rvt_config.LoadFromFile(get_commanline_option("settings_file"))
    return batch_rvt_config
def get_commanline_option(option):
    # "settings_file"
    commandlin_options = dict(CommandSettings.GetCommandLineOptions())
    optionvalue = commandlin_options.get(option)
    return optionvalue

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


def reactivate_all_addins(deactivatefoldername=None, Output=None):
    """ Reactivate all addins in Revit. """
    if Output is not None:
        Output("Reactivering av addins...")

    AVClr.clr_batchrvtutil()
    import BatchRvtUtil

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

def create_temp_paths_file(rvt_paths, output_file, output):
    with codecs.open(output_file, 'w', encoding="utf-8") as fi:
        tofile = []
        for rvt_path in rvt_paths:
            if os.path.exists(rvt_path):
                tofile.append(rvt_path + "\n")
            else:
                output("Filen eksisterer ikke: " + rvt_path)

        for line in tofile:
            fi.write(line)

def get_paths_from_file(file_path):
    with codecs.open(file_path, 'r', encoding="utf-8") as fi:
        rvt_paths = fi.readlines()
        rvt_paths = [avs.ServerPath(x) for x in rvt_paths]
    return rvt_paths


class PathFromCSVACC(object):
    """ En filbane hentet fra en csv fil """
    def __init__(self, local_path, ifc_outfolder, ifc_psets, ifc_mapping, ifc_settings):
        # "LocalPath", "IFCPath", "IFCpSets", "IFCMapping", "IFCSettings"
        super(PathFromCSVACC, self).__init__()
        self.path = os.path.normpath(local_path)
        self.ifc_outfolder = os.path.normpath(ifc_outfolder)
        self.psets_file = os.path.normpath(ifc_psets)
        self.mappings_file = os.path.normpath(ifc_mapping)
        self.ifc_export_settings = os.path.normpath(ifc_settings)

class PathFromFileACC(object):

    def __init__(self, local_path):
        # "LocalPath", "IFCPath", "IFCpSets", "IFCMapping", "IFCSettings"
        super(PathFromFileACC, self).__init__()
        self.path = os.path.normpath(unicode(local_path).strip())

    def get_node_path(self, rvt_in_folder):
        node_path = self.path.replace(rvt_in_folder, "")
        node_path = node_path.lstrip("\\")
        return node_path

    def get_ifc_out_folder(self, ifc_out_folder, rvt_in_folder):
        node_path = self.get_node_path(rvt_in_folder)
        ifc_out_folder = os.path.join(ifc_out_folder, node_path)
        return ifc_out_folder

    def get_ifc_psets_file(self, psets_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
        the_file = os.path.join(psets_folder, my_basename + ".txt")
        if not os.path.exists(the_file):
            the_file = os.path.join(psets_folder, "default.txt")
        assert os.path.exists(the_file)
        return the_file

    def get_ifc_mappings_file(self, mappings_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
        the_file = os.path.join(mappings_folder, my_basename + ".txt")
        if not os.path.exists(the_file):
            the_file = os.path.join(mappings_folder, "default.txt")
        assert os.path.exists(the_file)
        return the_file

    def get_ifc_settings_file(self, ifc_settings_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
        the_file = os.path.join(ifc_settings_folder, my_basename + ".json")
        if not os.path.exists(the_file):
            the_file = os.path.join(ifc_settings_folder, "default.json")
        assert os.path.exists(the_file)
        return the_file

# class PathFromCSVServer(object):
#     def __init__(self, local_path, ServerPath, Date, IFCPath, IFCpSets, IFCMapping, IFCSettings, Version):
#         super(PathFromCSVServer, self).__init__()
#
#         self.local_path = os.path.normpath(unicode(local_path).strip())
#         self.server_path = ServerPath
#         self.date = Date
#         self.ifc_outfolder = IFCPath
#         self.psets_file = IFCpSets
#         self.mappings_file = IFCMapping
#         self.ifc_export_settings = IFCSettings
#         self.version = Version

class PathFromFileServer(object):
    """ En filbane hentet fra en csv fil """
    def __init__(self, local_path, ServerPath, Date, IFCPath, IFCpSets, IFCMapping, IFCSettings, Version):
        super(PathFromFileServer, self).__init__()

        self.local_path = os.path.normpath(unicode(local_path).strip())
        self.server_path = ServerPath
        self.date = Date
        self.ifc_outfolder = IFCPath
        self.psets_file = IFCpSets
        self.mappings_file = IFCMapping
        self.ifc_export_settings = IFCSettings
        self.version = Version


