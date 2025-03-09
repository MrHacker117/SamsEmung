from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QLineEdit, QGroupBox, QCheckBox, QMessageBox)
from PyQt6.QtGui import QIntValidator
from PyQt6.QtCore import Qt, pyqtSignal

class EmulatorTab(QWidget):
    log_message = pyqtSignal(str)

    def __init__(self, qemu_controller):
        super().__init__()
        self.qemu_controller = qemu_controller
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Device Model selection
        model_layout = QHBoxLayout()
        model_label = QLabel("Device Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Galaxy S10", "Galaxy S20", "Galaxy Note 10", "SM-G900F"])
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        self.layout.addLayout(model_layout)

        # Kernel in dump checkbox
        self.kernel_in_dump_checkbox = QCheckBox("Kernel found in dump (no separate ZIP needed)")
        self.kernel_in_dump_checkbox.setEnabled(False)
        self.layout.addWidget(self.kernel_in_dump_checkbox)

        # Virtual memory configuration
        memory_group = QGroupBox("Virtual Memory Configuration")
        memory_layout = QVBoxLayout()
        memory_group.setLayout(memory_layout)

        memory_input_layout = QHBoxLayout()
        memory_label = QLabel("Virtual Memory (MB):")
        self.memory_input = QLineEdit()
        self.memory_input.setValidator(QIntValidator(1, 1000000))
        memory_input_layout.addWidget(memory_label)
        memory_input_layout.addWidget(self.memory_input)
        memory_layout.addLayout(memory_input_layout)

        create_vm_button = QPushButton("Create Virtual Memory")
        create_vm_button.clicked.connect(self.create_virtual_memory)
        memory_layout.addWidget(create_vm_button)

        self.vm_info_label = QLabel()
        memory_layout.addWidget(self.vm_info_label)

        self.layout.addWidget(memory_group)

        # Emulator control buttons
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

        self.layout.addWidget(control_group)

    def create_virtual_memory(self):
        try:
            size = int(self.memory_input.text())
            model = self.model_combo.currentText()
            vm_path = self.qemu_controller.create_virtual_memory(size, model)
            self.vm_info_label.setText(f"Virtual memory created at: {vm_path}")
            self.log_message.emit(f"Virtual memory file created: {vm_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create virtual memory: {str(e)}")
            self.log_message.emit(f"Error: Failed to create virtual memory - {str(e)}")

    def start_emulator(self):
        try:
            model = self.model_combo.currentText()
            memory = int(self.memory_input.text()) if self.memory_input.text() else 0
            self.qemu_controller.start_emulator(model, "TouchWiz", memory)
            self.log_message.emit(f"Started emulator for {model}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start emulator: {str(e)}")
            self.log_message.emit(f"Error: Failed to start emulator - {str(e)}")

    def stop_emulator(self):
        try:
            self.qemu_controller.stop_emulator()
            self.log_message.emit("Emulator stopped")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop emulator: {str(e)}")
            self.log_message.emit(f"Error: Failed to stop emulator - {str(e)}")

    def test_emulator(self):
        try:
            model = self.model_combo.currentText()
            memory = int(self.memory_input.text()) if self.memory_input.text() else 0
            self.qemu_controller.test_emulator(model, memory)
            self.log_message.emit(f"Started test emulator for {model}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to test emulator: {str(e)}")
            self.log_message.emit(f"Error: Failed to test emulator - {str(e)}")

