# 2017 by Gregor Engberding , MIT License

import sys
import re
import traceback
from data_base import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

pattern_number = ''': [1-9]'''
pattern_decimal = ''': 0.0*[1-9]{1,}.*?,'''
pattern_true = ''': true'''
pattern_no_empty_string = ''':""[^""]"'''
pattern_negative = ''': -'''

class QJsonTreeItem(object):
    def __init__(self, parent=None):
        self.mParent = parent
        self.mChilds = {}
        self.mType = None
        self.mValue = None
        self.mField = None
        self.mVaild = False
        self.mDepth = None
        self.mNote = None
        self.mCustomNote = ""

    def appendChild(self, key, item):
        self.mChilds[key] = item

    def child(self, row:int):
        return self.mChilds[list(self.mChilds.keys())[row]]

    def childByKey(self, key:str):
        if key in self.mChilds:
            return self.mChilds[key]
        return None

    def brother(self, key: str):
        try:
            return self.mParent.mChilds[key]
        except Exception as ex:
            return None

    def newItem(parent, mKey = None, mType = None, mValue = None, mField = None, mVaild = False):
        item = QJsonTreeItem(parent)
        if parent is None:
            item.setDepth(0)
        else:
            item.setDepth(parent.depth() + 1)
        item.setKey(mKey)
        item.setType(mType)
        item.setValue(mValue)
        item.setField(mField)
        item.setVaild(mVaild)
        return item

    def parent(self):
        return self.mParent

    def parentDepth(self, depth: int):
        if depth >= self.depth():
            return None
        parentItem = self.mParent
        while True:
            if parentItem is None:
                return None 
            if parentItem.depth() == depth:
                return parentItem
            parentItem = parentItem.mParent

    def childCount(self):
        return len(self.mChilds)

    def childRow(self, key: str):
        if key in self.mChilds:
            return list(self.mChilds.keys()).index(key)
        return None

    def row(self):
        if self.mParent is not None:
            return list(self.mParent.mChilds.keys()).index(self.mKey)
        return 0

    def setKey(self, key:str):
        self.mKey = key

    def setValue(self, value:str):
        if self.mType == "bool" or (self.mType == "str" and self.mField == "Boolean"):
            if value == "True":
                self.mValue = True
            else:
                self.mValue = False
        else:
            self.mValue = value

    def setField(self, value:str):
       self.mField = value

    def setVaild(self, value:bool):
       self.mVaild = value

    def setDepth(self, value:int):
       self.mDepth = value
    
    def setNote(self, value:str):
        self.mNote = value

    def setCustomNote(self, value:str):
        self.mCustomNote = value

    def setType(self, type:QJsonValue.Type):
        if type == QJsonValue.Type.Array or type == list:
            self.mType = "list"
        elif type == QJsonValue.Type.Bool or type == bool:
            self.mType = "bool"
        elif type == QJsonValue.Type.Double or type == float:
            self.mType = "float"
        elif type == QJsonValue.Type.String or type == str:
            self.mType = "str"
        elif type == QJsonValue.Type.Object or type == dict:
            self.mType = "dict"
        elif type == int:
            self.mType = "int"
        else:
            self.mType = type

    def key(self):
        return self.mKey

    def field(self):
        return self.mField

    def value(self):
        return self.mValue

    def depth(self):
        return self.mDepth

    def type(self):
        return self.mType

    def vaild(self):
        return self.mVaild

    def note(self):
        return self.mNote

    def customNote(self):
        return self.mCustomNote

    def load(value, itemField = "", parent = None, itemKey = None):
        rootItem = QJsonTreeItem(parent)
        if itemKey is None:
            rootItem.setKey("root")
        else:
            rootItem.setKey(itemKey)

        if itemField in DataBase.AllTypeField:
            rootItem.setField(itemField)
            
        jsonType = None
        if parent is None:
            rootItem.setDepth(0)
        else:
            rootItem.setDepth(parent.depth() + 1)

        try:
            value = value.toVariant()
            jsonType = value.type()
        except AttributeError:
            pass

        try:
            value = value.toObject()
            jsonType = value.type()
        except AttributeError:
            pass

        if isinstance(value, dict):
            rootItem.setType(dict)

            # process the key/value pairs
            if re.search(pattern_number, str(value)):
                if rootItem.parent() is not None:
                    rootItem.parent().setVaild(True)
                rootItem.setVaild(True)
            elif re.search(pattern_decimal, str(value)):
                if rootItem.parent() is not None:
                    rootItem.parent().setVaild(True)
                rootItem.setVaild(True)
            elif re.search(pattern_true, str(value)):
                if rootItem.parent() is not None:
                    rootItem.parent().setVaild(True)
                rootItem.setVaild(True)
            elif re.search(pattern_negative, str(value)):
                if rootItem.parent() is not None:
                    rootItem.parent().setVaild(True)
                rootItem.setVaild(True)
            elif re.search(pattern_no_empty_string, str(value)):
                if rootItem.parent() is not None:
                    rootItem.parent().setVaild(True)
                rootItem.setVaild(True)
            else:
                pass

            for key in value:
                v = value[key]
                if itemField in DataBase.AllTypeField:
                    if key in DataBase.AllTypeField[itemField]:
                        child = QJsonTreeItem.load(v, DataBase.AllTypeField[itemField][key], rootItem, key)
                        child.setField(DataBase.AllTypeField[itemField][key])
                        if itemField in DataBase.AllNotes:
                            if key in DataBase.AllNotes[itemField]:
                                child.setNote(DataBase.AllNotes[itemField][key])
                    elif key.endswith("WarpData") and key[:-8] + "WarpType" in value and (value[key[:-8] + "WarpType"] == 4 or value[key[:-8] + "WarpType"] == 5):
                        child = QJsonTreeItem.load(v, DataBase.AllTypeField[itemField][key[:-8]], rootItem, key)
                    else:
                        child = QJsonTreeItem.load(v, "", rootItem, key)
                else:
                    child = QJsonTreeItem.load(v, "", rootItem, key)               
                child.setKey(key)
                try:
                    child.setType(v.type())
                except AttributeError:
                    child.setType(v.__class__)
                rootItem.appendChild(key, child)
        elif isinstance(value, list):
            rootItem.setType(list)
            if len(value) > 0:
                if rootItem.parent is not None:
                    rootItem.parent().setVaild(True)
                rootItem.setVaild(True)

            # process the values in the list
            for i, v in enumerate(value):
                child = QJsonTreeItem.load(v, itemField, rootItem, rootItem.mKey)
                child.setKey(str(i))
                child.setType(v.__class__)
                child.setField(itemField)
                rootItem.appendChild(str(i), child)
        else:
            if value:
                if rootItem.parent is not None:
                    rootItem.parent().setVaild(True)
                rootItem.setVaild(True)
            else:
                rootItem.setVaild(False)
                
            # value is processed
            rootItem.setValue(value)
            try:
                rootItem.setType(value.type())
            except AttributeError:
                if jsonType is not None:
                    rootItem.setType(jsonType)
                else:
                    rootItem.setType(value.__class__)

        if isinstance(value, dict):
            # process the key/value pairs
            for key in value:
                if key.endswith("WarpType"):
                    if key[:-8] in rootItem.mChilds:
                        rootItem.mChilds[key[:-8]].setVaild(True)

        if rootItem.mVaild:
            if rootItem.parent() is not None:
                rootItem.parent().setVaild(True)

        # if rootItem.mChilds:
        #     rootItem.mChilds = {k: v for k, v in sorted(rootItem.mChilds.items(), key=lambda item: item[1].mVaild, reverse=True)}
        return rootItem

class reversor:
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        return other.obj == self.obj

    def __lt__(self, other):
           return other.obj < self.obj

class QJsonProxyModel(QSortFilterProxyModel):
    def __init__(self, parent = None):
        super(QJsonProxyModel, self).__init__(parent)
        self.vaildFilter = QRegExp("True")
        self.keyFilter = QRegExp("")
        self.keyFilter.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

    def getSourceModelItemIndex(self, index: QModelIndex):
        srcIndex = self.mapToSource(index)
        srcModel = self.sourceModel()
        srcItem = srcIndex.internalPointer()
        return srcModel, srcItem, srcIndex

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        item = self.sourceModel().index(source_row, 0, source_parent).internalPointer()
        if item.depth() == 1:
            if self.keyFilter.indexIn(str(item.key())) != -1 and self.vaildFilter.indexIn(str(item.vaild())) != -1:
                return True
        else:
            if self.vaildFilter.indexIn(str(item.vaild())) != -1:
                return True
        return False

    def setVaildFilter(self, vaild: bool):
        if vaild:
            self.vaildFilter.setPattern("True")
        else:
            self.vaildFilter.setPattern("")
        self.invalidateFilter()

    def setKeyFilter(self, match: str):
        self.keyFilter.setPattern(match)
        self.invalidateFilter()

class QJsonModel(QAbstractItemModel):
    def __init__(self, root_field, parent = None, is_modify = False):
        super().__init__(parent)
        self.mRootItem = QJsonTreeItem()
        self.mHeaders = ["key", "value", "field", "type", "vaild", "note", "custom note"]
        self.root_field = root_field
        self.is_modify = is_modify

    def loadJson(self, json):
        error = QJsonParseError()
        self.mDocument = QJsonDocument.fromJson(json, error)
        if self.mDocument is not None:
            self.beginResetModel()
            if self.mDocument.isArray():
                self.mRootItem.setType(list)
                self.mRootItem = QJsonTreeItem.load(list(self.mDocument.array()), self.root_field)
            else:
                self.mRootItem.setType(dict)
                self.mRootItem = QJsonTreeItem.load(self.mDocument.object(), self.root_field)
            self.loopSetWarpField(self.mRootItem, self.mRootItem)
            self.endResetModel()
            return True
        print("QJsonModel: error loading Json")
        return False

    def loopSetWarpField(self, item: QJsonTreeItem, src_item: QJsonTreeItem):
        for key, child in item.mChilds.items():
            if key.endswith("WarpType"):
                child.setField("WarpType")
            elif key.endswith("WarpData"):
                if key[:-8] + "WarpType" in item.mChilds.keys():
                    warpTypeItem = item.mChilds[key[:-8] + "WarpType"]
                    if warpTypeItem.value() == 3 or warpTypeItem.value() == 6:
                        child.setField("WarpRef")
                    # elif warpTypeItem.value() == 4:
                    #     child.setField("WarpAdd")
                    # elif warpTypeItem.value() == 5:
                    #     child.setField("WarpModity")
            elif (child.field() is None or child.field() == "") and item.key().endswith("WarpData"):
                child.setField(item.field())
            self.loopSetWarpField(child, src_item)

    def removeListItem(self, index: QModelIndex):
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

            if item.parent() is not None and item.parent().type() == "list":
                self.beginRemoveRows(srcIndex.parent(), item.row(), item.row())
                del item.parent().mChilds[item.key()]
                self.endRemoveRows()

    def addRefWarp(self, index: QModelIndex, value: str, key: str = None, field: str = None, brother: bool = True):
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

            if key is None:
                key = item.key()

            if field is None:
                field = "WarpRef"

            if brother:
                if value:
                    warpTypeItem = item.brother(key + "WarpType")
                    warpDataItem = item.brother(key + "WarpData")
                    if warpTypeItem is None:
                        self.addBrother(srcIndex, key + "WarpType", int, 3, "WarpType", True)
                    else:
                        warpTypeItem.setValue(3)
                    if warpDataItem is None:
                        if item.type() == "list":
                            self.addBrother(srcIndex, key + "WarpData", list, "", field, True)
                            warpDataItem = item.brother(key + "WarpData")
                            warpDataIndex = self.index(warpDataItem.row(), 0, srcIndex.parent())
                            child_key = 0
                            while str(child_key) in warpDataItem.mChilds:
                                child_key += 1
                            self.addItem(warpDataIndex, str(child_key), str, value, field, True)
                        else:
                            self.addBrother(srcIndex, key + "WarpData", str, value, field, True)
                    else:
                        if item.type() == "list":
                            warpDataIndex = self.index(warpDataItem.row(), 0, srcIndex.parent())
                            child_key = 0
                            while str(child_key) in warpDataItem.mChilds:
                                child_key += 1
                            self.addItem(warpDataIndex, str(child_key), str, value, field, True)
                        else:
                            warpDataItem.setValue(value)
                    item.setVaild(True)
                else:
                    self.deleteBrother(srcIndex, key + "WarpType")
                    self.deleteBrother(srcIndex, key + "WarpData")
                    item.setVaild(False)
            else:
                if value:
                    warpTypeItem = item.childByKey(key + "WarpType")
                    warpDataItem = item.childByKey(key + "WarpData")
                    if warpTypeItem is None:
                        self.addItem(srcIndex, key + "WarpType", int, 3, "WarpType", True)
                    else:
                        warpTypeItem.setValue(3)
                    if warpDataItem is None:
                        if item.type() == "list":
                            self.addItem(srcIndex, key + "WarpData", list, "", field, True)
                            warpDataItem = item.childByKey(key + "WarpData")
                            warpDataIndex = self.index(warpDataItem.row(), 0, srcIndex)
                            child_key = 0
                            while str(child_key) in warpDataItem.mChilds:
                                child_key += 1
                            self.addItem(warpDataIndex, str(child_key), str, value, field, True)
                        else:
                            self.addItem(srcIndex, key + "WarpData", str, value, field, True)
                    else:
                        if item.type() == "list":
                            warpDataIndex = self.index(warpDataItem.row(), 0, srcIndex)
                            child_key = 0
                            while str(child_key) in warpDataItem.mChilds:
                                child_key += 1
                            self.addItem(warpDataIndex, str(child_key), str, value, field, True)
                        else:
                            warpDataItem.setValue(value)
                    item.setVaild(True)
                else:
                    self.deleteChildItem(srcIndex, key + "WarpType")
                    self.deleteChildItem(srcIndex, key + "WarpData")
                    item.setVaild(False)

    def addAddRefWarp(self, index: QModelIndex, value: str = "", key: str = None, field: str = None, brother: bool = True):
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index
            
            if key is None:
                key = item.key()

            if field is None:
                field = "WarpRef"

            if value:
                if brother:
                    warpTypeItem = item.brother(key + "WarpType")
                    warpDataItem = item.brother(key + "WarpData")
                    
                    if warpTypeItem is None:
                        self.addBrother(srcIndex, key + "WarpType", int, 6, "WarpType", True)
                    else:
                        warpTypeItem.setValue(6)

                    if warpDataItem is None:
                        self.addBrother(srcIndex, key + "WarpData", list, value, field, True)
                    warpDataItem = item.brother(key + "WarpData")
                    warpDataIndex = self.index(warpDataItem.row(), 0, srcIndex.parent())
                    child_key = 0
                    while str(child_key) in warpDataItem.mChilds:
                        child_key += 1
                    self.addItem(warpDataIndex, str(child_key), str, value, field, True)
                else:
                    warpTypeItem = item.childByKey(key + "WarpType")
                    warpDataItem = item.childByKey(key + "WarpData")
                    
                    if warpTypeItem is None:
                        self.addItem(srcIndex, key + "WarpType", int, 6, "WarpType", True)
                    else:
                        warpTypeItem.setValue(6)

                    if warpDataItem is None:
                        self.addItem(srcIndex, key + "WarpData", list, value, field, True)
                    warpDataItem = item.mChilds[key + "WarpData"]
                    warpDataIndex = self.index(warpDataItem.row(), 0, srcIndex)
                    child_key = 0
                    while str(child_key) in warpDataItem.mChilds:
                        child_key += 1
                    self.addItem(warpDataIndex, str(child_key), str, value, field, True)

    def addAddWarp(self, index: QModelIndex, srcItem: QJsonTreeItem = None, brother: bool = True):
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index
            
            if srcItem is None:
                key = item.key()
                field = "WarpModify"
                type = item.type()
            else:
                key = srcItem.key()
                field = srcItem.field()
                type = srcItem.type()

            if brother:
                warpTypeItem = item.brother(key + "WarpType")
                warpDataItem = item.brother(key + "WarpData")
                
                if warpTypeItem is None:
                    self.addBrother(srcIndex, key + "WarpType", int, 4, "WarpType", True)
                else:
                    warpTypeItem.setValue(4)

                if warpDataItem is None:
                    self.addBrother(srcIndex, key + "WarpData", type, "", field, True)
                else:
                    self.deleteBrother(srcIndex, key + "WarpData")
                    self.addBrother(srcIndex, key + "WarpData", type, "", field, True)
            else:
                warpTypeItem = item.childByKey(key + "WarpType")
                warpDataItem = item.childByKey(key + "WarpData")
                
                if warpTypeItem is None:
                    self.addItem(srcIndex, key + "WarpType", int, 4, "WarpType", True)
                else:
                    warpTypeItem.setValue(4)

                if warpDataItem is None:
                    self.addItem(srcIndex, key + "WarpData", type, "", field, True)
                else:
                    self.deleteChildItem(srcIndex, key + "WarpData")
                    self.addItem(srcIndex, key + "WarpData", type, "", field, True)

    def addModifyWarp(self, index: QModelIndex, srcItem: QJsonTreeItem = None, brother: bool = True):
        if index.isValid():
            model = index.model()
            if hasattr(model, 'mapToSource'):
                srcModel, item, srcIndex = model.getSourceModelItemIndex(index)
            else:
                srcModel, item, srcIndex = model, index.internalPointer(), index

            if srcItem is None:
                key = item.key()
                field = "WarpModify"
                type = item.type()
            else:
                key = srcItem.key()
                field = srcItem.field()
                type = srcItem.type()

            if brother:
                warpTypeItem = item.brother(key + "WarpType")
                warpDataItem = item.brother(key + "WarpData")
                
                if warpTypeItem is None:
                    self.addBrother(srcIndex, key + "WarpType", int, 5, "WarpType", True)
                else:
                    warpTypeItem.setValue(5)

                if warpDataItem is None:
                    self.addBrother(srcIndex, key + "WarpData", type, "", field, True)
                else:
                    self.deleteBrother(srcIndex, key + "WarpData")
                    self.addBrother(srcIndex, key + "WarpData", type, "", field, True)
            else:
                warpTypeItem = item.childByKey(key + "WarpType")
                warpDataItem = item.childByKey(key + "WarpData")
                
                if warpTypeItem is None:
                    self.addItem(srcIndex, key + "WarpType", int, 5, "WarpType", True)
                else:
                    warpTypeItem.setValue(5)

                if warpDataItem is None:
                    self.addItem(srcIndex, key + "WarpData", type, "", field, True)
                else:
                    self.deleteChildItem(srcIndex, key + "WarpData")
                    self.addItem(srcIndex, key + "WarpData", type, "", field, True)

    def addBrother(self, index: QModelIndex, key: str, type: type, value: any, field: str, vaild: bool):
        try:
            parentItem = index.parent().internalPointer()
            if parentItem is None:
                parentItem = self.mRootItem
            self.beginInsertRows(index.parent(), parentItem.childCount(), parentItem.childCount())
            brotherItem = QJsonTreeItem.newItem(parentItem, key, type, value, field, vaild)
            parentItem.appendChild(key, brotherItem)
            self.endInsertRows()
        except Exception as ex:
            print(traceback.format_exc())

    def addJsonItem(self, index: QModelIndex, json: dict, field: str, key: str):
        try:
            item = index.internalPointer()
            if item is None:
                item = self.mRootItem
            if key in item.mChilds:
                childIndex = self.index(item.childRow(key), 0, index)
                self.deleteItem(childIndex)
            self.beginInsertRows(index, item.childCount(), item.childCount())
            childItem = QJsonTreeItem.load(json, field, item, key)
            childItem.setVaild(True)
            item.appendChild(key, childItem)
            item.setVaild(True)
            self.endInsertRows()
            childIndex = self.index(childItem.row(), 0, index)
            self.loopSetWarpField(item, item)
        except Exception as ex:
            print(traceback.format_exc())

    def loopInsertJsonRow(self, item: QJsonTreeItem, index: QModelIndex):
        print(item.key(), item.childCount())
        # if item.childCount() != 0:
        #     self.beginInsertRows(index, 0, item.childCount() - 1)
        #     self.endInsertRows()
        # for key, childItem in item.mChilds.items():
        #     childIndex = index.model().index(childItem.row(), 0, index)
        #     self.loopInsertJsonRow(childItem, childIndex)

    def addItem(self, index: QModelIndex, key: str, type: type, value: any, field: str, vaild: bool):
        try:
            item = index.internalPointer()
            if item is None:
                item = self.mRootItem
            if key in item.mChilds:
                childIndex = self.index(item.childRow(key), 0, index)
                self.deleteItem(childIndex)
            self.beginInsertRows(index, item.childCount(), item.childCount())
            childItem = QJsonTreeItem.newItem(item, key, type, value, field, vaild)
            childItem.setVaild(True)
            item.appendChild(key, childItem)
            item.setVaild(True)
            self.endInsertRows()
        except Exception as ex:
            print(traceback.format_exc())

    def deleteBrother(self, index: QModelIndex, key: str):
        try:
            item = index.internalPointer()
            brotherItem = item.brother(key)
            if brotherItem is not None:
                brotherIndex = self.index(brotherItem.row(), 0, index.parent())
                self.deleteItem(brotherIndex)
        except Exception as ex:
            print(traceback.format_exc())

    def deleteItem(self, index: QModelIndex):
        try:
            item = index.internalPointer()
            parentItem = index.parent().internalPointer()
            if parentItem is None:
                parentItem = self.mRootItem
            self.beginRemoveRows(index.parent(), item.row(), item.row())
            del parentItem.mChilds[item.key()]
            self.endRemoveRows()
        except Exception as ex:
            print(traceback.format_exc())

    def deleteChildItem(self, index: QModelIndex, key: str):
        try:
            item = index.internalPointer()
            self.beginRemoveRows(index, item.childRow(key), item.childRow(key))
            del item.mChilds[key]
            self.endRemoveRows()
        except Exception as ex:
            print(traceback.format_exc())

    def setData(self, index: QModelIndex, value, role: int = ...) -> bool:
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            item = index.internalPointer()
            if index.column() == 1:
                item.setValue(value)
            elif index.column() == 4:
                if str(value) == "False":
                    item.setVaild(False)
                else:
                    item.setVaild(True)
            elif index.column() == 6:
                item.setCustomNote(value)
        else:
            return False
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if self.is_modify:
            if index.column() == 0:
                return Qt.ItemFlag.ItemIsEnabled
            elif index.column() == 1:
                item = index.internalPointer()
                parentItem = item.parentDepth(1)
                if parentItem is not None and not parentItem.key().endswith("WarpData"):
                    return Qt.ItemFlag.NoItemFlags
                if item.depth() == 1:
                    return Qt.ItemFlag.NoItemFlags
                if item.key() == "UniqueID":
                    return Qt.ItemFlag.ItemIsEnabled
                if item.key() == "m_FileID" or item.key() == "m_PathID" or item.key().endswith("WarpType") or item.key().endswith("WarpData"):
                    return Qt.ItemFlag.NoItemFlags
                if item.type() == "list":
                    return Qt.ItemFlag.NoItemFlags
                if item.field() in DataBase.AllEnum:
                    return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled
                if item.field() != "Boolean" and item.field() != "Int32" and item.field() != "Single" and item.field() != "String":
                    return Qt.ItemFlag.NoItemFlags
                return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled
            elif index.column() == 6:
                return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled
            else:
                return Qt.ItemFlag.NoItemFlags
        if index.column() == 1:
            item = index.internalPointer()
            if item.key() == "UniqueID":
                return Qt.ItemFlag.ItemIsEnabled
            if item.key() == "m_FileID" or item.key() == "m_PathID" or item.key().endswith("WarpType") or item.key().endswith("WarpData"):
                return Qt.ItemFlag.NoItemFlags
            if item.type() == "list":
                return Qt.ItemFlag.NoItemFlags
            if item.field() in DataBase.AllEnum:
                return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled 
            if item.field() != "Boolean" and item.field() != "Int32" and item.field() != "Single" and item.field() != "String":
                return Qt.ItemFlag.NoItemFlags
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled
        elif index.column() == 2:
            return Qt.ItemFlag.NoItemFlags
        elif index.column() == 3:
            return Qt.ItemFlag.NoItemFlags
        elif index.column() == 4:
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled
        elif index.column() == 5:
            return Qt.ItemFlag.ItemIsEnabled
        elif index.column() == 6:
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled
        return super().flags(index)

    def data(self, index: QModelIndex, role: int = ...):
        if not index.isValid():
            return QVariant()

        item = index.internalPointer()
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return str(item.key())
            elif col == 1:
                if item.type() == "dict" or item.type() == "list":
                    return ""
                if item.key() == "m_FileID" or item.key() == "m_PathID":
                    return ""
                if item.field() == "WarpRef":
                    if item.value() in DataBase.AllGuidPlainRev:
                        return DataBase.AllGuidPlainRev[item.value()]
                if item.field() in DataBase.AllEnumRev:
                    if item.value() in DataBase.AllEnumRev[item.field()]:
                        return DataBase.AllEnumRev[item.field()][item.value()]
                return str(item.value())
            elif col == 2:
                if item.type() == "list":
                    return str(item.field()) + "[]"
                else:
                    return str(item.field())
            elif col == 3:
                return str(item.type())
            elif col == 4:
                return str(item.vaild())
            elif col == 5:
                if item.note() is not None and item.note():
                    return item.note()
                else:
                    return ""
            elif col == 6:
                return item.customNote()
        return QVariant()

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            return self.mHeaders[section]

        return QVariant()

    def index(self, row: int, column: int, parent: QModelIndex = ...):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.mRootItem
        else:
            parentItem = parent.internalPointer()
            
        # try:
        childItem = parentItem.child(row)
        return self.createIndex(row, column, childItem)
        # except IndexError:
            # return QModelIndex()

    def parent(self, index: QModelIndex):
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        parentItem = item.parent()

        if parentItem == self.mRootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent: QModelIndex = ...):
        # if parent.column() > 0:
        #     return 0
        if not parent.isValid():
            parentItem = self.mRootItem
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()

    def columnCount(self, parent: QModelIndex = ...):
        return 7

    def to_json(self, item=None):
        if item is None:
            item = self.mRootItem
        nchild = item.childCount()

        if item.mType == "dict":
            document = {}
            for i in range(nchild):
                ch = item.child(i)
                document[ch.mKey] = self.to_json(ch)
            return document
        elif item.mType == "list":
            document = []
            for i in range(nchild):
                ch = item.child(i)
                document.append(self.to_json(ch))
            return document
        else:
            return item.mValue

    # def insertRows(self, row: int, count: int, parent: QModelIndex = ...) -> bool:
    #     print("insertRows")
    #     if row < 0 or count < 1 or row > self.rowCount():
    #         return
    #     self.beginInsertRows(parent, row, row + count - 1)
        
    #     self.endInsertRows()
    #     return True

    #     return super().insertRows(row, count, parent)

    # def beginInsertColumns(self, parent: QModelIndex, first: int, last: int) -> None:
    #     print("beginInsertColumns")
    #     return super().beginInsertColumns(parent, first, last)

    # def beginInsertRows(self, parent: QModelIndex, first: int, last: int) -> None:
    #     print("beginInsertRows")
    #     return super().beginInsertRows(parent, first, last)

    # def insertColumns(self, position, columns, parent=QModelIndex()):
    #     self.beginInsertColumns(parent, position, position + columns - 1)
    #     success = self.rootItem.insertColumns(position, columns)
    #     self.endInsertColumns()

    #     return success

    # def insertRows(self, position, rows, parent=QModelIndex(), *args, **kwargs):
    #     parentItem = self.getItem(parent)
    #     self.beginInsertRows(parent, position, position + rows - 1)
    #     success = parentItem.insertChildren(position, rows,
    #             self.rootItem.columnCount())
    #     self.endInsertRows()

    #     return success