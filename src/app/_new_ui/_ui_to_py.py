import os
import subprocess

# Remember to paste from . resources_rc import * at the beginning of new ui.py

# Paths
ui_file = '/Users/alexwade/Documents/GitHub/wade-bot/src/app/_dev/Modern_GUI_PyDracula_PySide6_or_PyQt6/main.ui'
new_ui_folder = '/Users/alexwade/Documents/GitHub/wade-bot/src/app/_dev/_new_ui'
output_python_file = os.path.join(new_ui_folder, 'ui_main.py')

# Check if the target folder exists, if not, create it
if not os.path.exists(new_ui_folder):
    os.makedirs(new_ui_folder)
    print(f"Created new folder: {new_ui_folder}")

# Run pyside6-uic to convert the .ui file to a Python file
subprocess.run(["pyside6-uic", ui_file, "-o", output_python_file])

# Check if the Python file was created
if os.path.exists(output_python_file):
    print(f"Successfully converted {ui_file} to {output_python_file}")
else:
    print(f"Failed to convert {ui_file}")