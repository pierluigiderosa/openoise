# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_SourceDetailsPts.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SourceDetailsPts_window(object):
    def setupUi(self, SourceDetailsPts_window):
        SourceDetailsPts_window.setObjectName("SourceDetailsPts_window")
        SourceDetailsPts_window.resize(832, 234)
        self.buttonBox = QtWidgets.QDialogButtonBox(SourceDetailsPts_window)
        self.buttonBox.setGeometry(QtCore.QRect(440, 180, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.implementation_label_24 = QtWidgets.QLabel(SourceDetailsPts_window)
        self.implementation_label_24.setGeometry(QtCore.QRect(51, 76, 101, 16))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.implementation_label_24.sizePolicy().hasHeightForWidth())
        self.implementation_label_24.setSizePolicy(sizePolicy)
        self.implementation_label_24.setAlignment(QtCore.Qt.AlignCenter)
        self.implementation_label_24.setObjectName("implementation_label_24")
        self.line_11 = QtWidgets.QFrame(SourceDetailsPts_window)
        self.line_11.setWindowModality(QtCore.Qt.NonModal)
        self.line_11.setGeometry(QtCore.QRect(21, 90, 781, 20))
        self.line_11.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_11.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_11.setObjectName("line_11")
        self.layoutWidget_2 = QtWidgets.QWidget(SourceDetailsPts_window)
        self.layoutWidget_2.setGeometry(QtCore.QRect(21, 110, 791, 35))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.layoutWidget_2)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.n_l_label_15 = QtWidgets.QLabel(self.layoutWidget_2)
        self.n_l_label_15.setMaximumSize(QtCore.QSize(16777215, 27))
        self.n_l_label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.n_l_label_15.setObjectName("n_l_label_15")
        self.horizontalLayout_9.addWidget(self.n_l_label_15)
        self.POWER_P_L_gen_comboBox = QtWidgets.QComboBox(self.layoutWidget_2)
        self.POWER_P_L_gen_comboBox.setMaximumSize(QtCore.QSize(16777215, 27))
        self.POWER_P_L_gen_comboBox.setObjectName("POWER_P_L_gen_comboBox")
        self.horizontalLayout_9.addWidget(self.POWER_P_L_gen_comboBox)
        self.POWER_P_L_day_comboBox = QtWidgets.QComboBox(self.layoutWidget_2)
        self.POWER_P_L_day_comboBox.setMaximumSize(QtCore.QSize(16777215, 27))
        self.POWER_P_L_day_comboBox.setObjectName("POWER_P_L_day_comboBox")
        self.horizontalLayout_9.addWidget(self.POWER_P_L_day_comboBox)
        self.POWER_P_L_eve_comboBox = QtWidgets.QComboBox(self.layoutWidget_2)
        self.POWER_P_L_eve_comboBox.setMaximumSize(QtCore.QSize(16777215, 27))
        self.POWER_P_L_eve_comboBox.setObjectName("POWER_P_L_eve_comboBox")
        self.horizontalLayout_9.addWidget(self.POWER_P_L_eve_comboBox)
        self.POWER_P_L_nig_comboBox = QtWidgets.QComboBox(self.layoutWidget_2)
        self.POWER_P_L_nig_comboBox.setMaximumSize(QtCore.QSize(16777215, 27))
        self.POWER_P_L_nig_comboBox.setObjectName("POWER_P_L_nig_comboBox")
        self.horizontalLayout_9.addWidget(self.POWER_P_L_nig_comboBox)
        self.POWER_P_L_gen_checkBox = QtWidgets.QCheckBox(SourceDetailsPts_window)
        self.POWER_P_L_gen_checkBox.setGeometry(QtCore.QRect(221, 70, 91, 21))
        self.POWER_P_L_gen_checkBox.setChecked(False)
        self.POWER_P_L_gen_checkBox.setObjectName("POWER_P_L_gen_checkBox")
        self.POWER_P_L_day_checkBox = QtWidgets.QCheckBox(SourceDetailsPts_window)
        self.POWER_P_L_day_checkBox.setGeometry(QtCore.QRect(381, 70, 81, 22))
        self.POWER_P_L_day_checkBox.setChecked(False)
        self.POWER_P_L_day_checkBox.setObjectName("POWER_P_L_day_checkBox")
        self.POWER_P_L_eve_checkBox = QtWidgets.QCheckBox(SourceDetailsPts_window)
        self.POWER_P_L_eve_checkBox.setGeometry(QtCore.QRect(541, 70, 71, 22))
        self.POWER_P_L_eve_checkBox.setChecked(False)
        self.POWER_P_L_eve_checkBox.setObjectName("POWER_P_L_eve_checkBox")
        self.label_2 = QtWidgets.QLabel(SourceDetailsPts_window)
        self.label_2.setGeometry(QtCore.QRect(20, 20, 751, 17))
        self.label_2.setObjectName("label_2")
        self.POWER_P_L_nig_checkBox = QtWidgets.QCheckBox(SourceDetailsPts_window)
        self.POWER_P_L_nig_checkBox.setGeometry(QtCore.QRect(701, 70, 81, 22))
        self.POWER_P_L_nig_checkBox.setChecked(False)
        self.POWER_P_L_nig_checkBox.setObjectName("POWER_P_L_nig_checkBox")

        self.retranslateUi(SourceDetailsPts_window)
        self.buttonBox.accepted.connect(SourceDetailsPts_window.accept)
        self.buttonBox.rejected.connect(SourceDetailsPts_window.reject)
        QtCore.QMetaObject.connectSlotsByName(SourceDetailsPts_window)

    def retranslateUi(self, SourceDetailsPts_window):
        _translate = QtCore.QCoreApplication.translate
        SourceDetailsPts_window.setWindowTitle(_translate("SourceDetailsPts_window", "Points Source Details"))
        self.implementation_label_24.setText(_translate("SourceDetailsPts_window", "Data type"))
        self.n_l_label_15.setText(_translate("SourceDetailsPts_window", "Power"))
        self.POWER_P_L_gen_checkBox.setText(_translate("SourceDetailsPts_window", "Generic"))
        self.POWER_P_L_day_checkBox.setText(_translate("SourceDetailsPts_window", "L day"))
        self.POWER_P_L_eve_checkBox.setText(_translate("SourceDetailsPts_window", "L eve"))
        self.label_2.setText(_translate("SourceDetailsPts_window", "For the point sources, you can set the type of implementation as follow:"))
        self.POWER_P_L_nig_checkBox.setText(_translate("SourceDetailsPts_window", "L nig"))
