from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from ModuleVersionFeatures import module_version_features

class LEDPinWidget(QtWidgets.QScrollArea):
    def __init__(self, parent, pin_num, version, appctxt):
        super(QtWidgets.QScrollArea, self).__init__()
        self.parent = parent
        self.pin_num = pin_num
        self.version = version
        self.appctxt = appctxt

        self.current_status = ""
        self.queue_data = False
        self.data_queue = ''
        self.testing = False

        self.num_pulse_controls = 2
        self.pulse_control_widgets = [LEDPulseWidget(self, i+1, pin_num, appctxt) for i in range(self.num_pulse_controls)]
        
        self.base_widget = QtWidgets.QFrame()
        self.base_layout = QtWidgets.QVBoxLayout(self)
        self.base_widget.setLayout(self.base_layout)
        self.base_layout.setAlignment(Qt.AlignCenter)

        self.base_layout.addWidget(QtWidgets.QLabel('<h3>LED Mode</h3>'))

        # Status Updates Groupbox
        self.status_group_box = QtWidgets.QGroupBox("LED Status")
        self.status_layout = QtWidgets.QVBoxLayout()
        self.status_checkbox = QtWidgets.QCheckBox("Get Updates From Module")
        self.status_checkbox.stateChanged.connect(self.get_updates)
        self.status_layout.addWidget(self.status_checkbox)
        self.led_status_label = QtWidgets.QLabel()
        self.led_status_label.setAlignment(Qt.AlignLeft)
        self.show_status()
        self.status_layout.addWidget(self.led_status_label)
        self.status_group_box.setLayout(self.status_layout)
        self.base_layout.addWidget(self.status_group_box)

        # Manual Control Groupbox
        self.manual_group_box = QtWidgets.QGroupBox("Manual Control")
        self.manual_layout = QtWidgets.QVBoxLayout()
        self.multi_pulse_control_layout = QtWidgets.QHBoxLayout()
        self.multi_stop_button = QtWidgets.QToolButton(self)
        self.multi_stop_button.setIcon(QtGui.QIcon(self.appctxt.get_resource(f'Control_Icons/Control_Stop.png')))
        self.multi_stop_button.setToolTip('Stop')
        self.multi_stop_button.setIconSize(QSize(48, 48))
        self.multi_stop_button.clicked.connect(self.stop)
        self.multi_pulse_control_layout.addWidget(self.multi_stop_button)

        self.multi_start_buttons = []
        for i in range(self.num_pulse_controls):
            self.multi_start_buttons.append(QtWidgets.QToolButton(self))
            self.multi_start_buttons[i].setIcon(QtGui.QIcon(self.appctxt.get_resource(f'Control_Icons/Control_Start.png')))
            self.multi_start_buttons[i].setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            self.multi_start_buttons[i].setText(f'{i+1}')
            self.multi_start_buttons[i].setToolTip(f'Start {i+1}')
            self.multi_start_buttons[i].setIconSize(QSize(48, 48))
            self.multi_start_buttons[i].clicked.connect(lambda pressed, pulse_num=i: self.start_pulse(pulse_num))
            self.multi_pulse_control_layout.addWidget(self.multi_start_buttons[i])
        self.manual_layout.addLayout(self.multi_pulse_control_layout)

        self.output_checkbox = QtWidgets.QCheckBox("LED On")
        self.output_checkbox.stateChanged.connect(self.set_led_on)
        self.manual_layout.addWidget(self.output_checkbox)
        self.manual_group_box.setLayout(self.manual_layout)
        self.base_layout.addWidget(self.manual_group_box)

        for p in self.pulse_control_widgets:
            self.base_layout.addWidget(p)

        # Test Groupbox
        self.test_group_box = QtWidgets.QGroupBox("Test LED Functionality")
        self.test_layout = QtWidgets.QHBoxLayout()
        self.test_button = QtWidgets.QPushButton('Run Test')
        self.test_button.clicked.connect(self.test_LED)
        self.test_layout.addWidget(self.test_button)
        self.test_label = QtWidgets.QLabel('Test Results:')
        self.test_layout.addWidget(self.test_label)
        self.test_group_box.setLayout(self.test_layout)
        self.base_layout.addWidget(self.test_group_box)
        
        self.base_layout.addStretch()

        self.setWidgetResizable(True)
        self.setWidget(self.base_widget)

    def activate(self):
        self.start_queue()
        self.get_updates(self.status_checkbox.isChecked())
        self.send_data(f'S,{self.pin_num},P,L;')
        self.pulse_control_widgets[0].set_all_parameters()
        self.set_led_on(self.output_checkbox.isChecked())
        self.empty_queue()

    def deactivate(self):
        self.start_queue()
        self.get_updates(False)
        self.stop()
        self.set_led_on(False)
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

    def set_led_on(self, set_on):
        update_char = 'O' if set_on else 'o'
        self.send_data(f'L,{self.pin_num},{update_char};')

    def get_updates(self, should_get_updates):
        update_char = 'U' if should_get_updates else 'u'
        self.send_data(f'L,{self.pin_num},{update_char};')

    def start(self):
        self.send_data(f'L,{self.pin_num},S;')

    def start_pulse(self, pulse_num):
        self.start_queue()
        self.pulse_control_widgets[pulse_num].stop()
        self.pulse_control_widgets[pulse_num].set_all_parameters()
        self.pulse_control_widgets[pulse_num].start()
        self.empty_queue()

    def stop(self):
        self.send_data(f'L,{self.pin_num},s;')
        
    def restart(self):
        self.send_data(f'L,{self.pin_num},R;')

    def test_LED(self):
        self.testing = True
        self.start_queue()
        self.stop()
        self.set_led_on(True)
        self.send_data(f'P,{self.pin_num},I,R;')
        self.set_led_on(False)
        self.empty_queue()
        self.test_label.setText("Test Results: Pending")

    def test_results_received(self, data):
        if self.testing:
            data_val = int(data)
            if data_val > module_version_features[self.version]['led_on_thresh']:
                result = 'LED OK'
            else:
                result = 'LED Malfunction'
            self.testing = False
        else:
            result = data
        self.test_label.setText(f'Test Results: {result}')

    def show_status(self):
        self.led_status_label.setText(f'Status: {self.current_status}')

    def status_update(self, status):
        self.current_status = status
        self.show_status()

    def handle_data(self, command, is_input, data):
        print(f'LED pin {self.pin_num} received command {command} for {"input" if is_input else "output"} with {data}')
        if command == 'S':
            self.status_update(data)
        elif command == 'd':
            self.test_results_received(data)
    
    def sync(self):
        self.activate()

class LEDParameterWidget(QtWidgets.QGroupBox):
    def __init__(self, parent, pin_num, parameter, units, name, default, command):
        super(QtWidgets.QGroupBox, self).__init__(parameter)
        self.parent = parent
        self.command = command
        self.pin_num = pin_num
        self.setStyleSheet('QGroupBox {font-weight: bold;}')
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel(name))
        
        self.command_layout = QtWidgets.QHBoxLayout()
        self.data_input = QtWidgets.QLineEdit(default)
        self.data_input.setAlignment(Qt.AlignRight)
        self.data_input.setValidator(QtGui.QIntValidator(0,2000000000)) 
        self.units_label = QtWidgets.QLabel(units)
        self.command_layout.addWidget(self.data_input)
        self.command_layout.addWidget(self.units_label)
        layout.addLayout(self.command_layout)

        self.send_button = QtWidgets.QPushButton(f'Set {name}')
        self.send_button.clicked.connect(self.send)
        self.data_input.returnPressed.connect(self.send_button.click)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def send(self):
        self.parent.send_data(f'L,{self.pin_num},{self.command},{self.get_value()};')

    def get_value(self):
        return self.data_input.text()

class LEDPulseWidget(QtWidgets.QGroupBox):
    def __init__(self, parent, pulse_number, pin_num, appctxt):
        super(QtWidgets.QGroupBox, self).__init__(f'Pulse Control {pulse_number}')
        self.parent = parent
        self.pin_num = pin_num
        self.appctxt = appctxt

        # Pulse Control Groupbox
        self.pulse_layout = QtWidgets.QVBoxLayout()
        # Pulse Waveform Parameter Guide
        self.chart_label = QtWidgets.QLabel()
        self.chart_image = QtGui.QPixmap(self.appctxt.get_resource('LED_Images/LED_Chart_Transparent.png'))
        self.chart_label.setPixmap(self.chart_image.scaled(self.chart_image.width() * 3 // 4, self.chart_image.height() * 3 // 4))
        self.pulse_layout.addWidget(self.chart_label)
        # LED Parameters
        self.led_param_layout = QtWidgets.QHBoxLayout()
        self.led_on_param = LEDParameterWidget(self, self.pin_num, 'a', 'ms', 'LED On Duration', '10', 'n')
        self.led_off_param = LEDParameterWidget(self, self.pin_num, 'b', 'ms', 'LED Off Duration', '40', 'f')
        self.led_param_layout.addWidget(self.led_on_param)
        self.led_param_layout.addWidget(self.led_off_param)
        self.pulse_layout.addLayout(self.led_param_layout)
        # Pulse Parameters
        self.pulse_param_layout = QtWidgets.QHBoxLayout()
        self.pulse_param = LEDParameterWidget(self, self.pin_num, 'c', 'ms', 'Pulse Duration', '1000', 'N')
        self.rest_param = LEDParameterWidget(self, self.pin_num, 'd', 'ms', 'Rest Duration', '4000', 'F')
        self.pulse_param_layout.addWidget(self.pulse_param)
        self.pulse_param_layout.addWidget(self.rest_param)
        self.pulse_layout.addLayout(self.pulse_param_layout)
        # Set All Parameters
        self.set_all_button = QtWidgets.QPushButton('Set All Parameters')
        self.set_all_button.clicked.connect(self.set_all_parameters)
        self.pulse_layout.addWidget(self.set_all_button)

        # Control Buttons
        self.control_button_layout = QtWidgets.QHBoxLayout()
        # Start Button
        self.start_button = QtWidgets.QToolButton(self)
        self.start_button.setIcon(QtGui.QIcon(self.appctxt.get_resource(f'Control_Icons/Control_Start.png')))
        self.start_button.setToolTip('Start')
        self.start_button.setIconSize(QSize(48, 48))
        self.start_button.clicked.connect(self.start)
        self.control_button_layout.addWidget(self.start_button)
        # Restart Button
        self.restart_button = QtWidgets.QToolButton(self)
        self.restart_button.setIcon(QtGui.QIcon(self.appctxt.get_resource(f'Control_Icons/Control_Restart.png')))
        self.restart_button.setToolTip('Restart')
        self.restart_button.setIconSize(QSize(48, 48))
        self.restart_button.clicked.connect(self.restart)
        self.control_button_layout.addWidget(self.restart_button)
        # Stop Button
        self.stop_button = QtWidgets.QToolButton(self)
        self.stop_button.setIcon(QtGui.QIcon(self.appctxt.get_resource(f'Control_Icons/Control_Stop.png')))
        self.stop_button.setToolTip('Stop')
        self.stop_button.setIconSize(QSize(48, 48))
        self.stop_button.clicked.connect(self.stop)
        self.control_button_layout.addWidget(self.stop_button)
        self.pulse_layout.addLayout(self.control_button_layout)

        self.setLayout(self.pulse_layout)
        
    def set_all_parameters(self):
        pulse = self.pulse_param.get_value()
        rest = self.rest_param.get_value()
        led_on = self.led_on_param.get_value()
        led_off = self.led_off_param.get_value()
        self.parent.send_data(f'L,{self.pin_num},C,{pulse},{rest},{led_on},{led_off};')

    def start(self):
        self.parent.start()

    def stop(self):
        self.parent.stop()
        
    def restart(self):
        self.parent.stop()