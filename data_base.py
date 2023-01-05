# -*- coding: utf-8 -*- 
import json
import sys
import os

class DataBase(object):
    DataDir = None
    RefNameList = ["ActionTag", "AudioClip", "CardTag", "EquipmentTag", "EndgameLogCategory", "Sprite"]
    RefGuidList = ["CardData", "CharacterPerk", "GameSourceModify", "GameStat", "Objective", "SelfTriggeredAction"]

    AllEnum = {}
    AllEnumRev = {}
    AllTypeField = {}

    AllRef = {}             # DataBase.AllRef["ActionTag"] -> list[Ref]              DataBase.AllRef["CardData"]["Item"] -> list[Guid]
    AllGuid = {}            # DataBase.AllGuid["GameStat"][Ref] -> Guid              DataBase.AllGuid["CardData"]["Item"][Ref] -> Guid
    AllGuidPlain = {}       # DataBase.AllGuidPlain[Ref] -> Guid
    AllGuidPlainRev = {}    # DataBase.AllGuidPlainRev[Guid] -> Ref
    AllCardData = {}        # DataBase.AllCardData[Ref] -> CardData Guid
    AllPath = {}            # DataBase.AllPath["GameStat"] [Ref] -> FilePath
    AllScriptableObject = {}   # DataBase.AllScriptableObject[Ref] -> Guid or Ref
    AllCollection = {}      # DataBase.AllCollection["CardsDropCollection"][Name] -> json data


    def __init__(self):
        pass

    def loadDataBase(data_dir):
        DataBase.DataDir = data_dir

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

        # Load Collection
        DataBase.loadCollection()

    def LoadModData(mod_name, mod_dir):
        DataBase.AllRef = {}            # DataBase.AllRef["ActionTag"] -> list[Ref]             DataBase.AllRef["CardData"]["Item"] -> list[Guid]
        DataBase.AllGuid = {}           # DataBase.AllGuid["GameStat"][Ref] -> Guid        DataBase.AllGuid["CardData"]["Item"][Ref] -> Guid
        DataBase.AllGuidPlain = {}      # DataBase.AllGuidPlain[Ref] -> Guid
        DataBase.AllGuidPlainRev = {}   # DataBase.AllGuidPlainRev[Guid] -> Ref
        DataBase.AllCardData = {}       # DataBase.AllCardData[Ref] -> CardData Guid
        DataBase.AllPath = {}           # DataBase.AllPath["GameStat"] [Ref] -> FilePath
        DataBase.AllScriptableObject = {}   # DataBase.AllScriptableObject[Ref] -> Guid or Ref

        DataBase.AllRef.update(DataBase.AllRefBase)
        DataBase.AllGuid.update(DataBase.AllGuidBase)
        DataBase.AllGuidPlain.update(DataBase.AllGuidPlainBase)
        DataBase.AllCardData.update(DataBase.AllCardDataBase)
        DataBase.AllPath.update(DataBase.AllPathBase)
        DataBase.AllScriptableObject.update(DataBase.AllScriptableObjectBase)

        DataBase.AllRef["CardData"]["Mod"] = []

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
                            elif dir == "GameSourceModify":
                                pass
                            else:
                                DataBase.AllRef[dir].append(ref)
                                DataBase.AllGuid[dir].update({ref : data["UniqueID"]})
                                DataBase.AllGuidPlain.update({ref : data["UniqueID"]})
                                DataBase.AllPath[dir].update({ref : mod_dir + r"/" + dir + r"/" + file})
                                DataBase.AllScriptableObject.update({ref : data["UniqueID"]})



        DataBase.AllGuidPlainRev = {v : k for k, v in DataBase.AllGuidPlain.items()}

        # print("1010f586b0571af4bac35f48ed42e05f" in  DataBase.AllGuidPlainRev)
        # print("LocalizedString" in  DataBase.AllTypeField)

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

    def loadCollection():
        if os.path.exists(DataBase.DataDir + r"/Mods/" + r"Collection.json"):
            with open(DataBase.DataDir + r"/Mods/" + r"Collection.json", "r", encoding='utf-8') as f:
                DataBase.AllCollection = json.load(f)

    def saveCollection():
        with open(DataBase.DataDir + r"/Mods/" + r"Collection.json", "w", encoding='utf-8') as f:
            json.dump(DataBase.AllCollection, f)


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
