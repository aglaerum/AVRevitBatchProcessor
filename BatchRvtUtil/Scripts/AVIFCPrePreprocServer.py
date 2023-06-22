# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
import AVClr
AVClr.clr_batchrvtutil()
import AVFunksjoner as avf
import AVServerFuncs as avs
import AVPathsAndSettings as avps
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

# todo: Legg til mulighet for å fjerne visse ting som for eksempel modeller som slutter med "_IFC_"
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
skip_download = exporter_settings.skip_download  # True/False

def run_and_get_serverpaths(exe_path, csv_path, force_refresh=False, max_csv_age=8, max_model_age=None, versions=None):

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

        if not versions:
            versions = avf.get_installed_revit_versions()

        versions = [str(v) for v in versions]
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
                server_path = avs.ServerPath(row[0], local_rvt_folder=input_rvt_folder)
                pa.append(server_path)
    return pa, refresh


def download_rvt_files(s_paths, target_folder, output, del_existing=False, make_new=True):

    suksess_files = []

    if del_existing:
        output("Sletter filer under: {}".format(target_folder))
        shutil.rmtree(target_folder, ignore_errors=True)

    output("Laster ned RVT filer lokalt...")
    remaining = len(s_paths)
    for pa in server_paths:
        output("Gjenstående: {} stk".format(str(remaining)))
        if not make_new and pa.local_exists:
            output("Fil eksisterer allerede lokalt, hopper over: {}".format(pa.local_path))
            suksess_files.append(pa)
            remaining -= 1
            continue

        pa.create_local(output)
        remaining -= 1

        if not pa.local_exists:
            append_to_error_paths_file(pa.path, output)
            continue
        suksess_files.append(pa)

    return suksess_files

def append_to_error_paths_file(path, output):
    try:
        with codecs.open(exporter_settings.error_paths_file, "a", encoding="utf-8") as f:
            f.write(path + "\n")
            output("Bane skrevet til errorfil: {}".format(path))
    except Exception as e:
        output("Kunne ikke skrive til errorfil:\n{}".format(e.message))

def path_is_in_errorfile(path):
    if not os.path.exists(exporter_settings.error_paths_file):
        return False

    with codecs.open(exporter_settings.error_paths_file, "r", encoding="utf-8") as f:
        for line in f:
            if os.path.normpath(line.strip()) == os.path.normpath(path):
                Output("Bane er i errorfil, fjernes: {}".format(path))
                return True
    return False

def filter_ignore_paths(paths, settings_class, output):
    # type: (list[avs.ServerPath], avf.AVAutoExporterSettingsServer, callable) -> list[avs.ServerPath]
    out = []
    for pa in paths:
        if pa.skal_ignoreres(settings_class.ignore_rvt_files_with_strings):
            output("Bane ignoreres: {}".format(pa.path))
            continue
        out.append(pa)
    return out

def create_csv_file(csv_path, lo_paths):
    # type: (str, list[avs.ServerPath]) -> None
    Output("Lager csv med filbaner for Rserver...")
    with codecs.open(csv_path, "w", encoding="utf-8") as f:
    # with open(csv_path, "w") as f:
        writer = csv.writer(f, delimiter=";", lineterminator="\n")
        # "LocalPath", "IFCPath", "IFCpSets", "IFCMapping", "IFCSettings"
        for pa in lo_paths:
            row = [pa.local_path,
                             pa.path,
                             pa.get_ifc_out_folder(output_ifc_folder),
                             pa.get_ifc_psets_file(config_pset_folder),
                             pa.get_ifc_mappings_file(mappings_folder),
                             pa.get_ifc_settings_file(config_ifcsettings_folder)]
            writer.writerow(row)

def clean_csv_file(csv_path):
    # type: (str) -> None
    Output("Fjerner baner som ikke eksisterer lokalt fra csv...")
    with codecs.open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";", lineterminator="\n")
        rows = [row for row in reader if os.path.exists(row[0])]

    with codecs.open(csv_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";", lineterminator="\n")
        writer.writerows(rows)


FORCE_REFRESH_CSV_SERVER_PATHS = exporter_settings.force_refresh_csv_server_paths
SLETT_ALLE_LOKALFILER = exporter_settings.slett_alle_lokalfiler
FORCE_NEW_LOCALS = exporter_settings.force_new_locals
MAX_MODELL_AGE = exporter_settings.max_modell_age
MAX_CSV_AGE = exporter_settings.max_csv_age
VERSIONS = exporter_settings.versions

""" Deaktiver alle addins som ikke er batchprocessor eller AVTools """
avf.deactivate_all_addins(deactivatefoldername=avps.addin_deactivate_foldername,output=Output)

""" Hent Rserverbaner (Tar Tid )"""
server_paths, refreshed = run_and_get_serverpaths(crawler_exe_path, crawler_server_paths_csv, force_refresh=FORCE_REFRESH_CSV_SERVER_PATHS, max_csv_age=MAX_CSV_AGE, max_model_age=MAX_MODELL_AGE, versions=VERSIONS)  # type: list[avs.ServerPath], bool

""" Filterer baner som er definert i settings fil at skal ignoreres """
server_paths = filter_ignore_paths(server_paths, exporter_settings, Output)

""" Filtrer bort baner som tidligere ikke har latt seg laste ned """
server_paths = filter(lambda pa: not path_is_in_errorfile(pa.path), server_paths)

""" Lag CSV fil """
create_csv_file(rvt_csv_file_list_path, server_paths)
Output("Csv fil laget: {}".format(rvt_csv_file_list_path))

""" Last ned RVT filer lokalt """

if refreshed:
    FORCE_NEW_LOCALS = True
if not skip_download:
    Output("Starter nedlasting av RVT filer lokalt...")
    server_paths = download_rvt_files(server_paths, input_rvt_folder, Output, make_new=FORCE_NEW_LOCALS, del_existing=SLETT_ALLE_LOKALFILER)
    Output("Lokale RVT filer lastet ned: {}".format(len(server_paths)))

if skip_download:
    Output("Skipper nedlasting av RVT filer lokalt i henhold til innstillinger for AutoExporter")

for x in server_paths:
    if not x.local_exists:
        Output("#################### Fil eksisterer ikke lokalt: {} ########################".format(x.local_path))
clean_csv_file(rvt_csv_file_list_path)
