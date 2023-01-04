from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_Item import *
from QJsonData import *
from SelectGUI import *
from data_base import *

class ItemDelegate(QItemDelegate):
    def __init__(self, data_type = "", parent = None):
        super(ItemDelegate, self).__init__(parent)
        self.data_type = data_type

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        model = index.model()

        if hasattr(model, 'mapToSource'):
            srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
        else:
            srcModel, item, srcIndex = model, index.internalPointer(), index

        # child_index = srcModel.index(2, 0, srcIndex)
        # if child_index.isValid():
        #     print("vaild", child_index.internalPointer().key())

        # parent_index = srcModel.parent(srcIndex)
        # if parent_index.isValid():
        #     print("parent vaild", parent_index.internalPointer().key())

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
        # elif item.field() in DataBase.RefNameList or item.field() in DataBase.RefGuidList or item.field() in DataBase.AllEnum or item.field() == "ScriptableObject" and item.type() != "list":
        #     return self.createSelectEditor(parent, option, index, item.field())
        # elif item.field() != "" and item.field() is not None:
        #     if item.depth() == 1:
        #         if item.type() == "list":
        #             return self.createSelectEditor(parent, option, index, self.data_type, SelectGUI.CopyOrNewOrAppend)
        #         else:
        #             return self.createSelectEditor(parent, option, index, self.data_type, SelectGUI.Copy)
        #     else:
        #         if item.type() == "list":
        #             return self.createSelectEditor(parent, option, index, self.data_type, SelectGUI.NewOrLoad)
        #         return None
        else:
            return super().createEditor(parent, option, index)
        return super().createEditor(parent, option, index)

    def createBoolEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        editor = QLabel(parent)
        editor.setAutoFillBackground(True)
        return editor

    def createIntEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(editor))
        return editor

    def createDoubleEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        editor = QLineEdit(parent)
        editor.setValidator(QDoubleValidator(editor))
        return editor

    def createSelectEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex, field_name = "", type = SelectGUI.Ref) -> QWidget:
        editor = SelectGUI(parent, field_name = field_name, type = type)
        return editor

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        model = index.model()
        if hasattr(model, 'mapToSource'):
            srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
        else:
            srcModel, item, srcIndex = model, index.internalPointer(), index

        if item.field() == "Boolean":
            self.setBoolEditorData(editor, index)
        elif item.field() == "Int32" or item.field() == "Single" or item.field() == "String":
            item.setVaild(True)
            editor.setText(str(index.data()))
        else:
            pass
            # if item.type() == "bool":
            #     self.setBoolEditorData(editor, index)
            # elif item.type() == "float" or item.type() == "str" or item.type() == "int":
            #     item.setVaild(True)
            #     editor.setText(str(index.data()))
        return super().setEditorData(editor, index)

    def setBoolEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
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

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        model = index.model()
        if hasattr(model, 'mapToSource'):
            srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
        else:
            srcModel, item, srcIndex = model, index.internalPointer(), index
            
        if item.field() == "Boolean" or item.field() == "Int32" or item.field() == "Single" or item.field() == "String":
            pass 
        elif item.field() in DataBase.RefNameList or item.field() in DataBase.RefGuidList:
            if editor.write_flag:
                if item.field() in DataBase.RefGuidList:
                    if item.field() == "CardData":
                        if editor.lineEdit.text() in DataBase.AllCardData:
                            srcModel.refWarp(srcIndex, DataBase.AllCardData[editor.lineEdit.text()], Qt.EditRole)
                            return
                    else:
                        if editor.lineEdit.text() in DataBase.AllGuid[item.field()]:
                            srcModel.beginResetModel()
                            srcModel.refWarp(srcIndex, DataBase.AllGuid[item.field()][editor.lineEdit.text()], Qt.EditRole)
                            return
                srcModel.refWarp(srcIndex, editor.lineEdit.text(), Qt.EditRole)
            return
        elif item.field() in DataBase.AllEnum:
            if editor.write_flag:
                if editor.lineEdit.text() in DataBase.AllEnum[item.field()]:
                    srcModel.setData(srcIndex, DataBase.AllEnum[item.field()][editor.lineEdit.text()], Qt.EditRole)
            return
        elif item.field() == "ScriptableObject":
            if editor.write_flag:
                if editor.lineEdit.text() in DataBase.AllScriptableObject:
                    srcModel.beginResetModel()
                    srcModel.refWarp(srcIndex, DataBase.AllScriptableObject[editor.lineEdit.text()], Qt.EditRole)
                    srcModel.endResetModel()
        elif item.field() != "" and item.field() is not None:
            if editor.write_flag:
                if self.data_type in DataBase.AllPath:
                    template_key = editor.lineEdit.text().split("(")[0]
                    if template_key in DataBase.AllPath[self.data_type]:
                        with open(DataBase.AllPath[self.data_type][template_key], 'r') as f:
                            data = json.load(f)[item.key()]
                        item = QJsonTreeItem.load(data, type_key = item.field(), parent = item.parent(), itemKey = item.key())
                        srcModel.beginResetModel()
                        item.parent().appendChild(item.key(), item)
                        srcModel.endResetModel()
                        return
            elif editor.new_flag:
                if os.path.exists(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableBaseJsonData/" + self.data_type + r"/" + item.field() + r".json"):
                    with open(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableBaseJsonData/" + self.data_type + r"/" + item.field() + r".json", 'r') as f:
                        data = json.load(f)
                    child_key = 0
                    while str(child_key) in item.mChilds:
                        child_key += 1
                    child = QJsonTreeItem.load(data, type_key = item.field(), parent = item, itemKey = str(child_key))
                    srcModel.beginResetModel()
                    item.appendChild(child.key(), child)
                    srcModel.endResetModel()
                    return
            elif editor.append_flag:
                if self.data_type in DataBase.AllPath:
                    template_key = editor.lineEdit.text().split("(")[0]
                    if template_key in DataBase.AllPath[self.data_type]:
                        with open(DataBase.AllPath[self.data_type][template_key], 'r') as f:
                            data = json.load(f)[item.key()]
                        if type(data) is list:
                            for sub_data in data:
                                child_key = 0
                                while str(child_key) in item.mChilds:
                                    child_key += 1
                                # srcModel.beginInsertRows(srcIndex, item.childCount(), item.childCount())
                                srcModel.beginResetModel()
                                child = QJsonTreeItem.load(sub_data, type_key = item.field(), parent = item, itemKey = str(child_key))
                                item.appendChild(child.key(), child)
                                # srcModel.endInsertRows()
                                srcModel.endResetModel()
                        return
            return
        return super().setModelData(editor, model, index)

    # def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
    #     editor.setGeometry(option.rect)
    #     return super().updateEditorGeometry(editor, option, index)

class EnableDelegate(QItemDelegate):
    def __init__(self, parent = None):
        super(EnableDelegate, self).__init__(parent)

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        editor = QLabel(parent)
        editor.setAutoFillBackground(True)
        return editor

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        if str(index.data()) == "False":
            editor.setText("True")
        else:
            editor.setText("False")

class ItemGUI(QWidget, Ui_Item):
    def __init__(self, data_type, parent = None):
        super(ItemGUI, self).__init__(parent)
        self.setupUi(self)
        self.data_type = data_type
        self.treeView.setItemDelegateForColumn(1, ItemDelegate(self.data_type, self.treeView))
        self.treeView.setItemDelegateForColumn(4, EnableDelegate(self.treeView))
        self.treeView.setSortingEnabled(True)
        self.treeView.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self.treeView.setDragEnabled(True)
        
        self.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.on_treeView_customContextMenuRequested)

        self.showInvalidButton.setText("显示未激活属性")
        self.showInvalidButton.clicked.connect(self.on_showInvalidButton_clicked)

        self.lineEdit.textChanged.connect(self.on_lineEdit_textChanged)
        # self.treeView.doubleClicked.connect(self.on_treeViewDoubleClicked)

        # self.test_button = QPushButton("Test")
        # self.horizontalLayout.addWidget(self.test_button)
        # self.test_button.clicked.connect(self.on_test)
        

    def loadJsonData(self, json_data):
        self.model = QJsonModel(self.data_type)
        self.model.loadJson(json_data)
        self.proxy_model = QJsonProxyModel(self.treeView)
        self.proxy_model.setSourceModel(self.model)
        # self.proxy_model.setDynamicSortFilter(True)
        regx = QRegExp("True")
        # self.treeView.setModel(model)
        self.treeView.setModel(self.proxy_model)
        for i in range(self.model.columnCount()):
            self.treeView.resizeColumnToContents(i)

    def on_showInvalidButton_clicked(self) -> None:
        if self.showInvalidButton.text() == "显示未激活属性":
            self.showInvalidButton.setText("隐藏未激活属性")
            self.proxy_model.setVaildFilter(False)
        else:
            self.showInvalidButton.setText("显示未激活属性")
            self.proxy_model.setVaildFilter(True)

    def on_lineEdit_textChanged(self, key: str) -> None:
        self.proxy_model.setKeyFilter(key)
    
    def on_treeView_customContextMenuRequested(self, pos: QPoint) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

            menu = QMenu(self.treeView)
            if item.parent() is not None:
                if item.parent().type() == "list" and item.depth() > 1:
                    pDeleteAct = QAction("删除", menu)
                    pDeleteAct.triggered.connect(self.on_delListItem)
                    menu.addAction(pDeleteAct)
                if item.type() == "list" and item.depth() == 1:
                    pAddAct = QAction("增加", menu)
                    pAddAct.triggered.connect(self.on_addListItem)
                    menu.addAction(pAddAct)
            menu.popup(self.sender().mapToGlobal(pos))

    def on_delListItem(self) -> None:
        index = self.treeView.currentIndex()
        self.model.removeListItem(index)

    def on_addListItem(self) -> None:
        index = self.treeView.currentIndex()
        self.model.removeListItem(index)

    # def on_test(self):
    #     index = self.treeView.currentIndex()
    #     if index.isValid():
    #         srcIndex = self.proxy_model.mapToSource(index)
    #         item = srcIndex.internalPointer()
    #         print(item.key(), item.childCount())
    #         print(id(self.model))
    #         self.model.beginInsertRows(srcIndex, item.childCount(), item.childCount())
    #         # child = QJsonTreeItem.load(sub_data, type_key = item.field(), parent = item, itemKey = str(child_key))
    #         # item.appendChild(child.key(), child)
    #         self.model.endInsertRows()

        