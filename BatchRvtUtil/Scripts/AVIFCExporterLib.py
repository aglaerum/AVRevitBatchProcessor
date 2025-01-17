# -*- coding: utf-8 -*-
import os

import clr
from Autodesk.Revit import DB
from System.Collections.Generic import Dictionary
from System.IO import File
import AVClr
import traceback

clr.AddReference("System.Web.Extensions")
from System.Web.Script.Serialization import JavaScriptSerializer


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
    # type: (DB.View, str, str, str, str, callable) -> None

    output("Eksporterer: {} - {}".format(type(view).__name__, view.Name))

    """ Sett ifc Filnavn """
    ifcfilnavn = get_safe_viewname(view)
    full_ifc_path = os.path.join(outfolder, ifcfilnavn)

    """ Sett IFC innstillinger """
    try:
        ifc_options = set_ifcoptions_from_json(ifc_settings, view, output)
    except Exception as e:
        output(traceback.format_exc())
        output("Kunne ikke hente innstillinger fra json fil: {}"
               "\n Er IFC Export addin installert for gjeldende Revit version??!".format(e))
        ifc_options = get_AVIFCExportOptions(view, psets_file, mappingfile, output)
        ifc_options.AddOption("ExportUserDefinedPsetsFileName", psets_file)
        ifc_options.FamilyMappingFile = mappingfile
        output(" ############ Standard IFC Export Options brukes!! #############")

    """ Legg til extra elementer som skal med i eksport """
    # extraelems = DB.FilteredElementCollector(view.Document).OfClass(DB.Grid).ToElementIds()c
    # extraelems = ",".join([str(x) for x in extraelems])
    # ifc_options.AddOption("ElementsForExport", "'{}'".format(extraelems))  # overstyres før funksjon

    """ Set IFC Location """
    set_ifclocation(view, output)

    if not ifc_options.IsValidObject:
        raise Exception("IFC Export Options er ikke gyldig!! Avbryter...")

    """ Lag mappen hvis den ikke eksisterer """
    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

    """ Sjekk om IFC faktisk ble laget """
    if not view.Document.Export(outfolder, ifcfilnavn, ifc_options):
        output("IFC eksporter svarer at IFC ikke ble eksportert")
    if os.path.exists(full_ifc_path):
        output("IFC eksportert til:\n{}".format(full_ifc_path))
    else:
        output("---------------- IFC BLE IKKE EKSPORTERT ----------------")
    """ Sjekk om noen som helst IFC filer er i mappen, hvis ikke. Slett den """
    filesinfolder = os.listdir(outfolder)
    if not filesinfolder:
        output("Mappen slettes fordi den er tom...")
        os.rmdir(outfolder)


def set_ifcoptions_from_json(jsonfile, view, output):
    # type: (str, DB.View, callable) -> DB.IFCExportOptions

    output("Prøver å hente IFC Export Options fra json fil: {}".format(jsonfile))
    AVClr.clr_IFCExportUIOverride()
    from BIM.IFC.Export import UI as BUI

    viewid = view.Id

    """ Lag ny exportconfig """
    configname = "AVAutoExporter"
    options = DB.IFCExportOptions()

    """ Ny default config """
    new_config = BUI.IFCExportConfiguration.CreateDefaultConfiguration()
    new_config.Name = configname

    """ Oppdater default config fra json """
    deserializer = JavaScriptSerializer()
    json_data = File.ReadAllText(jsonfile)
    data_dict = deserializer.Deserialize(json_data, Dictionary[str, object])  # type: Dictionary[str, object]
    """ Disse må være på plass ellers får man en feilmelding hvis det står noe annet i Json """
    data_dict["ActivePhaseId"] = "-1"
    data_dict["ActiveViewId"] = "-1"

    deserializer = JavaScriptSerializer()
    new_config.DeserializeFromJson(data_dict, deserializer)

    output("IFCConfigurasjon: {}".format(str(new_config)))
    output("IFC Exporter UI version: {}".format(BUI.IFCUISettings.GetAssemblyVersionForUI()))
    output("IFC Exporter version: {}".format(BUI.IFCUISettings.GetAssemblyVersion()))

    """ Oppdater ?"""
    new_config.UpdateOptions(options, viewid)
    output("Instillinger hentet fra Json: {}".format(jsonfile))
    for keyvalue in data_dict.GetEnumerator():
        output("    {}: {}".format(str(keyvalue.Key), str(keyvalue.Value)))
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
        viewnameifc = "NoView"
        return safefilename("{}.ifc".format(viewnameifc))


def get_AVIFCExportOptions(exportview, psetsfile, mappingfile, output):
    # type: (DB.View) -> DB.IFCExportOptions
    # https://knowledge.autodesk.com/support/revit-products/learn-explore/caas/CloudHelp/cloudhelp/2017/ENU/Revit-DocumentPresent/files/GUID-E029E3AD-1639-4446-A935-C9796BC34C95-htm.html
    # https://github.com/Autodesk/revit-ifc/blob/1f1876f1b84907eeefb5d11d4b12f558e77f8693/Source/IFCExporterUIOverride/IFCExportConfiguration.cs
    # http://www.revitapidocs.com/2018.1/b90adabd-0502-fb8f-3a0d-bfa412393f61.htm

    """ Må settes i Revit.ini
    * Exportlayers
    """
    output("Henter IFC Export Options")
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


# def set_default_location(view, output):
#     # type: (DB.View) -> None
#
#     # Henter lokasjoner(Sites)
#
#     default_location_name = "Project"
#
#     output("ADVARSEL: Ingen lokasjoner funnet. Setter til default location: {}".format(default_location_name))
#     locations = set(DB.FilteredElementCollector(view.Document).OfClass(DB.ProjectLocation))
#     default_locations = [x for x in locations if str(x.Name) == default_location_name]
#     output("Alle lokasjoner:\n{}".format("\n".join([x.Name for x in locations])))
#
#     the_location = default_locations[0]
#     view.Document.ActiveProjectLocation = the_location
#     output("Lokasjon satt til: {}".format(the_location.Name))

def get_locations(view, output):
    # type: (DB.View) -> list[DB.ProjectLocation]

    all_locations = set(DB.FilteredElementCollector(view.Document).OfClass(DB.ProjectLocation).ToElementIds())
    user_locations = view.Document.ProjectLocations  # type: list[DB.ProjectLocation]

    hidden_locations = all_locations.difference(set(x.Id for x in user_locations))
    hidden_locations = [view.Document.GetElement(x) for x in hidden_locations]  # type: list[DB.ProjectLocation]

    output("Alle ProjectLocations(Synlig for brukeren):\n{}".format("\n".join([x.Name for x in view.Document.ProjectLocations])))
    output("Alle ProjectLocations(Ikke synlig for brukeren):\n{}".format("\n".join([x.Name for x in hidden_locations])))

    return all_locations, user_locations, hidden_locations

def get_location(locations, name, output):
    # type: (list[DB.ProjectLocation], str) -> DB.ProjectLocation

    locations = [x for x in locations if str(x.Name) == name]
    if not locations:
        output("Fant ingen lokasjon med navn: {}".format(name))
        return None
    return locations[0]

def set_ifclocation(view, output):
    # type: (DB.View) -> None

    default_location_name = "Project"

    all_locations, user_locations, hidden_locations = get_locations(view, output)

    if not user_locations:
        output("Ingen user sites funnet. Prøver å finne default location ved navn: {}".format(default_location_name))
        default_locations = [x for x in hidden_locations if str(x.Name) == default_location_name]
        if not default_locations:
            raise ValueError("Fant ingen default location med navn: {}".format(default_location_name))

    ifc_locations = [x for x in user_locations if "ifc" in str(x.Name).lower()]

    the_location = None
    if not ifc_locations:
        output("Fant ingen IFC locations. Prøver å sette default location: {}".format(default_location_name))
        the_location = get_location(hidden_locations, default_location_name, output)

    if len(ifc_locations) == 1:
        the_location = ifc_locations[0]
        output("Fant nøyaktig 1 IFC location: {}".format(the_location.Name))

    if len(ifc_locations) > 1:
        the_location = ifc_locations[0]
        output("Fant flere IFC locations:\n{}".format("\n".join([x.Name for x in ifc_locations])))
        output("Setter location til første IFC location: {}".format(the_location.Name))

    if the_location is None:
        raise ValueError("Kunne ikke sette location")

    view.Document.ActiveProjectLocation = the_location

def safefilename(filnavn):
    keepcharacters = (' ', '-', '_', ")", "(", ".")
    return "".join(c for c in filnavn if c.isalnum() or c in keepcharacters)
