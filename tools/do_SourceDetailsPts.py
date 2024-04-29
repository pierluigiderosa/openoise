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

from builtins import str


from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsFieldProxyModel

import os, sys

sys.path.append(os.path.dirname(__file__))
SourceDetails_ui, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_SourceDetailsPts.ui'), resource_suffix='')

from. import on_Settings




class Dialog(QDialog,SourceDetails_ui):

    def __init__(self, iface,layer_name):
        QDialog.__init__(self, iface.mainWindow())
        self.iface = iface
        # Set up the user interface from Designer.
        self.setupUi(self)

        self.layer_name = layer_name

        # set widget
        self.POWER_P_radioButton.setChecked(0)
        self.POWER_P_freq_radioButton.setChecked(0)

        self.POWER_P_radioButton.toggled.connect(self.POWERstackedWidget_update)
        self.POWER_P_freq_radioButton.toggled.connect(self.POWERstackedWidget_update)

        self.InfoButtonBands.clicked.connect(self.HelpBands_show)


        # start definition
        self.POWER_P_emission_comboBoxes_dict = {
                                                'POWER_P_gen' : self.POWER_P_L_gen_comboBox,
                                                'POWER_P_day' : self.POWER_P_L_day_comboBox,
                                                'POWER_P_eve' : self.POWER_P_L_eve_comboBox,
                                                'POWER_P_nig' : self.POWER_P_L_nig_comboBox
                                                }
        self.POWER_P_Freq_GEN_comboboxes_dict = {'POWER_P_GEN_63': self.POWER_P_63_gen_combo,
                                                 'POWER_P_GEN_125': self.POWER_P_125_gen_combo,
                                                 'POWER_P_GEN_250': self.POWER_P_250_gen_combo,
                                                 'POWER_P_GEN_500': self.POWER_P_500_gen_combo,
                                                 'POWER_P_GEN_1000': self.POWER_P_1000_gen_combo,
                                                 'POWER_P_GEN_2000': self.POWER_P_2000_gen_combo,
                                                 'POWER_P_GEN_4000': self.POWER_P_4000_gen_combo,
                                                 'POWER_P_GEN_8000': self.POWER_P_8000_gen_combo,
                                                 }
        self.POWER_P_Freq_DAY_comboboxes_dict = {'POWER_P_DAY_63': self.POWER_P_63_day_combo,
                                                 'POWER_P_DAY_125': self.POWER_P_125_day_combo,
                                                 'POWER_P_DAY_250': self.POWER_P_250_day_combo,
                                                 'POWER_P_DAY_500': self.POWER_P_500_day_combo,
                                                 'POWER_P_DAY_1000': self.POWER_P_1000_day_combo,
                                                 'POWER_P_DAY_2000': self.POWER_P_2000_day_combo,
                                                 'POWER_P_DAY_4000': self.POWER_P_4000_day_combo,
                                                 'POWER_P_DAY_8000': self.POWER_P_8000_day_combo,
                                                 }
        self.POWER_P_Freq_EVE_comboboxes_dict = {'POWER_P_EVE_63': self.POWER_P_63_eve_combo,
                                                 'POWER_P_EVE_125': self.POWER_P_125_eve_combo,
                                                 'POWER_P_EVE_250': self.POWER_P_250_eve_combo,
                                                 'POWER_P_EVE_500': self.POWER_P_500_eve_combo,
                                                 'POWER_P_EVE_1000': self.POWER_P_1000_eve_combo,
                                                 'POWER_P_EVE_2000': self.POWER_P_2000_eve_combo,
                                                 'POWER_P_EVE_4000': self.POWER_P_4000_eve_combo,
                                                 'POWER_P_EVE_8000': self.POWER_P_8000_eve_combo,
                                                 }
        self.POWER_P_Freq_NIG_comboboxes_dict = {'POWER_P_NIG_63': self.POWER_P_63_nig_combo,
                                                 'POWER_P_NIG_125': self.POWER_P_125_nig_combo,
                                                 'POWER_P_NIG_250': self.POWER_P_250_nig_combo,
                                                 'POWER_P_NIG_500': self.POWER_P_500_nig_combo,
                                                 'POWER_P_NIG_1000': self.POWER_P_1000_nig_combo,
                                                 'POWER_P_NIG_2000': self.POWER_P_2000_nig_combo,
                                                 'POWER_P_NIG_4000': self.POWER_P_4000_nig_combo,
                                                 'POWER_P_NIG_8000': self.POWER_P_8000_nig_combo,
                                                 }

        self.all_emission_comboBoxes = [self.POWER_P_L_gen_comboBox, self.POWER_P_L_day_comboBox, self.POWER_P_L_eve_comboBox, self.POWER_P_L_nig_comboBox]

        self.all_emission_comboBoxes_Freq_GEN = [self.POWER_P_63_gen_combo, self.POWER_P_125_gen_combo,
                                                 self.POWER_P_250_gen_combo, self.POWER_P_500_gen_combo,
                                                 self.POWER_P_1000_gen_combo, self.POWER_P_2000_gen_combo,
                                                 self.POWER_P_4000_gen_combo, self.POWER_P_8000_gen_combo]
        self.all_emission_comboBoxes_Freq_DAY = [self.POWER_P_63_day_combo, self.POWER_P_125_day_combo,
                                                 self.POWER_P_250_day_combo, self.POWER_P_500_day_combo,
                                                 self.POWER_P_1000_day_combo, self.POWER_P_2000_day_combo,
                                                 self.POWER_P_4000_day_combo, self.POWER_P_8000_day_combo]
        self.all_emission_comboBoxes_Freq_EVE = [self.POWER_P_63_eve_combo, self.POWER_P_125_eve_combo,
                                                 self.POWER_P_250_eve_combo, self.POWER_P_500_eve_combo,
                                                 self.POWER_P_1000_eve_combo, self.POWER_P_2000_eve_combo,
                                                 self.POWER_P_4000_eve_combo, self.POWER_P_8000_eve_combo]
        self.all_emission_comboBoxes_Freq_NIG = [self.POWER_P_63_nig_combo, self.POWER_P_125_nig_combo,
                                                 self.POWER_P_250_nig_combo, self.POWER_P_500_nig_combo,
                                                 self.POWER_P_1000_nig_combo, self.POWER_P_2000_nig_combo,
                                                 self.POWER_P_4000_nig_combo, self.POWER_P_8000_nig_combo]
        

        self.source_checkBoxes = [self.POWER_P_L_gen_checkBox,self.POWER_P_L_day_checkBox,self.POWER_P_L_eve_checkBox,self.POWER_P_L_nig_checkBox]

        self.source_POWER_P_period_checkBoxes = [self.POWER_P_L_day_checkBox,self.POWER_P_L_eve_checkBox,self.POWER_P_L_nig_checkBox]
        # end definitions

        self.source_fields_update()

        for source_checkBox in self.source_checkBoxes:
            source_checkBox.setChecked(0)
            source_checkBox.toggled.connect(self.source_checkBox_update)

        self.POWER_P_L_gen_checkBox.toggled.connect(self.source_checkBox_update)

        # connection checkBox Freq and comboboxes
        self.POWER_P_L_gen_checkBox_Freq.toggled.connect(self.check_freq_gen_update)
        self.POWER_P_L_day_checkBox_Freq.toggled.connect(self.check_freq_gen_update)
        self.POWER_P_L_eve_checkBox_Freq.toggled.connect(self.check_freq_gen_update)
        self.POWER_P_L_nig_checkBox_Freq.toggled.connect(self.check_freq_gen_update)


        self.setToolTips()

        self.reload_settings()


    def POWERstackedWidget_update(self):
        if self.POWER_P_radioButton.isChecked():

            self.POWERstackedWidget.setCurrentIndex(0)

            self.POWER_P_L_gen_checkBox_Freq.setChecked(0)
            self.POWER_P_L_day_checkBox_Freq.setChecked(0)
            self.POWER_P_L_eve_checkBox_Freq.setChecked(0)
            self.POWER_P_L_nig_checkBox_Freq.setChecked(0)

        if self.POWER_P_freq_radioButton.isChecked():

            self.POWERstackedWidget.setCurrentIndex(1)

            self.POWER_P_L_gen_checkBox.setChecked(0)
            self.POWER_P_L_day_checkBox.setChecked(0)
            self.POWER_P_L_eve_checkBox.setChecked(0)
            self.POWER_P_L_nig_checkBox.setChecked(0)


    def source_fields_update(self):

        source_layer = QgsProject.instance().mapLayersByName(self.layer_name)[0]
        source_layer_fields = list(source_layer.dataProvider().fields())

        source_layer_fields_labels = [""]

        for f in source_layer_fields:
#            if f.type() == QVariant.Int or f.type() == QVariant.Double:
                source_layer_fields_labels.append(str(f.name()))


        for comboBox in self.all_emission_comboBoxes:
            comboBox.clear()
            comboBox.setEnabled(False)
            comboBox.setLayer(source_layer)

            comboBox.setFilters(QgsFieldProxyModel.Double | QgsFieldProxyModel.Int | QgsFieldProxyModel.Numeric)
            # for label in source_layer_fields_labels:
            #     comboBox.addItem(label)

        for comboBox in self.all_emission_comboBoxes_Freq_GEN:
            comboBox.clear()
            comboBox.setEnabled(False)
            comboBox.setLayer(source_layer)

            comboBox.setFilters(QgsFieldProxyModel.Double | QgsFieldProxyModel.Int | QgsFieldProxyModel.Numeric)
        for comboBox in self.all_emission_comboBoxes_Freq_DAY:
            comboBox.clear()
            comboBox.setEnabled(False)
            comboBox.setLayer(source_layer)

            comboBox.setFilters(QgsFieldProxyModel.Double | QgsFieldProxyModel.Int | QgsFieldProxyModel.Numeric)
        for comboBox in self.all_emission_comboBoxes_Freq_EVE:
            comboBox.clear()
            comboBox.setEnabled(False)
            comboBox.setLayer(source_layer)

            comboBox.setFilters(QgsFieldProxyModel.Double | QgsFieldProxyModel.Int | QgsFieldProxyModel.Numeric)
        for comboBox in self.all_emission_comboBoxes_Freq_NIG:
            comboBox.clear()
            comboBox.setEnabled(False)
            comboBox.setLayer(source_layer)

            comboBox.setFilters(QgsFieldProxyModel.Double | QgsFieldProxyModel.Int | QgsFieldProxyModel.Numeric)


    def source_checkBox_update(self):

        # POWER_P
        if self.POWER_P_L_gen_checkBox.isChecked():
            self.POWER_P_L_gen_comboBox.setEnabled(True)
        else:
            self.POWER_P_L_gen_comboBox.setEnabled(False)
        if self.POWER_P_L_day_checkBox.isChecked():
            self.POWER_P_L_day_comboBox.setEnabled(True)
        else:
            self.POWER_P_L_day_comboBox.setEnabled(False)
        if self.POWER_P_L_eve_checkBox.isChecked():
            self.POWER_P_L_eve_comboBox.setEnabled(True)
        else:
            self.POWER_P_L_eve_comboBox.setEnabled(False)
        if self.POWER_P_L_nig_checkBox.isChecked():
            self.POWER_P_L_nig_comboBox.setEnabled(True)
        else:
            self.POWER_P_L_nig_comboBox.setEnabled(False)

        self.setToolTips()


    def setToolTips(self):

        for comboBox in self.all_emission_comboBoxes:

            if comboBox.isEnabled() == True:
                string = "Choose from a numeric field of the source layer"
                comboBox.setToolTip(string)
            else:
                comboBox.setToolTip("")

    def check_freq_gen_update(self):
        # GEN
        if self.POWER_P_L_gen_checkBox_Freq.isChecked():
            for comboBox in self.all_emission_comboBoxes_Freq_GEN:
                comboBox.setEnabled(True)
        else:
            for comboBox in self.all_emission_comboBoxes_Freq_GEN:
                comboBox.setEnabled(False)
        # DAY
        if self.POWER_P_L_day_checkBox_Freq.isChecked():
            for comboBox in self.all_emission_comboBoxes_Freq_DAY:
                comboBox.setEnabled(True)
        else:
            for comboBox in self.all_emission_comboBoxes_Freq_DAY:
                comboBox.setEnabled(False)
        # EVE
        if self.POWER_P_L_eve_checkBox_Freq.isChecked():
            for comboBox in self.all_emission_comboBoxes_Freq_EVE:
                comboBox.setEnabled(True)
        else:
            for comboBox in self.all_emission_comboBoxes_Freq_EVE:
                comboBox.setEnabled(False)
        # NIG
        if self.POWER_P_L_nig_checkBox_Freq.isChecked():
            for comboBox in self.all_emission_comboBoxes_Freq_NIG:
                comboBox.setEnabled(True)
        else:
            for comboBox in self.all_emission_comboBoxes_Freq_NIG:
                comboBox.setEnabled(False)
        

    def check(self):

        for comboBox in self.all_emission_comboBoxes:

            if comboBox.isEnabled() == True and comboBox.currentText() == "":
                QMessageBox.information(self, self.tr("opeNoise Map - Calculate Noise Levels"), self.tr("Please select a field"))
                return False

        count = 0
        for key in list(self.POWER_P_emission_comboBoxes_dict.keys()):
            comboBox = self.POWER_P_emission_comboBoxes_dict[key]
            if comboBox.isEnabled():
                count = 1
        for key in list(self.POWER_P_Freq_GEN_comboboxes_dict.keys()):
            comboBox = self.POWER_P_Freq_GEN_comboboxes_dict[key]
            if comboBox.isEnabled():
                count = 1
        for key in list(self.POWER_P_Freq_DAY_comboboxes_dict.keys()):
            comboBox = self.POWER_P_Freq_DAY_comboboxes_dict[key]
            if comboBox.isEnabled():
                count = 1
        for key in list(self.POWER_P_Freq_EVE_comboboxes_dict.keys()):
            comboBox = self.POWER_P_Freq_EVE_comboboxes_dict[key]
            if comboBox.isEnabled():
                count = 1
        for key in list(self.POWER_P_Freq_NIG_comboboxes_dict.keys()):
            comboBox = self.POWER_P_Freq_NIG_comboboxes_dict[key]
            if comboBox.isEnabled():
                count = 1

        if count == 0:
            QMessageBox.information(self, self.tr("opeNoise Map - Calculate Noise Levels"), self.tr("Please specify at least one power value for a reference period"))
            return False

        return True


    def write_settings(self):

        settings = {}

        if self.POWER_P_radioButton.isChecked():
            settings['implementation_pts'] = 'True'
            settings['implementation_pts_freq'] = 'False'
        if self.POWER_P_freq_radioButton.isChecked():
            settings['implementation_pts_freq'] = 'True'
            settings['implementation_pts'] = 'False'

        if self.POWER_P_L_gen_checkBox.isChecked():
            settings['period_pts_gen'] = 'True'
        else:
            settings['period_pts_gen'] = 'False'
        if self.POWER_P_L_day_checkBox.isChecked():
            settings['period_pts_day'] = 'True'
        else:
            settings['period_pts_day'] = 'False'
        if self.POWER_P_L_eve_checkBox.isChecked():
            settings['period_pts_eve'] = 'True'
        else:
            settings['period_pts_eve'] = 'False'
        if self.POWER_P_L_nig_checkBox.isChecked():
            settings['period_pts_nig'] = 'True'
        else:
            settings['period_pts_nig'] = 'False'

        # settings of frequencies
        if self.POWER_P_L_gen_checkBox_Freq.isChecked():
            settings['period_pts_gen_freq'] = 'True'
        else:
            settings['period_pts_gen_freq'] = 'False'

        if self.POWER_P_L_day_checkBox_Freq.isChecked():
            settings['period_pts_day_freq'] = 'True'
        else:
            settings['period_pts_day_freq'] = 'False'

        if self.POWER_P_L_eve_checkBox_Freq.isChecked():
            settings['period_pts_eve_freq'] = 'True'
        else:
            settings['period_pts_eve_freq'] = 'False'

        if self.POWER_P_L_nig_checkBox_Freq.isChecked():
            settings['period_pts_nig_freq'] = 'True'
        else:
            settings['period_pts_nig_freq'] = 'False'


        for key in list(self.POWER_P_emission_comboBoxes_dict.keys()):
            if self.POWER_P_emission_comboBoxes_dict[key].isEnabled():
                settings[key] = self.POWER_P_emission_comboBoxes_dict[key].currentField()
            else:
                settings[key] = ''

        for key in list(self.POWER_P_Freq_GEN_comboboxes_dict.keys()):
            if self.POWER_P_Freq_GEN_comboboxes_dict[key].isEnabled():
                settings[key] = self.POWER_P_Freq_GEN_comboboxes_dict[key].currentField()

        for key in list(self.POWER_P_Freq_DAY_comboboxes_dict.keys()):
            if self.POWER_P_Freq_DAY_comboboxes_dict[key].isEnabled():
                settings[key] = self.POWER_P_Freq_DAY_comboboxes_dict[key].currentField()

        for key in list(self.POWER_P_Freq_EVE_comboboxes_dict.keys()):
            if self.POWER_P_Freq_EVE_comboboxes_dict[key].isEnabled():
                settings[key] = self.POWER_P_Freq_EVE_comboboxes_dict[key].currentField()

        for key in list(self.POWER_P_Freq_NIG_comboboxes_dict.keys()):
            if self.POWER_P_Freq_NIG_comboboxes_dict[key].isEnabled():
                settings[key] = self.POWER_P_Freq_NIG_comboboxes_dict[key].currentField()

        on_Settings.setSettings(settings)


    def reload_settings(self):

        try:
            settings = on_Settings.getAllSettings()

            if settings['implementation_pts'] == 'True':
                self.POWER_P_radioButton.setChecked(1)

            if settings['implementation_pts_freq'] == 'True':
                self.POWER_P_freq_radioButton.setChecked(1)


            if settings['period_pts_gen'] == "True":
                self.POWER_P_L_gen_checkBox.setChecked(1)
            if settings['period_pts_day'] == "True":
                self.POWER_P_L_day_checkBox.setChecked(1)
            if settings['period_pts_eve'] == "True":
                self.POWER_P_L_eve_checkBox.setChecked(1)
            if settings['period_pts_nig'] == "True":
                self.POWER_P_L_nig_checkBox.setChecked(1)

            for key in list(self.POWER_P_emission_comboBoxes_dict.keys()):
                if settings[key] is not None:
                    idx = self.POWER_P_emission_comboBoxes_dict[key].findText(settings[key])
                    self.POWER_P_emission_comboBoxes_dict[key].setCurrentIndex(idx)

            # reload data for frequencies
            if settings['period_pts_gen_freq'] == 'True':
                self.POWER_P_L_gen_checkBox_Freq.setChecked(1)

            if settings['period_pts_day_freq'] == 'True':
                self.POWER_P_L_day_checkBox_Freq.setChecked(1)

            if settings['period_pts_eve_freq'] == 'True':
                self.POWER_P_L_eve_checkBox_Freq.setChecked(1)

            if settings['period_pts_nig_freq'] == 'True':
                self.POWER_P_L_nig_checkBox_Freq.setChecked(1)

            for key in list(self.POWER_P_Freq_GEN_comboboxes_dict.keys()):
                if settings[key] is not None:
                    idx = self.POWER_P_Freq_GEN_comboboxes_dict[key].findText(settings[key])
                    self.POWER_P_Freq_GEN_comboboxes_dict[key].setCurrentIndex(idx)

            for key in list(self.POWER_P_Freq_DAY_comboboxes_dict.keys()):
                if settings[key] is not None:
                    idx = self.POWER_P_Freq_DAY_comboboxes_dict[key].findText(settings[key])
                    self.POWER_P_Freq_DAY_comboboxes_dict[key].setCurrentIndex(idx)

            for key in list(self.POWER_P_Freq_EVE_comboboxes_dict.keys()):
                if settings[key] is not None:
                    idx = self.POWER_P_Freq_EVE_comboboxes_dict[key].findText(settings[key])
                    self.POWER_P_Freq_EVE_comboboxes_dict[key].setCurrentIndex(idx)

            for key in list(self.POWER_P_Freq_NIG_comboboxes_dict.keys()):
                if settings[key] is not None:
                    idx = self.POWER_P_Freq_NIG_comboboxes_dict[key].findText(settings[key])
                    self.POWER_P_Freq_NIG_comboboxes_dict[key].setCurrentIndex(idx)

            self.source_checkBox_update()

        except:

            QMessageBox.information(self, self.tr("opeNoise Map - Calculate Noise Levels"), self.tr("Sorry, but somethigs wrong in import last settings"))


    def accept(self):

        if self.check() == False:
            return

        self.write_settings()

        self.close()

    def HelpBands_show(self):
        QMessageBox.information(self, self.tr("opeNoise Map - Help"), self.tr('''
<p><strong>Octave Bands: </strong>If data are unavailable for one or more octave bands, enter the value NULL or zero.</p>
'''))
