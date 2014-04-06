import bonehead
from bonehead.ui import Page
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
import threading

class FrontDoorPlugin(bonehead.Plugin):
    def newPage(self, name, args, ui):
        return FrontDoorPage(args['sensor-id'], ui)

class FrontDoorPage(Page):
    def __init__(self, sensorID, ui):
        super(FrontDoorPage, self).__init__('Open/Close Space', ui)
        self.__sensor = self.spiff.getOne('sensor', sensorID)
        self.setStyleSheet("*{font-size:32pt}")
        self.layout = QtGui.QVBoxLayout(self)
        self.button = QtGui.QPushButton(self)
        self.text = QtGui.QLabel(self)
        self.text.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.button.clicked.connect(self.toggle)
        self.updateButton()

    def _runToggle(self):
        if str(self.__sensor.value) == "True":
            self.text.setText("Closing space...")
            self.__sensor.value = False
        else:
            self.text.setText("Opening space...")
            self.__sensor.value = True
        self.__sensor.save()
        self.updateButton()

    def toggle(self):
        t = threading.Thread(target=self._runToggle)
        t.start()

    def updateButton(self):
        self.__sensor.refresh()
        if str(self.__sensor.value) == "True":
            self.button.setStyleSheet("*{background-color: #f00;}")
            self.button.setText("Close Space")
            self.text.setText("Space is OPEN")
        else:
            self.button.setStyleSheet("*{background-color: #0f0;}")
            self.button.setText("Open Space")
            self.text.setText("Space is CLOSED")


