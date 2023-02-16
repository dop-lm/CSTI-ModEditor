# -*- coding: utf-8 -*- 

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
import configparser
# import anytree
from myLogger import *
from data_base import *
import ItemGUI
import NewItemGUI
import ModifyItemGUI
import SelectGUI
import ExportToZip
from glob import glob
from pathlib import Path
from functools import partial

ModEditorVersion = "0.4.7"

class ModEditorGUI(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super(ModEditorGUI, self).__init__(parent)
        self.setupUi(self)

        self.trans = QTranslator()
        logInit(os.path.join(QDir.currentPath(), "logoutput.log"))
        self.loadConfig()
        self.loadLanguage()        

        self.dataInit()
        self.ui_Init()
        self.mod_path = None
        self.mod_info = None
        self.file_model = None
        self.root_depth = 0
        self.tab_item_dict = {}

    @log_exception(True)
    def saveConfig(self):
        with open(os.path.join(QDir.currentPath(), "config.ini"), "w") as f:
            self.config.write(f)

    @log_exception(True)
    def loadConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(QDir.currentPath(), "config.ini"))
        if self.config.has_option("Config", "Language"):
            self.language = self.config.get("Config", "Language")
        else:
            self.language = ""
            self.config.set("Config", "Language", self.language)
            self.saveConfig()
        
        if self.config.has_option("Config", "LastOpenDir"):
            self.last_open_dir = self.config.get("Config", "LastOpenDir")
        else:
            self.last_open_dir = ""
            self.config.set("Config", "LastOpenDir", self.last_open_dir)
            self.saveConfig()

    @log_exception(True)
    def loadLanguage(self):
        if hasattr(self, "language") and self.language is not None and self.language:
            self.trans.load(os.path.join(QDir.currentPath(), "Localization", self.language))
            _app = QApplication.instance()
            _app.installTranslator(self.trans)
            self.retranslateUi(self)
        else:
            _app = QApplication.instance()
            _app.removeTranslator(self.trans)
            self.retranslateUi(self)


    def reset(self):
        self.mod_path = None
        self.mod_info = None
        self.file_model = None
        self.root_depth = 0
        self.tab_item_dict = {}
        self.tabWidget.clear()

    @log_exception(True)
    def dataInit(self):
        DataBase.loadDataBase(QDir.currentPath())

    def ui_Init(self):
        self.treeView.doubleClicked.connect(self.on_treeViewDoubleClicked)
        self.treeView.setEditTriggers(QAbstractItemView.EditTrigger.EditKeyPressed)
        self.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.on_treeViewCustomContextMenuRequested)

        self.autoresize = True
        self.action_ResizeMode.setText(self.tr("Turn off auto contents resize"))
        
        width = QtWidgets.qApp.desktop().availableGeometry(self).width()
        self.splitter.setSizes([int(width * 1/8), int(width * 7/8)])
        for i in range(self.splitter.count()):
            self.splitter.setCollapsible(i, False)

        self.action_newMod.triggered.connect(self.on_newMod)
        self.action_loadMod.triggered.connect(self.on_loadMod)
        self.action_save.triggered.connect(self.on_saveMod)
        self.action_ExportZip.triggered.connect(self.on_exportZip)
        self.action_ResizeMode.triggered.connect(self.on_ChangeCustomContextMenu)

        self.actionChinese.triggered.connect(self.on_select_Chinese)
        self.actionEnglish.triggered.connect(self.on_select_English)

        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.tabCloseRequested.connect(self.on_tabWidgetTabCloseRequested)
        self.tabWidget.tabBar().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tabWidget.tabBar().customContextMenuRequested.connect(self.on_tabWidgetCustomContextMenuRequested)

        self.srcTitle = self.windowTitle() + " " + ModEditorVersion
        self.setWindowTitle(self.srcTitle)

        self.pushButton.clicked.connect(self.on_pushButtonClicked)

        self.quick_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.quick_save.activated.connect(self.on_saveMod)

        self.quick_close = QShortcut(QKeySequence("Esc"), self)
        self.quick_close.activated.connect(self.on_quick_close)

        self.lineEdit.returnPressed.connect(self.on_lineEditReturnPressed)

    @log_exception(True)
    def on_select_Chinese(self, checked: bool=False):
        self.language = "zh_CN"
        self.config.set("Config", "Language", self.language)
        self.saveConfig()
        self.loadLanguage()
    
    @log_exception(True)
    def on_select_English(self, checked: bool=False):
        self.language = ""
        self.config.set("Config", "Language", self.language)
        self.saveConfig()
        self.loadLanguage()

    @log_exception(True)
    def on_ChangeCustomContextMenu(self, checked: bool=False):
        if self.autoresize:
            self.autoresize = False
            self.action_ResizeMode.setText(self.tr("Turn on auto contents resize"))
        else:
            self.autoresize = True
            self.action_ResizeMode.setText(self.tr("Turn off auto contents resize"))

    @log_exception(True)
    def treeItemRenamed(self, path: str, old_file: str, new_file: str):
        old_tab_key = path + "/" + old_file
        new_tab_key = path + "/" + new_file
        if old_tab_key in self.tab_item_dict:
            self.tab_item_dict[new_tab_key] = self.tab_item_dict[old_tab_key]
            for i in range(self.tabWidget.count()):
                if self.tabWidget.widget(i) == self.tab_item_dict[new_tab_key]["widget"]:
                    if new_file.endswith(".json"):
                        self.tabWidget.setTabText(i, new_file[:-5])
                    else:
                        self.tabWidget.setTabText(i, new_file)
                    break
            self.tab_item_dict[new_tab_key]["widget"].setTabKey(new_tab_key)
            del self.tab_item_dict[old_tab_key]

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
            pCloseNowAct = QAction(self.tr("Close(Auto-Save)"), pmenu)
            pCloseNowAct.triggered.connect(lambda: self.on_closeNow(tab))
            pmenu.addAction(pCloseNowAct)

            pCloseRightAct = QAction(self.tr("Close to the Right(Auto-Save)"), pmenu)
            pCloseRightAct.triggered.connect(lambda: self.on_closeRight(tab))
            pmenu.addAction(pCloseRightAct)

            pCloseAllExAct = QAction(self.tr("Close Others(Auto-Save)"), pmenu)
            pCloseAllExAct.triggered.connect(lambda: self.on_closeAllEx(tab))
            pmenu.addAction(pCloseAllExAct)

            pCloseAllAct = QAction(self.tr("Close All(Auto-Save)"), pmenu)
            pCloseAllAct.triggered.connect(lambda: self.on_closeAll(tab))
            pmenu.addAction(pCloseAllAct)
        if len(pmenu.actions()):
            pmenu.popup(self.sender().mapToGlobal(pos))

    def on_closeNow(self, tab: int, checked: bool=False):
        if tab >= 0:
            self.on_tabWidgetTabCloseRequested(tab, False)

    def on_closeRight(self, tab: int, checked: bool=False):
        if tab >= 0:
            for i in reversed(range(tab + 1, self.tabWidget.count())):
                self.on_tabWidgetTabCloseRequested(i, False)

    def on_closeAllEx(self, tab: int, checked: bool=False):
        if tab >= 0:
            for i in reversed(range(tab + 1, self.tabWidget.count())):
                self.on_tabWidgetTabCloseRequested(i, False)
            for i in reversed(range(self.tabWidget.count() - 1)):
                self.on_tabWidgetTabCloseRequested(i, False)

    def on_closeAll(self, tab: int, checked: bool=False):
        if tab >= 0:
            for i in reversed(range(self.tabWidget.count())):
                self.on_tabWidgetTabCloseRequested(i, False)

    def on_lineEditReturnPressed(self):
        self.on_pushButtonClicked()

    def init_completer(self):
        paths = [y for x in os.walk(self.mod_path) for y in glob(os.path.join(x[0], '*.json'))]
        files = list(map(lambda x: x.split(self.mod_path)[1].replace("\\", "/"), paths))
        self.m_completer = QCompleter(files, self.treeView)
        self.m_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.m_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.lineEdit.setCompleter(self.m_completer)
    
    @log_exception(True)
    def on_pushButtonClicked(self, checked: bool=False):
        tab_key = self.mod_path + self.lineEdit.text()
        if tab_key in self.tab_item_dict:
            self.tabWidget.setCurrentWidget(self.tab_item_dict[tab_key]["widget"])
        else:
            self.openTreeViewItem(self.file_model.index(tab_key))

    @log_exception(True)
    def on_quick_close(self) -> None:
        index = self.tabWidget.currentIndex()
        if index >= 0:
            self.on_tabWidgetTabCloseRequested(index)
        
    def closeEvent(self, event) -> None:
        reply = QMessageBox.question(self, self.tr('Save'), self.tr('Save the changes before exit?(Collection, Localization, Opened files...)'), QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel , QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.on_saveMod()
            event.accept()
        elif reply == QMessageBox.No:
            event.accept()      
        else:
            event.ignore()

    @log_exception(True)
    def on_treeViewCustomContextMenuRequested(self, pos: QPoint) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            depth = self.treeItemDepth(index)
            file_name = self.file_model.fileName(index)
            file_path = self.file_model.filePath(index)
            pmenu = QMenu(self)
            if self.file_model.isDir(index):
                if depth == 0:
                    pass
                elif depth == 1:
                    if file_name in DataBase.SupportList:
                        if file_name == "GameSourceModify":
                            pAddAct = QAction(self.tr("New Modify"), pmenu)
                            pAddAct.triggered.connect(self.on_newModify)
                            pmenu.addAction(pAddAct)
                        elif file_name == "ScriptableObject":
                            pass
                        else:
                            pAddAct = QAction(self.tr("New File"), pmenu)
                            pAddAct.triggered.connect(self.on_newCard)
                            pmenu.addAction(pAddAct)
                elif depth == 2:
                    top_parent = self.getDepthParent(index, depth=1)
                    if top_parent is None:
                        return
                    top_name = self.file_model.fileName(top_parent)
                    if top_name == "ScriptableObject":
                        if self.file_model.isDir(index) and file_name in DataBase.AllRef:
                            pAddAct = QAction(self.tr("New File"), pmenu)
                            pAddAct.triggered.connect(self.on_newScriptableObject)
                            pmenu.addAction(pAddAct)
                    elif top_name == "GameSourceModify":
                        pass
                    else:
                        pAddAct = QAction(self.tr("New File"), pmenu)
                        pAddAct.triggered.connect(self.on_newCard)
                        pmenu.addAction(pAddAct)
                else:
                    top_parent = self.getDepthParent(index, depth=1)
                    if top_parent is None:
                        return
                    top_name = self.file_model.fileName(top_parent)
                    if file_name in DataBase.SupportList:
                        if top_name == "GameSourceModify" or top_name == "ScriptableObject":
                            pass
                        else:
                            pAddAct = QAction(self.tr("New File"), pmenu)
                            pAddAct.triggered.connect(self.on_newCard)
                            pmenu.addAction(pAddAct)
            if depth > 1:
                if not self.file_model.isDir(index) and file_name.endswith(".json"):
                    if not file_path in self.tab_item_dict:
                        pDeleteAct = QAction(self.tr("Delete"), pmenu)
                        pDeleteAct.triggered.connect(self.on_delCard)
                        pmenu.addAction(pDeleteAct)
            if len(pmenu.actions()):
                pmenu.popup(self.sender().mapToGlobal(pos))

    @log_exception(True)
    def on_newScriptableObject(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            file_name = self.file_model.fileName(index)
            file_path = self.file_model.filePath(index)
            top_parent = self.getDepthParent(index, depth=1)
            if top_parent is None:
                return
            top_name = self.file_model.fileName(top_parent)
            if top_name == "ScriptableObject":
                group_name = file_name
                select = SelectGUI.SelectGUI(self, field_name = group_name, checked = False, type = SelectGUI.SelectGUI.NewData)
                select.exec_()
                template_key = select.lineEdit.text()
                try:
                    card_name = select.name_editor.text()
                    if card_name and template_key:
                        card_path = file_path + "/" + card_name + ".json"
                        if not os.path.exists(card_path):
                            with open(DataBase.AllPath[group_name][template_key], "r") as f:
                                temp_data = f.read(-1)
                            with open(card_path, "w") as f:
                                f.write(temp_data)
                        else:
                            QMessageBox.warning(self, self.tr("Warning"), self.tr('A file with the same name exists'))
                except Exception as ex:
                    QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))
                self.init_completer()

    @log_exception(True)
    def on_newCard(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            file_name = self.file_model.fileName(index)
            file_path = self.file_model.filePath(index)
            top_parent = self.getDepthParent(index, depth=1)
            if top_parent is None:
                return
            top_name = self.file_model.fileName(top_parent)
            if file_name:
                group_name = top_name
                select = SelectGUI.SelectGUI(self, field_name = group_name, checked = False, type = SelectGUI.SelectGUI.NewData)
                select.exec_()
                if select.write_flag:
                    template_key = select.lineEdit.text()
                    if select.lineEdit.text().rfind("(") >= 0:
                        template_key = select.lineEdit.text()[0:select.lineEdit.text().rfind("(")]
                    try:
                        card_name = select.name_editor.text()
                        if card_name and template_key:
                            card_path = file_path + "/" + card_name + ".json"
                            if not os.path.exists(card_path):
                                with open(DataBase.AllPath[group_name][template_key], "r") as f:
                                    temp_data = f.read(-1)
                                temp_json = json.loads(temp_data)
                                guid = temp_json["UniqueID"]
                                temp_data = temp_data.replace(guid, str(uuid.uuid4()).replace("-",""))
                                with open(card_path, "w") as f:
                                    f.write(temp_data)
                            else:
                                QMessageBox.warning(self, self.tr("Warning"), self.tr('A file with the same name exists'))
                    except Exception as ex:
                        QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))
                    self.init_completer()

    @log_exception(True)
    def on_newModify(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            file_name = self.file_model.fileName(index)
            file_path = self.file_model.filePath(index)
            top_parent = self.getDepthParent(index, depth=1)
            if top_parent is None:
                return
            top_name = self.file_model.fileName(top_parent)
            if file_name:
                group_name = top_name
                select = SelectGUI.SelectGUI(self, field_name = group_name, checked = False, type = SelectGUI.SelectGUI.NewModify)
                select.exec_()
                if select.write_flag:
                    target_key = select.lineEdit.text()
                    try:
                        dir_name = select.name_editor.text()
                        if dir_name and target_key:
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
                                card_dir = file_path + "/" + dir_name
                                card_path = file_path + "/" + dir_name + "/" + target_guid + ".json"
                                if not os.path.exists(card_dir):
                                    os.mkdir(card_dir)
                                if not os.path.exists(card_path):                                    
                                    with open(card_path, "w") as f:
                                        f.write("{\n\n}")
                                else:
                                    QMessageBox.warning(self, self.tr("Warning"), self.tr('A file with the same name exists'))
                    except Exception as ex:
                        QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))
                    self.init_completer()

    @log_exception(True)
    def on_delCard(self, checked: bool=False) -> None:
        index = self.treeView.currentIndex()
        if index.isValid():
            file_name = self.file_model.fileName(index)
            file_path = self.file_model.filePath(index)
            top_parent = self.getDepthParent(index, depth=1)
            if top_parent is None:
                return
            top_name = self.file_model.fileName(top_parent)
            reply = QMessageBox.question(self, self.tr("Warning"), self.tr('Make sure to delete ') + top_name + ":" + file_name + '?', QMessageBox.Yes | QMessageBox.No , QMessageBox.No)
            if reply == QMessageBox.Yes:
                if self.file_model.isDir(index):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
            self.init_completer()

    def saveTabJsonItem(self, index: int):
        item = self.tabWidget.widget(index)
        treeViewIndex = self.file_model.index(item.tab_key)
        top_parent = self.getDepthParent(treeViewIndex, depth=1)
        if top_parent is None:
            return
        top_name = self.file_model.fileName(top_parent)
        if top_name == "GameSourceModify":
            save_data = self.tabWidget.widget(index).treeView.model().sourceModel().to_json()
            self.delGameSourceModifyTemplate(save_data)
        else:
            save_data = self.tabWidget.widget(index).treeView.model().sourceModel().to_json()
        with open(item.tab_key, "w") as f:
            json.dump(save_data, f, sort_keys=True, indent = 4)
        DataBase.loopLoadModSimpCn(save_data, self.mod_info["Name"])
    
    @log_exception(True)
    def on_tabWidgetTabCloseRequested(self, index: int, ask: bool = True):
        if ask:
            reply = QMessageBox.question(self, self.tr('Save'), self.tr('Save the changes before exit?'), QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel , QMessageBox.Yes)
        else:
            reply = QMessageBox.Yes
        item = self.tabWidget.widget(index)
        tab_key = item.tab_key
        if reply == QMessageBox.Yes:
            self.saveTabJsonItem(index)
            del self.tab_item_dict[tab_key]
            self.tabWidget.removeTab(index)  
        elif reply == QMessageBox.No:
            del self.tab_item_dict[tab_key]
            self.tabWidget.removeTab(index)
        elif reply == QMessageBox.Cancel:
            return
            
    def treeItemDepth(self, index: QModelIndex):
        depth = 0 
        while index.parent().isValid():
            depth += 1
            index = index.parent()
        return depth - self.root_depth

    def getDepthParent(self, index: QModelIndex, depth: int):
        if self.treeItemDepth(index) < depth:
            return None
        if self.treeItemDepth(index) == depth:
            return index
        if depth < 0:
            return None
        if depth == 0:
            return self.treeView.rootIndex()
        else:
            parent = index.parent()
            while self.treeItemDepth(parent) != depth:
                parent = parent.parent()
            return parent
        return None

    def openTreeViewItem(self, index: QModelIndex):
        tab_key = self.file_model.filePath(index)
        if tab_key in self.tab_item_dict:
            pass
        else:
            top_parent = self.getDepthParent(index, depth=1)
            if top_parent is None:
                return
            top_name = self.file_model.fileName(top_parent)
            file_name = self.file_model.fileName(index)
            file_path = self.file_model.filePath(index)
            if top_name == "GameSourceModify":
                template_reftrans = DataBase.AllGuidPlainRev[file_name[:-5]]
                for type_key in DataBase.AllRef["CardData"].keys():
                    if template_reftrans in DataBase.AllRef["CardData"][type_key]:
                        target_group_name = "CardData"
                        break
                for group_key in DataBase.AllGuid.keys():
                    if template_reftrans in DataBase.AllGuid[group_key]:
                        target_group_name = group_key
                        break
                item = ModifyItemGUI.ModifyItemGUI(field=target_group_name, auto_resize=self.autoresize, key=tab_key, parent=self.tabWidget)
                template_ref = template_reftrans
                if template_reftrans.rfind("(") >= 0:
                    template_ref = template_reftrans[0:template_reftrans.rfind("(")]
                template_path = DataBase.AllPathPlain[template_ref]
                with open(file_path, 'rb') as f:
                    src_json = json.load(f)
                with open(template_path, 'rb') as f:
                    template_json = json.load(f)
                    self.loopDelGameSourceModifyTemplateWarpper(template_json)
                src_json.update(template_json)
                item.loadJsonData(src_json, is_modify=True)
            elif top_name in DataBase.RefGuidList:
                item = ItemGUI.ItemGUI(field=top_name, auto_resize=self.autoresize, key=tab_key, parent=self.tabWidget)
                with open(file_path, 'r') as f:
                    item.loadJsonData(json.load(f))
            elif top_name == "ScriptableObject":
                top2nd_parent = self.getDepthParent(index, depth=2)
                top2nd_name = self.file_model.fileName(top2nd_parent)
                item = ItemGUI.ItemGUI(field=top2nd_name, auto_resize=self.autoresize, key=tab_key, parent=self.tabWidget)
                with open(file_path, 'r') as f:
                    item.loadJsonData(json.load(f))
            else:
                print("openTreeViewItem Unexport Type")
                return
            self.tabWidget.addTab(item, file_name[:-5])
            self.tab_item_dict[tab_key] = {"widget": item}
        self.tabWidget.setCurrentWidget(self.tab_item_dict[tab_key]["widget"])

    @log_exception(True)
    def on_treeViewDoubleClicked(self, index: QModelIndex):
        if index.isValid() and not self.file_model.isDir(index) and self.file_model.fileName(index).endswith(".json"):
            self.openTreeViewItem(index)

    def loopDelGameSourceModifyTemplateWarpper(self, json):
        for key in list(json.keys()):
            if key.endswith("WarpType") or key.endswith("WarpData"):
                del json[key]

    def delGameSourceModifyTemplate(self, json):
        if type(json) == dict:
            for key in list(json.keys()):
                if not key.endswith("WarpType") and not key.endswith("WarpData"):
                    del json[key]

    @log_exception(True)
    def on_newMod(self, checked: bool=False):
        if self.tab_item_dict:
            QMessageBox.warning(self, self.tr("Warning"), self.tr('Please close all opened files first'))
            return
        self.new_mod = NewItemGUI.NewItemGUI(self)
        self.new_mod.buttonBox.accepted.connect(self.on_newModButtonBoxAccepted)
        self.new_mod.exec_()

    @log_exception(True)
    def on_newModButtonBoxAccepted(self):
        mod_name = self.new_mod.lineEdit.text()
        if not mod_name:
            return
        if os.path.exists(QDir.currentPath() + r"/Mods/" + mod_name):
            QMessageBox.warning(self, self.tr("Warning"), self.tr('Mod folder with the same name exists'))
            return
        shutil.copytree(QDir.currentPath() + r"/CSTI-JsonData/BaseMod", QDir.currentPath() + r"/Mods/" + mod_name)
        self.loadMod(QDir.currentPath() + r"/Mods/" + mod_name)

    @log_exception(True)
    def on_saveMod(self, checked: bool=False):
        if self.mod_info:
            for i in range(self.tabWidget.count()):
                self.saveTabJsonItem(i)
            with open(self.mod_path + "/ModInfo.json", "w") as f:
                json.dump(self.mod_info, f, sort_keys=True, indent = 4)
            DataBase.saveCollection()
            DataBase.saveModSimpCn(self.mod_path)
            DataBase.LoadModData(self.mod_info["Name"], self.mod_path)

    @log_exception(True)
    def on_exportZip(self, checked: bool=False):
        if self.mod_info:
            self.on_saveMod()
            ExportToZip.exportToZip(self.mod_path, self.mod_info)
    
    @log_exception(True)
    def on_loadMod(self, checked: bool=False):
        if self.tab_item_dict:
            QMessageBox.warning(self, self.tr("Warning"), self.tr('Please close all opened files first'))
            return
        if self.last_open_dir == "":
            mod_path = QFileDialog.getExistingDirectory(self, caption=self.tr('Select a Mod folder'), directory=QDir.currentPath())
        else:
            mod_path = QFileDialog.getExistingDirectory(self, caption=self.tr('Select a Mod folder'), directory=self.last_open_dir)
        if mod_path is None or mod_path == "":
            return
        if "ModInfo.json" not in os.listdir(mod_path):
            QMessageBox.warning(self, self.tr("Warning"), self.tr('Not a valid Mod folder'))
            return
        self.last_open_dir = str(Path(mod_path).parent.absolute())
        self.config.set("Config", "LastOpenDir", self.last_open_dir)
        self.saveConfig()
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

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.mod_path)
        self.file_model.setReadOnly(False)
        self.file_model.fileRenamed.connect(self.treeItemRenamed)
        self.treeView.setModel(self.file_model)
        self.treeView.setRootIndex(self.file_model.index(self.mod_path))
        self.root_depth = self.treeItemDepth(self.file_model.index(self.mod_path))
        self.treeView.setDragDropMode(QAbstractItemView.DragDrop)
        self.treeView.setDefaultDropAction(Qt.MoveAction)
        self.treeView.setColumnHidden(1, True)
        self.treeView.setColumnHidden(2, True)
        self.treeView.setColumnHidden(3, True)

        self.setWindowTitle("%s (%s)" % (self.srcTitle, self.mod_info["Name"]))
        self.init_completer()

if __name__ == '__main__':
    QTextCodec.setCodecForLocale(QTextCodec.codecForName("UTF-8"))
    app = QApplication(sys.argv)
    main = ModEditorGUI()
    main.show()
    sys.exit(app.exec_())