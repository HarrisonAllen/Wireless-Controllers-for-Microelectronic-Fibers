from math import log
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from ModuleVersionFeatures import module_version_features
import pyqtgraph as pg
import numpy as np
import time

MAX_POINTS = 1000000
MAX_DISPLAY_POINTS = 100000

class TemperaturePinWidget(QtWidgets.QScrollArea):
    def __init__(self, parent, pin_num, version, appctxt):
        super(QtWidgets.QScrollArea, self).__init__()
        self.parent = parent
        self.pin_num = pin_num
        self.version = version
        self.appctxt = appctxt
        
        self.queue_data = False
        self.data_queue = ''
        self.last_read_data = '0'
        self.intercept_single = False
        self.temperature_data = []
        self.timestamps = []
        self.saved_data = np.array(np.zeros(MAX_POINTS), dtype=np.ushort)
        self.data_position = 0
        self.num_points_to_plot = 100
        self.smoothing_factor = 1
        
        self.base_widget = QtWidgets.QFrame()
        self.base_layout = QtWidgets.QVBoxLayout(self)
        self.base_widget.setLayout(self.base_layout)
        self.base_layout.setAlignment(Qt.AlignCenter)

        self.base_layout.addWidget(QtWidgets.QLabel('<h3>Temperature Sensing Mode</h3>'))

        # Calibration
        self.calibration_group_box = QtWidgets.QGroupBox('Calibration')

        self.calibration_layout = QtWidgets.QVBoxLayout()

        self.cal_resistor_layout = QtWidgets.QHBoxLayout()
        self.cal_resistor_label = QtWidgets.QLabel('Module Resistor')
        self.cal_resistor_input = QtWidgets.QLineEdit('10000')
        self.cal_resistor_input.setAlignment(Qt.AlignRight)
        self.cal_resistor_input.setValidator(QtGui.QIntValidator(0,2000000000))
        self.cal_resistor_units = QtWidgets.QLabel('<span>&#8486;</span>')
        self.cal_resistor_layout.addWidget(self.cal_resistor_label)
        self.cal_resistor_layout.addWidget(self.cal_resistor_input)
        self.cal_resistor_layout.addWidget(self.cal_resistor_units)

        self.cal_res_0_layout = QtWidgets.QHBoxLayout()
        self.cal_res_0_label = QtWidgets.QLabel('<span>NTC R<sub>0</sub> @ 25&#176;C</span>')
        self.cal_res_0_input = QtWidgets.QLineEdit('10000')
        self.cal_res_0_input.setAlignment(Qt.AlignRight)
        self.cal_res_0_input.setValidator(QtGui.QIntValidator(0,2000000000))
        self.cal_res_0_units = QtWidgets.QLabel('<span>&#8486;</span>')
        self.cal_res_0_layout.addWidget(self.cal_res_0_label)
        self.cal_res_0_layout.addWidget(self.cal_res_0_input)
        self.cal_res_0_layout.addWidget(self.cal_res_0_units)
        
        self.cal_beta_layout = QtWidgets.QHBoxLayout()
        self.cal_beta_label = QtWidgets.QLabel('<span>NTC &beta; @ 25&#176;C</span>')
        self.cal_beta_input = QtWidgets.QLineEdit('3380')
        self.cal_beta_input.setAlignment(Qt.AlignRight)
        self.cal_beta_input.setValidator(QtGui.QDoubleValidator(0.0,200000000.0, 10, None))
        self.cal_beta_layout.addWidget(self.cal_beta_label)
        self.cal_beta_layout.addWidget(self.cal_beta_input)

        self.calibration_layout.addLayout(self.cal_resistor_layout)
        self.calibration_layout.addLayout(self.cal_res_0_layout)
        self.calibration_layout.addLayout(self.cal_beta_layout)
        self.calibration_group_box.setLayout(self.calibration_layout)
        self.base_layout.addWidget(self.calibration_group_box)

        # Manual Control Group Box
        self.manual_group_box = QtWidgets.QGroupBox('Manual Control')
        self.manual_layout = QtWidgets.QVBoxLayout()
        # Data Button
        self.data_layout = QtWidgets.QHBoxLayout()
        self.data_button = QtWidgets.QPushButton("Read Pin")
        self.data_button.clicked.connect(self.read_pin)
        self.data_format_options = QtWidgets.QComboBox()
        self.data_format_options.addItems(["Temperature", "Voltage", "Resistance", "Raw"])
        self.data_format_options.currentTextChanged.connect(self.change_data_format)
        self.data_layout.addWidget(self.data_button)
        self.data_layout.addWidget(self.data_format_options)
        self.manual_layout.addLayout(self.data_layout)
        # Single Data Displayer
        self.data_label = QtWidgets.QLabel()
        self.data_label.setAlignment(Qt.AlignLeft)
        self.show_data()
        self.manual_layout.addWidget(self.data_label)
        self.manual_group_box.setLayout(self.manual_layout)
        self.base_layout.addWidget(self.manual_group_box)


        # Automatic Control Group Box
        self.automatic_group_box = QtWidgets.QGroupBox("Automatic Control")
        self.automatic_layout = QtWidgets.QVBoxLayout()
        # Parameters
        self.param_layout = QtWidgets.QHBoxLayout()
        self.read_period_param = NTCParameterWidget(self, self.pin_num, 'ms', 'Time Between Data Points', '1000', 'P')
        self.num_points_param = NTCParameterWidget(self, self.pin_num, 'point(s)', '# Points to Collect', '1', 'd')
        self.param_layout.addWidget(self.read_period_param)
        self.param_layout.addWidget(self.num_points_param)
        self.automatic_layout.addLayout(self.param_layout)
        # Set All Parameters
        self.set_all_button = QtWidgets.QPushButton('Set All Parameters')
        self.set_all_button.clicked.connect(self.set_all_parameters)
        self.automatic_layout.addWidget(self.set_all_button)

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
        self.automatic_layout.addLayout(self.control_button_layout)

        # Data Plot
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.data_graph = pg.PlotWidget(self, axisItems={'bottom': pg.DateAxisItem()})
        self.data_graph.show()
        self.data_graph.setMinimumHeight(200)
        self.automatic_layout.addWidget(self.data_graph)
        # Plot Sliders
        self.num_points_slider = InputSliderWidget(self, 'Points to Display', 1, MAX_POINTS, self.num_points_to_plot, use_slider=False)
        self.num_points_slider.valueChanged.connect(self.set_num_points)
        self.automatic_layout.addWidget(self.num_points_slider)
        # self.smoothing_slider = InputSliderWidget(self, 'Smoothing', 1, 50, self.smoothing_factor)
        # self.smoothing_slider.valueChanged.connect(self.set_smoothing)
        # self.automatic_layout.addWidget(self.smoothing_slider)

        # Graph Buttons
        graph_button_layout = QtWidgets.QHBoxLayout()
        self.export_data_button = QtWidgets.QPushButton('Export Data')
        self.export_data_button.clicked.connect(self.export_data)
        graph_button_layout.addWidget(self.export_data_button)
        self.clear_data_button = QtWidgets.QPushButton('Clear Data')
        self.clear_data_button.clicked.connect(self.clear_data)
        graph_button_layout.addWidget(self.clear_data_button)
        self.automatic_layout.addLayout(graph_button_layout)

        self.automatic_group_box.setLayout(self.automatic_layout)
        self.base_layout.addWidget(self.automatic_group_box)

        self.setWidgetResizable(True)
        self.setWidget(self.base_widget)

    def activate(self):
        self.start_queue()
        self.send_data(f'S,{self.pin_num},P,N;')
        self.set_all_parameters()
        self.empty_queue()

    def deactivate(self):
        self.start_queue()
        self.stop()
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

    def set_all_parameters(self):
        read_period = self.read_period_param.get_value()
        num_points = self.num_points_param.get_value()
        self.send_data(f'D,{self.pin_num},C,{read_period},{num_points};')
        
    def start(self):
        self.send_data(f'D,{self.pin_num},S;')

    def stop(self):
        self.send_data(f'D,{self.pin_num},s;')
        
    def restart(self):
        self.send_data(f'D,{self.pin_num},X;')

    def set_smoothing(self, value):
        if value < 1:
            value = 1
        self.smoothing_factor = value
        self.redraw_plot()

    def set_num_points(self, value):
        if value < 1:
            value = 1
        self.num_points_to_plot = value
        self.redraw_plot()

    @staticmethod
    def shift_elements(arr, num, fill_value):
        result = np.empty_like(arr)
        if num > 0:
            result[:num] = fill_value
            result[num:] = arr[:-num]
        elif num < 0:
            result[num:] = fill_value
            result[:num] = arr[-num:]
        else:
            result[:] = arr
        return result

    @staticmethod
    def moving_average(x, w):
        if w > x.size:
            w = 1
        return np.convolve(x, np.ones(w), 'valid') / w

    def plot_data(self, data):
        spacing = int(self.read_period_param.get_value())
        new_times = []
        time_index = 0
        now = time.time()
        recorded_data = data.split(',')
        new_times = [(now - (d * spacing / 1000)) for d in range(len(recorded_data))]
        new_times.reverse()
        for d in range(len(recorded_data)):
            if recorded_data[d] != '':
                self.temperature_data.append(int(recorded_data[d]))
                self.timestamps.append(new_times[d])
        
        self.redraw_plot()
    
    def redraw_plot(self):
        self.data_graph.plotItem.clear()
        converted_data = self.convert_data(np.array(self.temperature_data[-self.num_points_to_plot:]), self.data_format_options.currentText())
        timestamps = self.timestamps[-self.num_points_to_plot:]
        self.data_graph.plotItem.plot(timestamps, converted_data, pen=pg.mkPen(width=2))

    def export_data(self):
        save_filename, _extensions = QtGui.QFileDialog.getSaveFileName(
            self, 'Export temperature data as...', f'{self.data_format_options.currentText()}.csv', 'CSV (*.csv)')
        if not save_filename:
            return

        with open(save_filename, 'w') as f:
            f.write(f'Timestamp ,{self.data_format_options.currentText()}\n')
            for timestamp, temp in zip(self.timestamps, self.convert_data(np.array(self.temperature_data), self.data_format_options.currentText())):
                f.write(time.strftime(f"%Y-%m-%d %H:%M:%S:{int((timestamp * 1000) % 1000)}", time.localtime(timestamp)) + f',{temp}\n')

    def clear_data(self):
        self.temperature_data = []
        self.timestamps = []
        self.data_graph.plotItem.clear()
            
    def receive_data(self, data):
        if self.intercept_single and len(data.split(',')) <= 2:
            self.last_read_data = data
            self.show_data()
            self.intercept_single = False
        else:
            self.plot_data(data)

    def change_data_format(self, _value):
        self.show_data()
        self.redraw_plot()

    def calculate_temp_from_resistance(self, cal_res, cal_beta, cal_res0, val_max, val_meas):
        ntc_res = self.calculate_ntc_resistance(cal_res, val_max, val_meas) / 1000

        temperature = 1/(np.log(ntc_res/cal_res0)/cal_beta + 1/298.15) - 273.15
        
        return temperature

    def calculate_ntc_resistance(self, cal_res, val_max, val_meas):
        if isinstance(val_meas, int):
            if val_meas == 0:
                return 0
        elif not val_meas.any():
            return np.zeros_like(val_meas)
        cal_res = cal_res

        ntc_res = cal_res / (val_max / val_meas - 1)

        return ntc_res

    def convert_array(self, array, conversion_type):
        return np.array([self.convert_data(d, conversion_type) for d in array])

    def convert_data(self, data, conversion_type):
        if conversion_type == "Voltage":
            max_voltage = module_version_features[self.parent.version]['voltage']
            resolution = module_version_features[self.parent.version]['resolution']
            max_val = 2**resolution
            ratio = data / max_val
            voltage = ratio * max_voltage
            return voltage
        elif conversion_type == "Temperature":
            resolution = module_version_features[self.parent.version]['resolution']
            max_val = 2**resolution
            temperature = self.calculate_temp_from_resistance(int(self.cal_resistor_input.text()), float(self.cal_beta_input.text()), int(self.cal_res_0_input.text()) / 1000, max_val, data)
            return temperature
        elif conversion_type == "Resistance":
            resolution = module_version_features[self.parent.version]['resolution']
            max_val = 2**resolution
            resistance = np.rint(self.calculate_ntc_resistance(int(self.cal_resistor_input.text()), max_val, data))
            return resistance
        else:
            return data

    def show_data(self):
        data = int(self.last_read_data)
        result = self.convert_data(data, self.data_format_options.currentText())
        if self.data_format_options.currentText() == "Voltage":
            self.data_label.setText(f'Data: {round(result, 4)} V')
        elif self.data_format_options.currentText() == "Temperature":
            self.data_label.setText(f'<span>Data: {round(result, 3)} &#176;C</span>')
        elif self.data_format_options.currentText() == "Resistance":
            self.data_label.setText(f'<span>Data: {round(result)} &#8486;</span>')
        else:
            self.data_label.setText(f'Data: {result}')

    def read_pin(self):
        self.intercept_single = True
        self.parent.send_data(f'D,{self.pin_num},R')

    def handle_data(self, command, is_input, data):
        if command == 'd':
            self.receive_data(data)
        elif command == 'D':
            self.receive_data(data)

    def sync(self):
        self.activate()

class NTCParameterWidget(QtWidgets.QGroupBox):
    def __init__(self, parent, pin_num, units, name, default, command):
        super(QtWidgets.QGroupBox, self).__init__(name)
        self.parent = parent
        self.command = command
        self.pin_num = pin_num
        self.setStyleSheet('QGroupBox {font-weight: bold;}')
        
        layout = QtWidgets.QVBoxLayout()
        
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
        self.parent.send_data(f'D,{self.pin_num},{self.command},{self.get_value()};')

    def get_value(self):
        return self.data_input.text()

class InputSliderWidget(QtWidgets.QWidget):
    valueChanged = pyqtSignal(int)

    def __init__(self, parent, name, min_val, max_val, default_val, use_slider=True):
        super(QtWidgets.QWidget, self).__init__()

        self.parent = parent
        
        self.layout = QtWidgets.QHBoxLayout(self)

        self.name_label = QtWidgets.QLabel(name)
        self.layout.addWidget(self.name_label)

        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(min_val))
        self.slider.setMaximum(int(max_val))
        self.slider.setValue(int(default_val))
        self.slider.valueChanged.connect(self.slider_value_changed)
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
        self.slider.setSizePolicy(size_policy)
        if use_slider:
            self.layout.addWidget(self.slider)

        self.value_input = QtWidgets.QLineEdit()
        self.value_input.setText(str(default_val))
        self.value_input.setAlignment(Qt.AlignRight)
        self.value_input.setValidator(QtGui.QIntValidator(min_val, max_val))
        self.value_input.textChanged.connect(self.input_value_changed)
        self.layout.addWidget(self.value_input)

    def slider_value_changed(self, value):
        self.value_input.setText(str(value))
        self.valueChanged.emit(value)

    def input_value_changed(self, value):
        if not value:
            value = 0
        self.slider.setValue(int(value))
        self.valueChanged.emit(int(value))
