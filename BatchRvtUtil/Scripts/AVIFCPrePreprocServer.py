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

""" Input\Output """
input_rvt_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\IFCWorkfolder\RVTLokalfiler"  # .rvt filer
output_ifc_folder = r"\\trondheim\AVTools\AutoIFC\IFCOut"  # .ifc filer
# output_ifc_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656\TESTFOLDER\testoutput"  # .ifc filer

""" IFC innstillinger """
mappings_folder = r"\\trondheim\AVTools\AutoIFC\IFCMapping" # .txt filer
config_pset_folder = r"\\trondheim\AVTools\AutoIFC\IFCPsets" # .txt filer
config_ifcsettings_folder = r"\\trondheim\AVTools\AutoIFC\IFCSettings" # Json filer

""" Hovedmappen for programmet """
main_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterRServer"
rvt_csv_file_list_path = os.path.join(main_folder, "rvt_csv_file_list.csv")

temp_tolder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterRServer\Temp"  # Midlertidige filer for programmet
""" Disse filene blir autogenerert av programmet """
rvt_file_list_path = os.path.join(temp_tolder, "rvt_file_list.txt")
rvt_temp_server_paths = os.path.join(temp_tolder, "rvt_temp_server_paths.txt")

""" Annet """
crawler_exe_path = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterRServer\RServerCrawler.exe"  # Henter alle baner fra Rserver
server_paths_csv = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterRServer\RserverSQL.csv"  # Lagrer alle baner fra Rserver

""" Hent alle baner fra Rserver """


def run_and_get_serverpaths(exe_path, csv_path, force_refresh=False):
    max_age = 8
    refresh = False
    """ Sjekk alder på csv filen """
    file_age_seconds = time.time() - os.path.getmtime(csv_path)
    file_age_hours = int(file_age_seconds / 3600)
    Output("CSV sist oppdatert for {0} timer siden...".format(file_age_hours))

    if force_refresh:
        Output("Baner må hentes på nytt fordi force_refresh er satt til True...")
        refresh = True
    elif file_age_hours > max_age:
        Output("CSV er over 8 timer gammel, henter nye baner...")
        refresh = True

    if refresh:
        process = SU.Popen([exe_path, "--output", csv_path], creationflags=SU.CREATE_NEW_CONSOLE)
        process.wait()
        if process.returncode != 0:
            print("Feilmelding ved kjøring av Rserver path-exe:\n{}".format(exe_path))
            sys.exit()
    pa = []
    with codecs.open(csv_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if row:
                server_path = avs.ServerPath(row[0])
                pa.append(server_path)
    return pa, refresh


def filtrer_ikke_installert(all_paths, output):
    # type: (list[avs.ServerPath], callable) -> list[avs.ServerPath]
    Output("Filtrerer bort baner hvor riktig Revitversion ikke er installert...")
    Output("Før filtrering: {}".format(len(all_paths)))
    suported = BatchRvtUtil.RevitVersion.GetInstalledRevitVersions()
    suported = [str(version) for version in suported]
    output("Støttede Revit versjoner på denne maskin: {}".format(",".join(suported)))
    supported_paths = []
    for pa in all_paths:
        path_version = pa.serverversion
        if any(path_version in v for v in suported):
            supported_paths.append(pa)
    Output("Etter filtrering: {}".format(len(supported_paths)))

    return supported_paths


def filtrer_inaktive(all_paths, output):
    # type: (list[avs.ServerPath], callable) -> list[avs.ServerPath]
    timeout = 24
    Output("Filtrerer bort modeller som ikke har vert aktiv i løpet av de siste {} timene...".format(timeout))
    Output("Før filtrering: {}".format(len(all_paths)))
    active_paths = []
    for pa in all_paths:
        if not os.path.exists(pa.path):
            Output("Finner ikke bane: {}".format(pa.path))
            continue
        hours_since_sync = pa.get_hours_since_modified()
        if hours_since_sync < timeout:
            active_paths.append(pa)
            output("Bane {}\ner aktiv og har vert synkronisert for {} timer siden".format(pa.path, str(hours_since_sync)))
    Output("Etter filtrering: {}".format(len(active_paths)))
    return active_paths


def download_rvt_files(server_paths, target_folder, output):
    output("Sletter filer under: {}".format(target_folder))
    shutil.rmtree(target_folder, ignore_errors=True)

    output("Laster ned RVT filer lokalt...")
    remaining = len(paths)
    for pa in server_paths:
        pa.create_local(target_folder, output)
        remaining -= 1
        output("Gjenstående: {} stk".format(str(remaining)))


FORCE_REFRESH_CSV_SERVER_PATHS = False
REFRESH_SERVER_PATHS_FILE = False
CREATE_NEW_LOCALS = False

""" Deaktiver alle addins som ikke er batchprocessor eller AVTools """
avf.deactivate_all_addins(output=Output)

""" Hent Rserverbaner (Tar Tid )"""
paths, refreshed = run_and_get_serverpaths(crawler_exe_path, server_paths_csv, force_refresh=FORCE_REFRESH_CSV_SERVER_PATHS)  # Denne sjekker om csv er over 8 timer gammel og lager ny om den er det
# Hvis baner er hentet på nytt, må vi også lage en ny filbane fil
if refreshed:
    REFRESH_SERVER_PATHS_FILE = True
if REFRESH_SERVER_PATHS_FILE:
    paths = filtrer_ikke_installert(paths, Output)  # Denne filterer vekk alle baner hvor riktig revit version ikke er installert
    paths = filtrer_inaktive(paths, Output)  # Denne filterer vekk alle baner som ikke har vert aktiv i løpet av de siste 24 timene

if REFRESH_SERVER_PATHS_FILE:
    Output("Lager fil med alle relevante baner fra Rserver...")
    paths = [path.path for path in paths]
    avf.create_paths_file(paths, rvt_temp_server_paths, Output)

""" Hent ServerPaths fra fil """
Output("Henter serverbaner fra temp fil...")
paths = avf.get_paths_from_file(rvt_temp_server_paths)

""" Last ned RVT filer lokalt """
if REFRESH_SERVER_PATHS_FILE:
    CREATE_NEW_LOCALS = True
if CREATE_NEW_LOCALS:
    download_rvt_files(paths, input_rvt_folder, Output)

# """ Create a file with all the paths to the rvt files in the folder and subfolders. """
# Output("Lager filbanefil...")
# avf.search_folder_create_file(input_rvt_folder, rvt_file_list_path, ".rvt")

def create_csv_file(csv_path, server_paths):
    # type: (str, list[avs.ServerPath]) -> None
    Output("Lager csv fil med alle baner...")
    with codecs.open(csv_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        # writer.writerow(["LocalPath", "ServerPath", "Date", "IFCPath", "IFCpSets", "IFCMapping", "IFCSettings", "Version"])
        for pa in server_paths:
            writer.writerow([pa.get_local_path(input_rvt_folder),
                             pa.path,
                             pa.get_last_modified(),
                             pa.get_ifc_outfolder(output_ifc_folder),
                             pa.get_ifc_psets_file(config_pset_folder),
                             pa.get_ifc_mappings_file(mappings_folder),
                             pa.get_ifc_settings_file(config_ifcsettings_folder),
                             pa.serverversion])

create_csv_file(rvt_csv_file_list_path, paths)
Output("Csv fil laget: {}".format(rvt_csv_file_list_path))
