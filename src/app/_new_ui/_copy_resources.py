import os
import subprocess

# Paths
qrc_file = '/Users/alexwade/Documents/GitHub/wade-bot/src/app/_dev/Modern_GUI_PyDracula_PySide6_or_PyQt6/resources.qrc'
new_ui_folder = '/Users/alexwade/Documents/GitHub/wade-bot/src/app/_dev/_new_ui'
output_python_file = os.path.join(new_ui_folder, 'resources_rc.py')

# Check if the target folder exists, if not, create it
if not os.path.exists(new_ui_folder):
    os.makedirs(new_ui_folder)
    print(f"Created new folder: {new_ui_folder}")

# Run pyside6-rcc to convert the .qrc file to a Python file
subprocess.run(["pyside6-rcc", qrc_file, "-o", output_python_file])

# Check if the Python file was created
if os.path.exists(output_python_file):
    print(f"Successfully converted {qrc_file} to {output_python_file}")
else:
    print(f"Failed to convert {qrc_file}")