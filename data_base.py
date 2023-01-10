# -*- coding: utf-8 -*- 
import json
import sys
import os
import copy

class DataBase(object):
    DataDir = None
    RefNameList = ["ActionTag", "AudioClip", "CardTag", "EquipmentTag", "EndgameLogCategory", "Sprite", "WeatherSet"]
    RefGuidList = ["CardData", "CharacterPerk", "GameStat", "Objective", "SelfTriggeredAction"]
    SupportList = ["CardData", "CharacterPerk", "GameSourceModify", "GameStat", "Objective", "SelfTriggeredAction"]

    AllSpecialTypeField = {}
    AllSpecialTypeField["CardData"] = ["BlueprintCardDataCardTabGroup", "BlueprintCardDataCardTabSubGroup"]
    AllSpecialTypeField["CharacterPerk"] = ["CharacterPerkPerkGroup"]
    AllSpecialTypeField["GameStat"] = ["VisibleGameStatStatListTab"]

    AllBlueprintTab = []
    AllBlueprintSubTab = []

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
    AllNotes = {}           # DataBase.AllNotes["CardData"]["CardName"] -> Note


    def __init__(self):
        pass

    def loadDataBase(data_dir):
        DataBase.DataDir = data_dir

        if not os.path.exists(DataBase.DataDir + "/Mods"):
            os.mkdir(DataBase.DataDir + "/Mods")

        # Load Name
        DataBase.loadName()

        # Load GUID
        DataBase.loadGuid()

        # Load Path
        DataBase.loadPath()

        # Load UniqueIDScriptable FieldName FieldType
        DataBase.loadUniqueIDScriptableField()

        # Load Template
        # DataBase.loadTemplate()

        # Load SpecialTypeField
        DataBase.loadSpecialTypeField()

        # Load Collection
        DataBase.loadCollection()

        # Load Note
        DataBase.loadNote()

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
        
        DataBase.AllModSimpCn = {}

        for dir in os.listdir(mod_dir):
            if os.path.isdir(mod_dir + r"/" + dir):
                if dir in DataBase.RefGuidList:
                    for file in os.listdir(mod_dir + r"/" + dir):
                        if file.endswith(".json"):
                            with open(mod_dir + r"/" + dir + r"/" + file, "r") as f:
                                data = json.load(f)
                            ref = mod_name + "_" + file[:-5]
                            if dir == "CardData":
                                DataBase.AllRef[dir]["Mod"].append(ref)
                                DataBase.AllGuid[dir].update({ref : data["UniqueID"]})
                                DataBase.AllGuidPlain.update({ref : data["UniqueID"]})
                                DataBase.AllCardData.update({ref : data["UniqueID"]})
                                DataBase.AllPath[dir].update({ref : mod_dir + r"/" + dir + r"/" + file})
                                DataBase.AllScriptableObject.update({ref : data["UniqueID"]})
                            else:
                                DataBase.AllRef[dir].append(ref)
                                DataBase.AllGuid[dir].update({ref : data["UniqueID"]})
                                DataBase.AllGuidPlain.update({ref : data["UniqueID"]})
                                DataBase.AllPath[dir].update({ref : mod_dir + r"/" + dir + r"/" + file})
                                DataBase.AllScriptableObject.update({ref : data["UniqueID"]})
                elif dir == "GameSourceModify":
                    pass
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
                                    print("Wrong Format Key")
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

        for file in os.listdir(DataBase.DataDir + r"/CSTI-JsonData/ScriptableObjectObjectName/"):
            if file.endswith(".txt"):
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


    def loadGuid():
        DataBase.AllGuidBase = {}  # Type: {Key: Guid}
        DataBase.AllGuidPlainBase = {}
        DataBase.AllCardDataBase = {}  # Key: Guid

        for file in os.listdir(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableGUID/"):
            if file.endswith(".json"):
                with open(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableGUID/" + file, encoding='utf-8') as f:
                    temp = json.loads(f.read(-1))
                    DataBase.AllRefBase[file[:-5]] = list(temp.keys())
                    DataBase.AllGuidBase[file[:-5]] = temp
                    DataBase.AllGuidPlainBase.update(temp)
                    DataBase.AllScriptableObjectBase.update(temp)

        DataBase.AllRefBase["CardData"] = {}
        DataBase.AllGuidBase["CardData"] = {}
        for file in os.listdir(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableGUID/CardData/"):
            if file.endswith(".json"):
                with open(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableGUID/CardData/" + file, encoding='utf-8') as f:
                    temp = json.loads(f.read(-1))
                    DataBase.AllCardDataBase.update(temp)
                    DataBase.AllGuidBase["CardData"][file[:-5]] = temp
                    DataBase.AllRefBase["CardData"][file[:-5]] = list(temp.keys())
                    DataBase.AllGuidPlainBase.update(temp)
                    DataBase.AllScriptableObjectBase.update(temp)

        # print(DataBase.AllGuidPlainBase.keys())

    def loadPath():
        DataBase.AllPathBase = {}  # Type: {Key: Path}
        base_path = DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableJsonDataWithWarpLitAllInOne/"
        for dir in os.listdir(base_path):
            if os.path.isdir(base_path + r"/" + dir):
                DataBase.AllPathBase[dir] = {}
                if dir == "CardData":
                    for sub_dir in os.listdir(base_path + dir):
                        if os.path.isdir(base_path + r"/" + dir + r"/" + sub_dir):
                            for file in os.listdir(base_path + dir + r"/" + sub_dir):
                                if file.endswith(".json"):
                                    DataBase.AllPathBase[dir][file[:-5]] = base_path + dir + r"/" + sub_dir + r"/" + file
                else:
                    for file in os.listdir(base_path + dir):
                        if file.endswith(".json"):
                            DataBase.AllPathBase[dir][file[:-5]] = base_path + dir + r"/" + file

    def loadUniqueIDScriptableField():
        files = os.listdir(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableTypeJsonData")
        for file in files:
            if file.endswith(".json"):
                with open(DataBase.DataDir + r'/CSTI-JsonData/UniqueIDScriptableTypeJsonData/' + file, encoding='utf-8') as f:
                    try:
                        DataBase.AllTypeField[file[:-5]] = json.loads(f.read(-1))
                    except Exception as ex:
                        pass

        files = os.listdir(DataBase.DataDir + r"/CSTI-JsonData/UniqueIDScriptableTypeJsonData/EnumType")
        for file in files:
            if file.endswith(".json"):
                with open(DataBase.DataDir + r'/CSTI-JsonData/UniqueIDScriptableTypeJsonData/EnumType/' + file, encoding='utf-8') as f:
                    try:
                        DataBase.AllEnum[file[:-5]] = json.loads(f.read(-1))
                    except Exception as ex:
                        pass
        
        for key, item in DataBase.AllEnum.items():
            DataBase.AllEnumRev[key] = {v : k for k, v in DataBase.AllEnum[key].items()}

    def loadSpecialTypeField():
        for key, item_list in DataBase.AllSpecialTypeField.items():
            if key in DataBase.AllTypeField:
                for item in item_list:
                    DataBase.AllTypeField[key][item] = "Special"

    def loadCollection():
        if os.path.exists(DataBase.DataDir + r"/Mods/" + r"Collection.json"):
            with open(DataBase.DataDir + r"/Mods/" + r"Collection.json", "r", encoding='utf-8') as f:
                DataBase.AllCollection = json.load(f)

    def saveCollection():
        with open(DataBase.DataDir + r"/Mods/" + r"Collection.json", "w", encoding='utf-8') as f:
            json.dump(DataBase.AllCollection, f)

    def loopLoadModSimpCn(json, mod_name):
        if type(json) is dict:
            for key, item in json.items():
                if key == "LocalizationKey" and type(item) == str and item.startswith(mod_name) and item not in DataBase.AllModSimpCn:
                    if "DefaultText" in json:
                        DataBase.AllModSimpCn[item] = {"original": json["DefaultText"], "translate": ""}
                if type(item) == list:
                    for sub_item in item:
                        DataBase.loopLoadModSimpCn(sub_item, mod_name)
                if type(item) == dict:
                    DataBase.loopLoadModSimpCn(item, mod_name)

    def loadModSimpCn(mod_dir):
        for dir in os.listdir(mod_dir):
            if os.path.isdir(mod_dir + r"/" + dir):
                if dir == "Localization":
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
                                    print("Wrong Format Key")
        
    def saveModSimpCn(mod_dir):
        DataBase.loadModSimpCn(mod_dir)
        with open(mod_dir + r"/Localization/SimpCn.csv", "w", encoding='utf-8') as f:
            for key in DataBase.AllModSimpCn:
                f.write(key)
                f.write(',"')
                f.write(DataBase.AllModSimpCn[key]["original"].replace("\n", "\\n").replace("\t", "\\t"))
                f.write('",')
                f.write(DataBase.AllModSimpCn[key]["translate"].replace("\n", "\\n").replace("\t", "\\t"))
                f.write('\n')

    def loadNote():
        if os.path.exists(DataBase.DataDir + r'/CSTI-JsonData/Notes'):
            for file in os.listdir(DataBase.DataDir + r'/CSTI-JsonData/Notes'):
                if file.endswith(".txt"):
                    DataBase.AllNotes[file[:-4]] = {}
                    with open(DataBase.DataDir + r'/CSTI-JsonData/Notes/' + file, "r", encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines:
                            line = line.replace("\n", "")
                            items = line.split("\t")
                            if len(items) == 2:
                                DataBase.AllNotes[file[:-4]][items[0]] = items[1]

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
    #                                 json.load(open(base_path + dir + r"/" + sub_dir + r"/" + file, "r"))
    #             else:
    #                 for file in os.listdir(base_path + dir):
    #                     if file.endswith(".json"):
    #                         json.load(open(base_path + dir + r"/" + file, "r"))
