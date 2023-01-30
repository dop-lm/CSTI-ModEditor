# -*- coding: utf-8 -*- 

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_Item import *
from QJsonData import *
from SelectGUI import *
from NewItemGUI import *
from ItemDelegate import *
from ItemGUI import *
from data_base import *
from myLogger import *

class ModifyItemGUI(ItemGUI):
    def __init__(self, field, auto_resize = True, key: str = "", parent = None):
        super(ModifyItemGUI, self).__init__(field, auto_resize, key, parent)

    #override
    def addSpecialButton(self):
        if self.field == "CardData":
            cardTagButton = QPushButton("添加匹配CardTag", self)
            cardTagButton.clicked.connect(self.on_cardTagButton)
            self.horizontalLayout.insertWidget(2, cardTagButton)
            cardTypeButton = QPushButton("设置匹配CardType", self)
            cardTypeButton.clicked.connect(self.on_cardTypeButton)
            self.horizontalLayout.insertWidget(3, cardTypeButton)

    @log_exception(True)
    def on_cardTagButton(self, checked: bool=False) -> None:
        select = SelectGUI(self.treeView, field_name = "CardTag", type = SelectGUI.Ref)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            if "MatchTagWarpData" in self.model.mRootItem.mChilds:
                itemIndex = self.model.index(self.model.mRootItem.childRow("MatchTagWarpData"), 0, QModelIndex())
                child_key = 0
                while str(child_key) in itemIndex.internalPointer().mChilds:
                    child_key += 1
                self.model.addItem(itemIndex, str(child_key), str, select.lineEdit.text(), "SpecialWarp", True)
            else:
                self.model.addItem(QModelIndex(), "MatchTagWarpData", list, "", "SpecialWarp", True)
                itemIndex = self.model.index(self.model.mRootItem.childRow("MatchTagWarpData"), 0, QModelIndex())
                self.model.addItem(itemIndex, "0", str, select.lineEdit.text(), "SpecialWarp", True)
            return

    @log_exception(True)
    def on_cardTypeButton(self, checked: bool=False) -> None:
        select = SelectGUI(self.treeView, field_name = "CardTypes", type = SelectGUI.Ref)
        select.exec_()

        if select.write_flag and select.lineEdit.text():
            self.model.addItem(QModelIndex(), "MatchTypeWarpData", str, select.lineEdit.text(), "SpecialWarp", True)
            return
    
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
                if item.type() == "list" or item.type() == "dict":
                    pExpandAct = QAction("展开全部", menu)
                    pExpandAct.triggered.connect(self.on_actExpandAll)
                    menu.addAction(pExpandAct)

                if item.field() in DataBase.RefNameList or item.field() in DataBase.RefGuidList or item.field() == "ScriptableObject":
                    if item.parentDepth(1) is not None and item.parentDepth(1).key().endswith("WarpData"):
                        if item.type() == "list": 
                            pRefAct = QAction("追加引用", menu)
                        else:
                            pRefAct = QAction("引用", menu)
                        pRefAct.triggered.connect(self.on_addRefItem)
                        menu.addAction(pRefAct)
                    else:
                        if item.type() == "list":
                            pModifyRefAct = QAction("添加引用", menu)
                            pModifyRefAct.triggered.connect(self.on_addAddRefItem)
                            menu.addAction(pModifyRefAct)
                elif item.field() == "WarpType" or item.field() == "WarpData" or item.field() is None or item.field() == "" or \
                     item.field() == "None" or item.field() == "Boolean" or item.field() == "Int32" or item.field() == "Single" or item.field() == "String" or \
                        item.field() == "WarpAdd" or item.field() == "WarpModify":
                    pass
                elif item.key().endswith("WarpType"):
                    pass
                elif item.key().endswith("WarpData"):
                    if item.type() == "list":
                        pDelListAct = QAction("删除整个列表", menu)
                        pDelListAct.triggered.connect(self.on_delListItem)
                        menu.addAction(pDelListAct)
                else:
                    if item.parentDepth(1) is not None and item.parentDepth(1).key().endswith("WarpData"):
                        if item.parent().type() == "list":
                            pDeleteAct = QAction("删除", menu)
                            pDeleteAct.triggered.connect(self.on_delItemFromList)
                            menu.addAction(pDeleteAct)

                        if item.type() == "list":
                            pNewAct = QAction("新建空白项", menu)
                            pNewAct.triggered.connect(self.on_newItemToList)
                            menu.addAction(pNewAct)

                            pNewAct = QAction("载入收藏", menu)
                            pNewAct.triggered.connect(self.on_loadItem)
                            menu.addAction(pNewAct)

                            pNewListAct = QAction("载入整个列表收藏", menu)
                            pNewListAct.triggered.connect(self.on_loadListItem)
                            menu.addAction(pNewListAct)

                            pDelListAct = QAction("删除整个列表", menu)
                            pDelListAct.triggered.connect(self.on_delListItem)
                            menu.addAction(pDelListAct)
                        
                        if item.type() == "dict":              
                            pCopyCollAct = QAction("复制收藏并覆盖", menu)
                            pCopyCollAct.triggered.connect(self.on_copyCollItem)
                            menu.addAction(pCopyCollAct)
                    else:
                        if item.type() == "list":
                            pNewAct = QAction("引用新建空白项", menu)
                            pNewAct.triggered.connect(self.on_addEmptyItem)
                            menu.addAction(pNewAct)
                            pLoadAct = QAction("引用载入收藏", menu)
                            pLoadAct.triggered.connect(self.on_loadCollItem)
                            menu.addAction(pLoadAct)
                            pLoadListAct = QAction("引用载入整个列表收藏", menu)
                            pLoadListAct.triggered.connect(self.on_loadCollListItem)
                            menu.addAction(pLoadListAct)

                    if item.type() == "list":
                        pSaveListAct = QAction("收藏整个列表", menu)
                        pSaveListAct.triggered.connect(self.on_saveListItem)
                        menu.addAction(pSaveListAct)
                    
                    if item.type() == "dict":              
                        pSaveAct = QAction("收藏", menu)
                        pSaveAct.triggered.connect(self.on_saveItem)
                        menu.addAction(pSaveAct)
            if len(menu.actions()):
                menu.popup(self.sender().mapToGlobal(pos))

    @log_exception(True)
    def on_loadCollItem(self, checked: bool=False) -> None:
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
            self.addWarpItem(index, "Collection", DataBase.AllCollection[item.field()][name])

    @log_exception(True)
    def on_loadCollListItem(self, checked: bool=False) -> None:
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
                self.addWarpItem(index, "Collection", DataBase.AllListCollection[item.field()][name][i])

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
    def on_addAddRefItem(self, checked: bool=False) -> None:
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
                            self.addWarpItem(index, "Ref", DataBase.AllCardData[select.lineEdit.text()])
                            # self.model.addRefWarp(index, DataBase.AllCardData[select.lineEdit.text()])
                            return
                    else:
                        if select.lineEdit.text() in DataBase.AllGuid[item.field()]:
                            self.addWarpItem(index, "Ref", DataBase.AllGuid[item.field()][select.lineEdit.text()])
                            # self.model.addRefWarp(index, DataBase.AllGuid[item.field()][select.lineEdit.text()])
                            return
                elif item.field() in DataBase.RefNameList:
                    self.addWarpItem(index, "Ref", select.lineEdit.text())
                    # self.model.addRefWarp(index, select.lineEdit.text())
                elif item.field() == "ScriptableObject":
                    self.addWarpItem(index, "Ref", DataBase.AllScriptableObject[select.lineEdit.text()])
                    # self.model.addRefWarp(index, DataBase.AllScriptableObject[select.lineEdit.text()])
                    return

    @log_exception(True)
    def on_addEmptyItem(self, checked: bool=False):
        index = self.treeView.currentIndex()
        self.addWarpItem(index, "Empty")
                    
    def addWarpItem(self, index: QModelIndex, mode: str, param: str = ""):
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

            src_field = item.field()
            item_stack = []
            item_stack.append({"item": item, "index": srcIndex})
            while item.parent():
                item_stack.append({"item": item.parent(), "index": srcIndex.parent()})
                item = item.parent()
                srcIndex = srcIndex.parent()

            parentItem, parentIndex = item_stack.pop().values()
            warpDataItem, warpDataIndex = None, None
            while len(item_stack) != 0:
                childItem, childIndex = item_stack.pop().values()
                if len(item_stack) > 0:
                    if warpDataItem is None:
                        if childItem.key() + "WarpType" in parentItem.mChilds:
                            if parentItem.mChilds[childItem.key() + "WarpType"].value() != 5:
                                reply = QMessageBox.question(self, '警告', '存在其他类型的Warp，是否覆盖', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                if reply == QMessageBox.No:
                                    return  
                                self.model.addModifyWarp(childIndex, srcItem=childItem)
                                warpDataItem = parentItem.mChilds[childItem.key() + "WarpData"]
                                warpDataIndex = self.model.index(warpDataItem.row(), 0, parentIndex)
                                if childItem.type() == "list":
                                    for key in childItem.mChilds.keys():
                                        self.model.addItem(warpDataIndex, key, dict, "", childItem.field(), True)
                                elif childItem.type() == "dict":
                                    pass
                            else:
                                warpDataItem = parentItem.mChilds[childItem.key() + "WarpData"]
                                warpDataIndex = self.model.index(warpDataItem.row(), 0, parentIndex)
                        else:
                            self.model.addModifyWarp(childIndex, srcItem=childItem)
                            warpDataItem = parentItem.mChilds[childItem.key() + "WarpData"]
                            warpDataIndex = self.model.index(warpDataItem.row(), 0, parentIndex)
                            if childItem.type() == "list":
                                for key in childItem.mChilds.keys():
                                    self.model.addItem(warpDataIndex, key, dict, "", childItem.field(), True)
                            elif childItem.type() == "dict":
                                pass
                    else:
                        if parentItem.type() == "list":
                            warpDataItem = warpDataItem.mChilds[childItem.key()]
                            warpDataIndex = self.model.index(warpDataItem.row(), 0, warpDataIndex)
                        elif parentItem.type() == "dict":
                            if childItem.key() + "WarpType" in warpDataItem.mChilds:
                                if warpDataItem.mChilds[childItem.key() + "WarpType"].value() != 5:
                                    reply = QMessageBox.question(self, '警告', '存在其他类型的Warp，是否覆盖', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                    if reply == QMessageBox.No:
                                        return
                                    self.model.addModifyWarp(warpDataIndex, srcItem=childItem, brother=False)
                                    warpDataItem = warpDataItem.mChilds[childItem.key() + "WarpData"]
                                    warpDataIndex = self.model.index(warpDataItem.row(), 0, warpDataIndex)
                                    if childItem.type() == "list":
                                        for key in childItem.mChilds.keys():
                                            self.model.addItem(warpDataIndex, key,  dict, "", childItem.field(), True)
                                    elif childItem.type() == "dict":
                                        pass
                                else:
                                    warpDataItem = warpDataItem.mChilds[childItem.key() + "WarpData"]
                                    warpDataIndex = self.model.index(warpDataItem.row(), 0, warpDataIndex)
                            else:
                                self.model.addModifyWarp(warpDataIndex, srcItem=childItem, brother=False)
                                warpDataItem = warpDataItem.mChilds[childItem.key() + "WarpData"]
                                warpDataIndex = self.model.index(warpDataItem.row(), 0, warpDataIndex)
                                if childItem.type() == "list":
                                    print("key", childItem.key(), childItem.mChilds.keys())
                                    for key in childItem.mChilds.keys():
                                        self.model.addItem(warpDataIndex, key,  dict, "", childItem.field(), True)
                                elif childItem.type() == "dict":
                                    pass
                        else:
                            print("Unexpect type 1 !!!")
                else:
                    if warpDataItem is None:
                        if src_field in DataBase.RefNameList or src_field in DataBase.RefGuidList or src_field == "ScriptableObject":
                            self.model.addAddRefWarp(childIndex, param, key = childItem.key())
                        else:
                            if childItem.key() + "WarpType" in parentItem.mChilds:
                                if parentItem.mChilds[childItem.key() + "WarpType"].value() != 4:
                                    reply = QMessageBox.question(self, '警告', '存在其他类型的Warp，是否覆盖', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                    if reply == QMessageBox.No:
                                        return
                                    self.model.addAddWarp(childIndex, srcItem=childItem)
                            else:
                                self.model.addAddWarp(childIndex, srcItem=childItem)
                            warpDataItem = parentItem.mChilds[childItem.key() + "WarpData"]
                            warpDataIndex = self.model.index(warpDataItem.row(), 0, parentIndex)
                            if warpDataItem.type() == "list":
                                if mode == "Empty":
                                    if self.field in DataBase.AllBaseJsonData and childItem.field() in DataBase.AllBaseJsonData[self.field]:
                                        data = DataBase.AllBaseJsonData[self.field][childItem.field()]
                                    child_key = 0
                                    while str(child_key) in warpDataItem.mChilds:
                                        child_key += 1
                                    self.model.addJsonItem(warpDataIndex, data, childItem.field(), str(child_key))
                                elif mode == "Collection":
                                    child_key = 0
                                    while str(child_key) in warpDataItem.mChilds:
                                        child_key += 1
                                    self.model.addJsonItem(warpDataIndex, param, childItem.field(), str(child_key))
                                elif mode == "Ref":
                                    return
                            else:
                                print("Unexpect type 2 !!!")
                    else:
                        if src_field in DataBase.RefNameList or src_field in DataBase.RefGuidList or src_field == "ScriptableObject":
                            print(warpDataItem.key())
                            self.model.addAddRefWarp(warpDataIndex, param, key = childItem.key(), brother=False)
                        else:
                            if childItem.key() + "WarpType" in warpDataItem.mChilds:
                                if warpDataItem.mChilds[childItem.key() + "WarpType"].value() != 4:
                                    reply = QMessageBox.question(self, '警告', '存在其他类型的Warp，是否覆盖', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                    if reply == QMessageBox.No:
                                        return
                                    self.model.addAddWarp(warpDataIndex, srcItem=childItem, brother = False)
                            else:
                                self.model.addAddWarp(warpDataIndex, srcItem=childItem, brother = False)
                            warpDataItem = warpDataItem.mChilds[childItem.key() + "WarpData"]
                            warpDataIndex = self.model.index(warpDataItem.row(), 0, warpDataIndex)
                            if warpDataItem.type() == "list":
                                if mode == "Empty":
                                    if self.field in DataBase.AllBaseJsonData and childItem.field() in DataBase.AllBaseJsonData[self.field]:
                                        data = DataBase.AllBaseJsonData[self.field][childItem.field()]
                                    child_key = 0
                                    while str(child_key) in warpDataItem.mChilds:
                                        child_key += 1
                                    self.model.addJsonItem(warpDataIndex, data, childItem.field(), str(child_key))
                                elif mode == "Collection":
                                    child_key = 0
                                    while str(child_key) in warpDataItem.mChilds:
                                        child_key += 1
                                    self.model.addJsonItem(warpDataIndex, param, childItem.field(), str(child_key))
                                elif mode == "Ref":
                                    return
                            else:
                                print("Unexpect type 3 !!!")
                parentItem = childItem
                parentIndex = childIndex