# -*- coding: utf-8 -*- 
import ujson as json
import sys
import os
import copy
import time
from glob import glob
from MyLogger import *

def loopReplaceLocalizationKeyAndReplaceGuid(jsondata:dict, mod_name:str, card_name:str, guid:str="", entry_key:str="", index:int=-1):
    if isinstance(jsondata, list):
        for item in jsondata:
            loopReplaceLocalizationKeyAndReplaceGuid(item, mod_name, card_name, guid)
        return
    elif isinstance(jsondata, dict):
        pass
    else:
        return
    for key in jsondata.keys():
        if key == "LocalizationKey" and jsondata[key] != "":
            entry = jsondata[key][jsondata[key].rfind("_"):]
            if entry_key != "" and index > 0:
                st_idx = entry.rfind(entry_key)
                end_idx = entry[st_idx:].find("]") + st_idx
                entry = entry[:st_idx + len(entry_key) + 1] + str(index) +  entry[end_idx:]
            jsondata[key] = mod_name + "_" + card_name + entry
        elif isinstance(jsondata[key], dict):
            loopReplaceLocalizationKeyAndReplaceGuid(jsondata[key], mod_name, card_name, guid, entry_key, index)
        elif isinstance(jsondata[key], list):
            for item in jsondata[key]:
                loopReplaceLocalizationKeyAndReplaceGuid(item, mod_name, card_name, guid, entry_key, index)
        elif key == "ParentObjectID" and guid != "" and jsondata["ParentObjectID"] != "":
            jsondata["ParentObjectID"] = guid

def delete_keys_from_dict(src_dict, key: str):
    for field in list(src_dict.keys()):
        if field == key:
            del src_dict[field]
        elif type(src_dict[field]) == dict:
            delete_keys_from_dict(src_dict[field], key)

class DataBase(object):
    DataDir = None
    RefNameList = ["AudioClip", "Sprite", "WeatherSpecialEffect"]
    # RefNameList = ["ActionTag", "AudioClip", "CardTag", "EquipmentTag", "EndgameLogCategory", "Sprite", "WeatherSet", "WeatherSpecialEffect", "CardTabGroup"]
    RefGuidList = ["CardData", "CharacterPerk", "GameStat", "Objective", "SelfTriggeredAction", "PlayerCharacter", "PerkGroup", "EndgameLogCategory", "PerkTabGroup", "GameObject"]
    SupportList = ["CardData", "CharacterPerk", "GameStat", "Objective", "SelfTriggeredAction", "PlayerCharacter", "PerkGroup", "EndgameLogCategory", "PerkTabGroup", \
        "GameSourceModify", "ScriptableObject"]

    AllSpecialTypeField = {}
    AllSpecialTypeField["CardData"] = ["BlueprintCardDataCardTabGroup", "BlueprintCardDataCardTabSubGroup", "ItemCardDataCardTabGpGroup", "MatchTypeWarpData", "MatchTagWarpData", "CardDataCardFilterGroup"]
    AllSpecialTypeField["CharacterPerk"] = ["CharacterPerkPerkGroup"]
    AllSpecialTypeField["GameStat"] = ["VisibleGameStatStatListTab"]
    AllSpecialTypeField["CardTabGroup"] = ["BlueprintCardDataCardTabGroup"]
    AllSpecialTypeField["PlayerCharacter"] = ["PlayerCharacterJournalName"]

    AllBlueprintTab = []
    AllBlueprintSubTab = []
    AllItemTabGpGroup = []
    AllCardFilterGroup = []

    AllEnum = {}
    AllEnumRev = {}
    AllTypeField = {}

    AllRef = {}             # DataBase.AllRef["ActionTag"] -> list[Ref]              DataBase.AllRef["CardData"]["Item"] -> list[RefTrans]
    AllGuid = {}            # DataBase.AllGuid["GameStat"][Ref] -> Guid              DataBase.AllGuid["CardData"]["Item"][RefTrans] -> Guid
    AllGuidPlain = {}       # DataBase.AllGuidPlain[RefTrans/Ref] -> Guid
    AllGuidPlainRev = {}    # DataBase.AllGuidPlainRev[Guid] -> RefTrans/Ref
    AllCardData = {}        # DataBase.AllCardData[RefTrans] -> CardData Guid
    AllPath = {}            # DataBase.AllPath["GameStat"][Ref] -> FilePath
    AllPathPlain = {}       # DataBase.AllPathPlain[Ref] -> FilePath
    AllScriptableObject = {}   # DataBase.AllScriptableObject[Ref] -> Guid or Ref
    AllCollection = {}      # DataBase.AllCollection["CardsDropCollection"][CustomName] -> json data
    AllListCollection = {}      # DataBase.AllListCollection["CardsDropCollection"][CustomName] -> List json data
    AllNotes = {}           # DataBase.AllNotes["CardData"]["CardName"] -> Note
    AllBaseJsonData = {}    # DataBase.AllBaseJsonData["CardData"] -> base json data

    AllSimpCn = {}  # DataBase.AllSimpCn[key] -> {origin, trans}
    AllTranDict = {}  # DataBase.AllTranDict[origin] -> trans

    AutoCompleteUpdate = False

    def __init__(self):
        pass

    def loadDataBase(data_dir:str, lan:str):
        DataBase.DataDir = data_dir

        if not os.path.exists(DataBase.DataDir + "/Mods"):
            os.mkdir(DataBase.DataDir + "/Mods")

        # Load Name
        DataBase.loadName()

        # Load GUID
        DataBase.loadGuid()

        # Load Path
        DataBase.loadPath()

        # Load Base Json
        DataBase.loadBaseJson()

        # Load ScriptableObject FieldName FieldType
        DataBase.loadScriptableObjectField()

        # Load Template
        # DataBase.loadTemplate()

        # Load SpecialTypeField
        DataBase.loadSpecialTypeField()

        # Load Collection
        DataBase.loadCollection()

        # Load Note
        DataBase.loadNote(lan)

        # Load GameSimpCn
        DataBase.loadGameSimpCn()

    def LoadModData(mod_name, mod_dir):
        DataBase.AllRef = {}
        DataBase.AllGuid = {}
        DataBase.AllGuidPlain = {}
        DataBase.AllGuidPlainRev = {}
        DataBase.AllCardData = {}
        DataBase.AllPath = {}
        DataBase.AllScriptableObject = {}  

        DataBase.AllRef.update(copy.deepcopy(DataBase.AllRefBase))
        DataBase.AllGuid.update(copy.deepcopy(DataBase.AllGuidBase))
        DataBase.AllGuidPlain.update(copy.deepcopy(DataBase.AllGuidPlainBase))
        DataBase.AllCardData.update(copy.deepcopy(DataBase.AllCardDataBase))
        DataBase.AllPath.update(copy.deepcopy(DataBase.AllPathBase))
        DataBase.AllScriptableObject.update(copy.deepcopy(DataBase.AllScriptableObjectBase))

        DataBase.AllRef["CardData"]["Mod"] = []
        DataBase.AllRef["ContentDisplayer"] = []
        
        DataBase.AllModSimpCn = {}

        for dir in os.listdir(mod_dir):
            if os.path.isdir(mod_dir + r"/" + dir):
                if dir in DataBase.RefGuidList:
                    for file in [y for x in os.walk(mod_dir + r"/" + dir) for y in glob(os.path.join(x[0], '*.json'))]:
                        file_name = os.path.basename(file)
                        guid = None
                        with open(file, "rb") as f:
                            data = f.read(-1)
                            guid_idx = data.find(b'"UniqueID"')
                            if guid_idx == -1:
                                continue
                            start_mark = data.find(b'"', guid_idx + len('"UniqueID"'))
                            if start_mark == -1:
                                continue
                            end_mark = data.find(b'"', start_mark + 1)
                            if end_mark == -1:
                                continue
                            guid = data[start_mark + 1:end_mark].decode()
                        if guid is None or guid == "":
                            continue
                        ref = mod_name + "_" + file_name[:-5]
                        if dir == "CardData":
                            DataBase.AllRef[dir]["Mod"].append(ref)
                            DataBase.AllGuid[dir].update({ref : guid})
                            DataBase.AllGuidPlain.update({ref : guid})
                            DataBase.AllCardData.update({ref : guid})
                            DataBase.AllPath[dir].update({ref : file})
                            DataBase.AllScriptableObject.update({ref : guid})
                        else:
                            DataBase.AllRef[dir].append(ref)
                            DataBase.AllGuid[dir].update({ref : guid})
                            DataBase.AllGuidPlain.update({ref : guid})
                            DataBase.AllPath[dir].update({ref : file})
                            DataBase.AllScriptableObject.update({ref : guid})
                elif dir == "GameSourceModify":
                    pass
                elif dir == "ScriptableObject":
                    for sub_dir in os.listdir(mod_dir + r"/" + dir):
                        for file in [y for x in os.walk(mod_dir + r"/" + dir + r"/" + sub_dir) for y in glob(os.path.join(x[0], '*.json'))]:
                            file_name = os.path.basename(file)  
                            if sub_dir == "ContentPage":
                                if file_name.endswith("Default.json"):
                                    name_parts = file_name.split("_")
                                    if len(name_parts) > 2:
                                        DataBase.AllRef["ContentDisplayer"].append(name_parts[0] + "_" + name_parts[1])
                            if file.endswith(".json"):
                                ref = file_name[:-5]
                                DataBase.AllRef[sub_dir].append(file_name[:-5])
                                DataBase.AllPath[sub_dir].update({ref : file})
                                DataBase.AllScriptableObject.update({ref : ref})
                elif dir == "Localization":
                    if os.path.exists(mod_dir + r"/" + dir + r"/SimpCn.csv"):
                        with open(mod_dir + r"/" + dir + r"/SimpCn.csv", "r", encoding='utf-8') as f:
                            lines = f.readlines(-1)
                            for line in lines:
                                keys = line.split(',')
                                if len(keys) > 3:
                                    if line.find('"') != -1:
                                        new_keys = line.split('"')
                                        if len(new_keys) == 3 and new_keys[0][-1] == ',' and  new_keys[2][0] == ',':
                                            DataBase.AllModSimpCn[new_keys[0][:-1]] = {"original": new_keys[1].replace('"',''), "translate": new_keys[2][1:].replace("\n","")}  
                                elif len(keys) == 3:
                                    DataBase.AllModSimpCn[keys[0]] = {"original": keys[1].replace('"',''), "translate": keys[2].replace("\n","")}
                                else:
                                    QtCore.qWarning(b"Wrong Format Key")
                elif dir == "Resource":
                    if os.path.exists(mod_dir + r"/" + dir + r"/Picture"):
                        for file in os.listdir(mod_dir + r"/" + dir + r"/Picture"):
                            if file.endswith(".jpg") or file.endswith(".png"):
                                DataBase.AllRef["Sprite"].append(file[:-4])
                            if file.endswith(".jpeg"):
                                DataBase.AllRef["Sprite"].append(file[:-5])
                    if os.path.exists(mod_dir + r"/" + dir + r"/Audio"):
                        for file in os.listdir(mod_dir + r"/" + dir + r"/Audio"):
                            if file.endswith(".wav"):
                                DataBase.AllRef["AudioClip"].append(file[:-4])

        for key in DataBase.AllPath:
            DataBase.AllPathPlain.update(copy.deepcopy(DataBase.AllPath[key]))

        DataBase.AllGuidPlainRev = {v : k for k, v in DataBase.AllGuidPlain.items()}

    def loadName():
        DataBase.AllRefBase = {}
        DataBase.AllScriptableObjectBase = {}

        for dir in os.listdir(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableBaseJsonData/"):
            if os.path.isdir(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableBaseJsonData/" + dir):
                if dir not in DataBase.RefGuidList:
                    DataBase.RefGuidList.append(dir)
                    DataBase.SupportList.append(dir)

        for dir in os.listdir(DataBase.DataDir + r"/CSTI-JsonData/ScriptableObjectJsonDataWithWarpLitAllInOne/"):
            if os.path.isdir(DataBase.DataDir + r"/CSTI-JsonData/ScriptableObjectJsonDataWithWarpLitAllInOne/" + dir):
                DataBase.RefNameList.append(dir)

        for file in os.listdir(DataBase.DataDir + r"/CSTI-JsonData/ScriptableObjectObjectName/"):
            if not file.endswith(".txt"):
                continue
            with open(DataBase.DataDir + r"/CSTI-JsonData/ScriptableObjectObjectName/" + file, encoding='utf-8') as f:
                temp = f.readlines()
                temp = list(map(lambda x: x.replace("\n",""), temp))
                DataBase.AllRefBase[file[:-4]] = temp
                DataBase.AllScriptableObjectBase.update({k : k for k in temp})
                if file[:-4] == "CardTabGroup":
                    for item in temp:
                        if item.startswith("Tab_"):
                            if item.count("_") == 1:
                                DataBase.AllBlueprintTab.append(item)
                            else:
                                DataBase.AllBlueprintSubTab.append(item)
                        if item.startswith("GpTag_"):
                            DataBase.AllItemTabGpGroup.append(item)
                if file[:-4] == "CardFilterGroup":
                    DataBase.AllCardFilterGroup.extend(temp)

        if "WeatherParticles" in DataBase.AllRefBase and "WeatherSpecialEffect" in DataBase.AllRefBase:
            DataBase.AllRefBase["WeatherSpecialEffect"].extend(copy.deepcopy(DataBase.AllRefBase["WeatherParticles"]))

    def loadGuid():
        DataBase.AllGuidBase = {}  # Type: {Key: Guid}
        DataBase.AllGuidPlainBase = {}
        DataBase.AllCardDataBase = {}  # Key: Guid

        for file in os.listdir(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableGUID/"):
            if not file.endswith(".json"):
                continue
            with open(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableGUID/" + file, encoding='utf-8') as f:
                temp = json.loads(f.read(-1))
                DataBase.AllRefBase[file[:-5]] = list(temp.keys())
                DataBase.AllGuidBase[file[:-5]] = temp
                DataBase.AllGuidPlainBase.update(temp)
                DataBase.AllScriptableObjectBase.update(temp)

        DataBase.AllRefBase["CardData"] = {}
        DataBase.AllGuidBase["CardData"] = {}
        for file in os.listdir(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableGUID/CardData/"):
            if not file.endswith(".json"):
                continue
            with open(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableGUID/CardData/" + file, encoding='utf-8') as f:
                temp = json.loads(f.read(-1))
                DataBase.AllCardDataBase.update(temp)
                DataBase.AllGuidBase["CardData"][file[:-5]] = temp
                DataBase.AllRefBase["CardData"][file[:-5]] = list(temp.keys())
                DataBase.AllGuidPlainBase.update(temp)
                DataBase.AllScriptableObjectBase.update(temp)

        try:
            for mod_ref_dir in os.listdir(DataBase.DataDir + r"/CSTI-JsonData/ModReference/"):
                if os.path.isdir(DataBase.DataDir + r"/CSTI-JsonData/ModReference/" + mod_ref_dir):
                    for file in os.listdir(DataBase.DataDir + r"/CSTI-JsonData/ModReference/" + mod_ref_dir + r"/UniqueIDScriptableGUID/"):
                        if file.endswith(".json") and file[:-5] in DataBase.AllRefBase:
                            with open(DataBase.DataDir + r"/CSTI-JsonData/ModReference/" + mod_ref_dir + r"/UniqueIDScriptableGUID/" + file, encoding='utf-8') as f:
                                temp = json.loads(f.read(-1))
                                DataBase.AllRefBase[file[:-5]].extend(list(temp.keys()))
                                DataBase.AllGuidBase[file[:-5]].update(temp)
                                DataBase.AllGuidPlainBase.update(temp)
                                DataBase.AllScriptableObjectBase.update(temp)

                    for file in os.listdir(DataBase.DataDir + r"/CSTI-JsonData/ModReference/" + mod_ref_dir + r"/UniqueIDScriptableGUID/CardData/"):
                        if file.endswith(".json") and file[:-5] in DataBase.AllGuidBase["CardData"]:
                            with open(DataBase.DataDir + r"/CSTI-JsonData/ModReference/" + mod_ref_dir + r"/UniqueIDScriptableGUID/CardData/" + file, encoding='utf-8') as f:
                                temp = json.loads(f.read(-1))
                                DataBase.AllCardDataBase.update(temp)
                                DataBase.AllGuidBase["CardData"][file[:-5]].update(temp)
                                DataBase.AllRefBase["CardData"][file[:-5]].extend(temp.keys())
                                DataBase.AllGuidPlainBase.update(temp)
                                DataBase.AllScriptableObjectBase.update(temp)
        except Exception as ex:
            QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))

        try:
            for mod_ref_dir in os.listdir(DataBase.DataDir + r"/Mods/ModReference/"):
                if os.path.isdir(DataBase.DataDir + r"/Mods/ModReference/" + mod_ref_dir):
                    for file in os.listdir(DataBase.DataDir + r"/Mods/ModReference/" + mod_ref_dir + r"/UniqueIDScriptableGUID/"):
                        if file.endswith(".json") and file[:-5] in DataBase.AllRefBase:
                            with open(DataBase.DataDir + r"/Mods/ModReference/" + mod_ref_dir + r"/UniqueIDScriptableGUID/" + file, encoding='utf-8') as f:
                                temp = json.loads(f.read(-1))
                                DataBase.AllRefBase[file[:-5]].extend(list(temp.keys()))
                                DataBase.AllGuidBase[file[:-5]].update(temp)
                                DataBase.AllGuidPlainBase.update(temp)
                                DataBase.AllScriptableObjectBase.update(temp)

                    for file in os.listdir(DataBase.DataDir + r"/Mods/ModReference/" + mod_ref_dir + r"/UniqueIDScriptableGUID/CardData/"):
                        if file.endswith(".json") and file[:-5] in DataBase.AllGuidBase["CardData"]:
                            with open(DataBase.DataDir + r"/Mods/ModReference/" + mod_ref_dir + r"/UniqueIDScriptableGUID/CardData/" + file, encoding='utf-8') as f:
                                temp = json.loads(f.read(-1))
                                DataBase.AllCardDataBase.update(temp)
                                DataBase.AllGuidBase["CardData"][file[:-5]].update(temp)
                                DataBase.AllRefBase["CardData"][file[:-5]].extend(temp.keys())
                                DataBase.AllGuidPlainBase.update(temp)
                                DataBase.AllScriptableObjectBase.update(temp)
        except Exception as ex:
            QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))
            
    def loadPath():
        DataBase.AllPathBase = {}  # Type: {Key: Path}
        base_path = DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableJsonDataWithWarpLitAllInOne/"
        for dir in os.listdir(base_path):
            if os.path.isdir(base_path + r"/" + dir):
                DataBase.AllPathBase[dir] = {}
                files = [y for x in os.walk(base_path + dir) for y in glob(os.path.join(x[0], '*.json'))]
                for file in files:
                    DataBase.AllPathBase[dir][os.path.basename(file)[:-5]] = file

        base_path = DataBase.DataDir + r"/CSTI-JsonData/ScriptableObjectJsonDataWithWarpLitAllInOne/"
        for dir in os.listdir(base_path):
            if os.path.isdir(base_path + r"/" + dir):
                DataBase.AllPathBase[dir] = {}
                files = [y for x in os.walk(base_path + dir) for y in glob(os.path.join(x[0], '*.json'))]
                for file in files:
                    DataBase.AllPathBase[dir][os.path.basename(file)[:-5]] = file

    def loadBaseJson():
        for file in [y for x in os.walk(DataBase.DataDir + r'/CSTI-JsonData/UniqueIDScriptableBaseJsonData/') for y in glob(os.path.join(x[0], '*.json'))]:
            TypeName = os.path.basename(file)[:-5]
            if TypeName in DataBase.AllBaseJsonData:
                continue
            with open(file, encoding='utf-8') as f:
                try:
                    DataBase.AllBaseJsonData[TypeName] = json.load(f)
                    if DataBase.AllBaseJsonData[TypeName] == {}:
                        QtCore.qWarning(bytes(TypeName + " is empty", encoding="utf-8"))
                except Exception as ex:
                    QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))
        # Special
        DataBase.AllBaseJsonData["Vector2Int"] = DataBase.AllBaseJsonData["Vector2"]

    def loadScriptableObjectField():
        files = os.listdir(DataBase.DataDir + r"/CSTI-JsonData/ScriptableObjectTypeJsonData")
        for file in files:
            if file.endswith(".json"):
                with open(DataBase.DataDir + r'/CSTI-JsonData/ScriptableObjectTypeJsonData/' + file, encoding='utf-8') as f:
                    try:
                        DataBase.AllTypeField[file[:-5]] = json.loads(f.read(-1))
                    except Exception as ex:
                        QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))

        for key in list(DataBase.AllTypeField.keys()):
            if key in DataBase.AllBaseJsonData:
                DataBase.AllTypeField[key] = {k : DataBase.AllTypeField[key][k] for k in DataBase.AllBaseJsonData[key].keys() if k in DataBase.AllTypeField[key]}
        
        files = os.listdir(DataBase.DataDir + r"/CSTI-JsonData/ScriptableObjectTypeJsonData/EnumType")
        for file in files:
            if file.endswith(".json"):
                with open(DataBase.DataDir + r'/CSTI-JsonData/ScriptableObjectTypeJsonData/EnumType/' + file, encoding='utf-8') as f:
                    try:
                        DataBase.AllEnum[file[:-5]] = json.loads(f.read(-1))
                    except Exception as ex:
                        QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))
        
        for key, item in DataBase.AllEnum.items():
            DataBase.AllEnumRev[key] = {v : k for k, v in DataBase.AllEnum[key].items()}

    def loadSpecialTypeField():
        for key, item_list in DataBase.AllSpecialTypeField.items():
            if key in DataBase.AllTypeField:
                for item in item_list:
                    DataBase.AllTypeField[key][item] = "SpecialWarp"

    def loadCollection():
        if os.path.exists(DataBase.DataDir + r"/Mods/" + r"Collection.json"):
            with open(DataBase.DataDir + r"/Mods/" + r"Collection.json", "r", encoding='utf-8') as f:
                DataBase.AllCollection = json.load(f)

        for key in DataBase.AllBaseJsonData.keys():
            if key not in DataBase.AllCollection:
                DataBase.AllCollection[key] = {}
            DataBase.AllCollection[key]["Empty Default"] = DataBase.AllBaseJsonData[key]

        if os.path.exists(DataBase.DataDir + r"/Mods/" + r"ListCollection.json"):
            with open(DataBase.DataDir + r"/Mods/" + r"ListCollection.json", "r", encoding='utf-8') as f:
                DataBase.AllListCollection = json.load(f)
                            
    def saveCollection():
        with open(DataBase.DataDir + r"/Mods/" + r"Collection.json", "w", encoding='utf-8') as f:
            json.dump(DataBase.AllCollection, f)

        with open(DataBase.DataDir + r"/Mods/" + r"ListCollection.json", "w", encoding='utf-8') as f:
            json.dump(DataBase.AllListCollection, f)

    def loopLoadModSimpCn(json, mod_name:str, simpCn_dict:dict=None):
        if type(json) is dict:
            for key, item in json.items():
                if type(item) == str:
                    if key == "LocalizationKey" and item.startswith(mod_name):
                        if simpCn_dict is not None and type(simpCn_dict) is dict:
                            if item not in simpCn_dict:
                                if "DefaultText" in json:
                                    simpCn_dict[item] = {"original": json["DefaultText"], "translate": ""}
                            else:
                                if "DefaultText" in json:
                                    simpCn_dict[item]["original"] = json["DefaultText"]
                        else:
                            if item not in DataBase.AllModSimpCn:
                                if "DefaultText" in json:
                                    DataBase.AllModSimpCn[item] = {"original": json["DefaultText"], "translate": ""}
                            else:
                                if "DefaultText" in json:
                                    DataBase.AllModSimpCn[item]["original"] = json["DefaultText"]
                elif type(item) == list:
                    for sub_item in item:
                        DataBase.loopLoadModSimpCn(sub_item, mod_name, simpCn_dict)
                elif type(item) == dict:
                    DataBase.loopLoadModSimpCn(item, mod_name, simpCn_dict)
        elif type(json) is list:
            for value in json:
                DataBase.loopLoadModSimpCn(value, mod_name, simpCn_dict)

    def loadModSimpCn(mod_dir):
        for dir in os.listdir(mod_dir):
            if os.path.isdir(mod_dir + r"/" + dir) and dir == "Localization" and os.path.exists(mod_dir + r"/" + dir + r"/SimpCn.csv"):
                with open(mod_dir + r"/" + dir + r"/SimpCn.csv", "r", encoding='utf-8') as f:
                    lines = f.readlines(-1)
                    for line in lines:
                        keys = line.split(',')
                        if len(keys) > 3 and line.find('"') != -1:
                            new_keys = line.split('"')
                            if len(new_keys) == 3 and new_keys[0][-1] == ',' and  new_keys[2][0] == ',':
                                if new_keys[0][:-1] not in DataBase.AllModSimpCn:
                                    DataBase.AllModSimpCn[new_keys[0][:-1]] = {"original": new_keys[1].replace('"',''), "translate": new_keys[2][1:].replace("\n","")}
                                else:
                                    DataBase.AllModSimpCn[new_keys[0][:-1]]["translate"] = new_keys[2][1:].replace("\n","")
                        elif len(keys) == 3:
                            if keys[0] not in DataBase.AllModSimpCn:
                                DataBase.AllModSimpCn[keys[0]] = {"original": keys[1].replace('"',''), "translate": keys[2].replace("\n","")}
                            else:
                                DataBase.AllModSimpCn[keys[0]]["translate"] = keys[2].replace("\n","")
                        else:
                            QtCore.qWarning(b"Wrong Format Key")

    def autoTranslationDuplicates(mod_dir):
        DataBase.loadModSimpCn(mod_dir)
        if len(DataBase.AllTranDict) == 0:
            for item in DataBase.AllSimpCn.values():
                if not item["original"] in DataBase.AllTranDict and "translate" in item and item["translate"] != "":
                    DataBase.AllTranDict[item["original"]] = item["translate"]
        for item in DataBase.AllModSimpCn.values():
            if not item["original"] in DataBase.AllTranDict and "translate" in item and item["translate"] != "":
                DataBase.AllTranDict[item["original"]] = item["translate"]
        for item in DataBase.AllModSimpCn.values():
            if "translate" in item and item["translate"] == "":
                if item["original"] in DataBase.AllTranDict:
                    item["translate"] = DataBase.AllTranDict[item["original"]]
        DataBase.saveModSimpCn(mod_dir, False)

    def deleteObsolete(mod_dir:str, mod_name:str):
        DataBase.loadModSimpCn(mod_dir)
        files = [y for x in os.walk(mod_dir) for y in glob(os.path.join(x[0], '*.json'))]
        ModSimpCnDict = {}
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    DataBase.loopLoadModSimpCn(data, mod_name, ModSimpCnDict)
            except Exception as ex:
                QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))
        obsolete_keys = set(DataBase.AllModSimpCn.keys()).difference(ModSimpCnDict.keys())
        for key in obsolete_keys:
            del DataBase.AllModSimpCn[key]
        DataBase.saveModSimpCn(mod_dir, False)

    def formatAllLocalizationKey(mod_dir:str, mod_name:str):
        DataBase.loadModSimpCn(mod_dir)
        files = [y for x in os.walk(mod_dir) for y in glob(os.path.join(x[0], '*.json'))]
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    DataBase.loopFormatSimpCn(data, mod_name)
                with open(file, "w", encoding="utf-8") as f:
                    json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)
            except Exception as ex:
                QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))
        DataBase.saveModSimpCn(mod_dir, False)
        
    def dumpAllJsonFileWithoutEnsureAscii(mod_dir:str, mod_name:str):
        files = [y for x in os.walk(mod_dir) for y in glob(os.path.join(x[0], '*.json'))]
        for file in files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                with open(file, "w", encoding="utf-8") as f:
                    json.dump(data, f, sort_keys=True, indent=4, ensure_ascii=False)
            except Exception as ex:
                QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))

    def loopFormatSimpCn(json, mod_name:str):
        if type(json) is dict:
            for key, item in json.items():
                if type(item) == str:
                    if key == "LocalizationKey" and json[key] != "":
                        if not item.startswith(mod_name):
                            json[key] = mod_name + "_" + json[key]
                        if json[key] not in DataBase.AllModSimpCn:
                            if "DefaultText" in json:
                                DataBase.AllModSimpCn[json[key]] = {"original": json["DefaultText"], "translate": ""}
                        else:
                            if "DefaultText" in json:
                                DataBase.AllModSimpCn[json[key]]["original"] = json["DefaultText"]
                elif type(item) == list:
                    for sub_item in item:
                        DataBase.loopFormatSimpCn(sub_item, mod_name)
                elif type(item) == dict:
                    DataBase.loopFormatSimpCn(item, mod_name)
        elif type(json) is list:
            for value in json:
                DataBase.loopFormatSimpCn(value, mod_name)

    def saveModSimpCn(mod_dir, loadSrc:bool=True):
        if loadSrc:
            DataBase.loadModSimpCn(mod_dir)
        with open(mod_dir + r"/Localization/SimpCn.csv", "w", encoding='utf-8') as f:
            for key in DataBase.AllModSimpCn:
                f.write(key)
                f.write(',"')
                f.write(DataBase.AllModSimpCn[key]["original"].replace("\n", "\\n").replace("\t", "\\t"))
                f.write('",')
                f.write(DataBase.AllModSimpCn[key]["translate"].replace("\n", "\\n").replace("\t", "\\t"))
                f.write('\n')

    def loadNote(lan:str="zh_CN"):
        if lan == "zh_CN":
            note_name = "Notes"
        else:
            note_name = "Notes-En"
        if os.path.exists(DataBase.DataDir + r'/CSTI-JsonData/' + note_name):
            for file in os.listdir(DataBase.DataDir + r'/CSTI-JsonData/' + note_name):
                try:
                    if file.endswith(".txt"):
                        if file[:-4] not in DataBase.AllNotes:
                            DataBase.AllNotes[file[:-4]] = {}
                        with open(DataBase.DataDir + r'/CSTI-JsonData/' + note_name + r'/' + file, "r", encoding='utf-8') as f:
                            lines = f.readlines()
                            for line in lines:
                                line = line.replace("\n", "")
                                items = line.split("\t")
                                if len(items) == 2:
                                    DataBase.AllNotes[file[:-4]][items[0]] = items[1]
                    elif file.endswith(".json"):
                        if file[:-5] not in DataBase.AllNotes:
                            DataBase.AllNotes[file[:-5]] = {}
                        with open(DataBase.DataDir + r'/CSTI-JsonData/' + note_name + r'/' + file, "r", encoding='utf-8') as f:
                            data = json.load(f)
                            for key, item in data.items():
                                if type(item) == str:
                                    DataBase.AllNotes[file[:-5]][key] = item
                except Exception as ex:
                    QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))

    def loadGameSimpCn():
        try:
            if os.path.exists(DataBase.DataDir + r'/CSTI-JsonData/SimpCn.csv'):
                with open(DataBase.DataDir + r'/CSTI-JsonData/SimpCn.csv', "r", encoding='utf-8') as f:
                    lines = f.readlines(-1)
                    for line in lines:
                        keys = line.split(',')
                        if len(keys) > 3 and line.find('"') != -1:
                            new_keys = line.split('"')
                            if len(new_keys) == 3 and new_keys[0][-1] == ',' and  new_keys[2][0] == ',':
                                if new_keys[0][:-1] not in DataBase.AllSimpCn:
                                    DataBase.AllSimpCn[new_keys[0][:-1]] = {"original": new_keys[1].replace('"',''), "translate": new_keys[2][1:].replace("\n","")}
                                else:
                                    DataBase.AllSimpCn[new_keys[0][:-1]]["translate"] = new_keys[2][1:].replace("\n","")
                        elif len(keys) == 3:
                            if keys[0] not in DataBase.AllSimpCn:
                                DataBase.AllSimpCn[keys[0]] = {"original": keys[1].replace('"',''), "translate": keys[2].replace("\n","")}
                            else:
                                DataBase.AllSimpCn[keys[0]]["translate"] = keys[2].replace("\n","")
                        else:
                            QtCore.qWarning(bytes("Wrong Format Key" + line, encoding="utf-8"))
        except Exception as ex:
            QtCore.qWarning(bytes(traceback.format_exc(), encoding="utf-8"))

    # def loadTemplate():
    #     DataBase.AllTemplateBase = {}
    #     base_path = DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableJsonDataWithWarpLitAllInOne/"
    #     for dir in os.listdir(base_path):
    #         if os.path.isdir(base_path + r"/" + dir):
    #             if dir == "CardData":
    #                 for sub_dir in os.listdir(base_path + dir):
    #                     if os.path.isdir(base_path + r"/" + dir + r"/" + sub_dir):
    #                         for file in os.listdir(base_path + dir + r"/" + sub_dir):
    #                             if file.endswith(".json"):
    #                                 json.load(open(base_path + dir + r"/" + sub_dir + r"/" + file, "r", encoding='utf-8'))
    #             else:
    #                 for file in os.listdir(base_path + dir):
    #                     if file.endswith(".json"):
    #                         json.load(open(base_path + dir + r"/" + file, "r", encoding='utf-8'))
