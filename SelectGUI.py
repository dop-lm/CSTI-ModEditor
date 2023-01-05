from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_Select import *
from Ui_Collection import *
from data_base import *

class SelectGUI(QDialog, Ui_Select):
    Ref = 0
    NewData = 1
    Copy = 2
    Append = 3

    def __init__(self, parent = None, field_name = "", checked = False, type = 0):
        super(SelectGUI, self).__init__(parent)
        self.setupUi(self)
        self.field_name = field_name
        self.write_flag = False
        self.setWindowTitle("添加" + field_name + "引用类型")

        if type == SelectGUI.NewData:
            self.setWindowTitle("选择一个" + field_name + "模板")
            label = QLabel("卡片名字", self)
            self.name_editor = QLineEdit(self)
            self.verticalLayout.insertWidget(0, self.name_editor)
            self.verticalLayout.insertWidget(0, label)

        if type == SelectGUI.Copy:
            self.setWindowTitle("复制" + field_name + "属性")

        if type == SelectGUI.Append:
            self.setWindowTitle("追加" + field_name + "属性")

        try:
            if self.field_name == "CardData":
                reflist = []
                self.checkBoxList = {}
                for key in DataBase.AllRef[self.field_name].keys():
                    checkBox = QCheckBox()
                    checkBox.setText(key)
                    if checked:
                        checkBox.setChecked(True)
                    checkBox.stateChanged.connect(self.on_CardDataCheckBoxStateChanged)
                    self.checkBoxList[key] = checkBox
                    self.comboBox.addItems(DataBase.AllRef[self.field_name][key])
                    reflist.extend(DataBase.AllRef[self.field_name][key])
                    self.horizontalLayout_CheckBox.addWidget(checkBox)
                self.m_completer = QCompleter(reflist, self)
            elif self.field_name in DataBase.AllEnum:
                self.comboBox.addItems(DataBase.AllEnum[self.field_name].keys())
                self.m_completer = QCompleter(DataBase.AllEnum[self.field_name].keys(), self)
            elif self.field_name in DataBase.AllRef:
                self.comboBox.addItems(DataBase.AllRef[self.field_name])
                self.m_completer = QCompleter(DataBase.AllRef[self.field_name], self)
            elif self.field_name == "ScriptableObject":
                reflist = []
                self.checkBoxList = {}
                for key in DataBase.AllRef.keys():
                    if key == "CardData" or key.find("Tag") != -1:
                        checkBox = QCheckBox()
                        checkBox.setText(key)
                        if checked:
                            checkBox.setChecked(True)
                        self.checkBoxList[key] = checkBox
                        checkBox.stateChanged.connect(self.on_ScriptableObjectCheckBoxStateChanged)
                        if key == "CardData":
                            for sub_key in DataBase.AllRef[key].keys():
                                self.comboBox.addItems(DataBase.AllRef[key][sub_key])
                                reflist.extend(DataBase.AllRef[key][sub_key])
                        else:
                            self.comboBox.addItems(DataBase.AllRef[key])
                            reflist.extend(DataBase.AllRef[key])
                        self.horizontalLayout_CheckBox.addWidget(checkBox)
                self.m_completer = QCompleter(reflist, self)
            else:
                pass
            
            self.m_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.m_completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.m_completer.activated[str].connect(self.on_Choosed)
            self.lineEdit.setCompleter(self.m_completer)
            self.comboBox.currentTextChanged.connect(self.on_Choosed)
            self.buttonBox.clicked.connect(self.on_accepted)
        except Exception as ex:
            pass

    def on_CardDataCheckBoxStateChanged(self, a0: int):
        self.comboBox.clear()
        reflist = []
        for key in DataBase.AllRef[self.field_name].keys():
            if self.checkBoxList[key].isChecked():
                reflist.extend(DataBase.AllRef[self.field_name][key])
                self.comboBox.addItems(DataBase.AllRef[self.field_name][key])
        self.m_completer.setModel(QStringListModel(reflist, self.m_completer))

    def on_ScriptableObjectCheckBoxStateChanged(self, a0: int):
        self.comboBox.clear()
        reflist = []
        for key in DataBase.AllRef.keys():
            if key == "CardData" or key.find("Tag") != -1:
                if self.checkBoxList[key].isChecked():
                    if key == "CardData":
                        for sub_key in DataBase.AllRef[key].keys():
                            self.comboBox.addItems(DataBase.AllRef[key][sub_key])
                            reflist.extend(DataBase.AllRef[key][sub_key])
                    else:
                        reflist.extend(DataBase.AllRef[key])
                        self.comboBox.addItems(DataBase.AllRef[key])
        self.m_completer.setModel(QStringListModel(reflist, self.m_completer))

    def on_Choosed(self, name):
        self.lineEdit.setText(name)

    def on_accepted(self, button: QAbstractButton):
        if button == self.buttonBox.button(QDialogButtonBox.Ok):
            self.write_flag = True