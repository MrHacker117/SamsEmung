import os
import logging
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QPushButton, QTextEdit, QFileDialog,
                             QLineEdit, QSpinBox, QCheckBox, QMessageBox, QGroupBox)
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from qemu_controller import QEMUController
from config import CONFIG, save_config
from dump_analyzer import analyze_dump
from ai_file_searcher import AIFileSearcher


class EmulatorThread(QThread):
    error = pyqtSignal(str)
    success = pyqtSignal(str)
    command = pyqtSignal(str)
    ai_suggestion = pyqtSignal(str)

    def __init__(self, controller, action, *args):
        super().__init__()
        self.controller = controller
        self.action = action
        self.args = args

    def run(self):
        try:
            if self.action == 'start':
                cmd = self.controller.start_emulator(*self.args)
                self.command.emit(f"Executing command: {' '.join(cmd)}")
                self.success.emit(f"Started emulator for {self.args[0]}")
            elif self.action == 'test':
                cmd = self.controller.test_emulator(*self.args)
                self.command.emit(f"Executing test command: {' '.join(cmd)}")
                self.success.emit(f"Started test emulator for {self.args[0]}")
            elif self.action == 'stop':
                self.controller.stop_emulator()
                self.success.emit("Emulator stopped")
        except Exception as e:
            self.error.emit(str(e))
            if "AI Suggestion:" in str(e):
                self.ai_suggestion.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SamsEmung - Samsung Smartphone Emulator")
        self.setGeometry(100, 100, 1000, 800)

        self.qemu_controller = QEMUController(CONFIG)
        self.ai_file_searcher = AIFileSearcher()

        if 'boot_img_path' in CONFIG:
            self.qemu_controller.set_boot_img_path(CONFIG['boot_img_path'])

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.setup_emulator_tab()
        self.setup_settings_tab()

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)

    def setup_emulator_tab(self):
        emulator_tab = QWidget()
        self.tab_widget.addTab(emulator_tab, "Emulator")
        emulator_layout = QVBoxLayout(emulator_tab)

        model_layout = QHBoxLayout()
        model_label = QLabel("Device Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(CONFIG['samsung_models'].keys())
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        emulator_layout.addLayout(model_layout)

        ui_version_layout = QHBoxLayout()
        ui_version_label = QLabel("UI Version:")
        self.ui_version_combo = QComboBox()
        self.ui_version_combo.addItems(CONFIG['touchwiz_versions'] + CONFIG['oneui_versions'])
        ui_version_layout.addWidget(ui_version_label)
        ui_version_layout.addWidget(self.ui_version_combo)
        emulator_layout.addLayout(ui_version_layout)

        self.kernel_in_dump_checkbox = QCheckBox("Kernel found in dump (no separate ZIP needed)")
        self.kernel_in_dump_checkbox.setEnabled(False)
        emulator_layout.addWidget(self.kernel_in_dump_checkbox)

        memory_group = QGroupBox("Virtual Memory Configuration")
        memory_layout = QVBoxLayout()
        memory_group.setLayout(memory_layout)

        memory_input_layout = QHBoxLayout()
        memory_label = QLabel("Virtual Memory (MB):")
        self.memory_input = QLineEdit(str(CONFIG['virtual_memory']))
        self.memory_input.setValidator(QIntValidator(1, 1000000))
        memory_input_layout.addWidget(memory_label)
        memory_input_layout.addWidget(self.memory_input)
        memory_layout.addLayout(memory_input_layout)

        create_vm_button = QPushButton("Create Virtual Memory")
        create_vm_button.clicked.connect(self.create_virtual_memory)
        memory_layout.addWidget(create_vm_button)

        self.vm_info_label = QLabel()
        memory_layout.addWidget(self.vm_info_label)

        emulator_layout.addWidget(memory_group)

        control_group = QGroupBox("Emulator Control")
        control_layout = QHBoxLayout()
        control_group.setLayout(control_layout)

        start_button = QPushButton("Start Emulator")
        start_button.clicked.connect(self.start_emulator)
        control_layout.addWidget(start_button)

        stop_button = QPushButton("Stop Emulator")
        stop_button.clicked.connect(self.stop_emulator)
        control_layout.addWidget(stop_button)

        test_button = QPushButton("Test Emulator")
        test_button.clicked.connect(self.test_emulator)
        control_layout.addWidget(test_button)

        emulator_layout.addWidget(control_group)

    def setup_settings_tab(self):
        settings_tab = QWidget()
        self.tab_widget.addTab(settings_tab, "Settings")
        settings_layout = QVBoxLayout(settings_tab)

        qemu_group = QGroupBox("QEMU Configuration")
        qemu_layout = QVBoxLayout()
        qemu_group.setLayout(qemu_layout)

        qemu_path_layout = QHBoxLayout()
        self.qemu_path_input = QLineEdit(CONFIG['qemu_path'])
        qemu_path_layout.addWidget(QLabel("QEMU Path:"))
        qemu_path_layout.addWidget(self.qemu_path_input)
        qemu_path_button = QPushButton("Browse")
        qemu_path_button.clicked.connect(self.select_qemu_path)
        qemu_path_layout.addWidget(qemu_path_button)
        qemu_layout.addLayout(qemu_path_layout)

        qemu_exec_layout = QHBoxLayout()
        self.qemu_exec_input = QLineEdit(CONFIG['qemu_executable'])
        qemu_exec_layout.addWidget(QLabel("QEMU Executable:"))
        qemu_exec_layout.addWidget(self.qemu_exec_input)
        qemu_exec_button = QPushButton("Browse")
        qemu_exec_button.clicked.connect(self.select_qemu_executable)
        qemu_exec_layout.addWidget(qemu_exec_button)
        qemu_layout.addLayout(qemu_exec_layout)

        settings_layout.addWidget(qemu_group)

        dump_group = QGroupBox("Dump Configuration")
        dump_layout = QVBoxLayout()
        dump_group.setLayout(dump_layout)

        dump_folder_layout = QHBoxLayout()
        self.dump_folder_input = QLineEdit(CONFIG['dump_folder'])
        dump_folder_layout.addWidget(QLabel("Dump Folder:"))
        dump_folder_layout.addWidget(self.dump_folder_input)
        dump_folder_button = QPushButton("Browse")
        dump_folder_button.clicked.connect(self.select_dump_folder)
        dump_folder_layout.addWidget(dump_folder_button)
        dump_layout.addLayout(dump_folder_layout)

        settings_layout.addWidget(dump_group)

        boot_img_layout = QHBoxLayout()
        self.boot_img_input = QLineEdit(CONFIG.get('boot_img_path', ''))
        boot_img_layout.addWidget(QLabel("Boot Image (boot.img):"))
        boot_img_layout.addWidget(self.boot_img_input)
        boot_img_button = QPushButton("Browse")
        boot_img_button.clicked.connect(self.select_boot_img)
        boot_img_layout.addWidget(boot_img_button)
        settings_layout.addLayout(boot_img_layout)

        save_settings_button = QPushButton("Save Settings")
        save_settings_button.clicked.connect(self.save_settings)
        settings_layout.addWidget(save_settings_button)

        analyze_dump_button = QPushButton("Analyze Dump")
        analyze_dump_button.clicked.connect(self.analyze_dump)
        settings_layout.addWidget(analyze_dump_button)

    def start_emulator(self):
        model = self.model_combo.currentText()
        ui_version = self.ui_version_combo.currentText()
        memory = int(self.memory_input.text()) if self.memory_input.text() else 0

        self.log_output.append("Starting emulator...")
        try:
            self.qemu_controller._get_kernel_path(model)
            self.emulator_thread = EmulatorThread(self.qemu_controller, 'start', model, ui_version, memory)
            self.emulator_thread.success.connect(self.log_output.append)
            self.emulator_thread.error.connect(self.handle_error)
            self.emulator_thread.command.connect(self.log_output.append)
            self.emulator_thread.ai_suggestion.connect(self.handle_ai_suggestion)
            self.emulator_thread.start()

            QTimer.singleShot(10000, self.check_emulator_status)
        except FileNotFoundError as e:
            self.handle_error(str(e))
            reply = QMessageBox.question(self, 'Kernel Not Found',
                                         "Kernel file not found. Would you like to search thoroughly in the Dump folder?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.thorough_kernel_search()
            else:
                self.log_output.append("Emulator start cancelled due to missing kernel file.")

    def test_emulator(self):
        model = self.model_combo.currentText()
        memory = int(self.memory_input.text()) if self.memory_input.text() else 0

        self.log_output.append("Starting test emulator...")
        self.emulator_thread = EmulatorThread(self.qemu_controller, 'test', model, memory)
        self.emulator_thread.success.connect(self.log_output.append)
        self.emulator_thread.error.connect(self.handle_error)
        self.emulator_thread.command.connect(self.log_output.append)
        self.emulator_thread.ai_suggestion.connect(self.handle_ai_suggestion)
        self.emulator_thread.start()

        QTimer.singleShot(10000, self.check_emulator_status)

    def stop_emulator(self):
        self.emulator_thread = EmulatorThread(self.qemu_controller, 'stop')
        self.emulator_thread.success.connect(self.log_output.append)
        self.emulator_thread.error.connect(self.handle_error)
        self.emulator_thread.start()
        self.qemu_controller.cleanup_virtual_memory()

    def create_virtual_memory(self):
        size = int(self.memory_input.text())
        model = self.model_combo.currentText()
        try:
            vm_path = self.qemu_controller.create_virtual_memory(size, model)
            self.vm_info_label.setText(f"Virtual memory created at: {vm_path}")
            self.log_output.append(f"Virtual memory file created: {vm_path}")
        except Exception as e:
            self.handle_error(str(e))

    def select_qemu_path(self):
        qemu_path = QFileDialog.getExistingDirectory(self, "Select QEMU Directory")
        if qemu_path:
            self.qemu_path_input.setText(qemu_path)

    def select_qemu_executable(self):
        qemu_executable, _ = QFileDialog.getOpenFileName(self, "Select QEMU Executable",
                                                         filter="Executable files (*.exe);;All files (*.*)")
        if qemu_executable:
            self.qemu_exec_input.setText(qemu_executable)

    def select_dump_folder(self):
        dump_folder = QFileDialog.getExistingDirectory(self, "Select Dump Folder")
        if dump_folder:
            self.dump_folder_input.setText(dump_folder)

    def save_settings(self):
        CONFIG['qemu_path'] = self.qemu_path_input.text()
        CONFIG['qemu_executable'] = self.qemu_exec_input.text()
        CONFIG['dump_folder'] = self.dump_folder_input.text()
        CONFIG['virtual_memory'] = int(self.memory_input.text()) if self.memory_input.text() else 0
        CONFIG['boot_img_path'] = self.boot_img_input.text()
        save_config(CONFIG)
        self.log_output.append("Settings saved successfully")

    def handle_error(self, error_message):
        self.log_output.append(f"Error: {error_message}")
        QMessageBox.critical(self, 'Error', error_message)
        if "Kernel file not found" in error_message:
            reply = QMessageBox.question(self, 'Kernel Not Found',
                                         "Kernel file not found. Would you like to search thoroughly in the Dump folder?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.thorough_kernel_search()

    def handle_ai_suggestion(self, suggestion):
        self.log_output.append(f"AI Suggestion: {suggestion}")
        QMessageBox.information(self, 'AI Suggestion', suggestion)

    def analyze_dump(self):
        dump_folder = self.dump_folder_input.text()
        if not dump_folder:
            self.handle_error("Error: No dump folder selected")
            return

        try:
            touchwiz_version, samsung_model = analyze_dump(dump_folder)
            self.log_output.append(f"Analysis complete:")
            self.log_output.append(f"TouchWiz/One UI version: {touchwiz_version}")
            self.log_output.append(f"Samsung model: {samsung_model}")

            if touchwiz_version != "Unknown":
                self.ui_version_combo.setCurrentText(touchwiz_version)
            if samsung_model != "Unknown":
                if samsung_model in CONFIG['samsung_models']:
                    self.model_combo.setCurrentText(samsung_model)
                else:
                    self.model_combo.addItem(samsung_model)
                    self.model_combo.setCurrentText(samsung_model)
                    CONFIG['samsung_models'][samsung_model] = "arm"

            self.check_kernel_in_dump(samsung_model)
        except Exception as e:
            self.handle_error(f"Error analyzing dump: {str(e)}")

    def check_kernel_in_dump(self, model):
        kernel_in_dump = self.qemu_controller.check_kernel_in_dump(model)
        self.kernel_in_dump_checkbox.setChecked(kernel_in_dump)
        self.kernel_in_dump_checkbox.setEnabled(True)

    def check_emulator_status(self):
        if self.qemu_controller.is_running():
            self.log_output.append("Emulator started successfully.")
        else:
            self.handle_error("Emulator failed to start or crashed. Please check the logs for more information.")

    def thorough_kernel_search(self):
        model = self.model_combo.currentText()
        dump_folder = self.dump_folder_input.text()
        found_kernel = self.qemu_controller._thorough_kernel_search(dump_folder)
        if found_kernel:
            self.log_output.append(f"Kernel file found: {found_kernel}")
            QMessageBox.information(self, 'Kernel Found', f"Kernel file found: {found_kernel}")
            self.start_emulator()
        else:
            self.log_output.append(f"Kernel file not found for {model} after thorough search")
            QMessageBox.warning(self, 'Kernel Not Found', f"Kernel file not found for {model} after thorough search")

    def select_boot_img(self):
        boot_img, _ = QFileDialog.getOpenFileName(self, "Select boot.img",
                                                  filter="Image files (*.img);;All files (*.*)")
        if boot_img:
            self.boot_img_input.setText(boot_img)
            self.qemu_controller.set_boot_img_path(boot_img)

