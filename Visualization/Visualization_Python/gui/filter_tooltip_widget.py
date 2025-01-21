from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

class FilterTooltipWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        self.label = QLabel()
        self.label.setStyleSheet(
            "color: white; background-color: rgba(45, 45, 45, 200); padding: 5px; border-radius: 5px;")
        layout.addWidget(self.label)

        self.setLayout(layout)
        self.hide()

    def setText(self, text):
        self.label.setText(text)
        self.adjustSize()

    def showTooltip(self, pos):
        self.move(pos)
        self.show()

    def hideTooltip(self):
        self.hide()


