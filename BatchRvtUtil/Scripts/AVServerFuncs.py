# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime
import os.path as op
import time
import AVFunksjoner as avf
avf.clr_highest_revitapi()
from Autodesk.Revit import DB
import rpws

RSERVER_MAX_NAME_LEN = 40  # max for modellnavn
RSERVER_MAX_FOLDER_LEN = 110  # max for mappenavn

""" Baner """
# httpRserverAdmin = "http://av-revit1/RevitServeradmin{}/".format(str(HOST_APP.version))


TEMPLATE_MAPPE = "ikke bruk"
revit_lokalfiler = "Revit Lokalfiler"  # mappe på egen disk


# def get_rserverstart(version):
#     RSERVER_START = r"RSN://av-revit1"
#     """ It skiftet servernavn fra 2022 version, skal fungere fremover med mindre de endrer servernavn"""
#     if int(version) >= 2022:
#         RSERVER_START = r"RSN://AV-Revit{}".format(str(version))
#     return RSERVER_START

# def get_rserverstart(version):
#     RSERVER_START = r"RSN://av-revit1"
#     """ It skiftet servernavn fra 2022 version, skal fungere fremover med mindre de endrer servernavn"""
#     if int(version) >= 2022:
#         RSERVER_START = r"RSN://AV-Revit{}".format(str(version))
#     return RSERVER_START

def get_rserverstart(unc_path):
    server_name = get_RserverName(unc_path)
    RSERVER_START = r"RSN://{}".format(unicode(server_name))
    return RSERVER_START

# def NodeToFullServerPath(unc_path):
#
#     serverversion = get_RserverVersion(unc_path)
#     rserverstart = get_rserverstart(unc_path)
#     full_path = os.path.join(rserverstart, node_path)
#     assert DB.ModelPathUtils.IsValidUserVisibleFullServerPath(full_path)
#     fullpath = DB.ModelPathUtils.ConvertUserVisiblePathToModelPath(full_path)
#     return DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(fullpath)

def get_full_rsn_path(unc_path):
    """ Get the full path to the model on the server """
    projsubfolder = get_projects_subfolder(unc_path)
    rserverstart = get_rserverstart(unc_path)
    full_path = os.path.join(rserverstart, projsubfolder)
    assert DB.ModelPathUtils.IsValidUserVisibleFullServerPath(full_path)
    fullpath = DB.ModelPathUtils.ConvertUserVisiblePathToModelPath(full_path)
    return DB.ModelPathUtils.ConvertModelPathToUserVisiblePath(fullpath)


def get_projects_subfolder(unc_path):
    """ Get the subfolder name for the projects folder """
    components = unicode(unc_path).split(os.sep)
    projects_index = components.index('Projects')
    projects_path = os.path.join(*components[projects_index + 1:])
    return projects_path

def get_nodepath(unc_path):
    """ Get the node path from the full path """
    components = unicode(unc_path).split(os.sep)
    projects_index = components.index('Projects')
    projects_path = os.path.join(*components[:projects_index + 1])
    return projects_path

def get_RserverVersion(unc_path):
    # Get the version number using regex from a string like \Revit Server 2022\
    res = re.search(r"\\Revit Server (\d+)\\", unc_path)
    if not res:
        return None
    return str(res.group(1))

def get_RserverName(unc_path):
    path_split = os.path.splitunc(unc_path)
    firstpart = path_split[0]
    # Get the name of the server using regex from a string like \\av-revit1\Autodesk
    res = re.search(r"\\\\(.*)\\", firstpart, flags=re.IGNORECASE)
    if not res:
        return None
    return str(res.group(1))

class ServerPath(object):
    def __init__(self, path):
        super(ServerPath, self).__init__()
        self.path = path
        self.servername = get_RserverName(path)
        self.serverversion = get_RserverVersion(path)
        self.serverstart = get_rserverstart(path)
        self.rsn_path = get_full_rsn_path(path)
        self.server_node = get_projects_subfolder(path)
        self._rserver = None

    def get_rserver(self):
        if self._rserver is None:
            self._rserver = rpws.RevitServer(self.servername, self.serverversion)
        return self._rserver

    def get_last_modified(self):
        modified = "Ukjent"
        server = self.get_rserver()
        try:
            modified = server.getmodelinfo(r"RSN://AV-Revit2022/2022/000000-00 test123/000000-00 Test123 RIE.rvt").date_modified
        except:
            pass
        return modified