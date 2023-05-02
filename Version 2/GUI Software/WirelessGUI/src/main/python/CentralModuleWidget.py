from PyQt5 import QtWidgets, QtSerialPort, QtGui, QtCore
from random import randint

from PyQt5.QtCore import Qt


class CentralModuleWidget(QtWidgets.QFrame):
    def __init__(self, parent, appctxt):
        super(QtWidgets.QFrame, self).__init__()
        self.parent = parent
        self.appctxt = appctxt
        self.setup()

    def setup(self):
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)

        self.central_image = QtWidgets.QLabel()
        central_pixmap = QtGui.QPixmap(self.appctxt.get_resource('Central_Images/Central.png'))
        scaled_central_pixmap = central_pixmap.scaledToWidth(central_pixmap.width() // 2)
        self.central_image.setPixmap(scaled_central_pixmap)
        self.central_image.setAlignment(Qt.AlignCenter)

        self.poll_button = QtWidgets.QPushButton(self)
        self.poll_button.setText('Scan For Modules')
        self.poll_button.clicked.connect(self.parent.poll_modules)

        self.rand_module_button = QtWidgets.QPushButton(self)
        self.rand_module_button.setText('Add Random Module')
        self.rand_module_button.clicked.connect(self.add_rand_module)

        self.module_num_input = QtWidgets.QLineEdit()
        self.module_num_input.setAlignment(Qt.AlignRight)
        self.module_num_input.setValidator(QtGui.QIntValidator(0,998))
        self.numbered_module_button = QtWidgets.QPushButton('Add this module')
        self.numbered_module_button.clicked.connect(self.add_numbered_module_from_input)
        self.module_num_input.returnPressed.connect(self.numbered_module_button.click)
        
        self.port_manager = PortManager(self)

        self.layout.addWidget(self.central_image)
        self.layout.addWidget(self.port_manager)
        self.layout.addWidget(self.poll_button)
        self.layout.addStretch()
        self.layout.addWidget(self.rand_module_button)
        self.layout.addWidget(self.module_num_input)
        self.layout.addWidget(self.numbered_module_button)

    def add_numbered_module_from_input(self):
        module_id = int(self.module_num_input.text())
        self.add_numbered_module(module_id)

    def add_numbered_module(self, module_id):
        self.parent.handle_data(f'{module_id:03}MI{module_id:03}')
        self.parent.handle_data(f'{module_id:03}MV1.1P')

    def add_rand_module(self):
        module_id = randint(0, 998)
        self.add_numbered_module(module_id)

    def get_port(self):
        return self.parent.get_port()

    def set_port(self, port):
        self.parent.set_port(port)

    def poll_modules(self):
        self.parent.poll_modules()

    def open(self):
        return self.parent.open()

    def is_open(self):
        return self.parent.is_open()

    def close(self):
        self.parent.close()
        
# QComboBox with a signal when box is clicked
class ClickedComboBox(QtWidgets.QComboBox):
    comboBoxClicked = QtCore.pyqtSignal()

    def showPopup(self):
        self.comboBoxClicked.emit()
        super(ClickedComboBox, self).showPopup()

# Handles Serial port connection
class PortManager(QtWidgets.QGroupBox):
    def __init__(self, parent):
        super(QtWidgets.QGroupBox, self).__init__('Serial Port')
        self.parent = parent
        
        layout = QtWidgets.QHBoxLayout()

        # Connection button
        self.connection_button = QtWidgets.QPushButton(self)
        self.connection_button.setText('Connect')
        self.connection_button.clicked.connect(self.update_connection)
        
        # List of available ports
        self.port_layout = QtWidgets.QHBoxLayout()
        self.port_dropdown = ClickedComboBox(self)
        self.port_dropdown.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.port_dropdown.currentTextChanged.connect(self.change_port)
        self.port_dropdown.comboBoxClicked.connect(self.reload_ports)
        self.reload_ports()
        
        self.port_layout.addWidget(self.port_dropdown)

        layout.addLayout(self.port_layout)
        layout.addWidget(self.connection_button)

        self.setLayout(layout)
        
    # Reloads the list of ports available
    def reload_ports(self):
        self.port_dropdown.clear()
        self.ports = [p.portName() for p in QtSerialPort.QSerialPortInfo.availablePorts()]
        self.port_dropdown.addItems(self.ports)

    # Connects/Disconnects to port
    def update_connection(self):
        if self.connection_button.text() == 'Connect' or self.connection_button.text() == 'Retry Connection':
            self.parent.set_port(self.port_dropdown.currentText())
            if self.parent.open():
                self.connection_button.setText('Disconnect')
                self.parent.poll_modules()
            else:
                self.connection_button.setText('Retry Connection')
        else:
            self.parent.close()
            self.connection_button.setText('Connect')

    # Changes current port
    def change_port(self, new_port):
        if new_port == self.parent.get_port() and self.parent.is_open():
            self.connection_button.setText('Disconnect')
        else:
            self.connection_button.setText('Connect')