from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_Item import *
from QJsonData import *
from SelectGUI import *
from NewItemGUI import *
from CollectionGUI import *
from data_base import *

class ItemDelegate(QItemDelegate):
    def __init__(self, field = "", parent = None):
        super(ItemDelegate, self).__init__(parent)
        self.field = field

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
            return
        elif item.field() == "Int32" or item.field() == "Single" or item.field() == "String":
            item.setVaild(True)
            editor.setText(str(index.data()))
            return
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
    def __init__(self, field, parent = None):
        super(ItemGUI, self).__init__(parent)
        self.setupUi(self)
        self.field = field
        self.treeView.setItemDelegateForColumn(1, ItemDelegate(self.field, self.treeView))
        self.treeView.setItemDelegateForColumn(4, EnableDelegate(self.treeView))
        self.treeView.setSortingEnabled(True)
        self.treeView.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self.treeView.header().setSortIndicator(4, Qt.SortOrder.DescendingOrder)
        self.treeView.setDragEnabled(True)
        
        self.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.on_treeViewCustomContextMenuRequested)

        self.showInvalidButton.setText("显示未激活属性")
        self.showInvalidButton.clicked.connect(self.on_showInvalidButtonClicked)

        self.lineEdit.textChanged.connect(self.on_lineEditTextChanged)

        if self.field == "CardData":
            tabButton = QPushButton("添加蓝图主分组", self)
            tabButton.clicked.connect(self.on_tabButtonCardDataMainTabGroup)
            self.horizontalLayout.insertWidget(2, tabButton)
            subTabButton = QPushButton("添加蓝图次分组", self)
            subTabButton.clicked.connect(self.on_tabButtonCardDataSubTabGroup)
            self.horizontalLayout.insertWidget(3, subTabButton)
            label = QLabel("不是蓝图的卡别添加")
            self.horizontalLayout.insertWidget(4, label)
        if self.field == "CharacterPerk":
            tabButton = QPushButton("添加特性互斥组", self)
            self.horizontalLayout.insertWidget(2, tabButton)
            tabButton.clicked.connect(self.on_tabButtonCharacterPerk)
        if self.field == "GameStat":
            tabButton = QPushButton("添加可显示状态分组", self)
            self.horizontalLayout.insertWidget(2, tabButton)
            tabButton.clicked.connect(self.on_tabButtonGameStat)

        # self.test_button = QPushButton("Test")
        # self.horizontalLayout.addWidget(self.test_button)
        # self.test_button.clicked.connect(self.on_test)

    def on_tabButtonCardDataMainTabGroup(self):
        select = SelectGUI(self.treeView, field_name = "BlueprintCardDataCardTabGroup", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            self.model.addItem(QModelIndex(), "BlueprintCardDataCardTabGroup", str, select.lineEdit.text(), "Special", True)
            return

    def on_tabButtonCardDataSubTabGroup(self):
        select = SelectGUI(self.treeView, field_name = "BlueprintCardDataCardTabSubGroup", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            self.model.addItem(QModelIndex(), "BlueprintCardDataCardTabSubGroup", str, select.lineEdit.text(), "Special", True)
            return

    def on_tabButtonCharacterPerk(self):
        select = SelectGUI(self.treeView, field_name = "CharacterPerkPerkGroup", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            self.model.addItem(QModelIndex(), "CharacterPerkPerkGroup", str, select.lineEdit.text(), "Special", True)
            return

    def on_tabButtonGameStat(self):
        select = SelectGUI(self.treeView, field_name = "VisibleGameStatStatListTab", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            self.model.addItem(QModelIndex(), "VisibleGameStatStatListTab", str, select.lineEdit.text(), "Special", True)
            return

    def loadJsonData(self, json_data):
        self.model = QJsonModel(self.field)
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
                elif item.field() == "WarpType" or item.field() == "WarpData" or item.field() is None or item.field() == "" or \
                    item.field() == "Special" or item.field() == "None" or item.field() == "Boolean" or item.field() == "Int32" or item.field() == "Single" or item.field() == "String":
                    pass
                else:
                    if item.depth() == 1:
                        pCopyAct = QAction("复制模板并覆盖", menu)
                        pCopyAct.triggered.connect(self.on_copyItem)
                        menu.addAction(pCopyAct)

                        if item.type() == "list":
                            pAddAct = QAction("追加模板项", menu)
                            pAddAct.triggered.connect(self.on_addListItem)
                            menu.addAction(pAddAct)

                    if item.type() == "dict":
                        pCopyCollAct = QAction("复制收藏并覆盖", menu)
                        pCopyCollAct.triggered.connect(self.on_copyCollItem)
                        menu.addAction(pCopyCollAct)
                    # if item.parent().type() == "list" and item.depth() > 1:
                    
                        pSaveAct = QAction("收藏", menu)
                        pSaveAct.triggered.connect(self.on_saveItem)
                        menu.addAction(pSaveAct)

                    if item.type() == "list":
                        pNewAct = QAction("新建空白项", menu)
                        pNewAct.triggered.connect(self.on_newListItem)
                        menu.addAction(pNewAct)

                        pNewAct = QAction("载入收藏", menu)
                        pNewAct.triggered.connect(self.on_loadListItem)
                        menu.addAction(pNewAct)

                    

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

            select = SelectGUI(self.treeView, field_name = self.field, type = SelectGUI.Append)
            select.exec_()

            if select.write_flag:
                if self.field in DataBase.AllPath:
                    template_key = select.lineEdit.text().split("(")[0]
                    if template_key in DataBase.AllPath[self.field]:
                        with open(DataBase.AllPath[self.field][template_key], 'r') as f:
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

        if os.path.exists(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableBaseJsonData/" + self.field + r"/" + item.field() + r".json"):
            with open(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableBaseJsonData/" + self.field + r"/" + item.field() + r".json", 'r') as f:
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
        if item.field() not in DataBase.AllCollection or len(DataBase.AllCollection[item.field()]) == 0:
            QMessageBox.information(self, '提示','相关收藏为空，请先添加收藏')
            return
        self.loadCollection = CollectionGUI(item.field(), self)
        self.loadCollection.exec_()
        
        name = self.loadCollection.lineEdit.text()
        
        if self.loadCollection.write_flag and name in DataBase.AllCollection[item.field()]:
            child_key = 0
            while str(child_key) in item.mChilds:
                child_key += 1
            self.model.addJsonItem(srcIndex, DataBase.AllCollection[item.field()][name], item.field(), str(child_key))
            return

    def on_saveItem(self) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

        self.newSave = NewItemGUI(self)
        self.newSave.buttonBox.accepted.connect(lambda : self.on_newSaveButtonBoxAccepted(item))
        self.newSave.exec_()

    def on_newSaveButtonBoxAccepted(self, item: QJsonTreeItem):
        name = self.newSave.lineEdit.text()
        if not name:
            return
        if item.field() not in DataBase.AllCollection:
            DataBase.AllCollection[item.field()] = {}
        if name in DataBase.AllCollection[item.field()]:
            reply = QMessageBox.question(self, '警告', '是否覆盖同名收藏', QMessageBox.Yes | QMessageBox.No , QMessageBox.No)
            if reply == QMessageBox.No:
                return
        DataBase.AllCollection[item.field()][name] = self.model.to_json(item)

    def on_copyItem(self) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

            select = SelectGUI(self.treeView, field_name = self.field, type = SelectGUI.Copy)
            select.exec_()

            if select.write_flag:
                if self.field in DataBase.AllPath:
                    template_key = select.lineEdit.text().split("(")[0]
                    if template_key in DataBase.AllPath[self.field]:
                        with open(DataBase.AllPath[self.field][template_key], 'r') as f:
                            data = json.load(f)[item.key()]
                        
                        self.model.deleteItem(srcIndex)
                        self.model.addJsonItem(srcIndex.parent(), data, item.field(), item.key())
                        return

    def on_copyCollItem(self) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

            if item.field() not in DataBase.AllCollection or len(DataBase.AllCollection[item.field()]) == 0:
                QMessageBox.information(self, '提示','相关收藏为空，请先添加收藏')
                return
            self.loadCollection = CollectionGUI(item.field(), self)
            self.loadCollection.exec_()
            
            name = self.loadCollection.lineEdit.text()
            if self.loadCollection.write_flag and name in DataBase.AllCollection[item.field()]:
                self.model.deleteItem(srcIndex)
                self.model.addJsonItem(srcIndex.parent(), DataBase.AllCollection[item.field()][name], item.field(), item.key())
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

        