import json
from schemas.module import ModuleCreate
from app import crud

f = open("./db/modules.json")
response =  json.load(f)
data = response['module_list']


for header in data:
    header["module_name"]
    header["display_name"]
    # crud.crud_module.ModuleCreate()
    for menu in header["sub_menu"]:
        print(menu)
