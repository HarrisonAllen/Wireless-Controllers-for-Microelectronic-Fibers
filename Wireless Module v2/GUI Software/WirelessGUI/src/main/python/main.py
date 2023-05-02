from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5 import QtCore, QtGui, QtWidgets, QtSerialPort
from PyQt5.QtCore import Qt
import sys
from CentralModuleWidget import CentralModuleWidget
from WirelessModuleWidget import WirelessModuleWidget
from WelcomeWidget import WelcomeWidget

class MainWindow(QtWidgets.QMainWindow):
    """This is the main UI container"""
    def __init__(self):
        super().__init__()
        self.init_UI()

    def init_UI(self):
        # Serial setup        
        self.serial = QtSerialPort.QSerialPort(
            '',
            baudRate=QtSerialPort.QSerialPort.Baud115200,
            readyRead=self.receive
        )

        # Window setup
        self.setWindowTitle('NeuroModular GUI')
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QHBoxLayout(self.central_widget)
        
        self.welcome_widget = WelcomeWidget(self, appctxt)
        welcome_dock = QtWidgets.QDockWidget("Welcome")
        welcome_dock.setWidget(self.welcome_widget)
        welcome_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.addDockWidget(Qt.LeftDockWidgetArea, welcome_dock)

        self.central_module_widget = CentralModuleWidget(self, appctxt)
        central_dock = QtWidgets.QDockWidget("Central")
        central_dock.setWidget(self.central_module_widget)
        central_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        central_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        self.addDockWidget(Qt.LeftDockWidgetArea, central_dock)
        self.tabifyDockWidget(central_dock, welcome_dock)

        self.setTabPosition(Qt.AllDockWidgetAreas, QtWidgets.QTabWidget.North)
        self.setDockOptions(self.GroupedDragging | self.AllowTabbedDocks | self.AllowNestedDocks)

        self.wireless_module_widgets = []

        self.resize(800, 900)

        self.show()

    def set_port(self, name):
        self.serial.setPortName(name)

    def get_port(self):
        return self.serial.portName()

    def is_open(self):
        return self.serial.isOpen()

    def open(self):
        if self.serial.open(QtCore.QIODevice.ReadWrite):
            self.serial.flush()
            print("Connection success!")
            return True
        print("Connection failure...")
        return False

    def close(self):
        self.serial.close()
        print("Disconnect success!")

    @QtCore.pyqtSlot()
    def receive(self):        
        while self.serial.canReadLine():
            text = self.serial.readLine().data().decode('utf-8').strip()
            self.handle_data(text)

    def get_module_of_id_from_dock(self, id):
        all_docks = self.findChildren(QtWidgets.QDockWidget)
        for child_dock in all_docks:
            if isinstance(child_dock.widget(), WirelessModuleWidget):
                module = child_dock.widget()
                if module.get_id() == id:
                    return module, child_dock
        return None, None

    def set_color_of_tab_name(self, name, color):
        all_tab_bars = self.findChildren(QtWidgets.QTabBar)
        for tab_bar in all_tab_bars:
            for t in range(tab_bar.count()):
                if tab_bar.tabText(t) == name:
                    tab_bar.setTabTextColor(t, color)
                    return True
        return False

    def check_for_id(self, id):
        # first check existing docks
        module, dock = self.get_module_of_id_from_dock(id)
        if module is not None:
            dock.setVisible(True)
            module.set_connected()
            dock.setGraphicsEffect(None)
            self.set_color_of_tab_name(module.get_name(), Qt.black)
            return
        
        # then check created modules
        module = self.get_module_of_id(id)

        # not found, make a new one
        if module is None:
            module = WirelessModuleWidget(self, id, appctxt)
            self.wireless_module_widgets.append(module)
        
        # Connect the module
        module.set_connected()

        # See if any module docks already exist
        target_dock = None
        all_docks = self.findChildren(QtWidgets.QDockWidget)
        for child_dock in all_docks:
            if isinstance(child_dock.widget(), WirelessModuleWidget):
                target_dock = child_dock
                break

        # Create the module dock
        module_dock = QtWidgets.QDockWidget(module.get_name())
        module_dock.setWidget(module)
        module_dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.addDockWidget(Qt.RightDockWidgetArea, module_dock)

        # And pair it with any existing docks
        if target_dock is not None:
            self.tabifyDockWidget(target_dock, module_dock)
    
    def get_module_of_id(self, id):
        for module in self.wireless_module_widgets:
            if module.get_id() == id:
                return module

    def poll_modules(self):
        for module in self.wireless_module_widgets:
            child_module, child_dock = self.get_module_of_id_from_dock(module.get_id())
            disconnect_color = QtWidgets.QGraphicsColorizeEffect(self)
            disconnect_color.setColor(Qt.red)
            child_dock.setGraphicsEffect(disconnect_color)
            self.set_color_of_tab_name(module.get_name(), Qt.red)
            child_module.set_disconnected()
        self.send_text('999;M,I;\r\n'.encode())

    def handle_data(self, data):
        if data == 'Connected':
            print('Connected to wireless module')
            self.poll_modules()
        elif data == 'Disconnected':
            print('Disconnected from wireless module')
            self.poll_modules()
        else:
            module_id = int(data[:3])
            command = data[3]
            identifier = data[4]
            content = data[5:]
            if command == 'M' and identifier == 'I':
                self.check_for_id(int(content))
            else:
                module = self.get_module_of_id(module_id)
                if module is not None:
                    module.handle_data(command, identifier, content)

    def send_text(self, text):
        self.to_send = text
        self.send()

    @QtCore.pyqtSlot()
    def send(self):
        print("Sending:", self.to_send)
        self.serial.write(self.to_send)

    @QtCore.pyqtSlot(int)
    def qtabwidget_tabcloserequested(self, index):
        self.wireless_module_tabs.removeTab(index)

if __name__ == '__main__':
    appctxt = ApplicationContext()

    app = QtWidgets.QApplication([])
    app.setStyle("Fusion")
    app_font = app.font()
    app_font.setPointSize(14)
    app.setFont(app_font)
    win = MainWindow()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
