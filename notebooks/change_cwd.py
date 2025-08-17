import os
from pathlib import Path
# Get the path of the current script file
current_file = Path(globals().get('__vsc_ipynb_file__', None))
# Get the parent directory of the script's directory (one folder back)
parent_dir = current_file.parent.parent

print("Current file path:", current_file)
print("Parent directory:", parent_dir)

# If you want to change the working directory to that parent directory:
os.chdir(parent_dir)
print("Changed working directory to:", Path.cwd())
   