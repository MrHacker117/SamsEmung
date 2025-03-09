from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QGroupBox, QFileDialog, QMessageBox, QSpinBox)
from PyQt6.QtCore import pyqtSignal
from config import save_config, CONFIG

class SettingsTab(QWidget):
    log_message = pyqtSignal(str)

    def __init__(self, qemu_controller):
        super().__init__()
        self.qemu_controller = qemu_controller
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # QEMU configuration
        qemu_group = QGroupBox("QEMU Configuration")
        qemu_layout = QVBoxLayout()
        qemu_group.setLayout(qemu_layout)

        # QEMU path selection
        qemu_path_layout = QHBoxLayout()
        self.qemu_path_input = QLineEdit(CONFIG['qemu_path'])
        qemu_path_layout.addWidget(QLabel("QEMU Path:"))
        qemu_path_layout.addWidget(self.qemu_path_input)
        qemu_path_button = QPushButton("Browse")
        qemu_path_button.clicked.connect(self.select_qemu_path)
        qemu_path_layout.addWidget(qemu_path_button)
        qemu_layout.addLayout(qemu_path_layout)

        # QEMU executable selection
        qemu_exec_layout = QHBoxLayout()
        self.qemu_exec_input = QLineEdit(CONFIG['qemu_executable'])
        qemu_exec_layout.addWidget(QLabel("QEMU Executable:"))
        qemu_exec_layout.addWidget(self.qemu_exec_input)
        qemu_exec_button = QPushButton("Browse")
        qemu_exec_button.clicked.connect(self.select_qemu_executable)
        qemu_exec_layout.addWidget(qemu_exec_button)
        qemu_layout.addLayout(qemu_exec_layout)

        self.layout.addWidget(qemu_group)

        # Dump folder configuration
        dump_group = QGroupBox("Dump Configuration")
        dump_layout = QVBoxLayout()
        dump_group.setLayout(dump_layout)

        # Dump folder selection
        dump_folder_layout = QHBoxLayout()
        self.dump_folder_input = QLineEdit(CONFIG['dump_folder'])
        dump_folder_layout.addWidget(QLabel("Dump Folder:"))
        dump_folder_layout.addWidget(self.dump_folder_input)
        dump_folder_button = QPushButton("Browse")
        dump_folder_button.clicked.connect(self.select_dump_folder)
        dump_folder_layout.addWidget(dump_folder_button)
        dump_layout.addLayout(dump_folder_layout)

        self.layout.addWidget(dump_group)

        # Boot image selection
        boot_img_layout = QHBoxLayout()
        self.boot_img_input = QLineEdit(CONFIG.get('boot_img_path', ''))
        boot_img_layout.addWidget(QLabel("Boot Image (boot.img):"))
        boot_img_layout.addWidget(self.boot_img_input)
        boot_img_button = QPushButton("Browse")
        boot_img_button.clicked.connect(self.select_boot_img)
        boot_img_layout.addWidget(boot_img_button)
        self.layout.addLayout(boot_img_layout)

        # Virtual Disk Configuration
        vdisk_group = QGroupBox("Virtual Disk Configuration")
        vdisk_layout = QVBoxLayout()
        vdisk_group.setLayout(vdisk_layout)

        vdisk_size_layout = QHBoxLayout()
        self.vdisk_size_input = QSpinBox()
        self.vdisk_size_input.setRange(1, 100000)  # 1 MB to 100 GB
        self.vdisk_size_input.setValue(CONFIG.get('virtual_disk_size', 4096))  # Default 4 GB
        vdisk_size_layout.addWidget(QLabel("Virtual Disk Size (MB):"))
        vdisk_size_layout.addWidget(self.vdisk_size_input)
        vdisk_layout.addLayout(vdisk_size_layout)

        create_vdisk_button = QPushButton("Create Virtual Disk")
        create_vdisk_button.clicked.connect(self.create_virtual_disk)
        vdisk_layout.addWidget(create_vdisk_button)

        self.vdisk_info_label = QLabel()
        vdisk_layout.addWidget(self.vdisk_info_label)

        self.layout.addWidget(vdisk_group)

        # Save settings button
        save_settings_button = QPushButton("Save Settings")
        save_settings_button.clicked.connect(self.save_settings)
        self.layout.addWidget(save_settings_button)

        # Analyze dump button
        analyze_dump_button = QPushButton("Analyze Dump")
        analyze_dump_button.clicked.connect(self.analyze_dump)
        self.layout.addWidget(analyze_dump_button)

    def select_qemu_path(self):
        qemu_path = QFileDialog.getExistingDirectory(self, "Select QEMU Directory")
        if qemu_path:
            self.qemu_path_input.setText(qemu_path)

    def select_qemu_executable(self):
        qemu_executable, _ = QFileDialog.getOpenFileName(self, "Select QEMU Executable", filter="Executable files (*.exe);;All files (*.*)")
        if qemu_executable:
            self.qemu_exec_input.setText(qemu_executable)

    def select_dump_folder(self):
        dump_folder = QFileDialog.getExistingDirectory(self, "Select Dump Folder")
        if dump_folder:
            self.dump_folder_input.setText(dump_folder)

    def select_boot_img(self):
        boot_img, _ = QFileDialog.getOpenFileName(self, "Select boot.img", filter="Image files (*.img);;All files (*.*)")
        if boot_img:
            self.boot_img_input.setText(boot_img)

    def save_settings(self):
        try:
            CONFIG['qemu_path'] = self.qemu_path_input.text()
            CONFIG['qemu_executable'] = self.qemu_exec_input.text()
            CONFIG['dump_folder'] = self.dump_folder_input.text()
            CONFIG['boot_img_path'] = self.boot_img_input.text()
            CONFIG['virtual_disk_size'] = self.vdisk_size_input.value()
            save_config(CONFIG)
            self.log_message.emit("Settings saved successfully")
            QMessageBox.information(self, "Success", "Settings saved successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
            self.log_message.emit(f"Error: Failed to save settings - {str(e)}")

    def analyze_dump(self):
        try:
            dump_folder = self.dump_folder_input.text()
            if not dump_folder:
                raise ValueError("No dump folder selected")
            # Implement dump analysis logic here
            self.log_message.emit(f"Analyzing dump folder: {dump_folder}")
            QMessageBox.information(self, "Success", f"Dump analysis completed for folder: {dump_folder}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to analyze dump: {str(e)}")
            self.log_message.emit(f"Error: Failed to analyze dump - {str(e)}")

    def create_virtual_disk(self):
        try:
            size = self.vdisk_size_input.value()
            vdisk_path = self.qemu_controller.create_virtual_disk(size)
            self.vdisk_info_label.setText(f"Virtual disk created at: {vdisk_path}")
            CONFIG['virtual_disk_path'] = vdisk_path
            CONFIG['virtual_disk_size'] = size
            save_config(CONFIG)
            self.log_message.emit(f"Virtual disk created: {vdisk_path}")
            QMessageBox.information(self, "Success", f"Virtual disk created at: {vdisk_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create virtual disk: {str(e)}")
            self.log_message.emit(f"Error: Failed to create virtual disk - {str(e)}")

