# -*- coding: utf-8 -*-
"""
/***************************************************************************
 opeNoise
 Qgis Plugin to compute noise levels
                             -------------------
        begin                : February 2019
        copyright            : (C) 2019 by Arpa Piemonte
        email                : s.masera@arpa.piemonte.it
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import QgsProject, QgsMapLayerProxyModel

try:
    from qgis.core import Qgis
except ImportError:
    from qgis.core import QGis as Qgis
from qgis.PyQt import QtCore
from PyQt5 import QtGui, uic
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog

import os
import sys

from . import on_CreateGrid, on_Settings

ui_path = os.path.join(
    os.path.dirname(__file__),
    'ui_CreateGrid.ui'
)

FORM_CLASS, _ = uic.loadUiType(ui_path, resource_suffix='')


class Dialog(QDialog, FORM_CLASS):

    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.iface = iface
        self.setupUi(self)
        self.populate_overlayLayer()
        self.populate_layerTOrasterize()
        self.gridSave_pushButton.clicked.connect(self.outputFile_grid)
        self.rasterSave_pushButton.clicked.connect(self.outputFile_raster)
        self.isolineSave_pushButton.clicked.connect(self.outputFile_contour)
        self.polygonSave_pushButton.clicked.connect(self.outputFile_polygon)
        self.runGrid_pushButton.clicked.connect(self.runGrid)
        self.runRaster_pushButton.clicked.connect(self.runRasterize)
        self.runContPoly_pushButton.clicked.connect(self.runContPoly)

        spacing = ['5', '10', '20', '30', '40', '50']
        self.resolution_comboBox.clear()
        self.resolution_raster_comboBox.clear()
        for space in spacing:
            self.resolution_comboBox.addItem(space)
            self.resolution_raster_comboBox.addItem(space)

    def populate_overlayLayer(self):

        if Qgis.QGIS_VERSION_INT < 31401:
            self.overlayLayer_ComboBox.clear()
        self.overlayLayer_ComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer)

    def populate_layerTOrasterize(self):

        if Qgis.QGIS_VERSION_INT < 31401:
            self.layerTOrasterize_ComboBox.clear()
        self.layerTOrasterize_ComboBox.setFilters(QgsMapLayerProxyModel.VectorLayer)

    def populate_rasterTOcontour(self):

        if Qgis.QGIS_VERSION_INT < 31401:
            self.rasterISOL_ComboBox.clear()
        self.rasterISOL_ComboBox.setFilters(QgsMapLayerProxyModel.RasterLayer)

    def outputFile_grid(self):

        self.gridpoint_lineEdit.clear()
        self.fileName = QFileDialog.getSaveFileName(
            None,
            'Open file',
            on_Settings.getOneSetting('directory_last'),
            "Shapefile (*.shp);;All files (*)"
        )

        if self.fileName is None or self.fileName == "":
            return

        if str.find(self.fileName[0], ".shp") == -1 and str.find(self.fileName[0], ".SHP") == -1:
            self.gridpoint_lineEdit.setText(self.fileName[0] + ".shp")
        else:
            self.gridpoint_lineEdit.setText(self.fileName[0])

        pathFile = on_Settings.setOneSetting(
            'directory_last',
            os.path.dirname(self.gridpoint_lineEdit.text())
        )

    def outputFile_raster(self):

        self.raster_lineEdit.clear()
        self.fileName = QFileDialog.getSaveFileName(
            None,
            'Open file',
            on_Settings.getOneSetting('directory_last'),
            "Raster (*.tif);;All files (*)"
        )

        if self.fileName is None or self.fileName == "":
            return

        if str.find(self.fileName[0], ".tif") == -1 and str.find(self.fileName[0], ".TIF") == -1:
            self.raster_lineEdit.setText(self.fileName[0] + ".tif")
        else:
            self.raster_lineEdit.setText(self.fileName[0])

        pathFile = on_Settings.setOneSetting(
            'directory_last',
            os.path.dirname(self.raster_lineEdit.text())
        )

    def outputFile_contour(self):

        self.isoline_lineEdit.clear()
        self.fileName = QFileDialog.getSaveFileName(
            None,
            'Open file',
            on_Settings.getOneSetting('directory_last'),
            "Shapefile (*.shp);;All files (*)"
        )

        if self.fileName is None or self.fileName == "":
            return

        if str.find(self.fileName[0], ".shp") == -1 and str.find(self.fileName[0], ".SHP") == -1:
            self.isoline_lineEdit.setText(self.fileName[0] + ".shp")
        else:
            self.isoline_lineEdit.setText(self.fileName[0])

        pathFile = on_Settings.setOneSetting(
            'directory_last',
            os.path.dirname(self.isoline_lineEdit.text())
        )

    def outputFile_polygon(self):

        self.polygon_lineEdit.clear()
        self.fileName = QFileDialog.getSaveFileName(
            None,
            'Open file',
            on_Settings.getOneSetting('directory_last'),
            "Shapefile (*.shp);;All files (*)"
        )

        if self.fileName is None or self.fileName == "":
            return

        if str.find(self.fileName[0], ".shp") == -1 and str.find(self.fileName[0], ".SHP") == -1:
            self.polygon_lineEdit.setText(self.fileName[0] + ".shp")
        else:
            self.polygon_lineEdit.setText(self.fileName[0])

        pathFile = on_Settings.setOneSetting(
            'directory_last',
            os.path.dirname(self.polygon_lineEdit.text())
        )

    def runGrid(self):

        resolution = int(self.resolution_comboBox.currentText())
        overlay_layer = self.overlayLayer_ComboBox.currentLayer()
        overlay_layer_path = overlay_layer.source()
        grid_path = self.gridpoint_lineEdit.text()

        on_CreateGrid.createGrid(
            resolution,
            overlay_layer_path,
            grid_path
        )

    def runRasterize(self):

        resolution = int(self.resolution_raster_comboBox.currentText())
        layerTOrasterize = self.layerTOrasterize_ComboBox.currentLayer()
        layerTOrasterize_path = layerTOrasterize.source()
        field = self.fieldsLayer_ComboBox.currentText()
        raster_path = self.raster_lineEdit.text()

        on_CreateGrid.createRaster(
            resolution,
            layerTOrasterize_path,
            field,
            raster_path
        )

    # run Contour and Polygonize
    def runContPoly(self):

        raster = self.rasterISOL_ComboBox.currentLayer()
        raster_path = raster.source()

        minimum = self.min_spinBox.value()
        maximum = self.max_spinBox.value()
        interval = self.interval_spinBox.value()

        contour_path = self.isoline_lineEdit.text()
        poly_path = self.polygon_lineEdit.text()

        # create isolines
        on_CreateGrid.createContour(
            raster_path,
            interval,
            contour_path
        )

        # create polygon from reclassified raster
        on_CreateGrid.polygonize(
            raster_path,
            minimum,
            maximum,
            interval,
            poly_path
        )