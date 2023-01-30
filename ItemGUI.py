# -*- coding: utf-8 -*- 

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_Item import *
from QJsonData import *
from SelectGUI import *
from NewItemGUI import *
from ItemDelegate import *
from CollectionGUI import *
from data_base import *

class ItemGUI(QWidget, Ui_Item):
    def __init__(self, field, auto_resize = True, key: str = "", parent = None):
        super(ItemGUI, self).__init__(parent)
        self.setupUi(self)
        self.field = field
        self.tab_key = key
        self.treeView.setItemDelegateForColumn(1, ItemDelegate(self.field, self.treeView))
        self.treeView.setItemDelegateForColumn(4, EnableDelegate(self.treeView))
        self.treeView.setSortingEnabled(True)
        self.treeView.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self.treeView.header().setSortIndicator(4, Qt.SortOrder.DescendingOrder)
        self.treeView.setDragEnabled(True)
        if auto_resize:
            self.treeView.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        self.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.on_treeViewCustomContextMenuRequested)

        self.showInvalidButton.setText("显示未激活属性")
        self.showInvalidButton.clicked.connect(self.on_showInvalidButtonClicked)

        self.lineEdit.textChanged.connect(self.on_lineEditTextChanged)

        self.addSpecialButton()

    def addSpecialButton(self):
        if self.field == "CardData":
            tabButton = QPushButton("添加蓝图主分组", self)
            tabButton.clicked.connect(self.on_tabButtonCardDataMainTabGroup)
            self.horizontalLayout.insertWidget(2, tabButton)
            subTabButton = QPushButton("添加蓝图次分组", self)
            subTabButton.clicked.connect(self.on_tabButtonCardDataSubTabGroup)
            self.horizontalLayout.insertWidget(3, subTabButton)
            label = QLabel("<-不是蓝图的卡别添加")
            self.horizontalLayout.insertWidget(4, label)
            subGpTabButton = QPushButton("添加所属类型组", self)
            subGpTabButton.clicked.connect(self.on_tabButtonCardDataGpTabGroup)
            self.horizontalLayout.insertWidget(5, subGpTabButton)
        if self.field == "CharacterPerk":
            tabButton = QPushButton("添加特性互斥组", self)
            self.horizontalLayout.insertWidget(2, tabButton)
            tabButton.clicked.connect(self.on_tabButtonCharacterPerk)
        if self.field == "GameStat":
            tabButton = QPushButton("添加可显示状态分组", self)
            self.horizontalLayout.insertWidget(2, tabButton)
            tabButton.clicked.connect(self.on_tabButtonGameStat)
        if self.field == "CardTabGroup":
            tabButton = QPushButton("添加蓝图主分组", self)
            tabButton.clicked.connect(self.on_tabButtonCardDataMainTabGroup)
            self.horizontalLayout.insertWidget(2, tabButton)
        if self.field == "PlayerCharacter":
            tabButton = QPushButton("添加角色任务", self)
            tabButton.clicked.connect(self.on_tabButtonPlayerCharacterJournalName)
            self.horizontalLayout.insertWidget(2, tabButton)

    def setTabKey(self, key: str):
        self.tab_key = key

    @log_exception(True)
    def on_tabButtonPlayerCharacterJournalName(self, checked: bool=False):
        select = SelectGUI(self.treeView, field_name = "PlayerCharacterJournalName", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            self.model.addItem(QModelIndex(), "PlayerCharacterJournalName", str, select.lineEdit.text(), "SpecialWarp", True)
            return

    @log_exception(True)
    def on_tabButtonCardDataMainTabGroup(self, checked: bool=False):
        select = SelectGUI(self.treeView, field_name = "BlueprintCardDataCardTabGroup", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            self.model.addItem(QModelIndex(), "BlueprintCardDataCardTabGroup", str, select.lineEdit.text(), "SpecialWarp", True)
            return

    @log_exception(True)
    def on_tabButtonCardDataSubTabGroup(self, checked: bool=False):
        select = SelectGUI(self.treeView, field_name = "BlueprintCardDataCardTabSubGroup", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            self.model.addItem(QModelIndex(), "BlueprintCardDataCardTabSubGroup", str, select.lineEdit.text(), "SpecialWarp", True)
            return

    @log_exception(True)
    def on_tabButtonCharacterPerk(self, checked: bool=False):
        select = SelectGUI(self.treeView, field_name = "CharacterPerkPerkGroup", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            self.model.addItem(QModelIndex(), "CharacterPerkPerkGroup", str, select.lineEdit.text(), "SpecialWarp", True)
            return

    @log_exception(True)
    def on_tabButtonCardDataGpTabGroup(self, checked: bool=False):
        select = SelectGUI(self.treeView, field_name = "ItemCardDataCardTabGpGroup", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            if "ItemCardDataCardTabGpGroup" in self.model.mRootItem.mChilds:
                itemIndex = self.model.index(self.model.mRootItem.childRow("ItemCardDataCardTabGpGroup"), 0, QModelIndex())
                child_key = 0
                while str(child_key) in itemIndex.internalPointer().mChilds:
                    child_key += 1
                self.model.addItem(itemIndex, str(child_key), str, select.lineEdit.text(), "SpecialWarp", True)
            else:
                self.model.addItem(QModelIndex(), "ItemCardDataCardTabGpGroup", list, "", "SpecialWarp", True)
                itemIndex = self.model.index(self.model.mRootItem.childRow("ItemCardDataCardTabGpGroup"), 0, QModelIndex())
                self.model.addItem(itemIndex, "0", str, select.lineEdit.text(), "SpecialWarp", True)
            return

    @log_exception(True)
    def on_tabButtonGameStat(self, checked: bool=False):
        select = SelectGUI(self.treeView, field_name = "VisibleGameStatStatListTab", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            self.model.addItem(QModelIndex(), "VisibleGameStatStatListTab", str, select.lineEdit.text(), "SpecialWarp", True)
            return

    def loadJsonData(self, json_data):
        self.model = QJsonModel(self.field)
        self.model.loadJson(json_data)
        self.proxy_model = QJsonProxyModel(self.treeView)
        self.proxy_model.setSourceModel(self.model)
        self.treeView.setModel(self.proxy_model)
        for i in range(self.model.columnCount()):
            self.treeView.resizeColumnToContents(i)

    @log_exception(True)
    def on_showInvalidButtonClicked(self, checked: bool=False) -> None:
        if self.showInvalidButton.text() == "显示未激活属性":
            self.showInvalidButton.setText("隐藏未激活属性")
            self.proxy_model.setVaildFilter(False)
        else:
            self.showInvalidButton.setText("显示未激活属性")
            self.proxy_model.setVaildFilter(True)

    @log_exception(True)
    def on_lineEditTextChanged(self, key: str) -> None:
        self.proxy_model.setKeyFilter(key)
    
    @log_exception(True)
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
                if item.field() == "SpecialWarp" and item.depth() == 1:
                    pDeleteAct = QAction("删除", menu)
                    pDeleteAct.triggered.connect(self.on_delItem)
                    menu.addAction(pDeleteAct)

                if item.parent().type() == "list" and item.depth() > 1:
                    pDeleteAct = QAction("删除", menu)
                    pDeleteAct.triggered.connect(self.on_delItemFromList)
                    menu.addAction(pDeleteAct)

                if item.type() == "list" or item.type() == "dict":
                    pExpandAct = QAction("展开全部", menu)
                    pExpandAct.triggered.connect(self.on_actExpandAll)
                    menu.addAction(pExpandAct)
                
                if item.field() in DataBase.RefNameList or item.field() in DataBase.RefGuidList or item.field() == "ScriptableObject":
                    if item.type() == "list": 
                        pRefAct = QAction("追加引用", menu)
                        if item.key() == "InventorySlots":
                            pEmptyRefAct = QAction("追加容器槽", menu)
                            pEmptyRefAct.triggered.connect(self.on_addEmptyRefItem)
                            menu.addAction(pEmptyRefAct)
                    else:
                        pRefAct = QAction("引用", menu)
                    pRefAct.triggered.connect(self.on_addRefItem)
                    menu.addAction(pRefAct)
                elif item.field() == "WarpType" or item.field() == "WarpRef" or item.field() is None or item.field() == "" or \
                    item.field() == "SpecialWarp" or item.field() == "None" or item.field() == "Boolean" or item.field() == "Int32" or item.field() == "Single" or item.field() == "String":
                    pass
                else:
                    if item.depth() == 1:
                        pCopyAct = QAction("复制模板并覆盖", menu)
                        pCopyAct.triggered.connect(self.on_copyItem)
                        menu.addAction(pCopyAct)

                        if item.type() == "list":
                            pAddAct = QAction("追加模板项", menu)
                            pAddAct.triggered.connect(self.on_addItemToList)
                            menu.addAction(pAddAct)

                    if item.type() == "dict":
                        pCopyCollAct = QAction("复制收藏并覆盖", menu)
                        pCopyCollAct.triggered.connect(self.on_copyCollItem)
                        menu.addAction(pCopyCollAct)
                    
                        pSaveAct = QAction("收藏", menu)
                        pSaveAct.triggered.connect(self.on_saveItem)
                        menu.addAction(pSaveAct)

                    if item.type() == "list":
                        pNewAct = QAction("新建空白项", menu)
                        pNewAct.triggered.connect(self.on_newItemToList)
                        menu.addAction(pNewAct)

                        pNewAct = QAction("载入收藏", menu)
                        pNewAct.triggered.connect(self.on_loadItem)
                        menu.addAction(pNewAct)

                        pSaveListAct = QAction("收藏整个列表", menu)
                        pSaveListAct.triggered.connect(self.on_saveListItem)
                        menu.addAction(pSaveListAct)

                        pNewListAct = QAction("载入整个列表收藏", menu)
                        pNewListAct.triggered.connect(self.on_loadListItem)
                        menu.addAction(pNewListAct)

                        pDelListAct = QAction("删除整个列表", menu)
                        pDelListAct.triggered.connect(self.on_delListItem)
                        menu.addAction(pDelListAct)

            if len(menu.actions()):
                menu.popup(self.sender().mapToGlobal(pos))

    @log_exception(True)
    def on_actExpandAll(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            self.treeView.expandRecursively(index)

    @log_exception(True)
    def on_delItem(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index
            self.model.deleteItem(srcIndex)

    @log_exception(True)
    def on_delItemFromList(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        self.model.removeListItem(index)

    @log_exception(True)
    def on_delListItem(self, checked: bool=False) -> None:
        reply = QMessageBox.question(self, '警告', '确定要删除整个列表吗', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel , QMessageBox.No)
        if reply == QMessageBox.Yes:
            index = self.treeView.currentIndex()
            self.model.removeAllListChild(index)

    @log_exception(True)
    def on_addItemToList(self, checked: bool=False) -> None:
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
    
    @log_exception(True)
    def on_newItemToList(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

        if self.field in DataBase.AllBaseJsonData and item.field() in DataBase.AllBaseJsonData[self.field]:
            data = DataBase.AllBaseJsonData[self.field][item.field()]            
            child_key = 0
            while str(child_key) in item.mChilds:
                child_key += 1
            self.model.addJsonItem(srcIndex, data, item.field(), str(child_key))
            return

    @log_exception(True)
    def on_loadItem(self, checked: bool=False) -> None:
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
        self.loadCollection = CollectionGUI(item.field(), DataBase.AllCollection, self)
        self.loadCollection.setWindowTitle(item.field() + "类型收藏列表")
        self.loadCollection.exec_()
        
        name = self.loadCollection.lineEdit.text()
        
        if self.loadCollection.write_flag and name in DataBase.AllCollection[item.field()]:
            child_key = 0
            while str(child_key) in item.mChilds:
                child_key += 1
            self.model.addJsonItem(srcIndex, DataBase.AllCollection[item.field()][name], item.field(), str(child_key))
            return

    @log_exception(True)
    def on_loadListItem(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index
        if item.field() not in DataBase.AllListCollection or len(DataBase.AllListCollection[item.field()]) == 0:
            QMessageBox.information(self, '提示','相关收藏为空，请先添加收藏')
            return
        self.loadCollection = CollectionGUI(item.field(), DataBase.AllListCollection, self)
        self.loadCollection.setWindowTitle(item.field() + "类型收藏列表")
        self.loadCollection.exec_()
        
        name = self.loadCollection.lineEdit.text()
        
        if self.loadCollection.write_flag and name in DataBase.AllListCollection[item.field()]:
            for i in range(len(DataBase.AllListCollection[item.field()][name])):
                child_key = 0
                while str(child_key) in item.mChilds:
                    child_key += 1
                self.model.addJsonItem(srcIndex, DataBase.AllListCollection[item.field()][name][i], item.field(), str(child_key))
            return

    @log_exception(True)
    def on_saveItem(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

        self.newSave = NewItemGUI(self)
        self.newSave.buttonBox.accepted.connect(lambda : self.on_newSaveButtonBoxAccepted(item))
        self.newSave.setWindowTitle("添加" + item.field() + "类型收藏")
        self.newSave.exec_()

    @log_exception(True)
    def on_saveListItem(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

        self.newSaveList = NewItemGUI(self)
        self.newSaveList.buttonBox.accepted.connect(lambda : self.on_newSaveListButtonBoxAccepted(item))
        self.newSaveList.setWindowTitle("添加" + item.field() + "[]类型收藏")
        self.newSaveList.exec_()

    @log_exception(True)
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

    @log_exception(True)
    def on_newSaveListButtonBoxAccepted(self, item: QJsonTreeItem):
        name = self.newSaveList.lineEdit.text()
        if not name:
            return
        if item.field() not in DataBase.AllListCollection:
            DataBase.AllListCollection[item.field()] = {}
        if name in DataBase.AllListCollection[item.field()]:
            reply = QMessageBox.question(self, '警告', '是否覆盖同名收藏', QMessageBox.Yes | QMessageBox.No , QMessageBox.No)
            if reply == QMessageBox.No:
                return
        DataBase.AllListCollection[item.field()][name] = self.model.to_json(item)

    @log_exception(True)
    def on_copyItem(self, checked: bool=False) -> None:
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

    @log_exception(True)
    def on_copyCollItem(self, checked: bool=False) -> None:
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
            self.loadCollection = CollectionGUI(item.field(), DataBase.AllCollection, self)
            self.loadCollection.setWindowTitle(item.field() + "类型收藏列表")
            self.loadCollection.exec_()
            
            name = self.loadCollection.lineEdit.text()
            if self.loadCollection.write_flag and name in DataBase.AllCollection[item.field()]:
                self.model.deleteItem(srcIndex)
                self.model.addJsonItem(srcIndex.parent(), DataBase.AllCollection[item.field()][name], item.field(), item.key())
                return

    @log_exception(True)
    def on_addRefItem(self, checked: bool=False) -> None:
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
                    else:
                        if select.lineEdit.text() in DataBase.AllGuid[item.field()]:
                            self.model.addRefWarp(index, DataBase.AllGuid[item.field()][select.lineEdit.text()])
                            return
                elif item.field() in DataBase.RefNameList:
                    self.model.addRefWarp(index, select.lineEdit.text())
                elif item.field() == "ScriptableObject":
                    self.model.addRefWarp(index, DataBase.AllScriptableObject[select.lineEdit.text()])
                    return

    @log_exception(True)
    def on_addEmptyRefItem(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

            child_key = 0
            while str(child_key) in item.mChilds:
                child_key += 1
            srcModel.addJsonItem(srcIndex, {"m_FileID": "", "m_PathID": ""}, None, str(child_key))