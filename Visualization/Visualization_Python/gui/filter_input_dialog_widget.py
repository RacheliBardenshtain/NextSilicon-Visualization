import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QFormLayout, QMessageBox, QWidget, QScrollArea)
from PyQt5.QtCore import Qt
from utils.type_names import AREAS, UNITS, DIE1, DIE2, DIE
from utils.filter_types import FILTER_TYPES_NAMES, CLUSTER, QUAD, THREADID, IO, AREA, UNIT
from utils.constants import WHITE ,X_BUTTON, RED,ROW, COLUMN, READ,ENTER_VALUES_FOR_FILTER
from utils.paths import DIALOG_FILTAR_CSS
from utils.error_messages import WarningMessages
from utils.filter_manager import FilterManager

class FilterInputDialogWidget(QDialog):

    def __init__(self, filter_type: str, filters_manager:FilterManager, parent=None) -> None:
        """Initialize the dialog with a filter name."""
        super().__init__(parent)
        self.parent = parent  # Reference to the parent widget
        self.filter_type=filter_type
        self.filters_manager = filters_manager
        self.filters = self.filters_manager.filters
        self.input_fields={}
        self.ThreadId_array = self.filters['ThreadId'].values  # Initialize ThreadId_array
        self.initUI()

    def initUI(self) -> None:
        """Initialize the user interface for the dialog."""
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(ENTER_VALUES_FOR_FILTER.format(filter_type=self.filter_type))
        self.setFixedSize(600, 450)  # Set a fixed size for the dialog

        self.load_stylesheet(DIALOG_FILTAR_CSS)
        self.setLayout(QVBoxLayout())  # Set the main layout of the dialog

        self.form_layout = QFormLayout()  # Initialize the form layout
        self.layout().addLayout(self.form_layout)  # Add form layout to main layout
        self.setup_form_fields()  # Set up form fields based on filter_type
        self.setup_buttons()

    def setup_form_fields(self) -> None:
        """Create and add form fields based on the filter name."""
        try:
            filter = self.filters[self.filter_type]
            option = filter.value_options.items()
            for key, value in option:
                if not value:  # If the value is an empty array
                    self.input_to_filter = QLineEdit(self)  # Use QLineEdit
                    self.input_to_filter.setPlaceholderText("Enter an integer")  # Placeholder text
                    self.form_layout.addRow("TID", self.input_to_filter)
                else:
                    self.input_to_filter = QComboBox(self)
                    self.input_to_filter.addItems(value)
                    self.form_layout.addRow(key, self.input_to_filter)
                    # Store the input field in the dictionary with the key as the identifier
                    if filter.is_active:
                        self.input_to_filter.setCurrentText(filter.values[key])
                self.input_fields[key] = self.input_to_filter

            if self.filter_type == FILTER_TYPES_NAMES[THREADID]:
                full_width_layout = QVBoxLayout()
                self.error_label = QLabel(self)
                self.error_label.setStyleSheet(
                    f"color: {RED}; font-size: 15px; background: transparent; border: none; padding-top: 1px;")
                self.error_label.hide()
                self.form_layout.addRow(self.error_label)

                scroll_area = QScrollArea(self)
                scroll_area.setWidgetResizable(True)

                # Create a QWidget to hold the list of Thread IDs
                thread_id_widget = QWidget()
                thread_id_layout = QVBoxLayout(thread_id_widget)

                # Ensure there are Thread IDs to display
                if self.ThreadId_array:
                    # Add each Thread ID with a red X button
                    for thread_id in self.ThreadId_array:
                        self.tid_layout = QHBoxLayout()  # Horizontal layout for TID and X button
                        # Create the Thread ID label
                        label = QLabel(str(thread_id), self)
                        label.setAlignment(Qt.AlignLeft)
                        label.setStyleSheet("font-size: 18px; padding: 10px;")
                        # Create the red X button
                        remove_button = QPushButton(X_BUTTON, self)
                        remove_button.setStyleSheet(""" QPushButton {
                                        background-color: red;
                                        color: white;
                                        border: none;
                                        font-size: 16px;
                                        width: 30px;
                                        height: 30px;
                                    }
                                    QPushButton:hover {
                                        background-color: darkred;
                                    }
                                """)
                        remove_button.clicked.connect(lambda _, tid=thread_id: self.remove_tid(tid))
                        # Add the Thread ID label and X button to the horizontal layout
                        self.tid_layout.addWidget(label)
                        self.tid_layout.addWidget(remove_button)
                        self.tid_layout.addStretch()  # Add stretch to push the button to the right

                        # Add the horizontal layout to the main thread ID layout
                        thread_id_layout.addLayout(self.tid_layout)

                # Set the thread ID layout in the widget
                thread_id_widget.setLayout(thread_id_layout)
                scroll_area.setWidget(thread_id_widget)
                # Add the scroll area with full width
                full_width_layout.addWidget(scroll_area)
                # Add the full width layout to the main layout
                self.layout().addLayout(full_width_layout)

        except AttributeError as e:
            QMessageBox.critical(self, "Configuration Error", "Invalid filter type configuration.")
            self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred: {str(e)}")
            print(f"error:{e}")
            self.reject()

    def remove_tid(self, tid):
        self.filters_manager.remove_tid(tid)
        self.accept()

    def update_tid_display(self):
        # Rebuild the TID list
        for thread_id in self.ThreadId_array:
            tid_item = QHBoxLayout()

            label = QLabel(str(thread_id), self)
            label.setAlignment(Qt.AlignLeft)
            label.setStyleSheet("font-size: 18px; padding: 10px;")

            remove_button = QPushButton(X_BUTTON, self)
            remove_button.setStyleSheet("""
                QPushButton {
                    background-color: red;
                    color: white;
                    border: none;
                    font-size: 16px;
                    width: 30px;
                    height: 30px;
                }
                QPushButton:hover {
                    background-color: darkred;
                }
            """)
            remove_button.clicked.connect(lambda _, tid=thread_id: self.remove_tid(tid))

            tid_item.addWidget(label)
            tid_item.addWidget(remove_button)
            tid_item.addStretch()


        # Update the main layout if needed
        self.form_layout.addRow(self.tid_layout)
        self.form_layout.addWidget(self.error_label)  # Ensure error label is still shown if necessary

    def check_input(self) -> None:
            text = self.tid_input.text()
            try:
                tid_value = int(text)

                # If conversion succeeds, enable the apply button and hide error label
                self.apply_button.setEnabled(True)
                self.tid_input.setStyleSheet("")
                self.error_label.hide()

            except ValueError:
                # If conversion fails, show the error message
                self.apply_button.setEnabled(False)
                self.tid_input.setStyleSheet(f"border: 1px solid {RED};")
                self.error_label.setText("Please enter a valid number.")
                self.error_label.show()

    def setup_buttons(self) -> None:
        """Create and add buttons to the dialog."""
        button_layout = QVBoxLayout()
        try:
            self.apply_button = QPushButton("apply", self)
            self.apply_button.clicked.connect(self.apply_filter)
            button_layout.addWidget(self.apply_button)
            self.cancel_button = QPushButton("cancel", self)
            self.cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(self.cancel_button)
            self.layout().addLayout(button_layout)  # Add buttons to the main layout

        except Exception as e:
         QMessageBox.critical(self, "Button Setup Error", f"Failed to set up buttons: {str(e)}")

    def apply_filter(self) -> None:
        """Validate and apply the filter based on user input."""
        try:
            filter = self.filters[self.filter_type]
            values = {}
            for key in filter.value_options.keys():
                input_widget = self.input_fields.get(key)
                if isinstance(input_widget, QComboBox):
                    values[key] = input_widget.currentText()  # Store the selected value
                elif isinstance(input_widget, QLineEdit):
                    values[key] = int(input_widget.text().strip())  # Store the entered text

            if self.filter_type == 'ThreadId':
                filter.values.append(values['TID'])
                print(filter.values)
            else:
                filter.values = values  # Update the values in the filter
            if not self.filter_type == 'ThreadId':
                ready_for_filter = {}
                for key, value in filter.value_options.items():
                    input_widget = self.input_fields[key]  # Get the input widget from the dictionary
                    if key == 'die' or key == 'quad' or key == 'chip':
                        ready_for_filter[key] = int(input_widget.currentIndex())
                        if key == 'quad' and ready_for_filter['die'] == 1:
                            ready_for_filter[key] = 3 - ready_for_filter[key]
                    elif isinstance(input_widget, QComboBox):  # If the input is a QComboBox
                        ready_for_filter[key] = input_widget.currentText()  # Store the selected value
                    elif isinstance(input_widget, QLineEdit):  # If the input is a QLineEdit
                        ready_for_filter[key] = input_widget.text().strip()  # Store the entered text
                    if key == 'row' or key == 'column':
                        ready_for_filter[key] = int(ready_for_filter[key])
                filter.ready_for_filter = ready_for_filter
                # Apply the filter with the collected values
            else:
                filter.ready_for_filter = filter.values

            if not values == {}:
                self.filters_manager.apply_filter(self.filter_type)
                self.accept()
            else:
                QMessageBox.warning(self, "Input Error", "No valid values provided.")


        # except AttributeError:
        #     QMessageBox.critical(self, "System Error", "An error occurred. Please try again.")
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred: {str(e)}")

    def load_stylesheet(self, filename):
        """Load a stylesheet from a file and set it to the dialog."""
        if os.path.exists(filename):
            with open(filename, READ) as file:
                stylesheet = file.read()
                self.setStyleSheet(stylesheet)
        else:
            print(WarningMessages.STYLE_SHEET_FILE_NOT_FOUND.value.format(filename=filename))


