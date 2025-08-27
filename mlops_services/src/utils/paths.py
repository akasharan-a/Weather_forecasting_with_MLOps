import os
from pathlib import Path

def feast_path(path):
    data_path =  path[:]
    parts = data_path.split(os.sep)
    new_path = os.sep.join(parts[1:])
    return new_path