import os
import subprocess
import fileinput
import sys

# Remember to paste from . resources_rc import * at the beginning of new ui.py
# Paths
ui_file = '/Users/alexwade/Documents/GitHub/wade-bot/src/app/_dev/Modern_GUI_PyDracula_PySide6_or_PyQt6/main.ui'
new_ui_folder = '/Users/alexwade/Documents/GitHub/wade-bot/src/app/_dev/__new_ui_functions'
output_python_file = os.path.join(new_ui_folder, 'ui_main.py')

# Check if the target folder exists, if not, create it
if not os.path.exists(new_ui_folder):
    os.makedirs(new_ui_folder)
    print(f"Created new folder: {new_ui_folder}")

# Run pyside6-uic to convert the .ui file to a Python file
subprocess.run(["pyside6-uic", ui_file, "-o", output_python_file])


def replace_resources_import():
    with fileinput.FileInput(output_python_file, inplace=True, backup='.bak') as file:
        for line in file:
            if line.strip() == "import resources_rc":
                print("from . import resources_rc", end='\n')
            else:
                print(line, end='')
    print(f"Replaced 'import resources_rc' with 'from . import resources_rc' in {output_python_file}")


def replace_font_weight():
    with fileinput.FileInput(output_python_file, inplace=True, backup='.bak') as file:
        for line in file:
            if "font1.setWeight(QFont.)" in line:
                print(line.replace("font1.setWeight(QFont.)", "font1.setBold(False)"), end='')
            else:
                print(line, end='')
    print(f"Replaced 'font1.setWeight(QFont.)' with 'font1.setBold(False)' in {output_python_file}")


# Check if the Python file was created
if os.path.exists(output_python_file):
    print(f"Successfully converted {ui_file} to {output_python_file}")

    # Call the new functions here
    replace_resources_import()
    replace_font_weight()
else:
    print(f"Failed to convert {ui_file}")