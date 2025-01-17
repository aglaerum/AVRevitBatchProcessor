# -*- coding: utf-8 -*-

""" Midlertidig bane for deaktivering av addins """

addin_deactivate_foldername = "AVDeaktivert"

# def read_config_file(config_file):
#     config = ConfigParser.ConfigParser()
#
#     # set default values
#     main_volo_folder = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656\TESTFOLDER"
#
#     input_rvt_folder_def = os.path.join(main_volo_folder, r"Input_models")
#     output_ifc_folder_def = os.path.join(main_volo_folder, "Output AG")
#     mappings_folder_def = os.path.join(main_volo_folder, "FamilymappingFile")
#     config_pset_folder_def = os.path.join(main_volo_folder, "Input_configs")
#     main_config_folder_def = r"C:\Users\andreas.glarum\OneDrive - Asplan Viak\RevitBatchProsessor\ExporterAV3656"
#
#     # check if configuration file exists
#     if not os.path.isfile(config_file):
#         # write configuration file with default values
#         config.add_section('Folders')
#         config.set('Folders', 'input_rvt_folder', input_rvt_folder_def)
#         config.set('Folders', 'output_ifc_folder', output_ifc_folder_def)
#         config.set('Folders', 'mappings_folder', mappings_folder_def)
#         config.set('Folders', 'config_pset_folder', config_pset_folder_def)
#
#         config.add_section('Paths')
#         config.set('Paths', 'main_config_folder', main_config_folder_def)
#         config.set('Paths', 'rvt_file_list_path', os.path.join(main_config_folder_def, "rvt_file_list.txt"))
#         config.set('Paths', 'psets_paths_path', os.path.join(main_config_folder_def, "pSets_Paths.txt"))
#         config.set('Paths', 'mapping_paths_path', os.path.join(main_config_folder_def, "mapping_paths.txt"))
#         config.set('Paths', 'generated_paths_and_settings_path', os.path.join(main_config_folder_def, "generated_paths_and_settings.csv"))
#
#         config.add_section('Addin')
#         config.set('Addin', 'addin_deactivate_foldername', 'AVDeaktivert')
#
#         with open(config_file, 'w') as configfile:
#             config.write(configfile)
#
#     # read configuration file
#     config.read(config_file)
#
#     # check if values exist in the config file, otherwise set default values
#     input_rvt_folder = config.get('Folders', 'input_rvt_folder', fallback=input_rvt_folder_def)
#     output_ifc_folder = config.get('Folders', 'output_ifc_folder', fallback=output_ifc_folder_def)
#     mappings_folder = config.get('Folders', 'mappings_folder', fallback=mappings_folder_def)
#     config_pset_folder = config.get('Folders', 'config_pset_folder', fallback=config_pset_folder_def)
#
#     main_config_folder = config.get('Paths', 'main_config_folder', fallback=main_config_folder_def)
#     rvt_file_list_path = config.get('Paths', 'rvt_file_list_path', fallback=os.path.join(main_config_folder_def, "rvt_file_list.txt"))
#     psets_paths_path = config.get('Paths', 'psets_paths_path', fallback=os.path.join(main_config_folder_def, "pSets_Paths.txt"))
#     mapping_paths_path = config.get('Paths', 'mapping_paths_path', fallback=os.path.join(main_config_folder_def, "mapping_paths.txt"))
#     generated_paths_and_settings_path = config.get('Paths', 'generated_paths_and_settings_path', fallback=os.path.join(main_config_folder_def, "generated_paths_and_settings.csv"))
#     addin_deactivate_foldername = config.get('Addin', 'addin_deactivate_foldername', fallback='AVDeaktivert')
#
#     return input_rvt_folder, output_ifc_folder, mappings_folder, config_pset_folder, main_config_folder, rvt_file_list_path, psets_paths_path, mapping_paths_path, generated_paths_and_settings_path, addin_deactivate_foldername
#
#
#
# input_rvt_folder_global,\
#     output_ifc_folder_global,\
#     mappings_folder_global,\
#     config_pset_folder_global,\
#     main_config_folder_global,\
#     rvt_file_list_path_global,\
#     psets_paths_path_global,\
#     mapping_paths_path_global,\
#     generated_paths_and_settings_path_global,\
#     addin_deactivate_foldername_global = read_config_file(config_file)
