from PySide2 import QtGui
from PySide2.QtWidgets import QWidget, QPushButton, QGroupBox, QVBoxLayout, QGridLayout


class Ui_FE14MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.chapters_button = QPushButton("Chapters")
        self.characters_button = QPushButton("Characters")
        self.items_button = QPushButton("Items")
        self.classes_button = QPushButton("Classes")
        self.skills_button = QPushButton("Skills")

        core_box = QGroupBox("Core Data")
        core_layout = QVBoxLayout()
        core_layout.setAlignment(QtGui.Qt.AlignTop)
        core_layout.addWidget(self.chapters_button)
        core_layout.addWidget(self.characters_button)
        core_layout.addWidget(self.items_button)
        core_layout.addWidget(self.classes_button)
        core_layout.addWidget(self.skills_button)
        core_box.setLayout(core_layout)

        self.edit_dialogue_button = QPushButton("Edit Dialogue")

        misc_box = QGroupBox("Misc.")
        misc_layout = QVBoxLayout()
        misc_layout.setAlignment(QtGui.Qt.AlignTop)
        misc_layout.addWidget(self.edit_dialogue_button)
        misc_box.setLayout(misc_layout)

        layout = QGridLayout()
        layout.addWidget(core_box, 0, 0)
        layout.addWidget(misc_box, 1, 0)

        self.setLayout(layout)