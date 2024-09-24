# ///////////////////////////////////////////////////////////////
#
# BY: WANDERSON M.PIMENTA
# PROJECT MADE WITH: Qt Designer and PySide6
# V: 1.0.0
#
# This project can be used freely for all uses, as long as they maintain the
# respective credits only in the Python scripts, any information in the visual
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
        widgets.titleRightInfo.setText(description)

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
        self.test_chart = self.ui.test_chart
        self.display_plotly_chart()

        if self.test_chart is None:
            print("Error: QWebEngineView 'test_chart' not found!")
        else:
            print("QWebEngineView 'test_chart' found successfully.")
            # Load the Plotly chart
            self.display_plotly_chart()

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

    def display_plotly_chart(self):
        # Create the Plotly chart with a time slider
        time = pd.date_range("2023-01-01", periods=100, freq='D')
        line1 = [i + 10 for i in range(100)]
        line2 = [i + 20 for i in range(100)]
        line3 = [i + 30 for i in range(100)]

        # Create the figure with three different lines
        fig = go.Figure()

        # Line 1
        fig.add_trace(go.Scatter(x=time, y=line1, mode='lines', name="Line 1"))
        # Line 2
        fig.add_trace(go.Scatter(x=time, y=line2, mode='lines', name="Line 2"))
        # Line 3
        fig.add_trace(go.Scatter(x=time, y=line3, mode='lines', name="Line 3"))

        # Add time slider
        fig.update_layout(
            title="Test Chart with Time Slider",
            title_font=dict(color='white'),  # Set title font color to white
            xaxis=dict(
                rangeselector=dict(
                    buttons=[
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(step="all")
                    ]
                ),
                rangeslider=dict(visible=True),
                type="date",
                tickfont=dict(color='white'),  # Set x-axis tick labels to white
                title=dict(text="Time", font=dict(color='white'))  # Set x-axis title to white
            ),
            yaxis=dict(
                tickfont=dict(color='white'),  # Set y-axis tick labels to white
                title=dict(text="Values", font=dict(color='white'))  # Set y-axis title to white
            ),
            font=dict(color='white'),  # Set the default font color to white for all elements
            legend=dict(font=dict(color='white')),  # Set legend font color to white
            paper_bgcolor='rgba(0,0,0,0)'  # Outer area (paper) background transparent
            # plot_bgcolor='rgba(0,0,0,0)'  # Inner plot area background transparent
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
        if self.test_chart is not None:
            # Enable transparency in the QWebEngineView widget
            self.test_chart.setAttribute(Qt.WA_TranslucentBackground, True)
            self.test_chart.setStyleSheet("background: transparent;")
            self.test_chart.page().setBackgroundColor(Qt.transparent)

            # Load the transparent HTML content
            self.test_chart.setHtml(transparent_html)
            self.test_chart.update()  # Forces a repaint to ensure the view is refreshed
        else:
            print("Error: QWebEngineView 'test_chart' not found!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("w-logo.png"))
    window = MainWindow()
    sys.exit(app.exec_())

