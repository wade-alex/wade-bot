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

# Downloading data from S3 to use in charts
# Initialize a session using Boto3
s3 = boto3.client(
    's3',
    aws_access_key_id='AKIA5MSUBXIYQH6JNS4X',
    aws_secret_access_key='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'
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
        reg_fodder_graph_df['rounded_date'] = pd.to_datetime(reg_fodder_graph_df['rounded_date'])
        # Step 2: Filter the data to show only the last 7 days by default
        last_7_days = reg_fodder_graph_df['rounded_date'].max() - timedelta(days=7)
        last_14_days = reg_fodder_graph_df['rounded_date'].max() - timedelta(days=14)

        default_visible_ratings = [84, 85, 87, 88]
        all_ratings = list(range(83, 92))  # Range from 83 to 91 inclusive
        # Step 3: Create the Plotly chart with the time slider
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

        # Step 4: Customize layout
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
                range=[last_7_days, reg_fodder_graph_df['rounded_date'].max()],  # Set default range to last 7 days
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("w-logo.png"))
    window = MainWindow()
    sys.exit(app.exec_())

