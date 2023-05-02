from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QFile, Qt
from enum import Enum
from ModuleVersionFeatures import module_version_features

class PinMode(Enum):
    Input = "Input"
    Input_Pullup = "Input Pullup"
    Output_Low = "Output Low"
    Output_High = "Output High"

class CustomPinWidget(QtWidgets.QScrollArea):
    def __init__(self, parent, pin_num, version):
        super(QtWidgets.QScrollArea, self).__init__()
        self.parent = parent
        self.pin_num = pin_num
        self.version = version

        self.queue_data = False
        self.data_queue = ''
        
        self.base_widget = QtWidgets.QFrame()
        self.base_layout = QtWidgets.QVBoxLayout(self)
        self.base_widget.setLayout(self.base_layout)
        self.base_layout.setAlignment(Qt.AlignCenter)

        self.base_layout.addWidget(QtWidgets.QLabel('<h3>Custom Pin Mode</h3>'))

        # Input pin section
        self.input_editor = PinEditorWidget(self, "Input Pin", self.pin_num, True)
        self.output_editor = PinEditorWidget(self, "Output Pin", self.pin_num, False)

        self.base_layout.addWidget(self.input_editor)
        self.base_layout.addWidget(self.output_editor)
        self.base_layout.addStretch()

        self.setWidgetResizable(True)
        self.setWidget(self.base_widget)

    def activate(self):
        self.start_queue()
        self.input_editor.apply_settings()
        self.output_editor.apply_settings()
        self.empty_queue()

    def deactivate(self):
        self.start_queue()
        self.input_editor.get_updates(False)
        self.output_editor.get_updates(False)
        self.empty_queue()

    def start_queue(self):
        self.queue_data = True

    def empty_queue(self):
        self.queue_data = False
        self.send_data('')

    def send_data(self, data):
        self.data_queue += data
        if not self.queue_data:
            self.parent.send_data(self.data_queue)
            self.data_queue = ''

    def handle_data(self, command, is_input, data):
        print(f'Custom pin {self.pin_num} received command {command} for {"input" if is_input else "output"} with {data}')
        if command == 'd':
            if is_input:
                self.input_editor.receive_data(data)
            else:
                self.output_editor.receive_data(data)
        elif command == 'S':
            if is_input:
                self.input_editor.receive_status_update(data)
            else:
                self.output_editor.receive_status_update(data)

    def sync(self):
        self.activate()

class PinEditorWidget(QtWidgets.QGroupBox):
    def __init__(self, parent, name, pin_num, is_input):
        super(QtWidgets.QGroupBox, self).__init__(name)
        self.parent = parent
        self.pin_num = pin_num
        self.is_input = is_input
        self.last_read_data = "0"
        self.current_status = ""
        self.pin_mode = PinMode.Input
        self.input_mode = PinMode.Input
        self.output_mode = PinMode.Output_Low

        layout = QtWidgets.QVBoxLayout()

        # Status Updates Checkbox
        self.status_checkbox = QtWidgets.QCheckBox("Get Updates From Module")
        self.status_checkbox.stateChanged.connect(self.get_updates)
        layout.addWidget(self.status_checkbox)
        self.pin_status_label = QtWidgets.QLabel()
        self.pin_status_label.setAlignment(Qt.AlignLeft)
        self.show_status()
        layout.addWidget(self.pin_status_label)
        separator = QtWidgets.QFrame()
        separator.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Sunken)
        layout.addWidget(separator)

        # Pin Mode Options
        pin_mode_layout = QtWidgets.QHBoxLayout()
        pin_mode_layout.addWidget(QtWidgets.QLabel("Pin Mode"))
        self.pin_mode_options = QtWidgets.QComboBox()
        self.pin_mode_options.addItems(["Input", "Output"])
        self.pin_mode_options.currentTextChanged.connect(self.mode_changed)
        pin_mode_layout.addWidget(self.pin_mode_options)
        layout.addLayout(pin_mode_layout)
        
        # Input Pin Options
        self.input_options = QtWidgets.QFrame()
        self.input_options_layout = QtWidgets.QVBoxLayout()
        self.input_options.setLayout(self.input_options_layout)
        layout.addWidget(self.input_options)
        # Pullup Checkbox
        self.pullup_checkbox = QtWidgets.QCheckBox("Use Internal Pullup")
        self.pullup_checkbox.stateChanged.connect(self.set_pullup)
        self.input_options_layout.addWidget(self.pullup_checkbox)
        # Data Button
        self.data_layout = QtWidgets.QHBoxLayout()
        self.data_button = QtWidgets.QPushButton("Read Pin")
        self.data_button.clicked.connect(self.read_pin)
        self.data_format_options = QtWidgets.QComboBox()
        self.data_format_options.addItems(["Voltage", "Raw"])
        self.data_format_options.currentTextChanged.connect(self.change_data_format)
        self.data_layout.addWidget(self.data_button)
        self.data_layout.addWidget(self.data_format_options)
        self.input_options_layout.addLayout(self.data_layout)
        # Data Displayer
        self.data_label = QtWidgets.QLabel()
        self.data_label.setAlignment(Qt.AlignLeft)
        self.show_data()
        self.input_options_layout.addWidget(self.data_label)

        # Output Pin Options
        self.output_options = QtWidgets.QFrame()
        self.output_options_layout = QtWidgets.QVBoxLayout()
        self.output_options.setLayout(self.output_options_layout)
        layout.addWidget(self.output_options)
        # On/Off checkbox
        self.output_checkbox = QtWidgets.QCheckBox("Pin On")
        self.output_checkbox.stateChanged.connect(self.set_pin_on)
        self.output_options_layout.addWidget(self.output_checkbox)
        # High Drive checkbox
        # TODO: Add a checkbox for High Drive (high power mode or something)
        self.output_options.hide()

        self.setLayout(layout)

    def apply_settings(self):
        self.get_updates(self.status_checkbox.isChecked())
        if self.pin_mode == PinMode.Input:
            self.set_pullup(False)
        elif self.pin_mode == PinMode.Input_Pullup:
            self.set_pullup(True)
        elif self.pin_mode == PinMode.Output_Low:
            self.set_pin_on(False)
        elif self.pin_mode == PinMode.Output_High:
            self.set_pin_on(True)

    def read_pin(self):
        input_char = 'I' if self.is_input else 'O'
        self.parent.send_data(f'P,{self.pin_num},{input_char},R')

    def change_data_format(self, _value):
        self.show_data()
    
    def show_data(self):
        data = int(self.last_read_data)
        if self.data_format_options.currentText() == "Voltage":
            max_voltage = module_version_features[self.parent.version]['voltage']
            resolution = module_version_features[self.parent.version]['resolution']
            max_val = 2**resolution
            ratio = data / max_val
            voltage = round(ratio * max_voltage, 4)
            self.data_label.setText(f'Data: {voltage} V')
        else:
            self.data_label.setText(f'Data: {data}')

    def receive_data(self, data):
        self.last_read_data = data
        self.show_data()

    def show_status(self):
        self.pin_status_label.setText(f'Status: {self.current_status}')

    def receive_status_update(self, status):
        self.current_status = status
        self.show_status()

    def mode_changed(self, value):
        if value == "Input":
            self.set_pullup(self.input_mode == PinMode.Input_Pullup)
            self.output_options.hide()
            self.input_options.show()
        elif value == "Output":
            self.set_pin_on(self.output_mode == PinMode.Output_High)
            self.input_options.hide()
            self.output_options.show()

    def set_pullup(self, is_pullup):
        self.pin_mode = PinMode.Input_Pullup if is_pullup else PinMode.Input
        self.input_mode = self.pin_mode
        input_char = 'I' if self.is_input else 'O'
        pullup_char = 'P' if is_pullup else 'I'
        self.parent.send_data(f'S,{self.pin_num},{input_char},{pullup_char};')

    def get_updates(self, should_get_updates):
        input_char = 'I' if self.is_input else 'O'
        update_char = 'U' if should_get_updates else 'u'
        self.parent.send_data(f'P,{self.pin_num},{input_char},{update_char};')

    def set_pin_on(self, set_on):
        self.pin_mode = PinMode.Output_High if set_on else PinMode.Output_Low
        self.output_mode = self.pin_mode
        input_char = 'I' if self.is_input else 'O'
        update_char = 'h' if set_on else 'l'
        # TODO: Add high drive low/high (if high drive checked)
        self.parent.send_data(f'S,{self.pin_num},{input_char},{update_char};')

    def sync(self):
        self.apply_settings()
