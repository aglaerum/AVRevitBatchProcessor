# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
import AVClr
AVClr.clr_batchrvtutil()
import AVFunksjoner as avf
import AVServerFuncs as avs
import codecs
import csv
import os
import subprocess as SU
import time
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

        if not os.path.exists(csv_path):
            with open(csv_path, "w") as f:
                f.write("")
        versions = [str(x) for x in avf.get_installed_revit_versions()]
        # versions = ["2023"]

        args = [exe_path, "--output", csv_path, "--versions", ",".join(versions)]

        if max_model_age:
            args = [exe_path,
                                "--output", csv_path,
                                "--hours_since_edit", str(max_model_age),
                                "--versions", ",".join(versions)]

        # process = SU.Popen(args, creationflags=SU.CREATE_NEW_CONSOLE, stdout=SU.PIPE, stderr=SU.PIPE)
        # stdout, stderr = process.communicate()
        # process.wait()
        # if process.returncode != 0:
        #     error_message = stderr.decode("utf-8")
        #     # Do something with the error message, e.g. print it
        #     print("Error message:\n", error_message)

        process = SU.Popen(args, creationflags=SU.CREATE_NEW_CONSOLE)
        process.wait()

        if process.returncode != 0:
            # Output(process.)
            raise Exception("Feilmelding ved kjøring av Rserver path-exe:\n{}".format(exe_path))

    pa = []
    with codecs.open(csv_path, "rb") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # skip header
        for row in reader:
            if row:
                server_path = avs.ServerPath(row[0])
                pa.append(server_path)
    return pa, refresh


def download_rvt_files(s_paths, target_folder, output, del_existing=False):
    if del_existing:
        output("Sletter filer under: {}".format(target_folder))
        shutil.rmtree(target_folder, ignore_errors=True)

    output("Laster ned RVT filer lokalt...")
    remaining = len(s_paths)
    for pa in server_paths:
        pa.create_local(target_folder, output)
        remaining -= 1
        output("Gjenstående: {} stk".format(str(remaining)))


FORCE_REFRESH_CSV_SERVER_PATHS = True
CREATE_NEW_LOCALS = True
MAX_MODELL_AGE = 24

""" Deaktiver alle addins som ikke er batchprocessor eller AVTools """
avf.deactivate_all_addins(output=Output)

""" Hent Rserverbaner (Tar Tid )"""
server_paths, refreshed = run_and_get_serverpaths(crawler_exe_path, crawler_server_paths_csv, force_refresh=FORCE_REFRESH_CSV_SERVER_PATHS, max_model_age=MAX_MODELL_AGE)

""" Last ned RVT filer lokalt """
if CREATE_NEW_LOCALS or refreshed:
    download_rvt_files(server_paths, input_rvt_folder, Output)

def create_csv_file(csv_path, lo_paths):
    # type: (str, list[avs.ServerPath]) -> None
    Output("Lager csv med filbaner for Rserver...")
    with codecs.open(csv_path, "w", encoding="utf-8") as f:
    # with open(csv_path, "w") as f:
        writer = csv.writer(f, delimiter=";", lineterminator="\n")
        # "LocalPath", "IFCPath", "IFCpSets", "IFCMapping", "IFCSettings"
        for pa in lo_paths:
            writer.writerow([pa.get_local_path(input_rvt_folder),
                             pa.path,
                             pa.get_ifc_out_folder(output_ifc_folder),
                             pa.get_ifc_psets_file(config_pset_folder),
                             pa.get_ifc_mappings_file(mappings_folder),
                             pa.get_ifc_settings_file(config_ifcsettings_folder)])

create_csv_file(rvt_csv_file_list_path, server_paths)
Output("Csv fil laget: {}".format(rvt_csv_file_list_path))