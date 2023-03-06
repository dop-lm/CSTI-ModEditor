# -*- coding: utf-8 -*- 

import ujson as json
import re
import os
import shutil
import traceback
from glob import glob

pattern_number = ''': [1-9]'''
pattern_decimal = ''': 0.0*[1-9]{1,}.*?,'''
pattern_true = ''': true'''
pattern_no_empty_string = "': '[^']"
pattern_negative = ''': -'''
pattern_FileID = '''m_FileID'''

def exportToZip(dir: str, mod_info: dict):
    try:
        temp_dir = dir + "_temp~"
        if os.path.isdir(dir):
            shutil.copytree(dir, temp_dir + "/" + mod_info["Name"], ignore=shutil.ignore_patterns(".git"))
            files = [y for x in os.walk(temp_dir) for y in glob(os.path.join(x[0], '*.json'))]
            for file in files:
                if file.endswith("ModInfo.json"):
                    continue
                else:
                    with open(file, "r") as f:
                        json_data = json.load(f)
                        toJsonMinimalism(json_data)
                    with open(file, "w") as f:
                        json.dump(json_data, f)
            zipname = os.path.split(temp_dir)[0] + "/%s-%s-ModLoader%s" % (mod_info["Name"], mod_info["Version"], mod_info["ModLoaderVerison"])
            shutil.make_archive(zipname, 'zip', temp_dir)
            shutil.rmtree(temp_dir)
    except Exception as ex:
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
        print(traceback.format_exc())

def toJsonMinimalism(json_data):
    if type(json_data) == dict:
        for key in list(json_data.keys()): 
            if type(json_data[key]) == dict:
                toJsonMinimalism(json_data[key])
            elif type(json_data[key]) == list:
                for i in  reversed(range(len(json_data[key]))):
                    if type(json_data[key][i]) == dict:
                        toJsonMinimalism(json_data[key][i])
            else:
                if key == "m_FileID" or key == "m_PathID":
                    continue
                if type(json_data[key]) == float and json_data[key] == 0.0:
                    del json_data[key]
                elif type(json_data[key]) == int and json_data[key] == 0:
                    del json_data[key]
                elif type(json_data[key]) == bool and json_data[key] == False:
                    del json_data[key]
                elif type(json_data[key]) == str and json_data[key] == "":
                    # del json_data[key]
                    pass

    else:
        print("toJsonMinimalism unexpect")

# def toJsonMinimalism(json_data):
#     if type(json_data) == dict:
#         for key in list(json_data.keys()): 
#             if type(json_data[key]) == dict:
#                 str_data = str(json_data[key])
#                 if re.search(pattern_number, str_data) or re.search(pattern_decimal, str_data) or re.search(pattern_true, str_data) or \
#                     re.search(pattern_no_empty_string, str_data) or re.search(pattern_negative, str_data) or re.search(pattern_FileID, str_data):
#                     toJsonMinimalism(json_data[key])
#                 else:
#                     del json_data[key]
#             elif type(json_data[key]) == list:
#                 for i in  reversed(range(len(json_data[key]))):
#                     if type(json_data[key][i]) == dict:
#                         toJsonMinimalism(json_data[key][i])
#             else:
#                 if key == "m_FileID" or key == "m_PathID":
#                     continue
#                 if type(json_data[key]) == float and json_data[key] == 0.0:
#                     del json_data[key]
#                 elif type(json_data[key]) == int and json_data[key] == 0:
#                     del json_data[key]
#                 elif type(json_data[key]) == bool and json_data[key] == False:
#                     del json_data[key]
#                 elif type(json_data[key]) == str and json_data[key] == "":
#                     del json_data[key]

#     else:
#         print("toJsonMinimalism unexpect")

# exportToZip("C:\Software\Steam\steamapps\common\Card Survival Tropical Island\BepInEx\DynamicModDebug\BambooTech", {"Name": "BambooTech", "Version": "1.0.2", "ModLoaderVerison": "1.1.5"})