from PyQt5 import QtGui, QtWidgets, QtCore
from enum import Enum

from CustomPinWidget import CustomPinWidget
from GroundPinWidget import GroundPinWidget
from LEDPinWidget import LEDPinWidget
from TemperaturePinWidget import TemperaturePinWidget
from ModuleVersionFeatures import module_version_features

class PinType(Enum):
    Custom = 0
    Ground = 1
    LED = 2
    Temperature = 3

class PinWidget(QtWidgets.QFrame):
    def __init__(self, parent, pin_num, version, appctxt):
        super(QtWidgets.QFrame, self).__init__()
        self.parent = parent
        self.appctxt = appctxt
        
        self.pin_num = pin_num
        self.version = version
        self.total_pins = module_version_features[version]['pins']
        self.voltage = module_version_features[version]['voltage']
        self.resolution = module_version_features[version]['resolution']

        self.setup()

    def press_pin_button(self, value):
        print(f'Pin {self.pin_num} {value.name} pressed')
        self.pin_type = value
        for mode in PinType:
            if self.pin_buttons[mode.value].isChecked():
                self.pin_widgets[mode].hide()
                self.pin_widgets[mode].deactivate()
            self.pin_buttons[mode.value].setChecked(False)
        self.pin_buttons[value.value].setChecked(True)
        self.pin_widgets[value].show()
        self.pin_widgets[value].activate()

    def setup(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        # self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)
        
        self.button_group_box = QtWidgets.QGroupBox(f'Pin {self.pin_num + 1} - Mode Selection')
        self.button_group_box.setStyleSheet('QGroupBox {font-weight: bold;}')
        self.button_layout = QtWidgets.QHBoxLayout()
        self.pin_buttons = []
        for mode in PinType:
            button = QtWidgets.QToolButton(self)
            button.setIcon(QtGui.QIcon(self.appctxt.get_resource(f'Pin_Icons/Pin_{mode.name}.png')))
            button.setToolTip(mode.name)
            button.setIconSize(QtCore.QSize(48, 48))
            button.setCheckable(True)
            button.clicked.connect(lambda checked, value=mode: self.press_pin_button(value))
            self.button_layout.addWidget(button)
            self.pin_buttons.append(button)
        self.button_group_box.setLayout(self.button_layout)
        self.layout.addWidget(self.button_group_box)
        
        # TODO: make this different depending on version
        self.pin_widgets = {
            PinType.Custom: CustomPinWidget(self, self.pin_num, self.version),
            PinType.Ground: GroundPinWidget(self, self.pin_num),
            PinType.LED: LEDPinWidget(self, self.pin_num, self.version, self.appctxt),
            PinType.Temperature: TemperaturePinWidget(self, self.pin_num, self.version, self.appctxt),
        }
        for mode in PinType:
            self.layout.addWidget(self.pin_widgets[mode])
            self.pin_widgets[mode].hide()

        self.press_pin_button(PinType.Custom)

    def handle_data(self, command, is_input, data):
        self.pin_widgets[self.pin_type].handle_data(command, is_input, data)

    def send_data(self, data):
        self.parent.send_data(data)

    def set_pin_type(self, pin_type):
        self.pin_type = pin_type

    def sync_module_to_pin(self):
        self.pin_widgets[self.pin_type].sync()