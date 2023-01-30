# -*- coding: utf-8 -*- 

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from data_base import *
from SelectGUI import *

class ItemDelegate(QItemDelegate):
    def __init__(self, field = "", parent = None):
        super(ItemDelegate, self).__init__(parent)
        self.field = field

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QModelIndex) -> QWidget:
        model = index.model()

        if hasattr(model, 'mapToSource'):
            srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
        else:
            srcModel, item, srcIndex = model, index.internalPointer(), index

        if item.field() == "Boolean":
            return self.createBoolEditor(parent, option, index)
        elif item.field() == "Int32":
            return self.createIntEditor(parent, option, index)
        elif item.field() == "Single":
            return self.createDoubleEditor(parent, option, index)
        elif item.field() == "String":
            pass
        elif item.field() in DataBase.AllEnum and item.type() != "list":
            return self.createSelectEditor(parent, option, index, item.field())
        else:
            return super().createEditor(parent, option, index)
        return super().createEditor(parent, option, index)

    def createBoolEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QModelIndex) -> QWidget:
        editor = QLabel(parent)
        editor.setAutoFillBackground(True)
        return editor

    def createIntEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QModelIndex) -> QWidget:
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(editor))
        return editor

    def createDoubleEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QModelIndex) -> QWidget:
        editor = QLineEdit(parent)
        editor.setValidator(QDoubleValidator(editor))
        return editor

    def createSelectEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QModelIndex, field_name = "", type = SelectGUI.Ref) -> QWidget:
        editor = SelectGUI(parent, field_name = field_name, type = type)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        model = index.model()
        if hasattr(model, 'mapToSource'):
            srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
        else:
            srcModel, item, srcIndex = model, index.internalPointer(), index

        if item.field() == "Boolean":
            self.setBoolEditorData(editor, index)
            return
        elif item.field() == "Int32" or item.field() == "Single" or item.field() == "String":
            item.setVaild(True)
            editor.setText(index.data())
            return
        else:
            pass
        return super().setEditorData(editor, index)

    def setBoolEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        model = index.model()
        if hasattr(model, 'mapToSource'):
            srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
        else:
            srcModel, item, srcIndex = model, index.internalPointer(), index

        item.setVaild(True)
        if str(index.data()) == "False":
            editor.setText("True")
        else:
            editor.setText("False")

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex) -> None:
        model = index.model()
        if hasattr(model, 'mapToSource'):
            srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
        else:
            srcModel, item, srcIndex = model, index.internalPointer(), index
            
        if item.field() == "Boolean" or item.field() == "Int32" or item.field() == "Single" or item.field() == "String":
            pass 
        elif item.field() in DataBase.AllEnum:
            if editor.write_flag:
                if editor.lineEdit.text() in DataBase.AllEnum[item.field()]:
                    srcModel.setData(srcIndex, DataBase.AllEnum[item.field()][editor.lineEdit.text()], Qt.EditRole)
            return
        return super().setModelData(editor, model, index)

    # def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
    #     editor.setGeometry(option.rect)
    #     return super().updateEditorGeometry(editor, option, index)

class EnableDelegate(QItemDelegate):
    def __init__(self, parent = None):
        super(EnableDelegate, self).__init__(parent)

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QModelIndex) -> QWidget:
        editor = QLabel(parent)
        editor.setAutoFillBackground(True)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        if str(index.data()) == "False":
            editor.setText("True")
        else:
            editor.setText("False")