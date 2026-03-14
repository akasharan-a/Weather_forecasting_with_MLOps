from importlib.metadata import version
import json
import yaml
from pathlib import Path
import shutil


def get_versions(packages :list):
    versions = [f"{pkg}=={version(pkg)}" for pkg in packages]
    return versions

def save_as_json(dictionary,path):
    with open(path, "w") as json_file:
        json.dump(dictionary, json_file, indent=4)  # indent for pretty printing

def read_yaml(path):
    with open(path, "r") as yaml_file:
        dictionary = yaml.safe_load(yaml_file) 
    return dictionary

def save_as_yaml(dictionary,path):
    with open(path, "w") as yaml_file:
        yaml.dump(dictionary, yaml_file) 

def create_folder(folder:Path):
    try:
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir()    
        return True
    except:
        return False
    