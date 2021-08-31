import sys
import cv2 as cv
import PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QRadioButton, QVBoxLayout, QWidget

app = QApplication([])
win = QMainWindow()

central_widget = QWidget()

layout = QVBoxLayout(central_widget)

buttons = {}

retVal = ""

def btnState(dataIndex):
    global retVal
    for x in range(dataIndex):
        if buttons[x].isChecked():
            print(buttons[x].text() + " is selected")
            retVal = buttons[x].text(); 


def trackSelectionPopup(goodTracks, dataIndex):
    for i in range(dataIndex):
        buttons[i] = QRadioButton(goodTracks[i].get("track_name"))
        buttons[i].toggled.connect(lambda: btnState(dataIndex))
        layout.addWidget(buttons[i], i)

    win.setCentralWidget(central_widget)
    win.show()

    app.exit(app.exec_())

    for i in range(dataIndex):
        buttons[i].setHidden(True)

    return retVal