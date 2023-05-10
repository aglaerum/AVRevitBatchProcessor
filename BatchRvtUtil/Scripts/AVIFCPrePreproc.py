# -*- coding: utf-8 -*-
import AVFunksjoner as avf
import codecs
import csv
from script_util import Output

#############################################
"""
Denne filen er for export av ACC prosjekter
"""
#############################################

exporter_settings = avf.AVAutoExporterSettings(Output)

""" Input\Output """
input_rvt_folder = exporter_settings.input_rvt_folder  # .rvt filer
output_ifc_folder = exporter_settings.output_ifc_folder  # .ifc filer

""" IFC innstillinger """
mappings_folder = exporter_settings.mappings_folder # .txt filer
config_pset_folder = exporter_settings.config_pset_folder # .txt filer
config_ifcsettings_folder = exporter_settings.config_ifcsettings_folder # Json filer
rvt_csv_file_list_path = exporter_settings.rvt_csv_file_list_path # .csv fil

""" Deaktiver alle addins som ikke er batchprocessor eller AVTools """
avf.deactivate_all_addins()

def create_csv_file(csv_path, local_paths):
    # type: (str, list[avf.PathFromFileACC]) -> None
    Output("Lager csv med filbaner for ACC...")
    with codecs.open(csv_path, "w", encoding="utf-8") as f:
    # with open(csv_path, "w") as f:
        writer = csv.writer(f, delimiter=";", lineterminator="\n")
        # "LocalPath", "IFCPath", "IFCpSets", "IFCMapping", "IFCSettings"
        for pa in local_paths:
            writer.writerow([pa.path,
                             pa.get_ifc_out_folder(output_ifc_folder, input_rvt_folder),
                             pa.get_ifc_psets_file(config_pset_folder),
                             pa.get_ifc_mappings_file(mappings_folder),
                             pa.get_ifc_settings_file(config_ifcsettings_folder)])

""" Henter lokale filer """
paths = avf.create_local_paths(input_rvt_folder, ".rvt")

create_csv_file(rvt_csv_file_list_path, paths)
Output("Csv fil for ACC laget: {}".format(rvt_csv_file_list_path))

Output(avf.get_home_folder())