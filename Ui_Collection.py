# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\CSTI-ModEditor\Collection.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Collection(object):
    def setupUi(self, Collection):
        Collection.setObjectName("Collection")
        Collection.resize(400, 290)
        self.gridLayout = QtWidgets.QGridLayout(Collection)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(Collection)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.lineEdit = QtWidgets.QLineEdit(Collection)
        self.lineEdit.setObjectName("lineEdit")
        self.verticalLayout_2.addWidget(self.lineEdit)
        self.listWidget = QtWidgets.QListWidget(Collection)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout_2.addWidget(self.listWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(Collection)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(Collection)
        self.buttonBox.accepted.connect(Collection.accept) # type: ignore
        self.buttonBox.rejected.connect(Collection.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Collection)

    def retranslateUi(self, Collection):
        _translate = QtCore.QCoreApplication.translate
        Collection.setWindowTitle(_translate("Collection", "Collection"))
        self.label.setText(_translate("Collection", "Search box"))
