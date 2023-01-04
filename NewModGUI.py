from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_NewMod import *

class NewModGUI(QDialog, Ui_NewMod):
    def __init__(self, parent = None):
        super(NewModGUI, self).__init__(parent)
        self.setupUi(self)