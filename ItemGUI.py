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
        elif item.field() in DataBase.AllEnum:
            if editor.write_flag:
                if editor.lineEdit.text() in DataBase.AllEnum[item.field()]:
                    srcModel.setData(srcIndex, DataBase.AllEnum[item.field()][editor.lineEdit.text()], Qt.EditRole)
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
        self.treeView.customContextMenuRequested.connect(self.on_treeViewCustomContextMenuRequested)

        self.showInvalidButton.setText("显示未激活属性")
        self.showInvalidButton.clicked.connect(self.on_showInvalidButtonClicked)

        self.lineEdit.textChanged.connect(self.on_lineEditTextChanged)
        # self.treeView.doubleClicked.connect(self.on_treeViewDoubleClicked)

        # self.test_button = QPushButton("Test")
        # self.horizontalLayout.addWidget(self.test_button)
        # self.test_button.clicked.connect(self.on_test)

    def loadJsonData(self, json_data):
        self.model = QJsonModel(self.data_type)
        self.model.loadJson(json_data)
        self.proxy_model = QJsonProxyModel(self.treeView)
        self.proxy_model.setSourceModel(self.model)
        self.treeView.setModel(self.proxy_model)
        for i in range(self.model.columnCount()):
            self.treeView.resizeColumnToContents(i)

    def on_showInvalidButtonClicked(self) -> None:
        if self.showInvalidButton.text() == "显示未激活属性":
            self.showInvalidButton.setText("隐藏未激活属性")
            self.proxy_model.setVaildFilter(False)
        else:
            self.showInvalidButton.setText("显示未激活属性")
            self.proxy_model.setVaildFilter(True)

    def on_lineEditTextChanged(self, key: str) -> None:
        self.proxy_model.setKeyFilter(key)
    
    def on_treeViewCustomContextMenuRequested(self, pos: QPoint) -> None:
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
                
                if item.field() in DataBase.RefNameList or item.field() in DataBase.RefGuidList or item.field() == "ScriptableObject":
                    if item.type() == "list": 
                        pRefAct = QAction("追加引用", menu)
                    else:
                        pRefAct = QAction("引用", menu)
                    pRefAct.triggered.connect(self.on_addRefItem)
                    menu.addAction(pRefAct)
                elif item.field() == "WarpType" or item.field() == "WarpData" or item.field() is None or item.field() == "":
                    pass
                else:
                    if item.depth() == 1:
                        pCopyAct = QAction("复制并覆盖", menu)
                        pCopyAct.triggered.connect(self.on_copyItem)
                        menu.addAction(pCopyAct)

                        pAddAct = QAction("追加模板项", menu)
                        pAddAct.triggered.connect(self.on_addListItem)
                        menu.addAction(pAddAct)

                    if item.type() == "list":
                        pNewAct = QAction("新建空白项", menu)
                        pNewAct.triggered.connect(self.on_newListItem)
                        menu.addAction(pNewAct)

                        pNewAct = QAction("载入收藏", menu)
                        pNewAct.triggered.connect(self.on_loadListItem)
                        menu.addAction(pNewAct)

                    if item.parent().type() == "list" and item.depth() > 1:
                        pSaveAct = QAction("收藏", menu)
                        pSaveAct.triggered.connect(self.on_saveListItem)
                        menu.addAction(pSaveAct)

            if len(menu.actions()):
                menu.popup(self.sender().mapToGlobal(pos))

    def on_delListItem(self) -> None:
        index = self.treeView.currentIndex()
        self.model.removeListItem(index)

    def on_addListItem(self) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

            select = SelectGUI(self.treeView, field_name = self.data_type, type = SelectGUI.Append)
            select.exec_()

            if select.write_flag:
                if self.data_type in DataBase.AllPath:
                    template_key = select.lineEdit.text().split("(")[0]
                    if template_key in DataBase.AllPath[self.data_type]:
                        with open(DataBase.AllPath[self.data_type][template_key], 'r') as f:
                            data = json.load(f)[item.key()]
                        if type(data) is list:
                            for sub_data in data:
                                child_key = 0
                                while str(child_key) in item.mChilds:
                                    child_key += 1
                                self.model.addJsonItem(srcIndex, sub_data, item.field(), str(child_key))
                        return
            

    def on_newListItem(self) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

        if os.path.exists(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableBaseJsonData/" + self.data_type + r"/" + item.field() + r".json"):
            with open(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableBaseJsonData/" + self.data_type + r"/" + item.field() + r".json", 'r') as f:
                data = json.load(f)
            
            child_key = 0
            while str(child_key) in item.mChilds:
                child_key += 1
            self.model.addJsonItem(srcIndex, data, item.field(), str(child_key))
            return

    def on_loadListItem(self) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

    def on_saveListItem(self) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

    def on_copyItem(self) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

            select = SelectGUI(self.treeView, field_name = self.data_type, type = SelectGUI.Copy)
            select.exec_()

            if select.write_flag:
                if self.data_type in DataBase.AllPath:
                    template_key = select.lineEdit.text().split("(")[0]
                    if template_key in DataBase.AllPath[self.data_type]:
                        with open(DataBase.AllPath[self.data_type][template_key], 'r') as f:
                            data = json.load(f)[item.key()]
                        
                        self.model.deleteItem(srcIndex)
                        self.model.addJsonItem(QModelIndex(), data, item.field(), item.key())
                        return

    def on_addRefItem(self) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

            select = SelectGUI(self.treeView, field_name = item.field(), type = SelectGUI.Ref)
            select.exec_()

            if select.write_flag:
                if item.field() in DataBase.RefGuidList:
                    if item.field() == "CardData":
                        if select.lineEdit.text() in DataBase.AllCardData:
                            self.model.addRefWarp(index, DataBase.AllCardData[select.lineEdit.text()])
                            return
                    elif item.field() == "ScriptableObject":
                        self.mode.addRefWarp(index, DataBase.AllScriptableObject[select.lineEdit.text()])
                    else:
                        if select.lineEdit.text() in DataBase.AllGuid[item.field()]:
                            self.model.addRefWarp(index, DataBase.AllGuid[item.field()][select.lineEdit.text()])
                            return
                self.model.addRefWarp(index, select.lineEdit.text())

        # elif item.field() != "" and item.field() is not None:
        #     if item.depth() == 1:
        #         if item.type() == "list":
        #             return self.createSelectEditor(parent, option, index, self.data_type, SelectGUI.CopyOrNewOrAppend)
        #         else:
        #             return self.createSelectEditor(parent, option, index, self.data_type, SelectGUI.Copy)
        #     else:
        #         if item.type() == "list":
        #             return self.createSelectEditor(parent, option, index, self.data_type, SelectGUI.NewOrLoad)
        #         return NoneA

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

        