import os

from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    QgsField,
    QgsFields,
    QgsRasterLayer,
    QgsWkbTypes,
    QgsVectorFileWriter,
QgsVectorDataProvider
)

from qgis.utils import iface
from qgis import processing


def createGrid(resolution, building_layer_path, grid_path, extent_iface):
    project = QgsProject.instance()

    overlay_layer_name = os.path.splitext(
        os.path.basename(building_layer_path))[0]

    buildings_layer = QgsVectorLayer(
        building_layer_path,
        overlay_layer_name,
        "ogr")

    crs_layer = buildings_layer.crs().authid()

    if extent_iface == True:
        extent = iface.mapCanvas().extent()
    elif extent_iface == False:
        extent = buildings_layer.extent()
    xmax = extent.xMaximum()
    ymax = extent.yMaximum()
    xmin = extent.xMinimum()
    ymin = extent.yMinimum()
    extent_coords = "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax)

    # native:creategrid
    params_creategrid = {
        'CRS': crs_layer,
        'EXTENT': extent_coords,
        'HOVERLAY': 0,
        'HSPACING': resolution,
        'OUTPUT': 'memory:',
        'TYPE': 0,
        'VOVERLAY': 0,
        'VSPACING': resolution
    }

    result_grid = processing.run("native:creategrid", params_creategrid)
    grid_output = result_grid['OUTPUT']

    # native:difference
    # params_difference = {
    #     'INPUT': grid_output,
    #     'OUTPUT': 'memory:',
    #     'OVERLAY': overlay_layer
    # }
    #
    # result_difference = processing.run("native:difference", params_difference)
    # difference_output = result_difference['OUTPUT']

    # native:extractbylocation
    params_extract = {
        'INPUT': grid_output,
        'INTERSECT': buildings_layer,
        'OUTPUT': 'memory:',
        'OVERLAY': buildings_layer,
        'PREDICATE': [2]
    }

    result_difference = processing.run("native:extractbylocation", params_extract)
    difference_output = result_difference['OUTPUT']

    # native:multipart to single partS
    params_multiTosingle = {
        'INPUT': difference_output,
        'OUTPUT': 'memory:',
    }

    result_multiTOsingle = processing.run("native:multiparttosingleparts", params_multiTosingle)
    output_singlepart = result_multiTOsingle['OUTPUT']

    # remove layer in already in TOC
    removeLayer(grid_path)
    writer = QgsVectorFileWriter.writeAsVectorFormat(
        output_singlepart,
        grid_path,
        'utf-8',
        driverName='ESRI Shapefile',
        filterExtent=output_singlepart.extent()
    )

    grid_layer = iface.addVectorLayer(
        grid_path,
        '',
        'ogr'
    )

    fieldsTOdelete = grid_layer.attributeList()

    pr = grid_layer.dataProvider()

    pr.deleteAttributes(fieldsTOdelete[1:5])

    grid_layer.updateFields()


def createRasterContour(resolution, layerTOrasterize_path, field, interval, contour_path,poly_path):
    project = QgsProject.instance()

    layerTOrasterize_name = os.path.splitext(
        os.path.basename(layerTOrasterize_path))[0]

    layerTOrasterize = QgsVectorLayer(
        layerTOrasterize_path,
        layerTOrasterize_name,
        "ogr"
    )

    extent = layerTOrasterize.extent()
    xmax = extent.xMaximum()
    ymax = extent.yMaximum()
    xmin = extent.xMinimum()
    ymin = extent.yMinimum()
    extent_coords = "%f,%f,%f,%f" % (xmin, xmax, ymin, ymax)

    params_rasterize = {
        'BURN': 0,
        'DATA_TYPE': 5,
        'EXTENT': extent_coords,
        'EXTRA': '',
        'FIELD': field,
        'HEIGHT': resolution,
        'INIT': None,
        'INPUT': layerTOrasterize,
        'INVERT': False,
        'NODATA': 0,
        'OPTIONS': '',
        'OUTPUT': 'TEMPORARY_OUTPUT',
        'UNITS': 1,
        'WIDTH': resolution
    }
    result_rasterize = processing.run("gdal:rasterize", params_rasterize)
    raster_output = result_rasterize['OUTPUT']
    raster_layer = QgsRasterLayer(
        raster_output,
        'Raster'
    )

    project.addMapLayer(raster_layer)

    params_contour = {
        'BAND': 1,
        'CREATE_3D': False,
        'EXTRA': '',
        'FIELD_NAME': field,
        'IGNORE_NODATA': False,
        'INPUT': raster_output,
        'INTERVAL': interval,
        'NODATA': None,
        'OFFSET': 0,
        'OUTPUT': contour_path
    }

    # remove contour if already in TOC
    removeLayer(contour_path)

    result_contour = processing.run("gdal:contour", params_contour)
    contour_output = result_contour['OUTPUT']

    contour_name = os.path.splitext(
        os.path.basename(contour_path))[0]

    contour_layer = QgsVectorLayer(
        contour_output,
        contour_name
    )

    project.addMapLayer(contour_layer)

    # gdal: polygonize Contour NEW method
    parameter_poly_contour = {
        'BAND': 1,
        'CREATE_3D': False,
        'EXTRA': '',
        'FIELD_NAME_MAX': field+'_MAX',
        'FIELD_NAME_MIN': field+'_MIN',
        'IGNORE_NODATA': False,
        'INPUT': raster_output,
        'INTERVAL': interval,
        'NODATA': None,
        'OFFSET': 0,
        'OUTPUT': poly_path
    }
    # remove polygon in already in TOC
    removeLayer(poly_path)

    result_poly = processing.run("gdal:contour_polygon", parameter_poly_contour)
    poly_output = result_poly['OUTPUT']
    poly_name = os.path.splitext(
        os.path.basename(poly_path))[0]

    poly_layer = QgsVectorLayer(
        poly_path,
        poly_name
    )

    project.addMapLayer(poly_layer)

    # ADD Area_mq field in table
    # Here we get the capabilities of your layer (Add attribute layer, edit feature ect ..
    caps = poly_layer.dataProvider().capabilities()

    # We make a list of fields from their name
    fields_name = [f.name() for f in poly_layer.fields()]

    # We check if we can add an attribute to the layer.
    if caps & QgsVectorDataProvider.AddAttributes:
        # We check if the attribute field is not exist
        if "Area_mq" not in fields_name:
            # We add the field name Area and with the double type (it can be integer or text
            poly_layer.dataProvider().addAttributes([QgsField("Area_mq", QVariant.Double)])
            # We update layer's field otherwise we'll not have the field
            poly_layer.updateFields()
            # Recreate the list field by the name to have index of the field
            fields_name = [f.name() for f in poly_layer.fields()]
            # we get the index of the Area field
            fareaidx = fields_name.index('Area_mq')
        else:
            # We are here because there is a field name Area
            print("The Area_mq field is already added")
            # Recreate the list field by the name to have index of the field
            fields_name = [f.name() for f in poly_layer.fields()]
            # we get the index of the Area field
            fareaidx = fields_name.index('Area_mq')

    # Here we check if we can change attribute of the layer
    if caps & QgsVectorDataProvider.ChangeAttributeValues:
        # we loop^on every feature
        for feature in poly_layer.getFeatures():
            # For each feature :
            # We calculate the area and put the index of the field Area
            # We round the area value by 2 digit expressed in km2
            attrs = {fareaidx: round(feature.geometry().area(), 2)}
            # We change the the value of Area Field for this feature.
            poly_layer.dataProvider().changeAttributeValues({feature.id(): attrs})


    return raster_output


def removeLayer(path_layer):
    # remove layer from TOC if already loaded
    basefile = os.path.basename(path_layer)
    diff_layer = os.path.splitext(basefile)[0]
    directory = os.path.dirname(path_layer)
    extensions = ["shp", "shx", "dbf", "prj", "sbn", "sbx", "fbn", "fbx", "ain", "aih", "ixs", "mxs", "atx", "xml",
                  "cpg", "qix"]
    if len(QgsProject.instance().mapLayersByName(diff_layer)) > 0:
        lyr = QgsProject.instance().mapLayersByName(diff_layer)[0]
        print('removing layer1: ', lyr.id())
        QgsProject.instance().removeMapLayer(lyr.id())
        QgsVectorFileWriter.deleteShapeFile(path_layer)

        # for ext in extensions:
        #     f = os.path.join(directory,diff_layer+'.'+ext)
        #     if os.path.exists(f):
        #         print('removing file: ',f)
        #         os.remove(f)


# def polygonize(raster_path, minimum, maximum, interval, poly_path):
#     project = QgsProject.instance()
#
#     raster_name = os.path.splitext(
#         os.path.basename(raster_path))[0]
#
#     raster = QgsRasterLayer(
#         raster_path,
#         raster_name,
#         "gdal"
#     )
#
#     # native: reclassify by table
#     table = []
#     for i in range(minimum, maximum, interval):
#         i += interval
#         value = (minimum + i) / 2
#         fillTbl = [minimum, i, value]
#         table.extend(fillTbl)
#         minimum += interval
#
#     parameter_reclaBYtbl = {
#         'DATA_TYPE': 5,
#         'INPUT_RASTER': raster,
#         'NODATA_FOR_MISSING': False,
#         'NO_DATA': -9999,
#         'OUTPUT': 'TEMPORARY_OUTPUT',
#         'RANGE_BOUNDARIES': 3,
#         'RASTER_BAND': 1,
#         'TABLE': table
#     }
#
#     result_reclas = processing.run("native:reclassifybytable", parameter_reclaBYtbl)
#     reclas_output = result_reclas['OUTPUT']
#
#     # gdal: polygonize OLD method
#     parameter_poly = {
#         'BAND': 1,
#         'EIGHT_CONNECTEDNESS': False,
#         'EXTRA': '',
#         'FIELD': 'dBA',
#         'INPUT': reclas_output,
#         'OUTPUT': poly_path
#     }
#
#     result_poly = processing.run("gdal:polygonize", parameter_poly)
#     poly_output = result_poly['OUTPUT']
#
#     poly_name = os.path.splitext(
#         os.path.basename(poly_path))[0]
#
#     poly_layer = QgsVectorLayer(
#         poly_path,
#         poly_name
#     )
#
#     project.addMapLayer(poly_layer)