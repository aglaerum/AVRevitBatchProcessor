# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
import AVClr
AVClr.clr_batchrvtutil()
import AVFunksjoner as avf
import AVServerFuncs as avs
import BatchRvtUtil
import codecs
import csv
import os
import subprocess as SU
import time
import sys
import shutil
from script_util import Output

#############################################
"""
Denne filen er for export av Rserver prosjekter
"""
#############################################

exporter_settings = avf.AVAutoExporterSettingsServer(Output)

""" Input\Output """
input_rvt_folder = exporter_settings.input_rvt_folder  # .rvt filer
output_ifc_folder = exporter_settings.output_ifc_folder  # .ifc filer

""" IFC innstillinger """
mappings_folder = exporter_settings.mappings_folder # .txt filer
config_pset_folder = exporter_settings.config_pset_folder # .txt filer
config_ifcsettings_folder = exporter_settings.config_ifcsettings_folder # Json filer
rvt_csv_file_list_path = exporter_settings.rvt_csv_file_list_path # .csv fil

# """ Rserver innstillinger """
crawler_exe_path = exporter_settings.crawler_path_exe  # exe som crawler hele allle og hele rserver(kun de versjonene som er installert)
crawler_server_paths_csv = exporter_settings.crawler_server_paths_csv  # csv fil som crawler genererer
rvt_filtered_server_paths_txt = exporter_settings.rvt_filtered_server_paths_txt  # fil med prosjektfiler som er endret de siste 24 timer(eller hva det er satt til)

def run_and_get_serverpaths(exe_path, csv_path, force_refresh=False, max_csv_age=8, max_model_age=None):

    refresh = False

    if not os.path.exists(csv_path):
        Output("CSV filen eksisterer ikke, henter nye baner...")
        refresh = True
    else:
        """ Sjekk alder på csv filen """
        file_age_seconds = time.time() - os.path.getmtime(csv_path)
        file_age_hours = int(file_age_seconds / 3600)
        Output("CSV sist oppdatert for {0} timer siden...".format(file_age_hours))

        if force_refresh:
            Output("Baner må hentes på nytt fordi force_refresh er satt til True...")
            refresh = True
        elif file_age_hours > max_csv_age:
            Output("CSV er over {} timer gammel, henter nye baner...".format(str(max_csv_age)))
            refresh = True

    if refresh:
        args = [exe_path, "--output", csv_path, "--versions", ",".join(str(x) for x in avf.get_installed_revit_versions())]

        if max_model_age:
            args = [exe_path,
                                "--output", csv_path,
                                "--hours_since_edit", str(max_model_age),
                                "--versions", ",".join(str(x) for x in avf.get_installed_revit_versions())]

        process = SU.Popen(args, creationflags=SU.CREATE_NEW_CONSOLE)

        process.wait()
        if process.returncode != 0:
            print("Feilmelding ved kjøring av Rserver path-exe:\n{}".format(exe_path))
            sys.exit()
    pa = []
    with codecs.open(csv_path, "rb") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # skip header
        for row in reader:
            if row:
                server_path = avs.ServerPath(row[0])
                pa.append(server_path)
    return pa, refresh


# def filtrer_ikke_installert(all_paths, output):
#     # type: (list[avs.ServerPath], callable) -> list[avs.ServerPath]
#     Output("Filtrerer bort baner hvor riktig Revitversion ikke er installert...")
#     Output("Før filtrering: {}".format(len(all_paths)))
#     suported = BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()
#     suported = [str(version) for version in suported]
#     output("Støttede Revit versjoner på denne maskin: {}".format(",".join(suported)))
#     supported_paths = []
#     for pa in all_paths:
#         path_version = pa.serverversion
#         if any(path_version in v for v in suported):
#             supported_paths.append(pa)
#     Output("Etter filtrering: {}".format(len(supported_paths)))
#
#     return supported_paths


# def filtrer_inaktive(all_paths, output):
#     # type: (list[avs.ServerPath], callable) -> list[avs.ServerPath]
#
#     timeout = 24
#     Output("Filtrerer bort modeller som ikke har vert aktiv i løpet av de siste {} timene...".format(timeout))
#     Output("Før filtrering: {}".format(len(all_paths)))
#     active_paths = []
#
#     for pa in all_paths:
#         if not os.path.exists(pa.path):
#             Output("Finner ikke bane: {}".format(pa.path))
#             continue
#         hours_since_sync = pa.get_hours_since_modified()
#         if hours_since_sync < timeout:
#             active_paths.append(pa)
#             output("Bane {}\ner aktiv og har vert synkronisert for {} timer siden".format(pa.path, str(hours_since_sync)))
#     Output("Etter filtrering: {}".format(len(active_paths)))
#     return active_paths


def download_rvt_files(s_paths, target_folder, output, del_existing=False):
    if del_existing:
        output("Sletter filer under: {}".format(target_folder))
        shutil.rmtree(target_folder, ignore_errors=True)

    output("Laster ned RVT filer lokalt...")
    remaining = len(s_paths)
    for pa in server_paths:
        output(pa)
        pa.create_local(target_folder, output)
        remaining -= 1
        output("Gjenstående: {} stk".format(str(remaining)))


FORCE_REFRESH_CSV_SERVER_PATHS = True
# REFRESH_BUFFERFILE = True
CREATE_NEW_LOCALS = False

""" Deaktiver alle addins som ikke er batchprocessor eller AVTools """
avf.deactivate_all_addins(output=Output)

""" Hent Rserverbaner (Tar Tid )"""
server_paths, refreshed = run_and_get_serverpaths(crawler_exe_path, crawler_server_paths_csv, force_refresh=FORCE_REFRESH_CSV_SERVER_PATHS)  # Denne sjekker om csv er over 8 timer gammel og lager ny om den er det

""" Dette gjøres for å spare tid ved testing """
# if not os.path.exists(rvt_filtered_server_paths_txt):
#     REFRESH_BUFFERFILE = True
# if REFRESH_BUFFERFILE or refreshed:
#     refreshed = True
#     Output("--------------- Lager bufferfil fil med alle relevante baner fra Rserver... ------------------")
    # server_paths = filtrer_ikke_installert(server_paths, Output)  # Denne filterer vekk alle baner hvor riktig revit version ikke er installert
    # server_paths = filtrer_inaktive(server_paths, Output)  # Denne filterer vekk alle baner som ikke har vert aktiv i løpet av de siste 24 timene
    # server_paths = [path.path for path in server_paths]
    # avf.create_temp_paths_file(server_paths, rvt_filtered_server_paths_txt, Output)

# Output("Henter serverbaner fra temp fil...")
# temp_server_paths = avf.get_paths_from_file(rvt_filtered_server_paths_txt)
# Output("Antall baner fra bufferfil: {}".format(len(temp_server_paths)))

server_paths = server_paths[:2]

""" Last ned RVT filer lokalt """
if CREATE_NEW_LOCALS or refreshed:
    download_rvt_files(server_paths, input_rvt_folder, Output)
    # download_rvt_files(temp_server_paths, input_rvt_folder, Output)

Output("Crawler download folder...")
local_paths = avf.create_local_paths(input_rvt_folder, ".rvt")

def create_csv_file(csv_path, lo_paths):
    # type: (str, list[avf.PathFromFileACC]) -> None
    Output("Lager csv med filbaner for ACC...")
    with codecs.open(csv_path, "w", encoding="utf-8") as f:
    # with open(csv_path, "w") as f:
        writer = csv.writer(f, delimiter=";", lineterminator="\n")
        # "LocalPath", "IFCPath", "IFCpSets", "IFCMapping", "IFCSettings"
        for pa in lo_paths:
            writer.writerow([pa.path,
                             pa.get_ifc_out_folder(output_ifc_folder, input_rvt_folder),
                             pa.get_ifc_psets_file(config_pset_folder),
                             pa.get_ifc_mappings_file(mappings_folder),
                             pa.get_ifc_settings_file(config_ifcsettings_folder)])

create_csv_file(rvt_csv_file_list_path, local_paths)
Output("Csv fil laget: {}".format(rvt_csv_file_list_path))