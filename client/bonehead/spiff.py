import spiff
from bonehead import Plugin
from bonehead.ui import Page
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork

class OpenClosePlugin(Plugin):
    def newPage(self, name, args, ui):
        api = spiff.API(args['url'], verify=False)
        return OpenClosePage(api.sensor(args['sensor-id']), ui)

class OpenClosePage(Page):
    def __init__(self, sensor, parent=None):
        super(OpenClosePage, self).__init__('Open/Close Space', parent)
        self.__sensor = sensor
        self.setStyleSheet("*{font-size:32pt}")
        self.layout = QtGui.QVBoxLayout(self)
        self.button = QtGui.QPushButton(self)
        self.text = QtGui.QLabel(self)
        self.text.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.toggle)
        self.updateButton()

    def toggle(self):
        if self.__sensor.value == True:
            self.__sensor.setValue(False)
        else:
            self.__sensor.setValue(True)
        self.updateButton()

    def updateButton(self):
        if self.__sensor.value == True:
            self.button.setStyleSheet("*{background-color: #f00;}")
            self.button.setText("Close Space")
            self.text.setText("Space is OPEN")
        else:
            self.button.setStyleSheet("*{background-color: #0f0;}")
            self.button.setText("Open Space")
            self.text.setText("Space is CLOSED")

