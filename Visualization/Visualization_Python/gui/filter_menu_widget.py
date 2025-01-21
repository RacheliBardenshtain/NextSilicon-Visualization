from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QMenu, QLabel, QWidgetAction, QPushButton, QHBoxLayout, QWidget, QMessageBox
from gui.filter_input_dialog_widget import FilterInputDialogWidget
from utils.constants import POINTING_CURSOR, FILTER
from utils.filter_manager import FilterManager
from gui.filter_tooltip_widget import FilterTooltipWidget

class FilterMenuWidget(QMenu):
    def __init__(self, parent=None):
        super().__init__(f'{FILTER} ▼', parent)
        self.parent = parent
        self.filterManager = FilterManager(self)
        self.filters = self.filterManager.filters
        self.tooltip = FilterTooltipWidget(self)
        self.tooltip_visible = False  # Flag for tooltip visibility management
        self.current_filter = None  # Store the current filter
        self.initUI()

    def initUI(self) -> None:
        self.setStyleSheet(""" 
            QMenu {
                background-color: #2d2d2d; 
                border: 1px solid #000; 
            }
            QMenu::item:selected {
                background-color: #555; 
            }
        """)

        self.hovered.connect(lambda: self.parent.setCursor(POINTING_CURSOR))

        self.actions = {}
        for filter_type in self.filters.keys():
            widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)

            label = QLabel(filter_type)
            label.setStyleSheet("padding: 8px 20px; color: white; background-color: #2d2d2d;")
            layout.addWidget(label)

            # Add hover event
            label.enterEvent = lambda event, name=filter_type: self.show_tooltip(name, event.globalPos())
            label.leaveEvent = lambda event: self.hide_tooltip()

            # Add "X" button
            remove_button = QPushButton("X")
            remove_button.setFixedWidth(30)
            remove_button.setStyleSheet(""" 
                QPushButton {
                    border: none; 
                    background-color: #ff4d4d; 
                    color: white; 
                    font-weight: bold; 
                }
                QPushButton:hover {
                    background-color: #ff6666; 
                    border: 1px solid grey; 
                }
            """)
            remove_button.clicked.connect(lambda _, ft=filter_type: self.filterManager.remove_filter(ft))
            layout.addWidget(remove_button)
            remove_button.hide()  # Hide the "X" button initially

            # Arrow button for additional options or input
            arrow_button = QPushButton("➕" if filter_type == 'ThreadId' else "🖋️")
            arrow_button.setFixedWidth(30)
            arrow_button.setStyleSheet(""" 
                QPushButton {
                    border: none; 
                    background-color: #2d2d2d; 
                    color: white; 
                    font-weight: bold; 
                }
                QPushButton:hover {
                    background-color: #0069d9; 
                    border: 1px solid grey; 
                }
            """)
            arrow_button.clicked.connect(lambda _, ft=filter_type: self.show_input_dialog(ft))
            layout.addWidget(arrow_button)
            arrow_button.hide()  # Hide the arrow button initially

            widget.setLayout(layout)
            action = QWidgetAction(self)
            action.setDefaultWidget(widget)
            self.addAction(action)

            # Connect action trigger to filter selection
            label.mouseReleaseEvent = lambda event, name=filter_type: self.filter_selected(name)

            # Store actions without the buttons
            self.actions[filter_type] = (label, remove_button, arrow_button)

        self.add_clear_filters_button()
        self.update_filter_Text()

    def show_tooltip(self, filter_type: str, global_pos):
        """Show tooltip information for the filter"""
        if self.current_filter != filter_type:  # Check if the current filter is different
            if self.filters[filter_type].is_active:
                values = self.filters[filter_type].ready_for_filter
                if filter_type == 'ThreadId':
                    values_str = ', '.join([f"TID: {values}"])
                else:
                    values_str = ', '.join([f"{key}: {value}" for key, value in values.items()])
                self.tooltip.setText(f"This filter is filtering by: {values_str}")
            else:
                self.tooltip.setText("This filter is inactive")

            self.tooltip.showTooltip(global_pos + QPoint(-30, -10))  # Slight adjustment
            self.tooltip_visible = True  # Mark that the tooltip is open
            self.current_filter = filter_type  # Update the current filter

    def hide_tooltip(self):
        """Hide the tooltip window"""
        self.tooltip.hideTooltip()
        self.tooltip_visible = False  # Mark that the tooltip is closed
        self.current_filter = None  # Clear the current filter

    def add_clear_filters_button(self) -> None:
        """Add a button to clear all filters."""
        clear_button = QPushButton('Clear Filters')
        clear_button.setStyleSheet(""" 
            QPushButton {
                padding: 8px 20px; 
                color: white; 
                background-color: #d9534f; 
                border: none; 
                border-radius: 5px; 
            }
            QPushButton:hover {
                background-color: #c9302c; 
            }
        """)
        clear_button.clicked.connect(self.filterManager.clear_all_filters)

        # Create a QWidgetAction for the button
        action = QWidgetAction(self)
        action.setDefaultWidget(clear_button)
        self.addAction(action)

    def filter_selected(self, filter_type: str) -> None:
        """Handle filter selection."""
        if not self.filters[filter_type].is_active:
            # Add filter and show the input dialog
            self.show_input_dialog(filter_type)

    def update_filter_Text(self) -> None:
        print("Updating text in filter")
        """Update the styles of the menu items based on the selected filters."""
        for filter_type, (label, remove_button, arrow_button) in self.actions.items():
            if self.filters[filter_type].is_active:
                label.setText(f"{filter_type}  ✓")
                remove_button.show()
                arrow_button.show()
                label.setToolTip(f"Filter active: {self.filters[filter_type].ready_for_filter}")  # Active values
                label.mouseReleaseEvent = lambda event: None  # Disable clicking on the label
            else:
                label.setText(filter_type)
                remove_button.hide()
                arrow_button.hide()
                label.setToolTip("This filter is inactive")
                label.mouseReleaseEvent = lambda event, name=filter_type: self.filter_selected(name)  # Enable clicking

    def show_input_dialog(self, filter_type: str) -> None:
        """Show the input dialog for the selected filter."""
        dialog = FilterInputDialogWidget(filter_type, self.filterManager, self)
        dialog.exec_()
