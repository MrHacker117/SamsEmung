from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QFormLayout,
                             QComboBox)
from PyQt6.QtCore import pyqtSignal
from config import CONFIG, save_config
from .font_manager import FontManager

class GlobalSettingsDialog(QDialog):
    settings_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Global Settings")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        # QEMU Path
        self.qemu_path_edit = QLineEdit(CONFIG['qemu_path'])
        qemu_path_button = QPushButton("Browse")
        qemu_path_button.clicked.connect(self.browse_qemu_path)
        qemu_path_layout = QHBoxLayout()
        qemu_path_layout.addWidget(self.qemu_path_edit)
        qemu_path_layout.addWidget(qemu_path_button)
        form_layout.addRow("QEMU Path:", qemu_path_layout)

        # QEMU Executable
        self.qemu_exec_edit = QLineEdit(CONFIG['qemu_executable'])
        form_layout.addRow("QEMU Executable:", self.qemu_exec_edit)

        # Font Selection
        self.font_combo = QComboBox()
        available_fonts = FontManager.load_fonts()
        self.font_combo.addItem("Default")
        self.font_combo.addItems(available_fonts)
        current_font = CONFIG.get('font', 'default')
        index = self.font_combo.findText(current_font)
        if index >= 0:
            self.font_combo.setCurrentIndex(index)
        form_layout.addRow("Application Font:", self.font_combo)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def browse_qemu_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select QEMU Directory")
        if path:
            self.qemu_path_edit.setText(path)

    def save_settings(self):
        CONFIG['qemu_path'] = self.qemu_path_edit.text()
        CONFIG['qemu_executable'] = self.qemu_exec_edit.text()
        CONFIG['font'] = self.font_combo.currentText()
        save_config(CONFIG)
        self.settings_updated.emit()
        self.accept()

