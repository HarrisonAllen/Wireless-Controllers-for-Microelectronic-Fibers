from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

class WelcomeWidget(QtWidgets.QScrollArea):
    def __init__(self, parent, appctxt):
        super(QtWidgets.QFrame, self).__init__()
        self.parent = parent
        self.appctxt = appctxt

        self.base_widget = QtWidgets.QFrame()
        self.base_layout = QtWidgets.QVBoxLayout(self)
        self.base_widget.setLayout(self.base_layout)

        self.welcome_text = QtWidgets.QLabel()
        text_contents = open(appctxt.get_resource('Files/Welcome.html'), 'r').read()
        converted_text = self.replace_with_appctxt_resource(text_contents)
        self.welcome_text.setText(converted_text)
        self.welcome_text.setWordWrap(True)
        self.welcome_text.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.base_layout.addWidget(self.welcome_text)

        self.base_widget.setLayout(self.base_layout)

        self.base_layout.addStretch()

        self.setWidgetResizable(True)
        self.setWidget(self.base_widget)
        
    def replace_with_appctxt_resource(self, to_replace):
        start_pos = to_replace.find('{{')
        if start_pos == -1:
            return to_replace
        end_pos = to_replace.find('}}', start_pos)
        substr = to_replace[start_pos:end_pos+2]
        og_filename = substr[2:-2]
        new_filename = self.appctxt.get_resource(og_filename)
        replaced = to_replace.replace(substr, new_filename)
        return self.replace_with_appctxt_resource(replaced)