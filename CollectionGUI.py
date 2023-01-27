from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_Collection import *
from data_base import *

class CollectionGUI(QDialog, Ui_Collection):
    def __init__(self, field, database, parent = None):
        super(CollectionGUI, self).__init__(parent)
        self.setupUi(self)
        self.field = field
        self.write_flag = False
        self.database = database

        self.listWidget.addItems(list(self.database[field].keys()))
        self.listWidget.setSortingEnabled(True)
        self.listWidget.setDragEnabled(True)
        
        self.listWidget.itemClicked.connect(self.on_listWidgetItemClicked)

        self.listWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.on_listWidgetCustomContextMenuRequested)

        self.m_completer = QCompleter(self.listWidget.model(), self)
        self.m_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.m_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.m_completer.activated[str].connect(self.on_Choosed)
        self.lineEdit.setCompleter(self.m_completer)

        self.buttonBox.clicked.connect(self.on_accepted)

    def on_Choosed(self, text):
        self.lineEdit.setText(text)

    def on_listWidgetItemClicked(self, item: QListWidgetItem):
        self.lineEdit.setText(item.text())

    def on_listWidgetCustomContextMenuRequested(self, pos: QPoint):
        item = self.listWidget.currentItem()
        if item is not None:
            menu = QMenu(self.listWidget)
            pDeleteAct = QAction("删除", menu)
            pDeleteAct.triggered.connect(self.on_delItem)
            menu.addAction(pDeleteAct)
            menu.popup(self.sender().mapToGlobal(pos))

    def on_delItem(self):
        item = self.listWidget.currentItem()
        self.listWidget.takeItem(self.listWidget.row(item))
        self.m_completer.setModel(self.listWidget.model())
        del self.database[self.field][item.text()]

    def on_accepted(self, button: QAbstractButton):
        if button == self.buttonBox.button(QDialogButtonBox.Ok):
            self.write_flag = True