
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QLabel, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt

class CardToolbar(QWidget):

    def __init__(self, *args,**kwargs) -> None:
        super().__init__(*args,**kwargs)
        self.setObjectName('card-toolbar')
        self.layout = QHBoxLayout()
        save = QLabel()
        save.setObjectName('save-btn')
        from fonts.font import loadFont
        font = loadFont("Font Awesome-400.otf")
        save.setFont(font)
        save.setText("\uf02e")
        self.layout.addWidget(save)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)