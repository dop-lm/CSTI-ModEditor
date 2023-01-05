from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_NewItem import *

class NewItemGUI(QDialog, Ui_NewItem):
    def __init__(self, parent = None):
        super(NewItemGUI, self).__init__(parent)
        self.setupUi(self)