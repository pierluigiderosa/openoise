# -*- coding: utf-8 -*-
"""
/***************************************************************************
 opeNoise

 Qgis Plugin to compute noise levels

                             -------------------
        begin                : February 2022
        copyright            : (C) 2022 by Arpa Piemonte
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

#from PyQt4.QtCore import *
import pandas as pd
import numpy as np
from builtins import str
from statistics import median
from qgis.PyQt.QtCore import QObject
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QDialog
#from qgis.core import *
from qgis.PyQt.QtWidgets import QDialogButtonBox
from qgis.PyQt.QtWidgets import QMessageBox

from qgis.core import (QgsProject,QgsVectorLayer,QgsFeature,
                       QgsWkbTypes,QgsFieldProxyModel,
                       QgsField, QgsMapLayerProxyModel)
try:
    from qgis.core import Qgis
except ImportError:
    from qgis.core import QGis as Qgis
from qgis.PyQt import uic
import os, sys, shutil
import traceback

#from math import *
from datetime import datetime
sys.path.append(os.path.dirname(__file__))
Ui_AssignLevelsToBuildings_window, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_AssignLevelsToBuildings.ui'), resource_suffix='')

from . import on_ApplyNoiseSymbology

def CreateTempDir():

    global temp_dir

    currentPath = os.path.dirname(__file__)
    temp_dir = os.path.abspath(os.path.join(currentPath + os.sep +'temp'))

    if os.path.isdir(temp_dir):
        DeleteTempDir()

    os.mkdir(temp_dir)

def DeleteTempDir():

    shutil.rmtree(temp_dir)

class Dialog(QDialog,Ui_AssignLevelsToBuildings_window):

    def __init__(self, iface):
        QDialog.__init__(self, iface.mainWindow())
        self.iface = iface
        # Set up the user interface from Designer.
        self.setupUi(self)

        string = self.tr("WARNING:") + '\n' +\
                 self.tr("This script works correctly only if the receiver points layer ") + '\n' +\
                 self.tr("is created from a buildings layer with opeNoise") + '\n' +\
                 self.tr("and its structure is not modified.")
        QMessageBox.information(self, self.tr("opeNoise - Assign Levels To Buildings"), self.tr(string))

        self.populate_comboBox()

        self.progressBar.setValue(0)

        self.run_buttonBox.button( QDialogButtonBox.Ok )

        self.receiver_points_layer_comboBox.currentIndexChanged.connect(self.update_field_receiver_points_layer)

        self.receiver_points_population_field.setFilters(
            QgsFieldProxyModel.Double | QgsFieldProxyModel.Int | QgsFieldProxyModel.Numeric)


    def populate_comboBox( self ):
        if Qgis.QGIS_VERSION_INT < 31401:
            self.receiver_points_layer_comboBox.clear()
        #self.receiver_points_layer_comboBox.setAllowEmptyLayer(True)
        self.receiver_points_layer_comboBox.setFilters(QgsMapLayerProxyModel.PointLayer)

        self.update_field_receiver_points_layer()

        if Qgis.QGIS_VERSION_INT < 31401:
            self.buildings_layer_comboBox.clear()
        self.buildings_layer_comboBox.setFilters(QgsMapLayerProxyModel.PolygonLayer)

        self.receiver_points_population_field.setLayer(self.buildings_layer_comboBox.currentLayer())
        self.receiver_points_population_field.setAllowEmptyFieldName(True)

        #self.buildings_layer_comboBox.addItems(buildings_layers)

    def outputTempTable(self,pddf,tablename):
        vl = QgsVectorLayer("None", tablename, "memory")
        pr = vl.dataProvider()
        pr.addAttributes([QgsField("level", QVariant.String),
                          QgsField("population", QVariant.Double)])
        vl.updateFields()
        labelsLev = ["<=35.0 dB(A)", "35 - 40 dB(A)", "40 - 45 dB(A)", "45 - 50 dB(A)",
                     "50 - 55 dB(A)", "55 - 60 dB(A)", "60 - 65 dB(A)", "65 - 70 dB(A)",
                     "70 - 75 dB(A)", "75 - 80 dB(A)", ">80 dB(A) lk mjkvm k"]
        for idx in range(len(pddf.values)):
            f = QgsFeature()
            f.setAttributes([labelsLev[idx], round(float(pddf.values[idx]), 2)])
            pr.addFeature(f)
        QgsProject.instance().addMapLayer(vl)


    def update_field_receiver_points_layer(self):

        if str(self.receiver_points_layer_comboBox.currentText()) == "":
            return

        receiver_points_layer = QgsProject.instance().mapLayersByName(self.receiver_points_layer_comboBox.currentText())[0]
        receiver_points_layer_fields = list(receiver_points_layer.dataProvider().fields())


        #self.id_field_comboBox.clear()
        self.level_1_comboBox.clear()
        self.level_2_comboBox.clear()
        self.level_3_comboBox.clear()
        self.level_4_comboBox.clear()
        self.level_5_comboBox.clear()

        receiver_points_layer_fields_number = [""]

        for f in receiver_points_layer_fields:
            if f.type() == QVariant.Int or f.type() == QVariant.Double:
                receiver_points_layer_fields_number.append(str(f.name()))

        if Qgis.QGIS_VERSION_INT < 31401:
            for f_label in receiver_points_layer_fields_number:
                #self.id_field_comboBox.addItem(f_label)
                self.level_1_comboBox.addItem(f_label)
                self.level_2_comboBox.addItem(f_label)
                self.level_3_comboBox.addItem(f_label)
                self.level_4_comboBox.addItem(f_label)
                self.level_5_comboBox.addItem(f_label)


    def controls(self):
        self.run_buttonBox.setEnabled( False )
        if self.receiver_points_layer_comboBox.currentText() == "":
            QMessageBox.information(self, self.tr("opeNoise - Assign Levels To Buildings"), self.tr("Please specify the receiver points vector layer."))
            return 0

        if self.level_1_comboBox.currentText() == "" and self.level_2_comboBox.currentText() == ""\
           and self.level_3_comboBox.currentText() == "" and self.level_4_comboBox.currentText() == ""\
           and self.level_5_comboBox.currentText() == "":
               message = self.tr("Please specify at least one level field to assing") + "\n" + self.tr("to the buildings layer.")
               QMessageBox.information(self, self.tr("opeNoise - Assign Levels To Buildings"), self.tr(message))
               return 0

        if self.buildings_layer_comboBox.currentText() == "":
            QMessageBox.information(self, self.tr("opeNoise - Assign Levels To Buildings"), self.tr("Please specify the buildings vector layer."))
            return 0

        return 1

    def populate_receiver_points_fields(self):

        receiver_points_dict = {}

        receiver_points_dict['id_field'] = 'id_bui'

        if self.level_1_comboBox.currentText() == '':
            receiver_points_dict['level_1'] = 'none'
        else:
            receiver_points_dict['level_1'] = self.level_1_comboBox.currentText()

        if self.level_2_comboBox.currentText() == '':
            receiver_points_dict['level_2'] = 'none'
        else:
            receiver_points_dict['level_2'] = self.level_2_comboBox.currentText()

        if self.level_3_comboBox.currentText() == '':
            receiver_points_dict['level_3'] = 'none'
        else:
            receiver_points_dict['level_3'] = self.level_3_comboBox.currentText()

        if self.level_4_comboBox.currentText() == '':
            receiver_points_dict['level_4'] = 'none'
        else:
            receiver_points_dict['level_4'] = self.level_4_comboBox.currentText()

        if self.level_5_comboBox.currentText() == '':
            receiver_points_dict['level_5'] = 'none'
        else:
            receiver_points_dict['level_5'] = self.level_5_comboBox.currentText()

        return receiver_points_dict


    def check_oldFields(self):
        buildings_layer = QgsProject.instance().mapLayersByName(self.buildings_layer_comboBox.currentText())[0]
        buildings_layer = self.buildings_layer_comboBox.currentLayer()
        buildings_layer_fields = buildings_layer.fields()
        fields = [x.name() for x in buildings_layer_fields.toList()]

        # get period to assign
        fields_to_calculate = []
        if self.level_1_comboBox.currentText() != "":
            fields_to_calculate.append(self.level_1_comboBox.currentText())
        if self.level_2_comboBox.currentText() != "":
            fields_to_calculate.append(self.level_2_comboBox.currentText())
        if self.level_3_comboBox.currentText() != "":
            fields_to_calculate.append(self.level_3_comboBox.currentText())
        if self.level_4_comboBox.currentText() != "":
            fields_to_calculate.append(self.level_4_comboBox.currentText())
        if self.level_5_comboBox.currentText() != "":
            fields_to_calculate.append(self.level_5_comboBox.currentText())

        #print("fields_to_calculate",fields_to_calculate)
        #personal_fields = ['gen', 'day', 'eve', 'nig','den']
        fields_already_present = list(set(fields_to_calculate) & set(fields))
        if fields_already_present:
            overwrite_begin = self.tr("In buildings layer you already have the fields: ")
            overwrite_end = self.tr(" . Do you want to overwrite data in attribute table?")
            reply = QMessageBox.question(self, self.tr("opeNoise - Assign Levels To Buildings"),
                                           overwrite_begin + '\n' + str(fields_already_present) + overwrite_end, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                reply2 = QMessageBox.question(self, self.tr("opeNoise - Assign Levels To Buildings"),
                                               self.tr("To mantain old data, copy them in a new field."), QMessageBox.Ok)
                return False
            else:
                fList = []
                for field_to_delete in fields_already_present:
                    idx_field = buildings_layer.dataProvider().fieldNameIndex(field_to_delete)
                    fList.append(idx_field)

                buildings_layer.dataProvider().deleteAttributes(fList)
                buildings_layer.updateFields()
                return True
        else:
            return True



    def accept(self):
        self.run_buttonBox.setEnabled( False )

        if self.controls() == 0:
            self.run_buttonBox.setEnabled( True )
            return

        self.log_start()
        receiver_points_layer = QgsProject.instance().mapLayersByName(self.receiver_points_layer_comboBox.currentText())[0]
        receiver_points_layer_details = self.populate_receiver_points_fields()
        buildings_layer = QgsProject.instance().mapLayersByName(self.buildings_layer_comboBox.currentText())[0]
        building_pop_Field = self.receiver_points_population_field.currentText()


        # CRS control (each layer must have the same CRS)
        if receiver_points_layer.crs().authid() != buildings_layer.crs().authid():
            QMessageBox.information(self, self.tr("opeNoise - Assign Levels To Buildings"), self.tr("The layers don't have the same CRS (Coordinate Reference System). Please use layers with same CRS."))
            self.run_buttonBox.setEnabled( True )
            return


        # check old fields in buildings
        if self.check_oldFields() == False:
            return


        self.time_start = datetime.now()

        # Run
        try:
            self.runLevelBuilding(receiver_points_layer,receiver_points_layer_details,buildings_layer,building_pop_Field)
            run = 1
        except:
            error= traceback.format_exc()
            log_errors.write(error)
            run = 0

        self.time_end = datetime.now()

        if run == 1:
            log_errors.write(self.tr("No errors.") + "\n\n")
            result_string = self.tr("Noise levels assigned with success.") + "\n\n" +\
                            self.tr("Start: ") + self.time_start.strftime("%a %d/%b/%Y %H:%M:%S") + "\n" +\
                            self.tr("End: ") + self.time_end.strftime("%a %d/%b/%Y %H:%M:%S") + "\n"+\
                            self.tr("Duration: ") + str(self.duration())
            QMessageBox.information(self, self.tr("opeNoise - Assign Levels To Buildings"), self.tr(result_string))
#            self.iface.messageBar().pushMessage(self.tr("opeNoise - Assign Levels To Buildings"), self.tr("Process complete"))
        else:
            result_string = self.tr("Sorry, process not complete.") + "\n\n" +\
                            self.tr("View the log file to understand the problem:") + "\n" +\
                            str(log_errors_path_name) + "\n\n" +\
                            self.tr("Start: ") + self.time_start.strftime("%a %d/%b/%Y %H:%M:%S.%f") + "\n" +\
                            self.tr("End: ") + self.time_end.strftime("%a %d/%b/%Y %H:%M:%S.%f") + "\n"+\
                            self.tr("Duration: ") + str(self.duration())
            QMessageBox.information(self, self.tr("opeNoise - Assign Levels To Buildings"), self.tr(result_string))
#            self.iface.messageBar().pushMessage(self.tr("opeNoise - Assign Levels To Buildings"), self.tr("Process not complete"))

        self.log_end()

        self.run_buttonBox.setEnabled( True )

#        self.iface.mainWindow().statusBar().clearMessage()
#        self.iface.mapCanvas().refresh()
        self.close()


    def duration(self):
        duration = self.time_end - self.time_start
        duration_h = duration.seconds // 3600
        duration_m = (duration.seconds // 60) % 60
        duration_s = duration.seconds
        duration_string = str(format(duration_h, '02')) + ':' + str(format(duration_m, '02')) + ':' + str(
            format(duration_s, '02'))
        return duration_string



    def log_start(self):

        global log_errors, log_errors_path_name
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        log_errors_path_name = os.path.join(dir_path,"log_AssignLevelsToBuildings_errors.txt")
        log_errors = open(log_errors_path_name,"w")
        log_errors.write(self.tr("opeNoise") + " - " + self.tr("Assign Levels To Buildings") + " - " + self.tr("Errors") + "\n\n")

    def log_end(self):

        log_errors.close()

    def popMedianAssign(self,popDic, buildingLevel, mediane):
        outPop = list()
        for id_bui in buildingLevel.keys():
            livelli = buildingLevel[id_bui]
            abitanti = popDic[id_bui]
            # remove minimum value in case even receivers
            if len(livelli) % 2 != 0:
                livelli.remove(min(livelli))

            livelliFiltered = [x for x in livelli if x > mediane[id_bui][0]]
            if len(livelliFiltered) == 0:
                outPop.append([0, abitanti, id_bui])
            else:
                for livello in livelliFiltered:
                    outPop.append([livello, abitanti / len(livelliFiltered), id_bui])

        df1 = pd.DataFrame(outPop, columns=['levels', 'popolazione', 'id_bui'])
        bins = pd.cut(df1['levels'], [-np.inf, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, np.inf])
        df2=df1.groupby(bins)['popolazione'].agg(['sum'])
        df3 = df2.rename({'sum': 'population'}, axis=1)
        return df3



    def runLevelBuilding(self,receiver_points_layer,receiver_points_layer_details,buildings_layer,building_pop_Field):

        CreateTempDir()

        # gets vector layers, features receiver points
        receiver_points_feat_total = receiver_points_layer.dataProvider().featureCount()
        receiver_points_feat_all = receiver_points_layer.dataProvider().getFeatures()

        # gets fields index from receiver points layer
        receiver_points_fields_index = {}
        receiver_points_fields_index['id_field'] = receiver_points_layer.dataProvider().fieldNameIndex(str(receiver_points_layer_details['id_field']))
        if receiver_points_layer_details['level_1'] != 'none':
            level_1_name = receiver_points_layer_details['level_1']
            receiver_points_fields_index['level_1'] = receiver_points_layer.dataProvider().fieldNameIndex(receiver_points_layer_details['level_1'])
        if receiver_points_layer_details['level_2'] != 'none':
            level_2_name = receiver_points_layer_details['level_2']
            receiver_points_fields_index['level_2'] = receiver_points_layer.dataProvider().fieldNameIndex(receiver_points_layer_details['level_2'])
        if receiver_points_layer_details['level_3'] != 'none':
            level_3_name = receiver_points_layer_details['level_3']
            receiver_points_fields_index['level_3'] = receiver_points_layer.dataProvider().fieldNameIndex(receiver_points_layer_details['level_3'])
        if receiver_points_layer_details['level_4'] != 'none':
            level_4_name = receiver_points_layer_details['level_4']
            receiver_points_fields_index['level_4'] = receiver_points_layer.dataProvider().fieldNameIndex(receiver_points_layer_details['level_4'])
        if receiver_points_layer_details['level_5'] != 'none':
            level_5_name = receiver_points_layer_details['level_5']
            receiver_points_fields_index['level_5'] = receiver_points_layer.dataProvider().fieldNameIndex(receiver_points_layer_details['level_5'])

        # gets fields from buildings layer and initializes the final buildings_levels_fields to populate the buildings layer attribute table
        buildings_fields_index = {}
        buildings_fields_number = int(buildings_layer.dataProvider().fields().count())
        if receiver_points_layer_details['level_1'] != 'none':
            buildings_fields_index['level_1'] = buildings_fields_number
            buildings_fields_number = buildings_fields_number + 1
        if receiver_points_layer_details['level_2'] != 'none':
            buildings_fields_index['level_2'] = buildings_fields_number
            buildings_fields_number = buildings_fields_number + 1
        if receiver_points_layer_details['level_3'] != 'none':
            buildings_fields_index['level_3'] = buildings_fields_number
            buildings_fields_number = buildings_fields_number + 1
        if receiver_points_layer_details['level_4'] != 'none':
            buildings_fields_index['level_4'] = buildings_fields_number
            buildings_fields_number = buildings_fields_number + 1
        if receiver_points_layer_details['level_5'] != 'none':
            buildings_fields_index['level_5'] = buildings_fields_number
            buildings_fields_number = buildings_fields_number + 1

        receiver_points_feat_number = 0

        buildings_levels_fields = {}

        # dict storing values for building
        buildings_levels_from_receiverL1 = {}
        buildings_levels_from_receiverL2 = {}
        buildings_levels_from_receiverL3 = {}
        buildings_levels_from_receiverL4 = {}
        buildings_levels_from_receiverL5 = {}

        for featReceiver in receiver_points_feat_all:

            receiver_points_feat_number = receiver_points_feat_number + 1
            bar = receiver_points_feat_number/float(receiver_points_feat_total)*100
            self.progressBar.setValue(bar)

            feat_levels_fields = {}

            id_edi = featReceiver.attributes()[receiver_points_fields_index['id_field']]



            if receiver_points_layer_details['level_1'] != 'none':
                level_1 = featReceiver.attributes()[receiver_points_fields_index['level_1']]
                feat_levels_fields[buildings_fields_index['level_1']] = level_1
            if receiver_points_layer_details['level_2'] != 'none':
                level_2 = featReceiver.attributes()[receiver_points_fields_index['level_2']]
                feat_levels_fields[buildings_fields_index['level_2']] = level_2
            if receiver_points_layer_details['level_3'] != 'none':
                level_3 = featReceiver.attributes()[receiver_points_fields_index['level_3']]
                feat_levels_fields[buildings_fields_index['level_3']] = level_3
            if receiver_points_layer_details['level_4'] != 'none':
                level_4 = featReceiver.attributes()[receiver_points_fields_index['level_4']]
                feat_levels_fields[buildings_fields_index['level_4']] = level_4
            if receiver_points_layer_details['level_5'] != 'none':
                level_5 = featReceiver.attributes()[receiver_points_fields_index['level_5']]
                feat_levels_fields[buildings_fields_index['level_5']] = level_5

            # assing maximum value level to building
            if (id_edi in buildings_levels_fields) == True:
                if receiver_points_layer_details['level_1'] != 'none':
                    if (buildings_levels_fields[id_edi][buildings_fields_index['level_1']] < level_1 and level_1 != None) or\
                      buildings_levels_fields[id_edi][buildings_fields_index['level_1']] == None:
                        buildings_levels_fields[id_edi][buildings_fields_index['level_1']] = level_1
                if receiver_points_layer_details['level_2'] != 'none':
                    if (buildings_levels_fields[id_edi][buildings_fields_index['level_2']] < level_2 and level_2 != None) or\
                      buildings_levels_fields[id_edi][buildings_fields_index['level_2']] == None:
                        buildings_levels_fields[id_edi][buildings_fields_index['level_2']] = level_2
                if receiver_points_layer_details['level_3'] != 'none':
                    if (buildings_levels_fields[id_edi][buildings_fields_index['level_3']] < level_3 and level_3 != None) or\
                      buildings_levels_fields[id_edi][buildings_fields_index['level_3']] == None:
                        buildings_levels_fields[id_edi][buildings_fields_index['level_3']] = level_3
                if receiver_points_layer_details['level_4'] != 'none':
                    if (buildings_levels_fields[id_edi][buildings_fields_index['level_4']] < level_4 and level_4 != None) or\
                      buildings_levels_fields[id_edi][buildings_fields_index['level_4']] == None:
                        buildings_levels_fields[id_edi][buildings_fields_index['level_4']] = level_4
                if receiver_points_layer_details['level_5'] != 'none':
                    if (buildings_levels_fields[id_edi][buildings_fields_index['level_5']] < level_5 and level_5 != None) or\
                      buildings_levels_fields[id_edi][buildings_fields_index['level_5']] == None:
                        buildings_levels_fields[id_edi][buildings_fields_index['level_5']] = level_5

            else:
                buildings_levels_fields[id_edi] = feat_levels_fields
        #     --------------
            if building_pop_Field != '':
                # Assigning dwellings and people living in dwellings to receiver points PAG 37 Directive 2020
                # creo dizionario che contiene per ogni edificio i livelli di ogni ricettore
                if receiver_points_layer_details['level_1'] != 'none':
                    if level_1 < 0: # filter in case level is -99
                        level_1 = 0
                    if id_edi in buildings_levels_from_receiverL1:
                        buildings_levels_from_receiverL1[id_edi].append(level_1)
                    else:
                        buildings_levels_from_receiverL1[id_edi] = [level_1]

                if receiver_points_layer_details['level_2'] != 'none':
                    if level_2 < 0:
                        level_2 = 0
                    if id_edi in buildings_levels_from_receiverL2:
                        buildings_levels_from_receiverL2[id_edi].append(level_2)
                    else:
                        buildings_levels_from_receiverL2[id_edi] = [level_2]

                if receiver_points_layer_details['level_3'] != 'none':
                    if level_3 < 0:
                        level_3 = 0
                    if id_edi in buildings_levels_from_receiverL3:
                        buildings_levels_from_receiverL3[id_edi].append(level_3)
                    else:
                        buildings_levels_from_receiverL3[id_edi] = [level_3]

                if receiver_points_layer_details['level_4'] != 'none':
                    if level_4 < 0:
                        level_4 = 0
                    if id_edi in buildings_levels_from_receiverL4:
                        buildings_levels_from_receiverL4[id_edi].append(level_4)
                    else:
                        buildings_levels_from_receiverL4[id_edi] = [level_4]

                if receiver_points_layer_details['level_5'] != 'none':
                    if level_5 < 0:
                        level_5 = 0
                    if id_edi in buildings_levels_from_receiverL5:
                        buildings_levels_from_receiverL5[id_edi].append(level_5)
                    else:
                        buildings_levels_from_receiverL5[id_edi] = [level_5]

        if building_pop_Field != '':
            # creation of dict that stores median e numbers of receiver relater to any buildings
            buildings_medianL1=dict()
            buildings_medianL2 = dict()
            buildings_medianL3 = dict()
            buildings_medianL4 = dict()
            buildings_medianL5 = dict()
            if receiver_points_layer_details['level_1'] != 'none':
                for keysB, valueB in buildings_levels_from_receiverL1.items():
                    buildings_medianL1[keysB] = (median(valueB), len(valueB) )

            if receiver_points_layer_details['level_2'] != 'none':
                for keysB, valueB in buildings_levels_from_receiverL2.items():
                    buildings_medianL2[keysB] = (median(valueB), len(valueB))

            if receiver_points_layer_details['level_3'] != 'none':
                for keysB, valueB in buildings_levels_from_receiverL3.items():
                    buildings_medianL3[keysB] = (median(valueB), len(valueB))

            if receiver_points_layer_details['level_4'] != 'none':
                for keysB, valueB in buildings_levels_from_receiverL4.items():
                    buildings_medianL4[keysB] = (median(valueB), len(valueB))

            if receiver_points_layer_details['level_5'] != 'none':
                for keysB, valueB in buildings_levels_from_receiverL5.items():
                    buildings_medianL5[keysB] = (median(valueB), len(valueB))

            # extract population from building layer and store in
            buildingPop = dict()
            for bFeat in buildings_layer.getFeatures():
                buildingPop[bFeat.id()] = bFeat[building_pop_Field]
            print('pop: ',buildingPop)
            print('BLeve1: ', buildings_levels_from_receiverL1)

            if receiver_points_layer_details['level_1'] != 'none':
                df1 = self.popMedianAssign(buildingPop,
                                     buildings_levels_from_receiverL1,
                                     buildings_medianL1)
                self.outputTempTable(df1,"Population - Lev1")
                print('L1 pop',df1)
            if receiver_points_layer_details['level_2'] != 'none':
                df2 = self.popMedianAssign(buildingPop,
                                     buildings_levels_from_receiverL2,
                                     buildings_medianL2)
                self.outputTempTable(df2,"Population - Lev2")
                print('L2 pop',df2)
            if receiver_points_layer_details['level_3'] != 'none':
                df3 = self.popMedianAssign(buildingPop,
                                     buildings_levels_from_receiverL3,
                                     buildings_medianL3)
                self.outputTempTable(df3,"Population - Lev3")
                print('L3 pop',df3)
            if receiver_points_layer_details['level_4'] != 'none':
                df4 = self.popMedianAssign(buildingPop,
                                     buildings_levels_from_receiverL4,
                                     buildings_medianL4)
                self.outputTempTable(df4,"Population - Lev4")
                print('L3 pop',df4)
            if receiver_points_layer_details['level_5'] != 'none':
                df5 = self.popMedianAssign(buildingPop,
                                     buildings_levels_from_receiverL5,
                                     buildings_medianL5)
                self.outputTempTable(df5,"Population - Lev5")
                print('L3 pop',df5)



            # del buildings_levels_from_receiverL2
            # del buildings_levels_from_receiverL3
            # del buildings_levels_from_receiverL4
            # del buildings_levels_from_receiverL5

            print('L1:',buildings_medianL1)
            print('L2',buildings_medianL2)
            print('L3',buildings_medianL3)
            print('L4',buildings_medianL4)
            print('L5',buildings_medianL5)
        # -- end new part

        # puts the sound level in the buildings attribute table
        new_level_fields = []
        if receiver_points_layer_details['level_1'] != 'none':
            new_level_fields.append(QgsField(level_1_name, QVariant.Double,len=5,prec=1))
        if receiver_points_layer_details['level_2'] != 'none':
            new_level_fields.append(QgsField(level_2_name, QVariant.Double,len=5,prec=1))
        if receiver_points_layer_details['level_3'] != 'none':
            new_level_fields.append(QgsField(level_3_name, QVariant.Double,len=5,prec=1))
        if receiver_points_layer_details['level_4'] != 'none':
            new_level_fields.append(QgsField(level_4_name, QVariant.Double,len=5,prec=1))
        if receiver_points_layer_details['level_5'] != 'none':
            new_level_fields.append(QgsField(level_5_name, QVariant.Double,len=5,prec=1))

        buildings_layer.dataProvider().addAttributes( new_level_fields )
        buildings_layer.updateFields()
        buildings_layer.dataProvider().changeAttributeValues(buildings_levels_fields)

        # render with noise colours
        level_fields_new = list(buildings_layer.dataProvider().fields())
        if len(level_fields_new) > 0:
            on_ApplyNoiseSymbology.renderizeXY(buildings_layer, level_fields_new[len(level_fields_new) - 1].name())
