# -*- coding: utf-8 -*-

import os
import re
import traceback

import AVClr
import subprocess as SU


def get_revit_file_version(path):
    # type: (str) -> str
    if path.startswith(r"\\"):
        version = get_RserverVersion(path)
        return version
    else:
        AVClr.clr_highest_revitapi(force=True)
        from Autodesk.Revit import DB
        fileinfo = DB.BasicFileInfo.Extract(path)
        return str(fileinfo.Format)

def get_nodepath(unc_path):
    """ Get the subfolder name for the projects folder """
    components = unc_path.split(os.sep)
    projects_index = components.index('Projects')
    projects_path = os.path.join(*components[projects_index + 1:])
    return projects_path.strip()


def get_RserverVersion(unc_path):
    try:
        # Get the version number using regex from a string like \Revit Server 2022\
        res = re.search(r"\\Revit Server (\d+)\\", unc_path, flags=re.IGNORECASE)
        return str(res.group(1))
    except Exception as e:
        traceback.print_exc()
        return None

def get_RserverName(unc_path):
    path_split = os.path.splitunc(unc_path)
    firstpart = path_split[0]
    # Get the name of the server using regex from a string like \\av-revit1\Autodesk
    res = re.search(r"\\\\(.*)\\", firstpart, flags=re.IGNORECASE)
    return str(res.group(1))


class ServerPath(object):
    def __init__(self, path):
        super(ServerPath, self).__init__()
        self.path = os.path.normpath(path).strip()
        self._servername = None
        self._serverversion = None
        self._serverstart = None
        self._rsn_path = None
        self._server_node_path = None
        self._rserver = None

    # def get_rserver(self):
    #     import rpws
    #     if self._rserver is None:
    #         self._rserver = rpws.RevitServer(self.servername, self.serverversion)
    #         assert self._rserver.version == self.serverversion
    #     return self._rserver

    @property
    def servername(self):
        if self._servername is None:
            self._servername = get_RserverName(self.path)
        return self._servername

    @property
    def serverversion(self):
        if self._serverversion is None:
            self._serverversion = get_RserverVersion(self.path)
        return self._serverversion

    @property
    def server_node_path(self):
        if self._server_node_path is None:
            self._server_node_path = get_nodepath(self.path)
        return self._server_node_path

    def get_ifc_out_folder(self, local_ifc_folder):
        server_node_path = self.server_node_path
        local_path = os.path.join(local_ifc_folder, server_node_path)
        local_path = os.path.dirname(local_path)
        return local_path.strip()

    # def get_last_modified(self):
    #
    #     server = self.get_rserver()
    #     modified = server.getmodelinfo(self.server_node_path)  # type: rpws.server.models.ModelInfoEx
    #     modified = modified.date_modified
    #     return modified

    # def get_hours_since_modified(self):
    #     modified = self.get_last_modified()
    #     hours = (datetime.datetime.now() - modified).total_seconds() / 3600
    #     return int(hours)

    def get_rservertool(self):
        AVClr.clr_batchrvtutil()
        import batch_rvt_util
        tail_path = "RevitServerToolCommand\RevitServerTool.exe"
        supported_version = batch_rvt_util.RevitVersion.GetSupportedRevitVersion(self.serverversion)
        revit_installation = batch_rvt_util.RevitVersion.GetRevitExecutableFolderPath(supported_version)
        rservertool_path = os.path.join(revit_installation, tail_path)
        assert os.path.exists(rservertool_path)
        return rservertool_path

    def get_local_path(self, local_rvt_folder):
        server_node_path = self.server_node_path
        local_path = os.path.join(local_rvt_folder, server_node_path)
        return local_path.strip()

    def create_local(self, local_folder, output):
        # type: (ServerPath, function) -> None
        central_path = self.server_node_path
        server_name = self.servername
        local_rvt_path = self.get_local_path(local_folder)

        dest_folder = os.path.dirname(local_rvt_path)
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        rserver_tool = self.get_rservertool()
        output("Laster ned:\n{}\ntil:\n{}".format(self.path, local_rvt_path))
        args = [rserver_tool, "createLocalRVT", central_path, "-s", server_name, "-d", local_rvt_path, "-o"]
        # shell = subprocess.check_output(args, shell=True)  # output(shell)
        process = SU.Popen(args, creationflags=SU.CREATE_NEW_CONSOLE)
        process.wait()

        if process.returncode != 0:
            # Output(process.)
            raise Exception("Feilmelding ved kjøring av Downloader exe:\n{}".format(rserver_tool))

    def get_ifc_psets_file(self, psets_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
        the_file = os.path.join(psets_folder, my_basename + ".txt")
        if not os.path.exists(the_file):
            the_file = os.path.join(psets_folder, "default.txt")
        assert os.path.exists(the_file)
        return the_file.strip()

    def get_ifc_mappings_file(self, mappings_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
        the_file = os.path.join(mappings_folder, my_basename + ".txt")
        if not os.path.exists(the_file):
            the_file = os.path.join(mappings_folder, "default.txt")
        assert os.path.exists(the_file)
        return the_file.strip()

    def get_ifc_settings_file(self, ifc_settings_folder):
        my_basename = os.path.basename(self.path)
        my_basename = os.path.splitext(my_basename)[0]  # fjern .rvt
        the_file = os.path.join(ifc_settings_folder, my_basename + ".json")
        if not os.path.exists(the_file):
            the_file = os.path.join(ifc_settings_folder, "default.json")
        assert os.path.exists(the_file)
        return the_file.strip()
