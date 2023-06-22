# -*- coding: utf-8 -*-

import codecs
import json
import os
import shutil

import AVClr
import AVPathsAndSettings as avps
import AVServerFuncs as avs
from System import Environment
from batch_rvt_util import CommandSettings, BatchRvtSettings, BatchRvt


def get_installed_revit_versions():
    """ Hent alle installerte Revit versjoner """
    from batch_rvt_util import RevitVersion
    versions = RevitVersion.GetInstalledRevitVersions()
    return [int(str(x)[-4:]) for x in versions]


class AVAutoExporterSettings(object):

    def __init__(self, output):
        # type: (callable) -> None

        self._home_folder = None
        output()
        output("---------------------- Hovedinnstillinger --------------------------")
        output("Scriptet kjøres fra: " + self.home_folder)
        output("Innstillingene for AVAutoExporter hentes fra: " + self.av_autoexporter_settings_path)
        output("Innstillingene for BatchRvt hentes fra: " + self.batch_rvt_settings_path)

        self.config_ifcsettings_folder = None
        self.config_pset_folder = None
        self.output_ifc_folder = None
        self.mappings_folder = None
        self.input_rvt_folder = None


        self._rvt_csv_file_list_path = None  # listen over alle rvt filer som skal eksporteres(Lokalt)
        self._default_input_rvt_folder = os.path.join(self.home_folder, "Input_models")
        self._default_output_ifc_folder = os.path.join(self.home_folder, "Output")
        self._default_mappings_folder = os.path.join(self.home_folder, "IFCMapping")
        self._default_config_pset_folder = os.path.join(self.home_folder, "IFCPsets")
        self._default_config_ifcsettings_folder = os.path.join(self.home_folder, "IFCSettings")

        self.load_settings()

        output("IFC Export Innstillinger hentes fra: " + self.config_ifcsettings_folder)
        output("Lokale RVT filer hentes fra: " + self.input_rvt_folder)
        output("IFC filer lagres i: " + self.output_ifc_folder)
        output("IFC Mapping filer hentes fra: " + self.mappings_folder)
        output("IFC Pset filer hentes fra: " + self.config_pset_folder)
        output()

        self.check_settings()
        self.create_default_files()


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

        # norm = os.path.normpath

        def norm(apath):
            apath = os.path.normpath(apath)
            apath = apath.replace("\\", "/")
            apath = os.path.normpath(apath)
            return apath

        if not os.path.exists(self.av_autoexporter_settings_path):
            with codecs.open(self.av_autoexporter_settings_path, "w", encoding="utf-8") as f:
                f.write("{}")

        with codecs.open(self.av_autoexporter_settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)

            self.input_rvt_folder = norm(settings.setdefault("input_rvt_folder", self._default_input_rvt_folder))
            self.output_ifc_folder = norm(settings.setdefault("output_ifc_folder", self._default_output_ifc_folder))
            self.mappings_folder = norm(settings.setdefault("mappings_folder", self._default_mappings_folder))
            self.config_pset_folder = norm(settings.setdefault("config_pset_folder", self._default_config_pset_folder))
            self.config_ifcsettings_folder = norm(settings.setdefault("config_ifcsettings_folder", self._default_config_ifcsettings_folder))

        with codecs.open(self.av_autoexporter_settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, sort_keys=True)


    def check_settings(self):
        """ Sjekk at alle innstillinger er satt """
        if not os.path.exists(self.input_rvt_folder):
            raise Exception("Input RVT folder does not exist: " + self.input_rvt_folder)
        if not os.path.exists(self.output_ifc_folder):
            raise Exception("Output IFC folder does not exist: " + self.output_ifc_folder)
        if not os.path.exists(self.mappings_folder):
            raise Exception("Mappings folder does not exist: " + self.mappings_folder)
        if not os.path.exists(self.config_pset_folder):
            raise Exception("Pset folder does not exist: " + self.config_pset_folder)
        if not os.path.exists(self.config_ifcsettings_folder):
            raise Exception("IFCSettings folder does not exist: " + self.config_ifcsettings_folder)

    def create_default_files(self):

        batch_scripts_folder = BatchRvt.GetBatchRvtScriptsFolderPath()

        """ Create default mappings file """
        default_path = os.path.join(self.mappings_folder, "default.txt")
        if not os.path.exists(default_path):
            class_mapping_file = os.path.join(batch_scripts_folder, r"IFCDefaultSettings\default_class_mapping.txt")
            shutil.copy2(class_mapping_file, default_path)

        """ Create default psets file """
        default_path = os.path.join(self.config_pset_folder, "default.txt")
        if not os.path.exists(default_path):
            psets_file = os.path.join(batch_scripts_folder, r"IFCDefaultSettings\default_psets.txt")
            shutil.copy2(psets_file, default_path)
    #
        """ Create Default Json """
        default_path = os.path.join(self.config_ifcsettings_folder, "default.json")
        if not os.path.exists(default_path):
            ifc_settings_file = os.path.join(batch_scripts_folder, r"IFCDefaultSettings\default_ifc_exp_settings.json")
            shutil.copy2(ifc_settings_file, default_path)


class AVAutoExporterSettingsServer(AVAutoExporterSettings):

    def __init__(self, output):
        super(AVAutoExporterSettingsServer, self).__init__(output)
        output()
        output("---------------------- Serverinnstillinger --------------------------")
        norm = os.path.normpath
        op = os.path.join

        self.crawler_path_exe = norm(op(self.home_folder, "RServerCrawler.exe"))  # exe som crawler hele allle og hele rserver(kun de versjonene som er installert)
        self.crawler_server_paths_csv = norm(op(self.home_folder, "crawler_server_paths.csv"))  # csv fil som crawler genererer
        self.skip_download = None  # skip download av rvt filer
        # self.rvt_filtered_server_paths_txt = os.path.join(self.home_folder, "rvt_filtered_server_paths.txt")  # fil med prosjektfiler som er endret de siste 24 timer(eller hva det er satt til)
        self.error_paths_file = norm(op(self.home_folder, "error_paths.txt"))  # fil med baner til prosjektfiler som ikke kunne lastes ned

        self.force_refresh_csv_server_paths = None
        self.slett_alle_lokalfiler = None
        self.force_new_locals = None
        self.max_modell_age = None
        self.max_csv_age = None
        self.ignore_rvt_files_with_strings = None
        self.versions = None

        """ Private vars er default settings """
        self._force_refresh_csv_server_paths = False
        self._slett_alle_lokalfiler = False
        self._force_new_locals = True
        self._max_modell_age = 24
        self._max_csv_age = 8
        self._ignore_rvt_files_with_strings = ["_IFC_", "test ", "Oppstartsmodell", "_backup", "_ARKIV", "000000-00", "123456"]
        self._skip_download = False
        self._versions = []

        self.load_server_settings()

        output("Crawler exe (Henter baner fra Rserver): " + self.crawler_path_exe)
        output("Crawler csv (Banene den hentet): " + self.crawler_server_paths_csv)
        output("Error paths (Baner som tidligere ikke har fungert, bortkastet tid): " + self.error_paths_file)
        output("Force refresh csv (Lag ny csv selv om den ikke er gammel): " + str(self.force_refresh_csv_server_paths))
        output("Slett alle lokalfiler(Slett alle filer i input_rvt folder før nedlasting): " + str(self.slett_alle_lokalfiler))
        output("Force new locals (Lag nye localfiler selv om de eksisterer, bør være True): " + str(self.force_new_locals))
        output("Max modell age (Hent kun modeller syncronisert innen x antall timer): " + str(self.max_modell_age))
        output("Max csv age (Lag ny Crawler CSV hvis den er over x antall timer): " + str(self.max_csv_age))
        output("Ignore rvt files with strings (Hopp over filbaner som har en eller flere av disse i navnet): " + str(self.ignore_rvt_files_with_strings))
        output("Skip download (Hopp over nedlasting av rvt filer) er satt til: " + str(self.skip_download))
        output("Henter fra Serverversioner(Tom liste betyr hent alle innstallerte versioner): " + str(self.versions))
        output()

    def load_server_settings(self):
        """ Load settings from json file """
        with codecs.open(self.av_autoexporter_settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)  # type: dict

            self.force_refresh_csv_server_paths = settings.setdefault("force_refresh_csv_server_paths", self._force_refresh_csv_server_paths)
            self.slett_alle_lokalfiler = settings.setdefault("slett_alle_lokalfiler", self._slett_alle_lokalfiler)
            self.force_new_locals = settings.setdefault("force_new_locals", self._force_new_locals)
            self.max_modell_age = settings.setdefault("max_modell_age", self._max_modell_age)
            self.max_csv_age = settings.setdefault("max_csv_age", self._max_csv_age)
            self.ignore_rvt_files_with_strings = settings.setdefault("ignore_rvt_files_with_strings", self._ignore_rvt_files_with_strings)
            self.skip_download = settings.setdefault("skip_download", self._skip_download)
            self.versions = settings.setdefault("versions", self._versions)


        with codecs.open(self.av_autoexporter_settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, sort_keys=True)


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


def deactivate_all_addins(deactivatefoldername, output):

    """ Deactivate all addins in Revit. """
    output("Deaktiverer alle addins...")

    folderpaths = []
    try:
        AVClr.clr_batchrvtutil()
        import BatchRvtUtil

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
                        output("Deaktivert addin: " + addin_file_path)
    except Exception as ex:
        output("Kunne ikke deaktivere addins: " + str(ex))
    return folderpaths


def reactivate_all_addins(deactivatefoldername, Output):
    """ Reactivate all addins in Revit. """
    Output("Reactivering av addins...")

    try:
        AVClr.clr_batchrvtutil()
        import BatchRvtUtil

        allrevitversions = BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()

        for version in allrevitversions:
            for addinsfolder in [Environment.SpecialFolder.CommonApplicationData, Environment.SpecialFolder.ApplicationData]:
                folderpath = BatchRvtUtil.RevitVersion.GetRevitAddinsFolderPath(version, addinsfolder)
                subfolderpath = os.path.join(folderpath, deactivatefoldername)

                if os.path.exists(subfolderpath):
                    addin_files = [f for f in os.listdir(subfolderpath) if f.endswith('.addin')]
                    for addin_file in addin_files:
                        deactivated_file_path = os.path.join(subfolderpath, addin_file)
                        target_file_path = os.path.join(folderpath, addin_file)
                        if os.path.exists(target_file_path):
                            Output("Manifestfilen finnes fra før: {}\nSletter fra AVDeaktivert mappe: {}".format(target_file_path, deactivated_file_path))
                            os.remove(deactivated_file_path)
                            continue
                        Output("Flytter manifestfil fra: {}\nTil: {}".format(deactivated_file_path, target_file_path))
                        shutil.move(deactivated_file_path, folderpath)
                    if not os.listdir(subfolderpath):
                        Output("Sletter tom mappe: {}".format(subfolderpath))
                        os.rmdir(subfolderpath)
    except Exception as e:
        Output("Feil ved reaktivering av addins: {}".format(e))

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


class LocalFilesPath(object):
    """
    Filbane hentet fra lokal fil
    """

    def __init__(self, local_path):
        # "LocalPath", "IFCPath", "IFCpSets", "IFCMapping", "IFCSettings"
        super(LocalFilesPath, self).__init__()
        self.path = os.path.normpath(local_path.strip())

    def get_node_path(self, rvt_in_folder):
        node_path = self.path.replace(rvt_in_folder, "")
        node_path = node_path.lstrip("\\")
        return node_path

    def get_version_number(self):
        # return "Version"
        AVClr.clr_highest_revitapi(force=True)
        from Autodesk.Revit import DB
        fileinfo = DB.BasicFileInfo.Extract(self.path)
        return str(fileinfo.Format)

    def get_ifc_out_folder(self, ifc_out_folder, rvt_in_folder):
        node_path = self.get_node_path(rvt_in_folder)
        node_path = os.path.splitext(node_path)[0]  # fjern .rvt
        ifc_out_folder = os.path.join(ifc_out_folder, node_path)
        return ifc_out_folder

    def get_ifc_out_folder_version(self, ifc_out_folder, rvt_in_folder):
        node_path = self.get_node_path(rvt_in_folder)
        node_path = os.path.splitext(node_path)[0]  # fjern .rvt

        ifc_out_folder = os.path.join(ifc_out_folder, self.get_version_number())
        ifc_out_folder = os.path.join(ifc_out_folder, node_path)
        return ifc_out_folder

    @staticmethod
    def _get_default_settings_folder():
        batch_scripts_folder = BatchRvt.GetBatchRvtScriptsFolderPath()
        settings_folder = os.path.join(batch_scripts_folder, "IFCDefaultSettings")
        return settings_folder
    def get_default_settings_file(self):
        settings_folder = self._get_default_settings_folder()
        settings_file = os.path.join(settings_folder, "default_ifc_exp_settings.json")
        return settings_file

    def get_default_psets_file(self):
        settings_folder = self._get_default_settings_folder()
        settings_file = os.path.join(settings_folder, "default_psets.txt")
        return settings_file

    def get_default_mapping_file(self):
        settings_folder = self._get_default_settings_folder()
        settings_file = os.path.join(settings_folder, "default_class_mapping.txt")
        return settings_file

    # def get_ifc_psets_file(self, psets_folder):
    #     my_basename = os.path.basename(self.path)
    #     my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
    #     the_file = os.path.join(psets_folder, my_basename + ".txt")
    #     if not os.path.exists(the_file):
    #         the_file = os.path.join(psets_folder, "default.txt")
    #     assert os.path.exists(the_file)
    #     return the_file
    #
    # def get_ifc_mappings_file(self, mappings_folder):
    #     my_basename = os.path.basename(self.path)
    #     my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
    #     the_file = os.path.join(mappings_folder, my_basename + ".txt")
    #     if not os.path.exists(the_file):
    #         the_file = os.path.join(mappings_folder, "default.txt")
    #     assert os.path.exists(the_file)
    #     return the_file
    #
    # def get_ifc_settings_file(self, ifc_settings_folder):
    #     my_basename = os.path.basename(self.path)
    #     my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
    #     the_file = os.path.join(ifc_settings_folder, my_basename + ".json")
    #     if not os.path.exists(the_file):
    #         the_file = os.path.join(ifc_settings_folder, "default.json")
    #     assert os.path.exists(the_file)
    #     return the_file


def create_local_paths(folder_path, file_ending):
    # For ACC
    local_paths = []
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(file_ending):
                file_path = os.path.join(root, filename)
                local_paths.append(LocalFilesPath(file_path))
    return local_paths