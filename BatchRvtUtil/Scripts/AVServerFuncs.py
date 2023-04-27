# -*- coding: utf-8 -*-

import os
import re
import traceback

import batch_rvt_util
import rpws
import datetime
import subprocess
from Autodesk.Revit import DB


RSERVER_MAX_NAME_LEN = 40  # max for modellnavn
RSERVER_MAX_FOLDER_LEN = 110  # max for mappenavn


TEMPLATE_MAPPE = "ikke bruk"
revit_lokalfiler = "Revit Lokalfiler"  # mappe på egen disk

def get_outputfolder(source_path, output_ifc_folder, output):
    """ Get output folder for the ifc file. """

    node_path = get_nodepath(source_path)
    ifc_folder = os.path.join(output_ifc_folder, node_path)
    ifc_folder = os.path.dirname(ifc_folder)
    return ifc_folder

    # node_path = avsf.get_nodepath(source_path)
    # source_path = os.path.dirname(source_path)
    #
    # relative_input_path = os.path.relpath(source_path, input_rvt_folder)
    # output_folder_path = os.path.join(output_ifc_folder, relative_input_path)
    # if not os.path.exists(output_folder_path):
    #     os.makedirs(output_folder_path)
    # return output_folder_path

def get_revit_file_version(path):
    # type: (str) -> str
    if path.startswith(r"\\"):
        version = get_RserverVersion(path)
        return version
    else:
        fileinfo = DB.BasicFileInfo.Extract(path)
        return str(fileinfo.Format)

def get_rserverstart(unc_path):
    server_name = get_RserverName(unc_path)
    RSERVER_START = r"RSN://{}".format(unicode(server_name))
    return RSERVER_START


def get_full_rsn_path(unc_path):
    """ Get the full path to the model on the server """
    projsubfolder = get_nodepath(unc_path)
    rserverstart = get_rserverstart(unc_path)
    full_path = os.path.join(rserverstart, projsubfolder)
    assert DB.ModelPathUtils.IsValidUserVisibleFullServerPath(full_path)
    fullpath = DB.ModelPathUtils.ConvertUserVisiblePathToModelPath(full_path)
    user_visible = DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(fullpath)
    return unicode(user_visible)


def get_nodepath(unc_path):
    """ Get the subfolder name for the projects folder """
    components = unc_path.split(os.sep)
    projects_index = components.index('Projects')
    projects_path = os.path.join(*components[projects_index + 1:])
    return projects_path

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
        self.path = os.path.normpath(unicode(path).strip())
        self._servername = None
        self._serverversion = None
        self._serverstart = None
        self._rsn_path = None
        self._server_node_path = None
        self._rserver = None

    def get_rserver(self):
        if self._rserver is None:
            self._rserver = rpws.RevitServer(self.servername, self.serverversion)
            assert self._rserver.version == self.serverversion
        return self._rserver

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
    def serverstart(self):
        if self._serverstart is None:
            self._serverstart = get_rserverstart(self.path)
        return self._serverstart

    @property
    def rsn_path(self):
        if self._rsn_path is None:
            self._rsn_path = get_full_rsn_path(self.path)
        return self._rsn_path

    @property
    def server_node_path(self):
        if self._server_node_path is None:
            self._server_node_path = get_nodepath(self.path)
        return self._server_node_path

    def get_last_modified(self):
        server = self.get_rserver()
        modified = server.getmodelinfo(self.server_node_path)  # type: rpws.server.models.ModelInfoEx
        modified = modified.date_modified
        return modified

    def get_hours_since_modified(self):
        modified = self.get_last_modified()
        hours = (datetime.datetime.now() - modified).total_seconds() / 3600
        return int(hours)

    def get_rservertool(self):
        tail_path = "RevitServerToolCommand\RevitServerTool.exe"
        supported_version = batch_rvt_util.RevitVersion.GetSupportedRevitVersion(self.serverversion)
        revit_installation = batch_rvt_util.RevitVersion.GetRevitExecutableFolderPath(supported_version)
        rservertool_path = os.path.join(revit_installation, tail_path)
        assert os.path.exists(rservertool_path)
        return rservertool_path

    def get_local_path(self, local_rvt_folder):
        server_node_path = self.server_node_path
        local_path = os.path.join(local_rvt_folder, server_node_path)
        return local_path

    def create_local(self, local_folder, output):
        # type: (ServerPath, function) -> str
        central_path = self.server_node_path
        server_name = self.servername
        local_rvt_path = self.get_local_path(local_folder)

        dest_folder = os.path.dirname(local_rvt_path)
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        rserver_tool = self.get_rservertool()
        output("Laster ned:\n{}\ntil:\n{}".format(self.path, local_rvt_path))
        args = [rserver_tool, "createLocalRVT", central_path, "-s", server_name, "-d", local_rvt_path, "-o"]
        shell = subprocess.check_output(args, shell=True)
        # output(shell)