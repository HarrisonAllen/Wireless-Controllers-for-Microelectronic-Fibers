from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt

class GroundPinWidget(QtWidgets.QScrollArea):
    def __init__(self, parent, pin_num):
        super(QtWidgets.QScrollArea, self).__init__()
        self.parent = parent
        self.pin_num = pin_num

        self.base_widget = QtWidgets.QFrame()
        self.base_layout = QtWidgets.QVBoxLayout(self)
        self.base_widget.setLayout(self.base_layout)
        self.base_layout.setAlignment(Qt.AlignCenter)


        self.text_label = QtWidgets.QLabel('<h3>Pin is set to Ground</h3>')
        self.base_layout.addWidget(self.text_label)

        self.base_widget.setLayout(self.base_layout)

        self.base_layout.addStretch()

        self.setWidgetResizable(True)
        self.setWidget(self.base_widget)

    def activate(self):
        self.send_data(f'S,{self.pin_num},P,G;')

    def deactivate(self):
        # Nothing needs to be done for ground pin
        pass

    def send_data(self, data):
        self.parent.send_data(data)

    def handle_data(self, command, is_input, data):
        print(f'Ground pin {self.pin_num} received command {command} for {"input" if is_input else "output"} with {data}')

    def sync(self):
        self.activate()