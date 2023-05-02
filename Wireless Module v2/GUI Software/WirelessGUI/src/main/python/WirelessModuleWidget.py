from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from ModuleVersionFeatures import module_version_features
from PinWidget import PinWidget

class WirelessModuleWidget(QtWidgets.QFrame):
    def __init__(self, parent, id, appctxt):
        super(QtWidgets.QFrame, self).__init__()
        self.parent = parent
        self.id = id
        self.appctxt = appctxt

        print(f'Module {id} created')
        self.name = f'Module {id}'
        self.version = None
        self.connected = False
        self.closed = False
        self.pins = []

        self.setup()

    def setup(self):
        self.layout = QtWidgets.QVBoxLayout(self)

        # Title
        self.title_layout = QtWidgets.QHBoxLayout(self)
        self.title_label = QtWidgets.QLabel()
        self.conn_label = QtWidgets.QLabel()
        self.set_title_text()
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addWidget(self.conn_label)
        self.title_layout.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(self.title_layout)

        # Manual commands
        self.command_layout = QtWidgets.QHBoxLayout()
        self.data_label = QtWidgets.QLabel('Manual Command:')
        self.data_input = QtWidgets.QLineEdit()
        self.send_button = QtWidgets.QPushButton('Send Data')
        self.send_button.clicked.connect(self.send)
        self.data_input.returnPressed.connect(self.send_button.click)
        self.command_layout.addWidget(self.data_label)
        self.command_layout.addWidget(self.data_input)
        self.command_layout.addWidget(self.send_button)
        self.layout.addLayout(self.command_layout)

        # Module Control Buttons
        self.control_layout = QtWidgets.QHBoxLayout()
        self.sync_button = QtWidgets.QPushButton('Sync Module to GUI')
        self.sync_button.clicked.connect(self.sync)
        self.control_layout.addWidget(self.sync_button)
        self.reset_button = QtWidgets.QPushButton('Reset Module')
        self.reset_button.clicked.connect(self.reset)
        self.control_layout.addWidget(self.reset_button)
        self.disconnect_button = QtWidgets.QPushButton('Disconnect Module')
        self.disconnect_button.clicked.connect(self.disconnect)
        self.control_layout.addWidget(self.disconnect_button)
        self.layout.addLayout(self.control_layout)

        # Pin Window (for holding pin docks)
        self.pin_window = QtWidgets.QMainWindow()
        self.pin_window.setWindowFlags(Qt.Widget)
        self.pin_window.setTabPosition(Qt.AllDockWidgetAreas, QtWidgets.QTabWidget.North)
        self.pin_window.setDockOptions(self.pin_window.GroupedDragging | self.pin_window.AllowTabbedDocks | self.pin_window.AllowNestedDocks)
        self.layout.addWidget(self.pin_window)

        self.reset()

    def sync(self):
        for pin in self.pins:
            pin.sync_module_to_pin()

    def reset(self):
        self.send_data('M,R;')

    def disconnect(self):
        self.send_data('M,D;')

    def set_title_text(self):
        name_text = f"Module {self.id} - v{self.version if self.version else '[Unknown]'}"
        title_text = f"<h1>{name_text}</h1>"
        self.title_label.setText(title_text)
        conn_icon = QtGui.QPixmap(self.appctxt.get_resource(f'BT_Icons/BT_{"Connected" if self.connected else "Disconnected"}.png'))
        self.conn_label.setPixmap(conn_icon)

    def set_connected(self):
        self.connected = True
        self.set_title_text()
        if self.version is None:
            self.send_data('M,V;')

    def set_disconnected(self):
        self.connected = False
        self.set_title_text()

    def send_data(self, data):
        self.parent.send_text(f'{self.id};{data}\r\n'.encode())

    def send(self):
        self.send_data(self.data_input.text())

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def handle_data(self, command, identifier, content):
        if command == 'M':
            print(f'Module info for module {self.id}: {identifier} with {content}')
            self.handle_module_metadata(identifier, content)
        elif command == 'S' or command == 'd' or command == 'D':
            pin_id = ord(identifier) - ord(' ')
            pin_num = pin_id % 4
            is_input = pin_id // 4 == 0
            self.pins[pin_num].handle_data(command, is_input, content)
        else:
            print(f'unknown data {command}{identifier}{content}')

    def handle_module_metadata(self, identifier, content):
        if identifier == 'V':
            if self.version is None:
                num_pins = module_version_features[content]['pins']
                for pin_num in range(num_pins):
                    pin_widget = PinWidget(self, pin_num, content, self.appctxt)
                    self.pins.append(pin_widget)

                    all_docks = self.pin_window.findChildren(QtWidgets.QDockWidget)
                    if all_docks:
                        target_dock = all_docks[0]
                    else:
                        target_dock = None

                    pin_dock = QtWidgets.QDockWidget(f'Pin {pin_num + 1}')
                    pin_dock.setWidget(pin_widget)
                    pin_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
                    pin_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
                    self.pin_window.addDockWidget(Qt.BottomDockWidgetArea, pin_dock)

                    if target_dock is not None:
                        self.pin_window.tabifyDockWidget(target_dock, pin_dock)
                self.version = content
                self.closed = False
                self.set_title_text()