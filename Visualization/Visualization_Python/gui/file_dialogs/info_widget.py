import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt

from utils.constants import CLOSE, SIMULATOR_INSTRUCTIONS, READ
from utils.paths import INFO_WIDGET_CSS
from utils.error_messages import WarningMessages ,ErrorMessages



class InfoDialog(QDialog):
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            self.setWindowTitle(SIMULATOR_INSTRUCTIONS)  # Set the title of the dialog
            size_x, size_y, width, height = 300, 300, 600, 400
            self.setGeometry(size_x, size_y, width, height)  # Set the initial size and position of the dialog

            # Load the stylesheet from the CSS file
            self.load_stylesheet(INFO_WIDGET_CSS)

            layout = QVBoxLayout()

            # Instructions text with added margins between lines using HTML
            instructions = """
            <h2 style="color: #2980b9;">Simulator Instructions</h2>
            <p style="color: #2c3e50; font-size: 15px; margin-bottom: 20px;">
            <span style="font-weight: bold;">•</span> To move to the next layer, click on the corresponding element.<br><br>
            <span style="font-weight: bold;">•</span> Right-click on any element to view its logs.<br><br>
            <span style="font-weight: bold;">•</span> Colored elements indicate they contain logs.<br><br>
            <span style="font-weight: bold;">•</span> Use the toolbar to navigate between Host Interface, DIE1, DIE2, and more.<br><br>
            <span style="font-weight: bold;">•</span> Click "Filter" to open the filter menu and refine your view.
            </p>
            """
            self.label = QLabel(instructions)
            self.label.setWordWrap(True)
            self.label.setAlignment(Qt.AlignTop)
            self.label.setTextFormat(Qt.RichText)

            layout.addWidget(self.label)

            button_layout = QHBoxLayout()
            self.close_button = QPushButton(CLOSE)
            self.close_button.clicked.connect(self.close)
            button_layout.addStretch(1)
            button_layout.addWidget(self.close_button)
            layout.addLayout(button_layout)

            self.setLayout(layout)

            # Center the dialog on the parent window
            self.setWindowModality(Qt.ApplicationModal)
            if self.parent():
                num_elements = 2
                self.move(self.parent().x() + (self.parent().width() - self.width()) // num_elements,
                          self.parent().y() + (self.parent().height() - self.height()) // num_elements)

        except Exception as e:
            self.show_error_message(ErrorMessages.ERROR_OCCURRED.value.format(error=e))

    def load_stylesheet(self, filename):
        """Load a stylesheet from a file and set it to the dialog."""
        try:
                with open(filename, READ) as file:
                    stylesheet = file.read()
                    self.setStyleSheet(stylesheet)
        except FileNotFoundError as fnf_error:
            self.show_error_message(WarningMessages.STYLE_SHEET_FILE_NOT_FOUND.value.format(filename=filename))
        except Exception as e:
            self.show_error_message(ErrorMessages.ERROR_OCCURRED.value.format(error=e))


    def show_error_message(self, message):
        """Display an error message to the user in a popup."""
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle(ErrorMessages.ERROR.value)
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.exec_()
