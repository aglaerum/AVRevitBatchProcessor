# -*- coding: utf-16 -*-

import os
import clr

clr.AddReference("Revit.IFC.Export")
clr.AddReference("Revit.IFC.Import")
clr.AddReference("Revit.IFC.Common")

from Autodesk.Revit import DB
from Autodesk.Revit.DB import IFC

# noinspection PyUnresolvedReferences
import revit_script_util
from revit_script_util import Output

""" Legg til og ekskluder ekstra kategorier"""
IncludeCatList = [
    DB.BuiltInCategory.OST_Grids,
    DB.BuiltInCategory.OST_MEPSpaces,
    DB.BuiltInCategory.OST_Rooms,
]

ExcludeCatList = [
    DB.BuiltInCategory.OST_Topography,
]


def samle_3dViews_from_name(doc):
    # type: (DB.Document) -> list[DB.View3D]
    Output("Samler 3D View fra navn...")
    views3d = DB.FilteredElementCollector(doc).OfClass(DB.View3D).ToElements()

    views = list(filter(lambda x: not x.IsTemplate and "ifc" in unicode(x.Name).lower(), views3d))
    # for v in views:
    #     Output(v.Name)
    # if not views:
    #     Output("Fant ingen view! Bruker opptil 2 tilfeldige 3DView")
    #     views = list(filter(lambda x: not x.IsTemplate, views3d))[:2]
    return views

def samle_3dviews_from_viewset(doc):
    # type: (DB.Document) -> list[DB.View3D]
    Output("Samler 3D View fra SheetSet...")
    views3d = []
    sheetsets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheetSet) # type: list[DB.ViewSheetSet]
    for sheetset in sheetsets:
        if "ifc" in unicode(sheetset.Name).lower():
            views3d.extend([x for x in sheetset.Views if isinstance(x, DB.View3D)])
    return views3d

def samle_3dViews(doc):

    allviews = []
    viewsfromname = samle_3dViews_from_name(doc)
    viewsfromviewset = samle_3dviews_from_viewset(doc)

    Output("Fant {} 3D Views fra navn".format(len(viewsfromname)))
    Output("Fant {} 3D Views fra ViewSet".format(len(viewsfromviewset)))

    allviews.extend(viewsfromname)
    allviews.extend(viewsfromviewset)
    return allviews

def export_view(view, outfolder, psets_file, mappingfile):
    Output("Eksporterer: {} - {}".format(type(view).__name__, view.Name))

    # extra_elems, elements_exclude = Setup_Export(view.Document)

    # """ Endre andre objekter før eksport"""
    # skriv_ifcGuid_AlternateGuid(extra_elems)

    """ Sett ifc filnavn og sett IFC type"""
    ifcfilnavn = get_safe_viewname(view)

    """ Hent AV Standardoptions """
    Avoptions = get_AVIFCExportOptions(view, psets_file, mappingfile)

    """ Endre view objekter før eksport"""
    elems_from_view = DB.FilteredElementCollector(view.Document, view.Id)
    # skriv_ifcGuid_AlternateGuid(elems_from_view)

    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    if view.Document.Export(outfolder, ifcfilnavn, Avoptions):
        Output("IFC eksportert til:\n{}".format(os.path.join(outfolder, ifcfilnavn)))
    else:
        Output("IFC eksporter svarer at IFC ikke ble eksportert")


def Setup_Export(doc):
    """ Skriv Prosjekt GUID`er """
    # todo: Fungerer ikke?
    # skriv_proj_level_ifcGuid(doc)

    """ Hent og bruk site location med IFC i navnet"""
    set_ifclocation(doc)

    """ Inkludere og excludere ekstra kategorier """
    extra_elements = IncludeCats(doc)
    exclude_elements = ExcludeCats(doc)

    return extra_elements, exclude_elements


def skriv_ifcGuid_AlternateGuid(all_elems):
    # Denne er godkjent av buildingsmart
    for elem in all_elems:  # type: DB.Element
        ifcguid = IFC.ExporterIFCUtils.CreateAlternateGUID(elem)
        IFC.ExporterIFCUtils.AddValueString(elem, DB.ElementId(DB.BuiltInParameter.IFC_GUID), ifcguid)
        elem_type = elem.Document.GetElement(elem.GetTypeId())
        if elem_type:
            ifcguid_type = IFC.ExporterIFCUtils.CreateAlternateGUID(elem_type)
            IFC.ExporterIFCUtils.AddValueString(elem_type, DB.ElementId(DB.BuiltInParameter.IFC_TYPE_GUID),
                                                ifcguid_type)


def get_safe_viewname(view=None):
    # prosjnavn = dokument.Title
    viewtypes = [DB.View3D, DB.ViewSchedule, DB.View, DB.ViewPlan]

    if type(view) in viewtypes:
        viewnameifc = view.Name
        return safefilename("{}.ifc".format(viewnameifc))

    elif type(view) is list:
        viewnameifc = "_".join([n.Name for n in view])
        return safefilename("{}.ifc".format(viewnameifc))

    elif view is None:
        viewnameifc = ""
        return safefilename("{}.ifc".format(viewnameifc))


def get_AVIFCExportOptions(exportview, psetsfile, mappingfile):
    # type: (DB.View) -> DB.IFCExportOptions
    # https://knowledge.autodesk.com/support/revit-products/learn-explore/caas/CloudHelp/cloudhelp/2017/ENU/Revit-DocumentPresent/files/GUID-E029E3AD-1639-4446-A935-C9796BC34C95-htm.html
    # https://github.com/Autodesk/revit-ifc/blob/1f1876f1b84907eeefb5d11d4b12f558e77f8693/Source/IFCExporterUIOverride/IFCExportConfiguration.cs
    # http://www.revitapidocs.com/2018.1/b90adabd-0502-fb8f-3a0d-bfa412393f61.htm

    """ Må settes i Revit.ini
    * Exportlayers
    """

    # Hent options objekt
    options = DB.IFCExportOptions()
    """ Builtin options """
    options.FilterViewId = exportview.Id
    options.WallAndColumnSplitting = False
    options.ExportBaseQuantities = True
    options.SpaceBoundaryLevel = 1
    """ IFC type """
    options.FileVersion = DB.IFCVersion.IFC2x3CV2
    options.FamilyMappingFile = mappingfile

    # Propertysets(parametere på objekter ut). Hvilke av disse trenger vi?
    options.AddOption("ExportIFCCommonPropertySets", "True")
    options.AddOption("ExportInternalRevitPropertySets", "False")
    options.AddOption("ExportSchedulesAsPsets", "False")
    # options.AddOption("ExportSpecificSchedules", "True")  # Kun med PSET|IFC|COMMON")
    options.AddOption("ExportSpecificSchedules", "False")  # Kun med PSET|IFC|COMMON")

    options.AddOption("ExportUserDefinedPsets", "True")
    options.AddOption("ExportUserDefinedPsetsFileName", psetsfile)

    options.AddOption("ExportUserDefinedParameterMapping", "False")
    # options.AddOption("ExportUserDefinedParameterMappingFileName", magi_ParametersMap())  # Denne ser ut til å gjøre ingenting.

    # Nullpunkt
    options.AddOption("SitePlacement", "0")  # 0 = SharedCoordinates 1, 1 = SurveyPoint, 2 = ProjectBasepoint DOBBELTSJEKK
    options.AddOption("IncludeSiteElevation", "True")  # Tar med Z verdi på nullpunkt

    # Ifc filtype og type
    # options.AddOption("IFCFileType", "False") #  Ivaretatt i funksjoner lenger ned
    # options.AddOption("IFCVersion", "False")

    # Inkludering\Ekskludering
    options.AddOption("SpaceBoundaries", "1")
    options.AddOption("Export2DElements", "True")
    options.AddOption("Use2DRoomBoundaryForVolume", "False")  # Nei.
    options.AddOption("UseFamilyAndTypeNameForReference", "True")
    options.AddOption("ExportPartsAsBuildingElements", "True")  # True = Deler eksporteres som egne objekter
    options.AddOption("ExportSolidModelRep", "True")  # False eksporterer ett enkelt objekt per part
    options.AddOption("ExportBoundingBox", "True")  # Må være true for at ikke alle space skal bli ved delexport.
    options.AddOption("ExportRoomsInView", "True")  # Active view og view id må settes
    options.AddOption("ExportLinkedFiles", "False")
    options.AddOption("ExcludeFilter", "")  # Mulighet til å ekskludere enkeltobjekter via en liste
    options.AddOption("IncludeSteelElements", "True")
    # options.AddOption("ExportLinkedFiles", "False")

    # Exportkvalitet
    options.AddOption("ActiveViewId", str(exportview.Id))  # Disse må eventuelt settes ut før funksjon hvis true
    options.AddOption("UseActiveViewGeometry", "True")  # Disse må eventuelt settes ut før funksjon hvis true
    options.AddOption("TessellationLevelOfDetail", "0,4")  # Meshkvalitet 0-1
    options.AddOption("UseOnlyTriangulation", "False")
    options.AddOption("ExportAnnotations", "True")

    # Guid
    options.AddOption("StoreIFCGUID", "True")  # Endret til False
    options.AddOption("ConfigName", "AsplanViak")

    # Nye properties
    options.AddOption("AlternateUIVersion", "AVTools")
    # options.AddOption("ElementsForExport", "")  # overstyres før funksjon
    # options.AddOption("SingleElement", "1112461")
    # options.AddOption("UseTypeNameOnlyForIfcType", "False")

    """ Nye """
    # options.AddOption("UseVisibleRevitNameAsEntityName", "False")
    # options.AddOption("UseCoarseTessellation", "False")
    # options.AddOption("TessellationLevelOfDetail", "2")
    # options.AddOption("AllowGUIDParameterOverride", "False")
    options.AddOption("PlanElems2D", "True")
    # options.AddOption("internalSets", "False")

    return options


def skriv_proj_level_ifcGuid(doc):
    # type: (DB.Document) -> None
    ifcguidSite = IFC.ExporterIFCUtils.CreateProjectLevelGUID(doc, IFC.IFCProjectLevelGUIDType.Site)
    ifcguidBuilding = IFC.ExporterIFCUtils.CreateProjectLevelGUID(doc, IFC.IFCProjectLevelGUIDType.Building)
    ifcguidProj = IFC.ExporterIFCUtils.CreateProjectLevelGUID(doc, IFC.IFCProjectLevelGUIDType.Project)

    # todo: Finn ut av hvorfor dette ikke fungerer plutselig
    # projectinfoelem = doc.ProjectInformation
    # IFC.ExporterIFCUtils.AddValueString(projectinfoelem, DB.ElementId(DB.BuiltInParameter.IFC_SITE_GUID), ifcguidSite)
    # IFC.ExporterIFCUtils.AddValueString(projectinfoelem, DB.ElementId(DB.BuiltInParameter.IFC_BUILDING_GUID), ifcguidBuilding)
    # IFC.ExporterIFCUtils.AddValueString(projectinfoelem, DB.ElementId(DB.BuiltInParameter.IFC_PROJECT_GUID), ifcguidProj)


def set_ifclocation(doku):
    """
    :type doku: DB.Document
    """
    # locationsdict = {l.Name: l for l in dokument.ProjectLocations}  # type: Dict(str, DB.ProjectLocation)
    ifclocations = [x for x in doku.ProjectLocations if "ifc" in str(x.Name).lower()]  # type: list[DB.ProjectLocation]
    if ifclocations:
        doku.ActiveProjectLocation = ifclocations[0]
    else:
        locations = set(DB.FilteredElementCollector(doku).OfClass(DB.ProjectLocation))
        # Trekker ifra de som er synlige for brukeren.
        hiddensites = locations.difference(set(doku.ProjectLocations))
        failsafelocations = [x for x in hiddensites if str(x.Name) == "Project"]
        doku.ActiveProjectLocation = failsafelocations[0]


def IncludeCats(doc):
    # type: (DB.Document, bool, bool) -> set[DB.Element]

    elems = set()
    # Todo: Dette blir sikkert feil
    cats = [x for x in doc.Settings.Categories.GetEnumerator() if x in IncludeCatList]  # type: list[DB.Category]
    Output("\n".join(str(x) for x in cats))
    if cats:
        cats = sorted((x for x in cats if x.state is True), key=lambda x: str(x))
        elems.update(get_cat_elems(doc, cats))
    return elems


def ExcludeCats(doc):
    # type: (DB.Document, bool, bool) -> set[DB.Element]
    elems = set()
    cats = [x for x in doc.Settings.Categories.GetEnumerator() if x in ExcludeCatList]  # type: list[DB.Category]
    Output("\n".join(str(x) for x in cats))
    if cats:
        cats = [x for x in cats if x.state is True]
        elems.update(get_cat_elems(doc, cats))
    return elems


def safefilename(filnavn):
    keepcharacters = (' ', '-', '_', ")", "(", ".")
    return "".join(c for c in filnavn if c.isalnum() or c in keepcharacters)


def get_cat_elems(doku, cats=None):
    # type: (object, list[DB.Category]) -> list[DB.Element]
    if not cats:
        cats = []

    elems = []
    for cat in cats:
        cat_elems = DB.FilteredElementCollector(doku).OfCategoryId(cat.cat_id)
        cat_elems = cat_elems.WhereElementIsNotElementType()
        elems.extend(cat_elems.ToElements())
    return elems
