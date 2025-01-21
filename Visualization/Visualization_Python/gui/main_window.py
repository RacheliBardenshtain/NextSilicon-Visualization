import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QApplication, QMainWindow, QLabel,
    QPushButton, QToolBar, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QPropertyAnimation
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie

from gui.die_widget import DieWidget
from gui.host_interface_widget import HostInterfaceWidget
from gui.log_colors_dialog import LogColorDialog
from gui.timeline_widget import TimelineWidget
from gui.filter_menu_widget import FilterMenuWidget
from gui.packets_colors import get_colors_by_tids
from gui.file_dialogs.info_widget import InfoDialog
from gui.worker_thread import WorkerThread

from utils.data_manager import DataManager
from utils.paths import APP_ICON_IMAGE, INSTRUCTIONS_ICON_IMAGE, LOADING_ICON_IMAGE, STYLES_CSS
from utils.type_names import HOST_INTERFACE, DIE1, DIE2, DIE2DIE, DIE
from utils.constants import TID, PACKET, LIGHTGRAY, WHITE, BLACK, FORBIDDEN_CURSOR, SIMULATOR, MAIN_TOOLBAR, \
    FILTER, GRAY, READ, MAIN_WINDOW, FILTER_MENU_WIDGET, HOST_INTERFACE_WIDGET, DIE_WIDGET, \
    TIME_LINE_WIDGET, UTF_8, TRANSPARENT, DIES, ANIMATION, WAIT_PROCESSING, TOOL_BAR, LIGHTBLUE, CLIK_FOR_INSTRUCTIONS, \
    COMPONENT_LOGS, OVERLAY
from utils.error_messages import ErrorMessages, WarningMessages


class MainWindow(QMainWindow):
    DIE_1_INDEX = 0
    DIE_2_INDEX = 1

    def __init__(self, data_manager: DataManager):
        try:
            super().__init__()
            self.die_widget = None
            self.data_manager = data_manager
            self.is_closing = False
            self.host_interface_widget = None
            self.dies = {}
            self.load_dies()
            self.initUI()
            self.fade_in()
        except Exception as e:
            self.show_error_message(ErrorMessages.INITIALIZING.value.format(file_name=MAIN_WINDOW, error=str(e)))
            self.dies = {}
            self.initUI()

    def initUI(self) -> None:
        try:
            self.setWindowTitle(SIMULATOR)
            icon_path = os.path.join(os.getcwd(), APP_ICON_IMAGE)
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))

            self.setGeometry(100, 100, 800, 600)
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.main_layout = QVBoxLayout(self.central_widget)

            try:
                self.filter_menu = FilterMenuWidget(self)
            except Exception as e:
                self.show_warning_message(
                    WarningMessages.CREATING_WIDGET.value.format(widget=FILTER_MENU_WIDGET, error=str(e)))
                self.filter_menu = QWidget()  # Fallback empty widget

            self.create_top_layout()
            self.create_scroll_area()
            self.create_timeline_widget()
            self.create_navbar()

            try:
                self.host_interface_widget = HostInterfaceWidget(self.data_manager.host_interface)
                self.die_widget = DieWidget(self.data_manager, self.dies, self)
                self.die_widget.setVisible(False)
            except Exception as e:
                self.show_warning_message(
                    WarningMessages.CREATING_WIDGET.value.format(file_name=HOST_INTERFACE_WIDGET + DIE_WIDGET,
                                                                 error=str(e)))

            self.apply_stylesheet()

        except Exception as e:
            self.show_error_message(ErrorMessages.ERROR_OCCURRED.value.format(error=e))
            # Create minimal UI to prevent crashes
            if not self.central_widget:
                self.central_widget = QWidget()
                self.setCentralWidget(self.central_widget)
                self.main_layout = QVBoxLayout(self.central_widget)

    def fade_in(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def create_top_layout(self) -> None:
        self.top_layout = QVBoxLayout()
        self.main_layout.addLayout(self.top_layout)

    def create_scroll_area(self) -> None:
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content_widget = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content_widget)
        self.scroll_content_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidget(self.scroll_content_widget)
        self.main_layout.addWidget(self.scroll_area)

    def create_timeline_widget(self) -> None:
        """ Create the timeline widget for event tracking"""
        try:
            self.timeline_widget = TimelineWidget(
                self.data_manager, self.data_manager.get_start_time(), self.data_manager.get_end_time(),
                main_window=self
            )
            self.top_layout.addWidget(self.timeline_widget)
        except Exception as e:
            self.show_warning_message(
                WarningMessages.CREATING_WIDGET.value.format(widget=TIME_LINE_WIDGET, error=str(e)))
            self.timeline_widget = QWidget()  # Fallback empty widget
            self.top_layout.addWidget(self.timeline_widget)

    def create_navbar(self) -> None:
        try:
            if hasattr(self, TOOL_BAR) and self.toolBar:
                self.removeToolBar(self.toolBar)
                self.toolBar = None

            self.toolBar = QToolBar(MAIN_TOOLBAR)
            self.toolBar.setStyleSheet(f"background-color: {LIGHTGRAY}; width: 220px; height: 60px;")
            self.addToolBar(self.toolBar)

            # Host Interface Button
            try:
                host_interface_colors = self.get_data_colors(self.data_manager.host_interface)
                self.host_interface_button = QPushButton(f'{HOST_INTERFACE} 🖥')
                if host_interface_colors and self.has_active_logs(self.data_manager.host_interface):
                    first_color = 0
                    self.host_interface_button.setStyleSheet(
                        f"background-color: {host_interface_colors[first_color]}; color: {BLACK}; padding: 10px;"
                    )
                else:
                    self.host_interface_button.setEnabled(False)
                self.host_interface_button.clicked.connect(self.show_host_interface)
                self.host_interface_button.setContextMenuPolicy(Qt.CustomContextMenu)
                self.host_interface_button.customContextMenuRequested.connect(self.show_host_interface_logs_and_colors)
                self.toolBar.addWidget(self.host_interface_button)
            except AttributeError:
                self.show_error_message(WarningMessages.ERROR_ACCESSING_DATA.value.format(object=HOST_INTERFACE))
            except IndexError:
                self.show_error_message(WarningMessages.NO_COLORS_AVAILABLE.value.format(object=HOST_INTERFACE))

            # DIE1 Button
            try:
                die1_colors = self.get_data_colors(self.dies.get(self.DIE_1_INDEX))
                self.die1_button = self.create_toolbar_button(f'{DIE1} 🔲', self.show_die1, index=self.DIE_1_INDEX)
                if not self.is_die1_enable():
                    self.die1_button.setEnabled(False)
                self.toolBar.addWidget(self.die1_button)
            except Exception as e:
                self.show_error_message(WarningMessages.CREATING_WIDGET.value.format(widget=DIE1, error=str(e)))

            # DIE2 Button
            try:
                self.die2_button = self.create_toolbar_button(f'{DIE2} 🔲', self.show_die2, index=self.DIE_2_INDEX)
                if not self.is_die2_enable():
                    self.die2_button.setEnabled(False)
                    self.die2_button.setStyleSheet(f"background-color: {LIGHTGRAY}; color: {GRAY}; padding: 10px;")
                self.toolBar.addWidget(self.die2_button)
            except Exception as e:
                self.show_error_message(WarningMessages.CREATING_WIDGET.value.format(widget=DIE2, error=str(e)))

            # DIE2DIE Button
            try:
                die2die_colors = self.get_data_colors(self.data_manager.die2die)
                self.die2die_button = QPushButton(f'{DIE2DIE} 🔲 ↔️ 🔲')
                if die2die_colors:
                    self.die2die_button.setStyleSheet(
                        f"padding: 10px; background-color: {die2die_colors[0]}; color: {BLACK};"
                    )
                else:
                    self.die2die_button.setStyleSheet(f"padding: 10px; background-color: #6e6e6e; color: {WHITE};")
                self.die2die_button.clicked.connect(self.clear_content)
                self.die2die_button.setContextMenuPolicy(Qt.CustomContextMenu)
                self.die2die_button.customContextMenuRequested.connect(self.show_die2die_logs)
                self.toolBar.addWidget(self.die2die_button)
            except AttributeError:
                self.show_error_message(WarningMessages.ERROR_ACCESSING_DATA.value.format(object=DIE2DIE))
            except IndexError:
                self.show_error_message(WarningMessages.NO_COLORS_AVAILABLE.value.format(object=DIE2DIE))

            # Filter Button
            self.filter_button = QPushButton(f'{FILTER} ▼')
            self.filter_button.setStyleSheet(f"background-color: #6e6e6e; color: {WHITE}; padding: 10px;")
            self.filter_button.clicked.connect(self.show_filter_menu)
            self.toolBar.addWidget(self.filter_button)

            # Filter Menu
            self.filter_menu.setVisible(False)
            self.filter_menu.setStyleSheet(f"background-color: {LIGHTBLUE};")
            self.filter_menu.raise_()
            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.toolBar.addWidget(spacer)

            # Info Button
            self.info_button = QPushButton()
            self.info_button.setToolTip(CLIK_FOR_INSTRUCTIONS)
            self.info_button.setIcon(QIcon(INSTRUCTIONS_ICON_IMAGE))
            self.info_button.setIconSize(QSize(34, 34))
            self.info_button.setStyleSheet(f"padding: 6px; border: none; background: {TRANSPARENT};")
            self.info_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self.info_button.clicked.connect(self.show_info_dialog)
            self.toolBar.addWidget(self.info_button)

            try:
                with open(STYLES_CSS, READ, encoding=UTF_8) as f:
                    self.setStyleSheet(f.read())
            except FileNotFoundError:
                self.show_warning_message(WarningMessages.STYLE_SHEET_FILE_NOT_FOUND.value.format(filename=STYLES_CSS))

        except Exception as e:
            self.show_error_message(ErrorMessages.ERROR_OCCURRED.value.format(str(e)))

    def show_info_dialog(self) -> None:
        info_dialog = InfoDialog(self)
        info_dialog.exec_()

    def is_die1_enable(self) -> bool:
        return self.data_manager.die_objects[self.DIE_1_INDEX].is_enable and self.get_colors_for_index(self.DIE_1_INDEX)

    def is_die2_enable(self) -> bool:
        return self.data_manager.die_objects[self.DIE_2_INDEX].is_enable and self.get_colors_for_index(self.DIE_2_INDEX)

    def has_active_logs(self, data) -> bool:
        """Check if there are active logs in the given data"""
        return bool(data.get_attribute_from_active_logs(TID))  # Adjust the method as necessary

    def create_toolbar_button(self, text: str, click_action, index: int = None) -> QPushButton:
        button = QPushButton(text)
        colors = self.get_colors_for_index(index)
        if colors:
            button.setStyleSheet(f"background-color: {colors[0]}; color: {BLACK}; padding: 10px;")
        button.clicked.connect(click_action)
        button.setContextMenuPolicy(Qt.CustomContextMenu)
        button.customContextMenuRequested.connect(
            lambda: self.show_die_colors_and_logs(index) if index is not None else None
        )
        return button

    def get_colors_for_index(self, index: int) -> list:
        if index is None:
            return []
        die_data = self.dies.get(index)
        if die_data:
            tids = die_data.get_attribute_from_active_logs(TID)
            return list(get_colors_by_tids(tids))
        return []

    def get_data_colors(self, data) -> list:
        tids = data.get_attribute_from_active_logs(TID)
        return list(get_colors_by_tids(tids))

    def load_dies(self) -> None:
        """Load DIE1 and DIE2 from the data manager"""
        try:
            self.dies[self.DIE_1_INDEX] = self.data_manager.load_die(self.DIE_1_INDEX)
            self.dies[self.DIE_2_INDEX] = self.data_manager.load_die(self.DIE_2_INDEX)
        except Exception as e:
            self.show_error_message(ErrorMessages.LOADING.value.format(object=DIES, error=str(e)))
            self.dies = {self.DIE_1_INDEX: None, self.DIE_2_INDEX: None}  # Initialize with None to prevent crashes

    def apply_stylesheet(self) -> None:
        try:
            with open(STYLES_CSS, READ, encoding=UTF_8) as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            self.show_warning_message(WarningMessages.STYLE_SHEET_FILE_NOT_FOUND.value.format(filename=STYLES_CSS))

    def clear_content(self) -> None:
        for i in reversed(range(self.scroll_content_layout.count())):
            widget = self.scroll_content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def show_die1(self) -> None:
        # Show content for DIE1
        self.show_die(self.DIE_1_INDEX)

    def show_die2(self) -> None:
        # Show content for DIE2
        self.show_die(self.DIE_2_INDEX)

    def show_die(self, die_index: int) -> None:
        try:
            self.clear_content()
            if die_index not in self.dies:
                raise ValueError(WarningMessages.INVALID_DATA.value.format(component=DIE, data=die_index))
            if self.dies[die_index] is None:
                raise ValueError(ErrorMessages.LOADING.value.format(object=DIE, error=None))

            self.die_widget.setVisible(True)
            self.die_widget.setCursor(FORBIDDEN_CURSOR)
            self.scroll_content_layout.addWidget(self.die_widget)
            self.die_widget.show_quads(die_index)
        except Exception as e:
            self.show_warning_message(ErrorMessages.SHOWING_WIDGET.value.format(widget=DIE) + str(e))

    def show_host_interface(self) -> None:
        self.clear_content()
        try:
            self.host_interface_widget = HostInterfaceWidget(self.data_manager.host_interface)
            self.scroll_content_layout.addWidget(self.host_interface_widget)
        except Exception as e:
            self.show_warning_message(
                WarningMessages.CREATING_WIDGET.value.format(widget=HOST_INTERFACE_WIDGET, error=str(e)))
            self.host_interface_widget = QWidget()  # Fallback empty widget

    def show_host_interface_logs_and_colors(self, pos) -> None:
        dialog = LogColorDialog(self.data_manager.host_interface, COMPONENT_LOGS.format(component=HOST_INTERFACE), self)
        dialog.exec_()

    def show_die_colors_and_logs(self, index) -> None:
        die_data = self.dies.get(index)
        if die_data:
            die_index = index + 1
            dialog = LogColorDialog(die_data, COMPONENT_LOGS.format(component=DIE + str(die_index)), self)
            dialog.exec_()

    def show_die2die_logs(self, pos):
        dialog = LogColorDialog(self.data_manager.die2die, COMPONENT_LOGS.format(DIE2DIE), self)
        dialog.exec_()

    def show_filter_menu(self) -> None:
        try:
            if not self.filter_menu.isVisible():
                button_rect = self.filter_button.rect()
                global_pos = self.filter_button.mapToGlobal(button_rect.bottomLeft())
                menu_width = self.filter_menu.sizeHint().width()
                menu_height = self.filter_menu.sizeHint().height()
                self.filter_menu.setGeometry(global_pos.x(), global_pos.y(), menu_width, menu_height)
                self.filter_menu.show()
            else:
                self.filter_menu.hide()
        except Exception as e:
            self.show_error_message(ErrorMessages.ERROR_OCCURRED.value.format(error=str(e)))

    def show_wait_message(self, message):
        try:
            self.setWindowOpacity(0.95)
            self.overlay = QWidget(self)
            self.overlay.setGeometry(self.rect())
            self.overlay.setStyleSheet(f"background-color: {TRANSPARENT};")
            self.overlay.setWindowFlags(Qt.WindowStaysOnTopHint)

            self.gif_label = QLabel(self.overlay)
            self.gif_label.setAlignment(Qt.AlignCenter)
            gif_path = os.path.join(os.getcwd(), LOADING_ICON_IMAGE)

            if not os.path.exists(gif_path):
                raise FileNotFoundError(ErrorMessages.ERROR.value +
                                        ErrorMessages.FILE_NOT_FOUND.value.format(filename=LOADING_ICON_IMAGE))

            self.movie = QMovie(gif_path)
            self.movie.setScaledSize(QSize(200, 200))
            self.gif_label.setMovie(self.movie)
            self.gif_label.setGeometry(self.overlay.rect())

            self.overlay.show()
            self.movie.start()
            self.overlay.raise_()
            self.gif_label.raise_()
            QApplication.processEvents()
        except Exception as e:
            self.show_warning_message(ErrorMessages.LOADING.value.format(object=ANIMATION, error=str(e)))

    def hide_wait_message(self):
        if hasattr(self, OVERLAY):
            self.movie.stop()
            self.overlay.hide()
            self.overlay.deleteLater()
            del self.overlay
            self.setWindowOpacity(1.0)

    def perform_action_with_wait(self, action, *args):
        try:
            self.show_wait_message(WAIT_PROCESSING)
            self.worker_thread = WorkerThread(action, args)
            self.worker_thread.finished.connect(self.on_action_finished)
            self.worker_thread.start()
        except Exception as e:
            self.hide_wait_message()
            self.show_error_message(ErrorMessages.PROCESSING_ERROR.value.format(error=str(e)))

    def on_action_finished(self):
        self.hide_wait_message()
        self.clear_content()
        self.create_navbar()

    def change_filter(self, filter_type: str, values: list) -> None:
        self.perform_action_with_wait(self.data_manager.change_filter, filter_type, values)

    def update_filter_in_chain(self, filter_type: str, values: list) -> None:
        self.perform_action_with_wait(self.data_manager.update_filter_in_chain, filter_type, values)

    def clear_all_filters(self) -> None:
        self.perform_action_with_wait(self.data_manager.clear_all_filters)

    def filter_removal(self, filter_type) -> None:
        self.perform_action_with_wait(self.data_manager.filter_removal, filter_type)

    def fade_out_and_close(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.close)
        self.animation.start()

    def closeEvent(self, event):

        if not self.is_closing:
            event.ignore()
            self.is_closing = True
            self.fade_out_and_close()
        else:
            event.accept()

    def show_error_message(self, message: str) -> None:
        """Display an error message to the user in a popup."""
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle(ErrorMessages.ERROR.value)
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)
        error_box.exec_()

    def show_warning_message(self, message: str) -> None:
        """Display an warning message to the user in a popup."""
        warning_box = QMessageBox()
        warning_box.setIcon(QMessageBox.Warning)
        warning_box.setWindowTitle(WarningMessages.WARNING.value)
        warning_box.setText(message)
        warning_box.setStandardButtons(QMessageBox.Ok)
        warning_box.exec_()
