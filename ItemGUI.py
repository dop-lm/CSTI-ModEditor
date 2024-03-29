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
from DataBase import *

class ItemGUI(QWidget, Ui_Item):
    def __init__(self, parent=None, field:str="", key:str="", item_name:str="", guid:str="", \
        auto_resize:bool=True, auto_replace_key_guid:bool=False, mod_info:dict=None, mod_path:str=""):
        super(ItemGUI, self).__init__(parent)
        self.setupUi(self)
        self.field = field
        self.item_name = item_name
        self.guid = guid
        self.mod_info = mod_info
        self.mod_path = mod_path
        self.tab_key = key
        self.auto_replace_key_guid = auto_replace_key_guid
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

        self.showInvalidButton.setText(self.tr("Show invalid entries"))
        self.show_invalid = False
        self.showInvalidButton.clicked.connect(self.on_showInvalidButtonClicked)

        self.lineEdit.textChanged.connect(self.on_lineEditTextChanged)

        self.addSpecialButton()

    def addSpecialButton(self):
        if self.field == "CardData":
            tabButton = QPushButton(self.tr("Add blueprint main group"), self)
            tabButton.clicked.connect(self.on_tabButtonCardDataMainTabGroup)
            self.horizontalLayout.insertWidget(2, tabButton)
            subTabButton = QPushButton(self.tr("Add blueprint sub group"), self)
            subTabButton.clicked.connect(self.on_tabButtonCardDataSubTabGroup)
            self.horizontalLayout.insertWidget(3, subTabButton)
            label = QLabel(self.tr("<-Don't add that cardtype are not blueprint"))
            self.horizontalLayout.insertWidget(4, label)
            subGpTabButton = QPushButton(self.tr("Add the CardTabGroup which it belong"), self)
            subGpTabButton.clicked.connect(self.on_tabButtonCardDataGpTabGroup)
            self.horizontalLayout.insertWidget(5, subGpTabButton)
            cardFilterGroupButton = QPushButton(self.tr("Add the CardFilterGroup which it belong"), self)
            cardFilterGroupButton.clicked.connect(self.on_tabButtonCardDataCardFilterGroup)
            self.horizontalLayout.insertWidget(6, cardFilterGroupButton)
        if self.field == "CharacterPerk":
            tabButton = QPushButton(self.tr("Add perk exclusive group"), self)
            self.horizontalLayout.insertWidget(2, tabButton)
            tabButton.clicked.connect(self.on_tabButtonCharacterPerk)
        if self.field == "GameStat":
            tabButton = QPushButton(self.tr("Add displayable status group"), self)
            self.horizontalLayout.insertWidget(2, tabButton)
            tabButton.clicked.connect(self.on_tabButtonGameStat)
        if self.field == "CardTabGroup":
            tabButton = QPushButton(self.tr("Add blueprint main group"), self)
            tabButton.clicked.connect(self.on_tabButtonCardDataMainTabGroup)
            self.horizontalLayout.insertWidget(2, tabButton)
            # addTagButton = QPushButton(self.tr("Add tag in IncludedCards"), self)
            # self.horizontalLayout.insertWidget(3, addTagButton)
            # addTagButton.clicked.connect(self.on_addTagButtonCardTabGroupIncludedCards)
            # delTagButton = QPushButton(self.tr("Del tag in IncludedCards"), self)
            # self.horizontalLayout.insertWidget(4, delTagButton)
            # delTagButton.clicked.connect(self.on_delTagButtonCardTabGroupIncludedCards)
        if self.field == "PlayerCharacter":
            tabButton = QPushButton(self.tr("Add character journal"), self)
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
        
    # @log_exception(True)
    # def on_addTagButtonCardTabGroupIncludedCards(self, checked: bool=False):
    #     if self.mod_path:
    #         pass

    # @log_exception(True)
    # def on_delTagButtonCardTabGroupIncludedCards(self, checked: bool=False):
    #     if self.mod_path:
    #         IncludedCardsItem = self.model.mRootItem.childByKey("IncludedCardsWarpData")
    #         if IncludedCardsItem is None:
    #             return
    #         select = SelectGUI(self.treeView, field_name = "CardTag", type = SelectGUI.Ref)
    #         select.exec_()
    #         if select.write_flag and select.lineEdit.text():
    #             for file in [y for x in os.walk(self.mod_path + r"/CardData") for y in glob(os.path.join(x[0], '*.json'))]:
    #                 with open(file, "r", encoding='utf-8') as f:
    #                     data = f.read(-1)
    #                     for child in IncludedCardsItem.mChilds.values():
    #                         guid_idx = data.find('"UniqueID": "{0}"'.format(child.mValue))
    #                         if guid_idx == -1:
    #                             continue
    #                         else:
    #                             print(file)

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
    def on_tabButtonCardDataCardFilterGroup(self, checked: bool=False):
        select = SelectGUI(self.treeView, field_name = "CardDataCardFilterGroup", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            if "CardDataCardFilterGroup" in self.model.mRootItem.mChilds:
                itemIndex = self.model.index(self.model.mRootItem.childRow("CardDataCardFilterGroup"), 0, QModelIndex())
                child_key = 0
                while str(child_key) in itemIndex.internalPointer().mChilds:
                    child_key += 1
                self.model.addItem(itemIndex, str(child_key), str, select.lineEdit.text(), "SpecialWarp", True)
            else:
                self.model.addItem(QModelIndex(), "CardDataCardFilterGroup", list, "", "SpecialWarp", True)
                itemIndex = self.model.index(self.model.mRootItem.childRow("CardDataCardFilterGroup"), 0, QModelIndex())
                self.model.addItem(itemIndex, "0", str, select.lineEdit.text(), "SpecialWarp", True)
            return

    @log_exception(True)
    def on_tabButtonGameStat(self, checked: bool=False):
        select = SelectGUI(self.treeView, field_name = "VisibleGameStatStatListTab", type = SelectGUI.Special)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            self.model.addItem(QModelIndex(), "VisibleGameStatStatListTab", str, select.lineEdit.text(), "SpecialWarp", True)
            return

    def loadJsonData(self, json_data: dict, is_modify: bool=False):
        self.model = QJsonModel(self.field, is_modify=is_modify)
        self.model.loadJson(json_data)
        self.proxy_model = QJsonProxyModel(self.treeView)
        self.proxy_model.setSourceModel(self.model)
        self.treeView.setModel(self.proxy_model)
        # for i in range(self.model.columnCount()):
        #     self.treeView.resizeColumnToContents(i)

    @log_exception(True)
    def on_showInvalidButtonClicked(self, checked: bool=False) -> None:
        if not self.show_invalid:
            self.showInvalidButton.setText(self.tr("Hide invalid entries"))
            self.proxy_model.setVaildFilter(False)
            self.show_invalid = True
        else:
            self.showInvalidButton.setText(self.tr("Show invalid entries"))
            self.proxy_model.setVaildFilter(True)
            self.show_invalid = False

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
                    pDeleteAct = QAction(self.tr("Delete"), menu)
                    pDeleteAct.triggered.connect(self.on_delItem)
                    menu.addAction(pDeleteAct)

                if item.parent().type() == "list" and item.depth() > 1:
                    pDeleteAct = QAction(self.tr("Delete"), menu)
                    pDeleteAct.triggered.connect(self.on_delItemFromList)
                    menu.addAction(pDeleteAct)

                if item.type() == "list" or item.type() == "dict":
                    pExpandAct = QAction(self.tr("Expand All"), menu)
                    pExpandAct.triggered.connect(self.on_actExpandAll)
                    menu.addAction(pExpandAct)

                    pCollapseAct = QAction(self.tr("Collapse All"), menu)
                    pCollapseAct.triggered.connect(self.on_actCollapseAll)
                    # menu.addAction(pCollapseAct)

                if item.type() == "list" and item.field() == "WarpRef":
                    pDelListAct = QAction(self.tr("Delete Whole List"), menu)
                    pDelListAct.triggered.connect(self.on_delListItem)
                    menu.addAction(pDelListAct)
                
                if item.field() in DataBase.RefNameList or item.field() in DataBase.RefGuidList or item.field() == "ScriptableObject":
                    if item.type() == "list": 
                        pRefAct = QAction(self.tr("Append Reference"), menu)
                        
                        pSaveListAct = QAction(self.tr("Save List Collection"), menu)
                        pSaveListAct.triggered.connect(self.on_saveRefListItem)
                        menu.addAction(pSaveListAct)

                        pNewListAct = QAction(self.tr("Load List Collection"), menu)
                        pNewListAct.triggered.connect(self.on_loadRefListItem)
                        menu.addAction(pNewListAct)

                        if item.key() == "InventorySlots":
                            pEmptyRefAct = QAction(self.tr("Append Inventory Slot"), menu)
                            pEmptyRefAct.triggered.connect(self.on_addEmptyRefItem)
                            menu.addAction(pEmptyRefAct)
                    else:
                        pRefAct = QAction(self.tr("Reference"), menu)
                    pRefAct.triggered.connect(self.on_addRefItem)
                    menu.addAction(pRefAct)
                elif item.field() == "WarpType" or item.field() == "WarpRef" or item.field() is None or item.field() == "" or \
                    item.field() == "SpecialWarp" or item.field() == "None" or item.field() == "Boolean" or item.field() == "Int32" or item.field() == "Single" or item.field() == "String":
                    pass
                else:
                    if item.depth() == 1:
                        pCopyAct = QAction(self.tr("Copy Template and Overwrite"), menu)
                        pCopyAct.triggered.connect(self.on_copyItem)
                        menu.addAction(pCopyAct)

                        if item.type() == "list":
                            pAddAct = QAction(self.tr("Append Template Entries"), menu)
                            pAddAct.triggered.connect(self.on_addItemToList)
                            menu.addAction(pAddAct)

                    if item.type() == "dict":
                        pCopyCollAct = QAction(self.tr("Copy Collection and Overwrite"), menu)
                        pCopyCollAct.triggered.connect(self.on_copyCollItem)
                        menu.addAction(pCopyCollAct)
                    
                        pSaveAct = QAction(self.tr("Save Collection"), menu)
                        pSaveAct.triggered.connect(self.on_saveItem)
                        menu.addAction(pSaveAct)

                    if item.type() == "list":
                        pNewAct = QAction(self.tr("New Empty Entry"), menu)
                        pNewAct.triggered.connect(self.on_newItemToList)
                        menu.addAction(pNewAct)

                        pNewAct = QAction(self.tr("Load Collection"), menu)
                        pNewAct.triggered.connect(self.on_loadItem)
                        menu.addAction(pNewAct)

                        pSaveListAct = QAction(self.tr("Save List Collection"), menu)
                        pSaveListAct.triggered.connect(self.on_saveListItem)
                        menu.addAction(pSaveListAct)

                        pNewListAct = QAction(self.tr("Load List Collection"), menu)
                        pNewListAct.triggered.connect(self.on_loadListItem)
                        menu.addAction(pNewListAct)

                        pDelListAct = QAction(self.tr("Delete Whole List"), menu)
                        pDelListAct.triggered.connect(self.on_delListItem)
                        menu.addAction(pDelListAct)

            if len(menu.actions()):
                menu.popup(self.sender().mapToGlobal(pos))

    def CollapseChildren(self, index: QModelIndex) -> None:
        if index.isValid():
            for i in range(index.model().rowCount(index)):
                child_index = index.child(i, 0)
                self.CollapseChildren(child_index)
            self.treeView.collapse(index)

    @log_exception(True)
    def on_actCollapseAll(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            self.CollapseChildren(index)

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
        reply = QMessageBox.question(self, self.tr("Warning"), self.tr("Sure you want to delete the whole list?"), QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel , QMessageBox.No)
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
                        with open(DataBase.AllPath[self.field][template_key], 'r', encoding='utf-8') as f:
                            data = json.load(f)[item.key()]
                        if type(data) is list:
                            for sub_data in data:
                                child_key = 0
                                while str(child_key) in item.mChilds:
                                    child_key += 1
                                if self.auto_replace_key_guid:
                                    loopReplaceLocalizationKeyAndReplaceGuid(sub_data, self.mod_info["Name"], self.item_name, self.guid, item.key(), child_key)
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

        if item.field() in DataBase.AllBaseJsonData:
            data = DataBase.AllBaseJsonData[item.field()]         
            if item.field() in DataBase.AllEnum:
                data = 0   
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
            QMessageBox.information(self, self.tr("Info"),self.tr("The related collection is empty, please add the collection first"))
            return
        self.loadCollection = CollectionGUI(item.field(), DataBase.AllCollection, self)
        self.loadCollection.setWindowTitle(item.field() + self.tr(" type collection list"))
        self.loadCollection.exec_()
        
        name = self.loadCollection.lineEdit.text()
        
        if self.loadCollection.write_flag and name in DataBase.AllCollection[item.field()]:
            child_key = 0
            while str(child_key) in item.mChilds:
                child_key += 1
            data = copy.deepcopy(DataBase.AllCollection[item.field()][name])
            if self.auto_replace_key_guid:
                loopReplaceLocalizationKeyAndReplaceGuid(data, self.mod_info["Name"], self.item_name, self.guid, item.key(), child_key)
            self.model.addJsonItem(srcIndex, data, item.field(), str(child_key))
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
            QMessageBox.information(self, self.tr("Info"), self.tr("The related collection is empty, please add the collection first"))
            return
        self.loadCollection = CollectionGUI(item.field(), DataBase.AllListCollection, self)
        self.loadCollection.setWindowTitle(item.field() + self.tr(" type collection list"))
        self.loadCollection.exec_()
        
        name = self.loadCollection.lineEdit.text()
        
        if self.loadCollection.write_flag and name in DataBase.AllListCollection[item.field()]:
            for i in range(len(DataBase.AllListCollection[item.field()][name])):
                child_key = 0
                while str(child_key) in item.mChilds:
                    child_key += 1
                data = copy.deepcopy(DataBase.AllListCollection[item.field()][name][i])
                if self.auto_replace_key_guid:
                    loopReplaceLocalizationKeyAndReplaceGuid(data, self.mod_info["Name"], self.item_name, self.guid, item.key(), child_key)
                self.model.addJsonItem(srcIndex, data, item.field(), str(child_key))
            return
        
    @log_exception(True)
    def on_loadRefListItem(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index
        if item.field() not in DataBase.AllListCollection or len(DataBase.AllListCollection[item.field()]) == 0:
            QMessageBox.information(self, self.tr("Info"), self.tr("The related collection is empty, please add the collection first"))
            return
        self.loadCollection = CollectionGUI(item.field(), DataBase.AllListCollection, self)
        self.loadCollection.setWindowTitle(item.field() + self.tr(" type collection list"))
        self.loadCollection.exec_()
        
        warpTypeItem = item.brother(item.key() + "WarpType")
        warpDataItem = item.brother(item.key() + "WarpData")
        if warpTypeItem is None or warpDataItem is None:
            return
        
        name = self.loadCollection.lineEdit.text()
        
        if self.loadCollection.write_flag and name in DataBase.AllListCollection[item.field()]:
            for i in range(len(DataBase.AllListCollection[item.field()][name])):
                data = copy.deepcopy(DataBase.AllListCollection[item.field()][name][i])
                self.addRefItem(data, item, index)
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
        self.newSave.setWindowTitle(self.tr("Add ") + item.field() + self.tr(" type collection"))
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
        self.newSaveList.setWindowTitle(self.tr("Add ") + item.field() + self.tr("[] type collection"))
        self.newSaveList.exec_()

    @log_exception(True)
    def on_saveRefListItem(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

        self.newSaveList = NewItemGUI(self)
        self.newSaveList.buttonBox.accepted.connect(lambda : self.on_newSaveRefListButtonBoxAccepted(item))
        self.newSaveList.setWindowTitle(self.tr("Add ") + item.field() + self.tr("[] type collection"))
        self.newSaveList.exec_()

    @log_exception(True)
    def on_newSaveButtonBoxAccepted(self, item: QJsonTreeItem):
        name = self.newSave.lineEdit.text()
        if not name:
            return
        if item.field() not in DataBase.AllCollection:
            DataBase.AllCollection[item.field()] = {}
        if name in DataBase.AllCollection[item.field()]:
            reply = QMessageBox.question(self, self.tr("Warning"), self.tr("Cover the collection of the same name?"), QMessageBox.Yes | QMessageBox.No , QMessageBox.No)
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
            reply = QMessageBox.question(self, self.tr("Warning"), self.tr("Cover the collection of the same name?"), QMessageBox.Yes | QMessageBox.No , QMessageBox.No)
            if reply == QMessageBox.No:
                return
        DataBase.AllListCollection[item.field()][name] = self.model.to_json(item)

    @log_exception(True)
    def on_newSaveRefListButtonBoxAccepted(self, item: QJsonTreeItem):
        name = self.newSaveList.lineEdit.text()
        if not name:
            return
        warpTypeItem = item.brother(item.key() + "WarpType")
        warpDataItem = item.brother(item.key() + "WarpData")
        if warpTypeItem is None or warpDataItem is None:
            return

        if item.field() not in DataBase.AllListCollection:
            DataBase.AllListCollection[item.field()] = {}
        if name in DataBase.AllListCollection[item.field()]:
            reply = QMessageBox.question(self, self.tr("Warning"), self.tr("Cover the collection of the same name?"), QMessageBox.Yes | QMessageBox.No , QMessageBox.No)
            if reply == QMessageBox.No:
                return
        DataBase.AllListCollection[item.field()][name] = self.model.to_json(warpDataItem)

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
                        with open(DataBase.AllPath[self.field][template_key], 'r', encoding='utf-8') as f:
                            data = json.load(f)[item.key()]
                        if self.auto_replace_key_guid:
                            loopReplaceLocalizationKeyAndReplaceGuid(data, self.mod_info["Name"], self.item_name, self.guid)
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
                QMessageBox.information(self, self.tr("Info"), self.tr("The related collection is empty, please add the collection first"))
                return
            self.loadCollection = CollectionGUI(item.field(), DataBase.AllCollection, self)
            self.loadCollection.setWindowTitle(item.field() + self.tr(" type collection"))
            self.loadCollection.exec_()
            
            name = self.loadCollection.lineEdit.text()
            if self.loadCollection.write_flag and name in DataBase.AllCollection[item.field()]:
                self.model.deleteItem(srcIndex)
                data = copy.deepcopy(DataBase.AllCollection[item.field()][name])
                if self.auto_replace_key_guid:
                    loopReplaceLocalizationKeyAndReplaceGuid(data, self.mod_info["Name"], self.item_name, self.guid)
                self.model.addJsonItem(srcIndex.parent(), data, item.field(), item.key())
                return

    def addRefItem(self, data:str, item, index:QModelIndex):
        if data == "":
            if item.type() == "list":
                reply = QMessageBox.question(self, self.tr('Warning'), self.tr('Sure you want to delete the whole list?'), QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel , QMessageBox.Yes)
                if reply != QMessageBox.Yes:
                    return
            self.model.addRefWarp(index, data)
        elif item.field() in DataBase.RefGuidList:
            if item.field() == "CardData":
                if data in DataBase.AllCardData:
                    self.model.addRefWarp(index, DataBase.AllCardData[data])
                    return
            else:
                if data in DataBase.AllGuid[item.field()]:
                    self.model.addRefWarp(index, DataBase.AllGuid[item.field()][data])
                    return
        elif item.field() in DataBase.RefNameList:
            self.model.addRefWarp(index, data)
        elif item.field() == "ScriptableObject":
            if data in DataBase.AllScriptableObject:
                self.model.addRefWarp(index, DataBase.AllScriptableObject[data])
            else:
                reply = QMessageBox.question(self, self.tr('Warning'), self.tr('Add an object that does not belong to this Mod (possibly a Tag)?'), QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel , QMessageBox.Yes)
                if reply == QMessageBox.Yes:
                    self.model.addRefWarp(index, data)
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
                self.addRefItem(select.lineEdit.text(), item, index)

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