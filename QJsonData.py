# 2017 by Gregor Engberding , MIT License

import sys
import re
from data_base import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

pattern_number = ''': [1-9]'''
pattern_decimal = ''': 0.0*[1-9]{1,}.*?,'''
pattern_true = ''':true'''
pattern_no_empty_string = ''':""[^""]"'''

class QJsonTreeItem(object):
    def __init__(self, parent=None):
        self.mParent = parent
        self.mChilds = {}
        self.mType = None
        self.mValue = None
        self.mField = None
        self.mVaild = False
        self.mDepth = None

    def appendChild(self, key, item):
        self.mChilds[key] = item

    def child(self, row:int):
        return self.mChilds[list(self.mChilds.keys())[row]]

    def brother(self, key: str):
        try:
            return self.mParent.mChilds[key]
        except Exception as ex:
            return None

    def delBrother(self, key: str):
        try:
            del self.mParent.mChilds[key]
        except Exception as ex:
            pass

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

    def addWarp(self, key, warp_type, warp_data, isList: bool = False):
        try:
            warp_type_item = self.brother(self.key() + "WarpType")
            warp_data_item = self.brother(self.key() + "WarpData")
            
            if warp_type_item is None:
                self.mParent.appendChild(key + "WarpType", QJsonTreeItem.newItem(self.mParent, key + "WarpType", int, warp_type, "WarpType", True))
            else:
                warp_type_item.setValue(warp_type)

            if warp_data_item is None:
                if isList:
                    warp_data_item = QJsonTreeItem.newItem(self.mParent, key + "WarpData", list, warp_data, "WarpData", True)
                    self.mParent.appendChild(key + "WarpData", warp_data_item)
                    warp_data_item.appendChild(str(warp_data_item.childCount()), QJsonTreeItem.newItem(warp_data_item, str(warp_data_item.childCount()), str, warp_data, "WarpData", True))
                else:
                    self.mParent.appendChild(key + "WarpData", QJsonTreeItem.newItem(self.mParent, key + "WarpData", str, warp_data, "WarpData", True))
            else:
                if isList:
                    warp_data_item.appendChild(str(warp_data_item.childCount()), QJsonTreeItem.newItem(warp_data_item, str(warp_data_item.childCount()), str, warp_data, "WarpData", True))
                else:
                    warp_data_item.setValue(warp_data)
        except Exception as ex:
            None

    def parent(self):
        return self.mParent

    def childCount(self):
        return len(self.mChilds)

    def row(self):
        if self.mParent is not None:
            return list(self.mParent.mChilds.keys()).index(self.mKey)
        return 0

    def setKey(self, key:str):
        self.mKey = key

    def setValue(self, value:str):
       self.mValue = value

    def setField(self, value:str):
       self.mField = value

    def setVaild(self, value:bool):
       self.mVaild = value

    def setDepth(self, value:int):
       self.mDepth = value

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

    def load(value, type_key = "", parent = None, itemKey = None):
        rootItem = QJsonTreeItem(parent)
        if itemKey is None:
            rootItem.setKey("root")
        else:
            rootItem.setKey(itemKey)

        if type_key in DataBase.AllTypeField:
            rootItem.setField(type_key)
            
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
                if rootItem.parent is not None:
                    rootItem.parent().setVaild(True)
                rootItem.setVaild(True)
            elif re.search(pattern_decimal, str(value)):
                if rootItem.parent is not None:
                    rootItem.parent().setVaild(True)
                rootItem.setVaild(True)
            elif re.search(pattern_true, str(value)):
                if rootItem.parent is not None:
                    rootItem.parent().setVaild(True)
                rootItem.setVaild(True)
            elif re.search(pattern_no_empty_string, str(value)):
                if rootItem.parent is not None:
                    rootItem.parent().setVaild(True)
                rootItem.setVaild(True)
            else:
                rootItem.setVaild(False)

            for key in value:
                v = value[key]
                if type_key in DataBase.AllTypeField:
                    if key in DataBase.AllTypeField[type_key]:
                        child = QJsonTreeItem.load(v, DataBase.AllTypeField[type_key][key], rootItem, key)
                        child.setField(DataBase.AllTypeField[type_key][key])
                    else:
                        child = QJsonTreeItem.load(v, "", rootItem, key)
                        if key.endswith("WarpData"):
                            child.setField("WarpData")
                        if key.endswith("WarpType"):
                            child.setField("WarpType")
                else:
                    child = QJsonTreeItem.load(v, "", rootItem, key)   
                    if key.endswith("WarpData"):
                        child.setField("WarpData")
                    if key.endswith("WarpType"):
                        child.setField("WarpType")                 
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
                child = QJsonTreeItem.load(v, type_key, rootItem, rootItem.mKey)
                child.setKey(str(i))
                child.setType(v.__class__)
                child.setField(type_key)
                if rootItem.mKey.endswith("WarpData"):
                    child.setField("WarpData")
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
    def __init__(self, root_type, parent = None):
        super().__init__(parent)
        self.mRootItem = QJsonTreeItem()
        self.mHeaders = ["key", "value", "field_type", "data_type", "vaild"]
        self.root_type = root_type

    def loadJson(self, json):
        error = QJsonParseError()
        self.mDocument = QJsonDocument.fromJson(json, error)
        if self.mDocument is not None:
            self.beginResetModel()
            if self.mDocument.isArray():
                self.mRootItem.setType(list)
                self.mRootItem = QJsonTreeItem.load(list(self.mDocument.array()), self.root_type)
            else:
                self.mRootItem.setType(dict)
                self.mRootItem = QJsonTreeItem.load(self.mDocument.object(), self.root_type)
            self.endResetModel()
            return True
        print("QJsonModel: error loading Json")
        return False

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

    def refWarp(self, index: QModelIndex, value, role: int = ...):
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            item = index.internalPointer()
            if index.column() == 1:
                if value:
                    item.addWarp(item.key(), 3, str(value), item.type() == "list")
                    item.setVaild(True)
                else:
                    item.delBrother(item.key() + "WarpType")
                    item.delBrother(item.key() + "WarpData")
                    item.setVaild(False)
        else:
            return False
        return True

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
        else:
            return False
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if index.column() == 1:
            item = index.internalPointer()
            if item.key() == "UniqueID" or item.key() == "m_FileID" or item.key() == "m_PathID" or item.key().endswith("WarpType") or item.key().endswith("WarpData"):
                return Qt.ItemFlag.NoItemFlags
            if item.field() == "WarpType" or item.field() == "WarpData":
                return Qt.ItemFlag.NoItemFlags
            return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsEnabled
        if index.column() == 4:
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
                if item.field() == "WarpData":
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
        return 5

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