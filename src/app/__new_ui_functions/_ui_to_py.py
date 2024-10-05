import os
import subprocess
import fileinput
import sys

# Get the current script's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Navigate to the project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

# Paths
ui_file = os.path.join(project_root, 'src', 'app', '_dev', 'Modern_GUI_PyDracula_PySide6_or_PyQt6', 'main.ui')
new_ui_folder = os.path.join(project_root, 'src', 'app', '_dev', '__new_ui_functions')
output_python_file = os.path.join(new_ui_folder, 'ui_main.py')

# Check if the target folder exists, if not, create it
if not os.path.exists(new_ui_folder):
    os.makedirs(new_ui_folder)
    print(f"Created new folder: {new_ui_folder}")

# Check if the UI file exists
if not os.path.exists(ui_file):
    print(f"Error: UI file not found at {ui_file}")
    sys.exit(1)

# Convert the .ui file to a Python file using pyside6-uic
try:
    subprocess.run(["pyside6-uic", ui_file, "-o", output_python_file], check=True)
    print(f"Successfully converted {ui_file} to {output_python_file}")
except subprocess.CalledProcessError as e:
    print(f"Error converting UI file: {e}")
    sys.exit(1)

# Function to replace 'import resources_rc' with 'from . import resources_rc'
def replace_resources_import():
    with fileinput.FileInput(output_python_file, inplace=True, backup='.bak') as file:
        for line in file:
            if line.strip() == "import resources_rc":
                print("from . import resources_rc", end='\n')
            else:
                print(line, end='')
    print(f"Replaced 'import resources_rc' with 'from . import resources_rc' in {output_python_file}")

# Function to replace incorrect font weight setting with setBold(False)
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
    # Call the functions to modify the generated Python file
    replace_resources_import()
    replace_font_weight()
else:
    print(f"Failed to convert {ui_file}")

print(f"Current working directory: {os.getcwd()}")
print(f"UI file path: {ui_file}")
print(f"Output Python file path: {output_python_file}")