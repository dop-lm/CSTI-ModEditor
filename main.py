from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Ui_Main import *

import traceback
import sys
import os
import shutil
import json
import uuid
from data_base import *
import ItemGUI
import NewItemGUI
import ModifyItemGUI
import SelectGUI
from functools import partial

ModEditorVersion = "0.3.3"

class ModEditorGUI(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(ModEditorGUI, self).__init__(parent)
        self.setupUi(self)
        self.dataInit()
        self.ui_Init()
        self.mod_path = None
        self.mod_info = None
        self.group_dict = {}
        self.tree_item_dict = {}
        self.tab_item_dict = {}
        self.group_dict_plain = {}

    def reset(self):
        self.mod_path = None
        self.mod_info = None
        self.group_dict = {}
        self.tree_item_dict = {}
        self.tab_item_dict = {}
        self.treeWidget.clear()
        self.tabWidget.clear()

    def dataInit(self):
        DataBase.loadDataBase(QDir.currentPath())

    def ui_Init(self):
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setColumnWidth(0,50)
        self.treeWidget.setHeaderLabels(["文件列表"])
        self.treeWidget.setSortingEnabled(True)
        self.treeWidget.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        # self.treeWidget.setDragEnabled(True)
        # self.treeWidget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        # self.treeWidget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.treeWidget.itemDoubleClicked.connect(self.on_treeWidgetItemDoubleClicked)
        self.treeWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeWidget_autoresize = True
        self.action_ResizeMode.setText("关闭自动内容展开")
        self.treeWidget.customContextMenuRequested.connect(self.on_treeWidgetCustomContextMenuRequested)
        width = QtWidgets.qApp.desktop().availableGeometry(self).width()
        self.splitter.setSizes([int(width * 1/8), int(width * 7/8)])
        for i in range(self.splitter.count()):
            self.splitter.setCollapsible(i, False)

        self.action_newMod.triggered.connect(self.on_newMod)
        self.action_loadMod.triggered.connect(self.on_loadMod)
        self.action_save.triggered.connect(self.on_saveMod)
        self.action_ResizeMode.triggered.connect(self.on_ChangeCustomContextMenu)

        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.tabCloseRequested.connect(self.on_tabWidgetTabCloseRequested)
        self.tabWidget.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabWidget.tabBar().customContextMenuRequested.connect(self.on_tabWidgetCustomContextMenuRequested)
        # self.tabWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        # self.tabWidget.customContextMenuRequested.connect(self.on_tabWidgetCustomContextMenuRequested)

        self.srcTitle = self.windowTitle() + " " + ModEditorVersion
        self.setWindowTitle(self.srcTitle)

        self.pushButton.setText("打开")
        self.pushButton.clicked.connect(self.on_pushButtonClicked)

        self.quick_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.quick_save.activated.connect(self.on_saveMod)

        self.quick_close = QShortcut(QKeySequence("Esc"), self)
        self.quick_close.activated.connect(self.on_quick_close)

        self.lineEdit.returnPressed.connect(self.on_lineEditReturnPressed)

    def on_ChangeCustomContextMenu(self):
        if self.treeWidget_autoresize:
            self.treeWidget_autoresize = False
            self.action_ResizeMode.setText("打开自动内容展开")
        else:
            self.treeWidget_autoresize = True
            self.action_ResizeMode.setText("关闭自动内容展开")

    def on_tabWidgetCustomContextMenuRequested(self, pos: QPoint):
        pmenu = QMenu(self)
        tabBar = self.tabWidget.tabBar()
        tab = -1
        gpos = self.sender().mapToGlobal(pos)
        posInbar = tabBar.mapFromGlobal(gpos)
        for i in range(tabBar.count()):
            if tabBar.tabRect(i).contains(posInbar):
                tab = i
                break
        if tab >= 0:
            pCloseNowAct = QAction("关闭当前页（自动保存）", pmenu)
            pCloseNowAct.triggered.connect(lambda: self.on_closeNow(tab))
            pmenu.addAction(pCloseNowAct)

            pCloseRightAct = QAction("关闭右侧页（自动保存）", pmenu)
            pCloseRightAct.triggered.connect(lambda: self.on_closeRight(tab))
            pmenu.addAction(pCloseRightAct)

            pCloseAllExAct = QAction("关闭除此之外所有页（自动保存）", pmenu)
            pCloseAllExAct.triggered.connect(lambda: self.on_closeAllEx(tab))
            pmenu.addAction(pCloseAllExAct)

            pCloseAllAct = QAction("关闭所有页（自动保存）", pmenu)
            pCloseAllAct.triggered.connect(lambda: self.on_closeAll(tab))
            pmenu.addAction(pCloseAllAct)
        if len(pmenu.actions()):
            pmenu.popup(self.sender().mapToGlobal(pos))

    def on_closeNow(self, tab: int):
        if tab >= 0:
            self.on_tabWidgetTabCloseRequested(tab, False)

    def on_closeRight(self, tab: int):
        if tab >= 0:
            for i in reversed(range(tab + 1, self.tabWidget.count())):
                self.on_tabWidgetTabCloseRequested(i, False)

    def on_closeAllEx(self, tab: int):
        if tab >= 0:
            for i in reversed(range(tab + 1, self.tabWidget.count())):
                self.on_tabWidgetTabCloseRequested(i, False)
            for i in reversed(range(self.tabWidget.count() - 1)):
                self.on_tabWidgetTabCloseRequested(i, False)

    def on_closeAll(self, tab: int):
        if tab >= 0:
            for i in reversed(range(self.tabWidget.count())):
                self.on_tabWidgetTabCloseRequested(i, False)

    def on_lineEditReturnPressed(self):
        self.on_pushButtonClicked()

    def init_completer(self):
        self.getQTreeWidgetItem()
        self.m_completer = QCompleter(self.group_dict_plain.keys(), self.treeWidget)
        self.m_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.m_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.lineEdit.setCompleter(self.m_completer)

    def loopGetQTreeWidgetItem(self, group_dict, list_group, prefix: str = ""):
        if type(group_dict) == dict:
            for key, value in group_dict.items():
                if type(value) == QTreeWidgetItem:
                    a = QTreeWidgetItem()
                    a.child
                    for i in range(value.childCount()):
                        child = value.child(i)
                        if child.childCount() == 0:
                            list_group[value.text(0) + ":" + child.text(0)] = child
                        else:
                            print("unexpect childCount")
                elif type(value) == dict:
                    self.loopGetQTreeWidgetItem(value, list_group, key + ":")
                else:
                    print("unexpect type")

    def getQTreeWidgetItem(self):
        self.group_dict_plain.clear()
        self.loopGetQTreeWidgetItem(self.group_dict, self.group_dict_plain, "")
            
    def on_pushButtonClicked(self):
        if self.lineEdit.text() in self.tab_item_dict:
            self.tabWidget.setCurrentWidget(self.tab_item_dict[self.lineEdit.text()]["widget"])
        else:
            if self.lineEdit.text() in self.group_dict_plain:
                self.openTreeWidgetItem(self.group_dict_plain[self.lineEdit.text()])

    def on_quick_close(self) -> None:
        index = self.tabWidget.currentIndex()
        if index >= 0:
            self.on_tabWidgetTabCloseRequested(index)
        
    def closeEvent(self, event) -> None:
        reply = QMessageBox.question(self, '保存', '是否在退出前保存(收藏、子菜单、本地化)', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel , QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.on_saveMod()
            event.accept()  
        elif reply == QMessageBox.No:
            event.accept()      
        else:
            event.ignore()

    def on_treeWidgetCustomContextMenuRequested(self, pos: QPoint) -> None:
        hititem = self.treeWidget.currentItem()
        if hititem:
            depth = self.treeItemDepth(hititem)
            pmenu = QMenu(self)
            if depth == 0:
                if hititem.text(0) == "GameSourceModify":
                    pAddAct = QAction("新建修改", pmenu)
                    pAddAct.triggered.connect(self.on_newModify)
                    pmenu.addAction(pAddAct)
                elif hititem.text(0) == "ScriptableObject":
                    pass
                else:
                    pAddAct = QAction("新建", pmenu)
                    pAddAct.triggered.connect(self.on_newCard)
                    pmenu.addAction(pAddAct)
            elif depth == 1:
                if hititem.parent().text(0) == "ScriptableObject":
                    pAddAct = QAction("新建", pmenu)
                    pAddAct.triggered.connect(self.on_newScriptableObject)
                    pmenu.addAction(pAddAct)
                else:
                    tab_key = hititem.parent().text(0) + ":" + hititem.text(0)
                    if not tab_key in self.tab_item_dict:
                        pDeleteAct = QAction("删除", pmenu)
                        pDeleteAct.triggered.connect(self.on_delCard)
                        pmenu.addAction(pDeleteAct)
            elif depth == 2:
                if hititem.parent().parent().text(0) == "ScriptableObject":
                    tab_key = hititem.parent().text(0) + ":" + hititem.text(0)
                    if not tab_key in self.tab_item_dict:
                        pDeleteAct = QAction("删除", pmenu)
                        pDeleteAct.triggered.connect(self.on_delCard)
                        pmenu.addAction(pDeleteAct)
            if len(pmenu.actions()):
                pmenu.popup(self.sender().mapToGlobal(pos))

    def on_newScriptableObject(self) -> None:
        hititem = self.treeWidget.currentItem()
        if hititem:
            root = hititem.parent()
            if root.text(0) == "ScriptableObject":
                group_name = hititem.text(0)
                select = SelectGUI.SelectGUI(self, field_name = group_name, checked = False, type = SelectGUI.SelectGUI.NewData)
                select.exec_()
                template_key = select.lineEdit.text()
                try:
                    card_name = select.name_editor.text()
                    # print(card_name, template_key)
                    if card_name and template_key:
                        if not card_name in self.tree_item_dict["ScriptableObject"][group_name]:
                            child = QTreeWidgetItem()
                            child.setText(0, card_name)
                            child_path = self.mod_path + "/ScriptableObject/" + group_name + "/" + card_name + ".json"
                            with open(DataBase.AllPath[group_name][template_key], "r") as f:
                                temp_data = f.read(-1)
                            temp_json = json.loads(temp_data)
                            with open(child_path, "w") as f:
                                f.write(temp_data)
                            self.group_dict["ScriptableObject"][group_name].addChild(child)
                            self.tree_item_dict["ScriptableObject"][group_name][card_name] = {"path": child_path}
                        else:
                            QMessageBox.warning(self, '警告','存在同名文件')
                except Exception as ex:
                    print(traceback.format_exc())
                self.init_completer()

    def on_newCard(self) -> None:
        hititem = self.treeWidget.currentItem()
        if hititem:
            root = hititem.parent()
            if root is None:
                group_name = hititem.text(0)
                select = SelectGUI.SelectGUI(self, field_name = group_name, checked = False, type = SelectGUI.SelectGUI.NewData)
                select.exec_()
                template_key = select.lineEdit.text().split("(")[0]
                try:
                    card_name = select.name_editor.text()
                    if card_name and template_key:
                        if not card_name in self.tree_item_dict[group_name]:
                            child = QTreeWidgetItem()
                            child.setText(0, card_name)
                            child_path = self.mod_path + "/" + group_name + "/" + card_name + ".json"
                            with open(DataBase.AllPath[group_name][template_key], "r") as f:
                                temp_data = f.read(-1)
                            temp_json = json.loads(temp_data)
                            guid = temp_json["UniqueID"]
                            temp_data = temp_data.replace(guid, str(uuid.uuid1()).replace("-",""))
                            with open(child_path, "w") as f:
                                f.write(temp_data)
                            self.group_dict[group_name].addChild(child)
                            self.tree_item_dict[group_name][card_name] = {"path": child_path}
                        else:
                            QMessageBox.warning(self, '警告','存在同名文件')
                except Exception as ex:
                    print(traceback.format_exc())
                self.init_completer()

    def on_newModify(self) -> None:
        hititem = self.treeWidget.currentItem()
        if hititem:
            root = hititem.parent()
            if root is None:
                group_name = hititem.text(0)
                select = SelectGUI.SelectGUI(self, field_name = group_name, checked = False, type = SelectGUI.SelectGUI.NewModify)
                select.exec_()
                target_key = select.lineEdit.text()
                template_key = select.lineEdit.text().split("(")[0]
                try:
                    card_name = select.name_editor.text()
                    if card_name and template_key:
                        if not card_name in self.tree_item_dict[group_name]:
                            child = QTreeWidgetItem()
                            child.setText(0, card_name)
                            os.mkdir(self.mod_path + "/" + group_name + "/" + card_name)
                            
                            target_group_name = ""
                            target_guid = DataBase.AllGuidPlain[target_key]
                            for type_key in DataBase.AllRef["CardData"].keys():
                                if target_key in DataBase.AllRef["CardData"][type_key]:
                                    target_group_name = "CardData"
                                    break
                            for group_key in DataBase.AllGuid.keys():
                                if target_key in DataBase.AllGuid[group_key]:
                                    target_group_name = group_key
                                    break
                            if target_group_name and target_guid:
                                child_path = self.mod_path + "/" + group_name + "/" + card_name + "/" + target_guid + ".json"
                                child_dir = self.mod_path + "/" + group_name + "/" + card_name
                                
                                if target_group_name:                                
                                    with open(child_path, "w") as f:
                                        f.write("{\n\n}")
                                    self.group_dict[group_name].addChild(child)
                                    self.tree_item_dict[group_name][card_name] = {"path": child_path, "dir": child_dir, "template_field": target_group_name}
                        else:
                            QMessageBox.warning(self, '警告','存在同名文件')
                except Exception as ex:
                    print(traceback.format_exc())
                self.init_completer()

    def on_delCard(self) -> None:
        hititem = self.treeWidget.currentItem()
        if hititem:
            depth = self.treeItemDepth(hititem)
            if depth == 0:
                pass
            elif depth == 1:
                father = hititem.parent()
                reply = QMessageBox.question(self,'警告','确定要删除' + father.text(0) + ":" + hititem.text(0) + '吗', QMessageBox.Yes | QMessageBox.No , QMessageBox.No)
                if reply == QMessageBox.Yes:
                    index = father.indexOfChild(hititem)
                    father.takeChild(index)
                    if "dir" in self.tree_item_dict[father.text(0)][hititem.text(0)]:
                        shutil.rmtree(self.tree_item_dict[father.text(0)][hititem.text(0)]["dir"])
                    else:
                        os.remove(self.tree_item_dict[father.text(0)][hititem.text(0)]["path"])
                    del self.tree_item_dict[father.text(0)][hititem.text(0)]
                    del hititem
            elif depth == 2:
                father = hititem.parent()
                grand_father = father.parent()
                reply = QMessageBox.question(self,'警告','确定要删除' + father.text(0) + ":" + hititem.text(0) + '吗', QMessageBox.Yes | QMessageBox.No , QMessageBox.No)
                if reply == QMessageBox.Yes:
                    index = father.indexOfChild(hititem)
                    father.takeChild(index)
                    if "dir" in self.tree_item_dict[grand_father.text(0)][father.text(0)][hititem.text(0)]:
                        shutil.rmtree(self.tree_item_dict[grand_father.text(0)][father.text(0)][hititem.text(0)]["dir"])
                    else:
                        os.remove(self.tree_item_dict[grand_father.text(0)][father.text(0)][hititem.text(0)]["path"])
                    del self.tree_item_dict[grand_father.text(0)][father.text(0)][hititem.text(0)]
                    del hititem
            else:
                pass
            self.init_completer()
                

    def saveTabJsonItem(self, index: int):
        if self.tabWidget.tabText(index).startswith("GameSourceModify"):
            save_data = self.tabWidget.widget(index).treeView.model().sourceModel().to_json()
            self.delGameSourceModifyTemplate(save_data)
        else:
            save_data = self.tabWidget.widget(index).treeView.model().sourceModel().to_json()
        with open(self.tab_item_dict[self.tabWidget.tabText(index)]["path"], "w") as f:
            json.dump(save_data, f, indent = 4)
        DataBase.loopLoadModSimpCn(save_data, self.mod_info["Name"])
    
    def on_tabWidgetTabCloseRequested(self, index: int, ask: bool = True):
        try:
            if ask:
                reply = QMessageBox.question(self, '保存', '是否在退出前保存', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel , QMessageBox.Yes)
            else:
                reply = QMessageBox.Yes
            if reply == QMessageBox.Yes:
                self.saveTabJsonItem(index)
                del self.tab_item_dict[self.tabWidget.tabText(index)]
                self.tabWidget.removeTab(index)  
            elif reply == QMessageBox.No:
                del self.tab_item_dict[self.tabWidget.tabText(index)]
                self.tabWidget.removeTab(index)
            elif reply == QMessageBox.Cancel:
                return
        except Exception as ex:
            print(traceback.format_exc())
            
    def treeItemDepth(self, treeItem: QTreeWidgetItem):
        depth = 0 
        while(treeItem.parent() is not None):
            depth += 1
            treeItem = treeItem.parent()
        return depth

    def openTreeWidgetItem(self, treeItem: QTreeWidgetItem):
        depth = self.treeItemDepth(treeItem)
        if depth == 0:
            return
        elif depth == 1:
            tab_key = treeItem.parent().text(0) + ":" + treeItem.text(0)
            if tab_key in self.tab_item_dict:
                pass
            else:
                if treeItem.parent().text(0) == "GameSourceModify":
                    item = ModifyItemGUI.ModifyItemGUI(self.tree_item_dict[treeItem.parent().text(0)][treeItem.text(0)]["template_field"], self.treeWidget_autoresize, self.tabWidget)
                    file_path = self.tree_item_dict[treeItem.parent().text(0)][treeItem.text(0)]["path"]
                    template_guid = os.path.basename(file_path)[:-5]
                    template_reftrans = DataBase.AllGuidPlainRev[template_guid]
                    template_ref = template_reftrans.split("(")[0]
                    template_path = DataBase.AllPathPlain[template_ref]
                    with open(file_path, 'rb') as f:
                        src_json = json.load(f)
                    with open(template_path, 'rb') as f:
                        template_json = json.load(f)
                        self.loopDelGameSourceModifyTemplateWarpper(template_json)
                    src_json.update(template_json)
                    item.loadJsonData(json.dumps(src_json).encode("utf-8"))
                elif treeItem.parent().text(0) in DataBase.RefGuidList:
                    item = ItemGUI.ItemGUI(treeItem.parent().text(0), self.treeWidget_autoresize, self.tabWidget)
                    file_path = self.tree_item_dict[treeItem.parent().text(0)][treeItem.text(0)]["path"]
                    with open(file_path, 'rb') as f:
                        item.loadJsonData(f.read(-1))
                else:
                    return
                self.tabWidget.addTab(item, tab_key)
                self.tab_item_dict[tab_key] = {"name": treeItem.text(0), "path":  file_path, "widget": item}
            self.tabWidget.setCurrentWidget(self.tab_item_dict[tab_key]["widget"])
        elif depth == 2:
            if treeItem.parent().parent().text(0) == "ScriptableObject":
                tab_key = treeItem.parent().text(0) + ":" + treeItem.text(0)
                if tab_key in self.tab_item_dict:
                    pass
                else:
                    item = ItemGUI.ItemGUI(treeItem.parent().text(0), self.treeWidget_autoresize, self.tabWidget)
                    file_path = self.tree_item_dict[treeItem.parent().parent().text(0)][treeItem.parent().text(0)][treeItem.text(0)]["path"]
                    with open(file_path, 'rb') as f:
                        item.loadJsonData(f.read(-1))
                    self.tabWidget.addTab(item, tab_key)
                    self.tab_item_dict[tab_key] = {"name": treeItem.text(0), "path":  file_path, "widget": item}
                self.tabWidget.setCurrentWidget(self.tab_item_dict[tab_key]["widget"])
        else:
            pass

    def on_treeWidgetItemDoubleClicked(self, treeItem: QTreeWidgetItem, column: int):
        if treeItem:
            self.openTreeWidgetItem(treeItem)

    def loopDelGameSourceModifyTemplateWarpper(self, json):
        for key in list(json.keys()):
            if key.endswith("WarpType") or key.endswith("WarpData"):
                del json[key]
        # if type(json) == list:
        #     for item in json:
        #         self.loopDelGameSourceModifyTemplateWarpper(item)
        # elif type(json) == dict:
        #     for key in list(json.keys()):
        #         if key.endswith("WarpType") or key.endswith("WarpData"):
        #             del json[key]
                # else:
                #     self.loopDelGameSourceModifyTemplateWarpper(json[key])

    def delGameSourceModifyTemplate(self, json):
        if type(json) == dict:
            for key in list(json.keys()):
                if not key.endswith("WarpType") and not key.endswith("WarpData"):
                    del json[key]

    def on_newMod(self):
        if self.tab_item_dict:
            QMessageBox.warning(self, '警告','请先关闭所有子菜单')
            return
        self.new_mod = NewItemGUI.NewItemGUI(self)
        self.new_mod.buttonBox.accepted.connect(self.on_newModButtonBoxAccepted)
        self.new_mod.exec_()

    def on_newModButtonBoxAccepted(self):
        mod_name = self.new_mod.lineEdit.text()
        if not mod_name:
            return
        if os.path.exists(QDir.currentPath() + r"/Mods/" + mod_name):
            QMessageBox.warning(self, '警告','存在同名Mod文件夹')
            return
        shutil.copytree(QDir.currentPath() + r"/CSTI-JsonData/BaseMod", QDir.currentPath() + r"/Mods/" + mod_name)
        self.loadMod(QDir.currentPath() + r"/Mods/" + mod_name)

    def on_saveMod(self):
        if self.mod_info:
            try:
                for i in range(self.tabWidget.count()):
                    self.saveTabJsonItem(i)
                with open(self.mod_path + "/ModInfo.json", "w") as f:
                    json.dump(self.mod_info, f, indent = 4)

                DataBase.saveCollection()
                DataBase.saveModSimpCn(self.mod_path)
                DataBase.LoadModData(self.mod_info["Name"], self.mod_path)
            except Exception as ex:
                print(traceback.format_exc())
        
    def on_loadMod(self):
        if self.tab_item_dict:
            QMessageBox.warning(self, '警告','请先关闭所有子菜单')
            return
        mod_path = QFileDialog.getExistingDirectory(self, caption='选择Mod文件夹', directory=QDir.currentPath())
        if mod_path is None or mod_path == "":
            return
        if "ModInfo.json" not in os.listdir(mod_path):
            QMessageBox.warning(self, '警告','不是一个有效的Mod文件夹')
            return
        self.loadMod(mod_path)

    def loadMod(self, mod_path):
        self.reset()
        self.mod_path = mod_path

        with open(self.mod_path + "/ModInfo.json", "r") as f:
            self.mod_info = json.load(f)
        if not "Name" in self.mod_info or not self.mod_info["Name"]:
            self.mod_info["Name"] = os.path.basename(self.mod_path)
        self.mod_info["ModEditorVersion"] = ModEditorVersion

        DataBase.LoadModData(self.mod_info["Name"], self.mod_path)
        for item in os.listdir(self.mod_path):
            if item in DataBase.SupportList:
                group = QTreeWidgetItem(self.treeWidget)
                group.setText(0, item)
                self.tree_item_dict[item] = {}
                if item == "GameSourceModify":
                    for sub_dir in os.listdir(self.mod_path + "/" + item):
                        if os.path.isdir(self.mod_path + "/" + item + "/" + sub_dir):
                            for file in os.listdir(self.mod_path + "/" + item + "/" + sub_dir):
                                if file.endswith(".json"):
                                    child = QTreeWidgetItem()
                                    child.setText(0, sub_dir)
                                    group.addChild(child)
                                    template_reftrans = DataBase.AllGuidPlainRev[file[:-5]]
                                    for type_key in DataBase.AllRef["CardData"].keys():
                                        if template_reftrans in DataBase.AllRef["CardData"][type_key]:
                                            target_group_name = "CardData"
                                            break
                                    for group_key in DataBase.AllGuid.keys():
                                        if template_reftrans in DataBase.AllGuid[group_key]:
                                            target_group_name = group_key
                                            break
                                    self.tree_item_dict[item][sub_dir] = {"path": self.mod_path + "/" + item  + "/" + sub_dir + "/" + file, \
                                        "dir": self.mod_path + "/" + item  + "/" + sub_dir, \
                                            "template_field": target_group_name}
                                    break
                    group.setExpanded(True)
                    self.group_dict[item] = group
                elif item == "ScriptableObject":
                    self.group_dict[item] = {}
                    for sub_dir in os.listdir(self.mod_path + "/" + item):
                        child = QTreeWidgetItem()
                        child.setText(0, sub_dir)
                        group.addChild(child)
                        self.tree_item_dict[item][sub_dir] = {}
                        for file in os.listdir(self.mod_path + "/" + item + "/" + sub_dir):
                            if file.endswith(".json"):
                                cchild = QTreeWidgetItem()
                                cchild.setText(0, file[:-5])
                                child.addChild(cchild)
                                child.setExpanded(True)
                                self.tree_item_dict[item][sub_dir][file[:-5]] = {"path": self.mod_path + "/" + item  + "/" + sub_dir + "/" + file}
                        self.group_dict[item][sub_dir] = child
                    group.setExpanded(True)
                else:
                    for sub_item in os.listdir(self.mod_path + "/" + item):
                        if sub_item.endswith(".json"):
                            child = QTreeWidgetItem()
                            child.setText(0, sub_item[:-5])
                            group.addChild(child)
                            self.tree_item_dict[item][sub_item[:-5]] = {"path": self.mod_path + "/" + item  + "/" + sub_item}
                    group.setExpanded(True)
                    self.group_dict[item] = group
        self.setWindowTitle("%s (%s)" % (self.srcTitle, self.mod_info["Name"]))
        self.init_completer()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ModEditorGUI()
    main.show()
    sys.exit(app.exec_())