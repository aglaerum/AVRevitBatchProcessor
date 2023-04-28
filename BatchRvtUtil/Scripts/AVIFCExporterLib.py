# -*- coding: utf-8 -*-
import codecs
import os
import clr
import json

clr.AddReference("Revit.IFC.Export")
clr.AddReference("Revit.IFC.Import")
clr.AddReference("Revit.IFC.Common")

from Autodesk.Revit import DB


def samle_3dViews_from_name(doc, output):
    # type: (DB.Document) -> list[DB.View3D]
    output("Samler 3D View fra navn...")
    views3d = DB.FilteredElementCollector(doc).OfClass(DB.View3D).ToElements()

    views = list(filter(lambda x: not x.IsTemplate and "ifc" in unicode(x.Name).lower(), views3d))
    # for v in views:
    #     output(v.Name)
    # if not views:
    #     output("Fant ingen view! Bruker opptil 2 tilfeldige 3DView")
    #     views = list(filter(lambda x: not x.IsTemplate, views3d))[:2]
    return views


def samle_3dviews_from_viewset(doc, output):
    # type: (DB.Document) -> list[DB.View3D]
    output("Samler 3D View fra SheetSet...")
    views3d = []
    sheetsets = DB.FilteredElementCollector(doc).OfClass(DB.ViewSheetSet)  # type: list[DB.ViewSheetSet]
    for sheetset in sheetsets:
        if "ifc" in unicode(sheetset.Name).lower():
            views3d.extend([x for x in sheetset.Views if isinstance(x, DB.View3D)])
    return views3d


def samle_3dViews(doc, output):
    allviews = []
    viewsfromname = samle_3dViews_from_name(doc, output)
    viewsfromviewset = samle_3dviews_from_viewset(doc, output)

    output("Fant {} 3D Views fra navn".format(len(viewsfromname)))
    output("Fant {} 3D Views fra ViewSet".format(len(viewsfromviewset)))

    allviews.extend(viewsfromname)
    allviews.extend(viewsfromviewset)
    return allviews


def export_view(view, outfolder, psets_file, mappingfile, ifc_settings, output):
    output("Eksporterer: {} - {}".format(type(view).__name__, view.Name))

    """ Sett ifc filnavn og sett IFC type"""
    ifcfilnavn = get_safe_viewname(view)

    """ Hent AV Standardoptions """
    # Setter grunninstillinger, disse blir overstyrt.
    ifc_options = get_AVIFCExportOptions(view, psets_file, mappingfile)
    """ Sett IFC innstillinger fra fil """
    # Hvis innstillinger er satt i json fil så er disse gjeldende
    # ifc_options = set_ifc_settings_from_file(ifc_settings, ifc_options, output)

    """ Overstyr noen innstillinger uansett om de er i json fil """
    ifc_options.AddOption("ExportUserDefinedPsetsFileName", psets_file)
    ifc_options.FamilyMappingFile = mappingfile

    """ Legg til extra elementer som skal med i eksport """
    # extraelems = DB.FilteredElementCollector(view.Document).OfClass(DB.Grid).ToElementIds()c
    # extraelems = ",".join([str(x) for x in extraelems])
    # ifc_options.AddOption("ElementsForExport", "'{}'".format(extraelems))  # overstyres før funksjon

    if not ifc_options.IsValidObject:
        raise Exception("IFC Export Options er ikke gyldig!! Avbryter...")
    """ Lag mappen hvis den ikke eksisterer """
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    # """ Print alle innstillingene som er satt """
    # Finn en måte å få bekreftet innstillingene på
    # print_ifc_export_options(ifc_options, output)

    full_ifc_path = os.path.join(outfolder, ifcfilnavn)
    if not view.Document.Export(outfolder, ifcfilnavn, ifc_options):
        output("IFC eksporter svarer at IFC ikke ble eksportert")
    if os.path.exists(full_ifc_path):
        output("IFC eksportert til:\n{}".format(full_ifc_path))
    else:
        output("---------------- IFC BLE IKKE EKSPORTERT ----------------")

    filesinfolder = os.listdir(outfolder)
    if not filesinfolder:
        output("Mappen slettes fordi den er tom...")
        os.rmdir(outfolder)


def print_ifc_export_options(ifc_export_options, output):
    # type: (DB.IFCExportOptions, callable) -> None
    output("Innstillinger som faktisk har blitt satt:")
    for name, value in ifc_export_options.GetValidOptions():
        output("    {}: {}".format(name, value))

    # for prop in dir(ifc_export_options):  #     # Ignore private properties and methods  #     if not prop.startswith("_"):  #         value = getattr(ifc_export_options, prop, "IKKE DEFINERT")  #         output("    {}: {}".format(prop, value))


def set_ifc_settings_from_file(ifc_settings, options, output):
    # type: (str, DB.IFCExportOptions, callable) -> DB.IFCExportOptions
    ifc_settings = ifc_settings
    output("Setter IFC innstillinger fra fil: {}".format(ifc_settings))

    with codecs.open(ifc_settings, "r", encoding="utf-8") as f:
        ifc_settings = json.load(f)
        for name, value in ifc_settings.items():
            output("        {} - {}".format(name, value))
            options.AddOption(name, '"{}"'.format(unicode(value)))
    return options


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
    options.AddOption("StoreIFCGUID", "False")  # Endret til False
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

# def get_alternateExportOptions(exportview):
#     # type: (DB.View) -> DB.IFCExportOptions
#     """ Henter options objekt for eksport av IFC. """
#     from Autodesk.Revit.DB import IFC
#     from Revit.IFC.Export import Toolkit
#     for key, value in dict(options):
#         print key, value

def set_ifclocation(doku):
    # type: (DB.Document) -> None
    ifclocations = [x for x in doku.ProjectLocations if "ifc" in str(x.Name).lower()]  # type: list[DB.ProjectLocation]
    if ifclocations:
        doku.ActiveProjectLocation = ifclocations[0]
    else:
        locations = set(DB.FilteredElementCollector(doku).OfClass(DB.ProjectLocation))
        # Trekker ifra de som er synlige for brukeren.
        hiddensites = locations.difference(set(doku.ProjectLocations))
        failsafelocations = [x for x in hiddensites if str(x.Name) == "Project"]
        doku.ActiveProjectLocation = failsafelocations[0]


def safefilename(filnavn):
    keepcharacters = (' ', '-', '_', ")", "(", ".")
    return "".join(c for c in filnavn if c.isalnum() or c in keepcharacters)
