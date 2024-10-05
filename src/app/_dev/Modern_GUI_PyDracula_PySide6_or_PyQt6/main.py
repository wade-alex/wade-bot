# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python __scripts, any information in the visual
# interface (GUI) can be modified without any implication.
#
# There are limitations on Qt licenses if you want to use your products
# commercially, I recommend reading them on the official website:
# https://doc.qt.io/qtforpython/licenses.html
#
# ///////////////////////////////////////////////////////////////

import sys
import os
import plotly.graph_objects as go
import pandas as pd
import boto3
import pandas as pd
import io
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import json
import csv
from PySide6.QtWidgets import QTableWidgetItem
import subprocess
import warnings
warnings.filterwarnings("ignore")

# Function to get AWS credentials from Secrets Manager
def get_secret():
    secret_name = "wade-bot-s3"  # Your secret name
    region_name = "us-east-2"  # Your AWS region

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        # Retrieve the secret value
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        # Parse the secret string and return it as a dictionary
        secret = get_secret_value_response['SecretString']
        return json.loads(secret)

    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        raise e


# Retrieve the secrets from AWS Secrets Manager
secrets = get_secret()
aws_access_key_id = secrets['aws_access_key_id']
aws_secret_access_key = secrets['aws_secret_access_key']

# Initialize the S3 client using the credentials from Secrets Manager
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name="us-east-2"  # Ensure the region matches your S3 bucket
)

# Bucket and object information
bucket_name = 'wade-bot-scraper-dumps'
reg_fodder_graph_csv = 'Display/reg_fodder_graph.csv'

# Download the file from S3
response = s3.get_object(Bucket=bucket_name, Key=reg_fodder_graph_csv)

# Read the data into a pandas DataFrame
csv_data = response['Body'].read()
reg_fodder_graph_df = pd.read_csv(io.BytesIO(csv_data))
reg_fodder_graph_df = reg_fodder_graph_df.sort_values(by='rounded_date')



# IMPORT / GUI AND MODULES AND WIDGETS
# ///////////////////////////////////////////////////////////////
from modules import *
from widgets import *
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

# SET AS GLOBAL WIDGETS
# ///////////////////////////////////////////////////////////////
widgets = None

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.run_pre_boot()

        # Initialize UI components from Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)  # This sets up all widgets defined in the .ui file

        # Set global reference to the widgets
        global widgets
        widgets = self.ui

        # USE CUSTOM TITLE BAR | USE AS "False" FOR MAC OR LINUX
        # ///////////////////////////////////////////////////////////////
        Settings.ENABLE_CUSTOM_TITLE_BAR = True

        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "Cathedral"
        description = "Cathedral"
        # APPLY TEXTS
        self.setWindowTitle(title)
        # widgets.titleRightInfo.setText(description)

        # TOGGLE MENU
        # ///////////////////////////////////////////////////////////////
        widgets.toggleButton.clicked.connect(lambda: UIFunctions.toggleMenu(self, True))

        # SET UI DEFINITIONS
        # ///////////////////////////////////////////////////////////////
        UIFunctions.uiDefinitions(self)

        # QTableWidget PARAMETERS
        # ///////////////////////////////////////////////////////////////
        widgets.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # BUTTONS CLICK
        # ///////////////////////////////////////////////////////////////

        # LEFT MENUS
        widgets.btn_home.clicked.connect(self.buttonClick)
        widgets.btn_widgets.clicked.connect(self.buttonClick)
        widgets.btn_new.clicked.connect(self.buttonClick)
        widgets.btn_save.clicked.connect(self.buttonClick)

        # EXTRA LEFT BOX
        def openCloseLeftBox():
            UIFunctions.toggleLeftBox(self, True)
        widgets.toggleLeftBox.clicked.connect(openCloseLeftBox)
        widgets.extraCloseColumnBtn.clicked.connect(openCloseLeftBox)

        # EXTRA RIGHT BOX
        def openCloseRightBox():
            UIFunctions.toggleRightBox(self, True)
        widgets.settingsTopBtn.clicked.connect(openCloseRightBox)

        # SHOW APP
        # ///////////////////////////////////////////////////////////////
        self.show()

        # SET CUSTOM THEME
        # ///////////////////////////////////////////////////////////////
        useCustomTheme = False
        themeFile = "themes\py_dracula_light.qss"

        # SET THEME AND HACKS
        if useCustomTheme:
            # LOAD AND APPLY STYLE
            UIFunctions.theme(self, themeFile, True)

            # SET HACKS
            AppFunctions.setThemeHack(self)

        # SET HOME PAGE AND SELECT MENU
        # ///////////////////////////////////////////////////////////////
        widgets.stackedWidget.setCurrentWidget(widgets.home)
        widgets.btn_home.setStyleSheet(UIFunctions.selectMenu(widgets.btn_home.styleSheet()))

        # Load Chart in and display it
        self.gold_fodder_line_chart = self.ui.gold_fodder_line_chart
        self.display_plotly_gold_fodder()

        if self.gold_fodder_line_chart is None:
            print("Error: QWebEngineView 'gold_fodder_line_chart' not found!")
        else:
            print("QWebEngineView 'gold_fodder_line_chart' found successfully.")
            # Load the Plotly chart
            self.display_plotly_gold_fodder()

        self.gold_fodder_table_load()

    # BUTTONS CLICK
    # Post here your functions for clicked buttons
    # ///////////////////////////////////////////////////////////////
    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # SHOW HOME PAGE
        if btnName == "btn_home":
            widgets.stackedWidget.setCurrentWidget(widgets.home)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW WIDGETS PAGE
        if btnName == "btn_widgets":
            widgets.stackedWidget.setCurrentWidget(widgets.widgets)
            UIFunctions.resetStyle(self, btnName)
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet()))

        # SHOW NEW PAGE
        if btnName == "btn_new":
            widgets.stackedWidget.setCurrentWidget(widgets.new_page) # SET PAGE
            UIFunctions.resetStyle(self, btnName) # RESET ANOTHERS BUTTONS SELECTED
            btn.setStyleSheet(UIFunctions.selectMenu(btn.styleSheet())) # SELECT MENU

        if btnName == "btn_save":
            print("Save BTN clicked!")

        # PRINT BTN NAME
        print(f'Button "{btnName}" pressed!')


    # RESIZE EVENTS
    # ///////////////////////////////////////////////////////////////
    def resizeEvent(self, event):
        # Update Size Grips
        UIFunctions.resize_grips(self)

    # MOUSE CLICK EVENTS
    # ///////////////////////////////////////////////////////////////
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        self.dragPos = event.globalPos()

        # PRINT MOUSE EVENTS
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')

    def display_plotly_gold_fodder(self):
        # Variable to control the number of days to show initially
        show_x_days = 1  # Change this value to adjust the initial view

        reg_fodder_graph_df['rounded_date'] = pd.to_datetime(reg_fodder_graph_df['rounded_date'])

        # Calculate the date range
        last_day = reg_fodder_graph_df['rounded_date'].max()
        start_day = last_day - timedelta(days=show_x_days)

        default_visible_ratings = [84, 85, 87, 88]
        all_ratings = list(range(83, 92))  # Range from 83 to 91 inclusive

        # Create the Plotly chart with the time slider
        fig = go.Figure()

        # Define colors for the ratings (you can customize as needed)
        colors = {
            83: 'blue', 84: 'green', 85: 'red', 86: 'purple',
            87: 'orange', 88: 'pink', 89: 'yellow', 90: 'cyan', 91: 'gray'
        }

        # Adding a trace for each rating, showing specific ratings by default
        for rating in all_ratings:
            rating_df = reg_fodder_graph_df[reg_fodder_graph_df['rating'] == rating]

            # Check if this rating should be visible by default
            visible = True if rating in default_visible_ratings else 'legendonly'

            fig.add_trace(go.Scatter(
                x=rating_df['rounded_date'],
                y=rating_df['index'],
                mode='lines',
                name=f"Rating {rating}",
                line=dict(color=colors.get(rating, 'gray')),  # Default to gray if no color defined
                visible=visible
            ))

        # Customize layout
        fig.update_layout(
            title="Fodder Price Index with Time Slider",
            title_font=dict(color='white'),
            xaxis=dict(
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1d", step="day", stepmode="backward"),
                        dict(count=7, label="7d", step="day", stepmode="backward"),
                        dict(count=14, label="14d", step="day", stepmode="backward"),
                        dict(count=30, label="30d", step="day", stepmode="backward"),
                        dict(step="all", label="All")
                    ],
                    font=dict(color='black')  # Set button text color to black
                ),
                rangeslider=dict(visible=True),
                range=[start_day, last_day],  # Set default range based on show_x_days
                type="date",
                tickfont=dict(color='white'),
                title=dict(text="Time", font=dict(color='white'))
            ),
            yaxis=dict(
                range=[80, 120],  # Limit y-axis from 80 to 120
                tickfont=dict(color='white'),
                title=dict(text="Price Index", font=dict(color='white'))
            ),
            font=dict(color='white'),
            legend=dict(font=dict(color='white')),  # Legend for ratings
            paper_bgcolor='rgba(0,0,0,0)',  # Outer area (paper) background transparent
            plot_bgcolor='rgba(0,0,0,0)'  # Inner plot area background transparent
        )
        # Generate HTML content from the figure
        html_content = fig.to_html(include_plotlyjs='cdn')

        # Set HTML with transparent body and container
        transparent_html = f"""
        <html>
            <head>
                <style>
                    html, body {{
                        margin: 0;
                        padding: 0;
                        background-color: transparent; /* Ensure the window background is transparent */
                    }}
                    #chart-container {{
                        width: 100%;
                        height: 100%;
                        background-color: transparent; /* Container background is transparent */
                    }}
                </style>
            </head>
            <body>
                <div id="chart-container">
                    {html_content}
                </div>
            </body>
        </html>
        """

        # Load the HTML content into the QWebEngineView widget
        if self.gold_fodder_line_chart is not None:
            # Enable transparency in the QWebEngineView widget
            self.gold_fodder_line_chart.setAttribute(Qt.WA_TranslucentBackground, True)
            self.gold_fodder_line_chart.setStyleSheet("background: transparent;")
            self.gold_fodder_line_chart.page().setBackgroundColor(Qt.transparent)

            # Load the transparent HTML content
            self.gold_fodder_line_chart.setHtml(transparent_html)
            self.gold_fodder_line_chart.update()  # Forces a repaint to ensure the view is refreshed
        else:
            print("Error: QWebEngineView 'gold_fodder_line_chart' not found!")

    def gold_fodder_table_load(self):
        # S3 bucket and file information
        bucket_name = 'wade-bot-scraper-dumps'
        file_key = 'Display/reg_fodder_table.csv'

        try:
            # Download the CSV file from S3
            response = s3.get_object(Bucket=bucket_name, Key=file_key)
            csv_content = response['Body'].read().decode('utf-8')

            # Parse CSV content
            csv_data = csv.reader(io.StringIO(csv_content))
            original_headers = next(csv_data)  # Get the original headers

            # Define custom headers (modify these as needed)
            custom_headers = [
                "Rating",
                "1 Day",
                "3 Days",
                "7 Days",
                "7-14 Days"
            ]

            # Ensure we have the correct number of custom headers
            if len(custom_headers) != len(original_headers):
                print("Warning: Number of custom headers doesn't match CSV headers.")
                custom_headers = original_headers  # Fallback to original headers

            # Set up the table
            self.ui.golder_fodder_table.setColumnCount(len(custom_headers))
            self.ui.golder_fodder_table.setHorizontalHeaderLabels(custom_headers)

            # Hide the vertical header (row numbers)
            self.ui.golder_fodder_table.verticalHeader().setVisible(False)

            # Populate the table
            for row, row_data in enumerate(csv_data):
                self.ui.golder_fodder_table.insertRow(row)
                for col, cell_data in enumerate(row_data):
                    if col == 0:  # Rating column
                        item = QTableWidgetItem(cell_data)
                    else:  # Other columns
                        try:
                            # Convert to float, round to 0 decimal places, format with commas
                            formatted_value = "{:,}".format(round(float(cell_data)))
                            item = QTableWidgetItem(formatted_value)
                        except ValueError:
                            # If conversion fails, use the original value
                            item = QTableWidgetItem(cell_data)
                    self.ui.golder_fodder_table.setItem(row, col, item)

            # Resize columns to content
            self.ui.golder_fodder_table.resizeColumnsToContents()

            print("Gold fodder table loaded successfully.")
        except Exception as e:
            print(f"Error loading gold fodder table: {str(e)}")

    def run_pre_boot(self):
        try:
            # Get the directory of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # Navigate to the project root (assuming the current file is in src/app/_dev/Modern_GUI_PyDracula_PySide6_or_PyQt6/)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))

            # Construct the path to pre_boot.py
            pre_boot_path = os.path.join(project_root, "src", "app", "__scripts", "pre_boot.py")

            print(f"Attempting to run pre_boot.py from: {pre_boot_path}")

            # Check if the file exists
            if not os.path.exists(pre_boot_path):
                raise FileNotFoundError(f"pre_boot.py not found at {pre_boot_path}")

            # Use the same Python interpreter that's running the current script
            python_executable = sys.executable

            # Run pre_boot.py
            result = subprocess.run([python_executable, pre_boot_path], check=True, capture_output=True, text=True)
            print("Successfully executed pre_boot.py")
            print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing pre_boot.py: {e}")
            print("Standard Output:", e.stdout)
            print("Standard Error:", e.stderr)
        except FileNotFoundError as e:
            print(e)
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("w-logo.png"))
    window = MainWindow()
    sys.exit(app.exec_())

