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
import SelectGUI
from functools import partial

ModEditorVersion = "0.0.2"

class ModEditorGUI(QMainWindow, Ui_MainWindow):
    groupname_list = ["CardData", "CharacterPerk", "GameSourceModify", "GameStat", "Objective", "SelfTriggeredAction"]

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
        self.treeWidget.itemDoubleClicked.connect(self.on_treeWidgetItemDoubleClicked)
        self.treeWidget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.on_treeWidgetCustomContextMenuRequested)

        self.action_newMod.triggered.connect(self.on_newMod)
        self.action_loadMod.triggered.connect(self.on_loadMod)
        self.action_save.triggered.connect(self.on_saveMod)

        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.on_tabWidgetTabCloseRequested)

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
            root = hititem.parent()
            pmenu = QMenu(self)
            if root is None:
                pAddAct = QAction("新建", pmenu)
                pAddAct.triggered.connect(self.on_newCard)
                pmenu.addAction(pAddAct)
            else:
                tab_key = root.text(0) + ":" + hititem.text(0)
                if not tab_key in self.tab_item_dict:
                    pDeleteAct = QAction("删除", pmenu)
                    pDeleteAct.triggered.connect(self.on_delCard)
                    pmenu.addAction(pDeleteAct)
            pmenu.popup(self.sender().mapToGlobal(pos))

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
                    if card_name:
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
                except Exception as ex:
                    print(traceback.format_exc())

    def on_delCard(self) -> None:
        hititem = self.treeWidget.currentItem()
        root = hititem.parent()
        if root is None:
            pass
        else:
            reply = QMessageBox.question(self,'警告','确定要删除' + root.text(0) + ":" + hititem.text(0) + '吗', QMessageBox.Yes | QMessageBox.No , QMessageBox.No)
            if reply == QMessageBox.Yes:
                index = root.indexOfChild(hititem)
                root.takeChild(index)
                os.remove(self.tree_item_dict[root.text(0)][hititem.text(0)]["path"])
                del self.tree_item_dict[root.text(0)][hititem.text(0)]
                del hititem
    
    def on_tabWidgetTabCloseRequested(self, index: int):
        reply = QMessageBox.question(self, '保存', '是否在退出前保存', QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel , QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            save_data = self.tabWidget.widget(index).treeView.model().sourceModel().to_json()
            with open(self.tab_item_dict[self.tabWidget.tabText(index)]["path"], "w") as f:
                json.dump(save_data, f, indent = 4)
            del self.tab_item_dict[self.tabWidget.tabText(index)]
            self.tabWidget.removeTab(index)  
        elif reply == QMessageBox.No:
            del self.tab_item_dict[self.tabWidget.tabText(index)]
            self.tabWidget.removeTab(index)
        elif reply == QMessageBox.Cancel:
            return
        # print("on_tabWidgetTabCloseRequested", index)

    def on_treeWidgetItemDoubleClicked(self, treeItem: QTreeWidgetItem, column: int):
        if treeItem:
            root = treeItem.parent()
            if root is None:
                return
            else:
                tab_key = treeItem.parent().text(0) + ":" + treeItem.text(0)
                if treeItem.text(0) in self.tab_item_dict:
                    pass
                else:
                    item = ItemGUI.ItemGUI(root.text(0), self.tabWidget)
                    file_path = self.tree_item_dict[treeItem.parent().text(0)][treeItem.text(0)]["path"]
                    with open(file_path, 'rb') as f:
                        item.loadJsonData(f.read(-1))
                    self.tabWidget.addTab(item, tab_key)
                    self.tab_item_dict[tab_key] = {"name": treeItem.text(0), "path":  file_path, "widget": item}
                self.tabWidget.setCurrentWidget(self.tab_item_dict[tab_key]["widget"])

    def on_newMod(self):
        if self.tab_item_dict:
            QMessageBox.warning(self, '警告','请先关闭所有子菜单')
            return
            
        self.new_mod = NewItemGUI.NewModGUI(self)
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
            for i in range(self.tabWidget.count()):
                save_data = self.tabWidget.widget(i).treeView.model().sourceModel().to_json()
                with open(self.tab_item_dict[self.tabWidget.tabText(i)]["path"], "w") as f:
                    json.dump(save_data, f, indent = 4)
            with open(self.mod_path + "/ModInfo.json", "w") as f:
                json.dump(self.mod_info, f, indent = 4)

            DataBase.saveCollection()
        
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
            if item in self.groupname_list:
                group = QTreeWidgetItem(self.treeWidget)
                group.setText(0, item)
                self.tree_item_dict[item] = {}
                for sub_item in os.listdir(self.mod_path + "/" + item):
                    if sub_item.endswith(".json"):
                        child = QTreeWidgetItem()
                        child.setText(0, sub_item[:-5])
                        group.addChild(child)
                        self.tree_item_dict[item][sub_item[:-5]] = {"path": self.mod_path + "/" + item  + "/" + sub_item}
                group.setExpanded(True)
                self.group_dict[item] = group
        self.setWindowTitle("ModEditor (%s)" % (self.mod_info["Name"]))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = ModEditorGUI()
    main.show()
    sys.exit(app.exec_())