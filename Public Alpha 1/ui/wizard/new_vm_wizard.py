from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QLabel,
                             QLineEdit, QComboBox, QSpinBox, QCheckBox,
                             QFileDialog, QPushButton, QMessageBox, QHBoxLayout,
                             QScrollArea, QWidget)
from PyQt6.QtCore import Qt
import os
from dump_analyzer import analyze_dump


class KernelInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Basic kernel information
        basic_info = QLabel(
            "Kernel Explanation for Beginners:\n\n"
            "The kernel is like the brain of your virtual Samsung device. "
            "It controls how the device works and interacts with its hardware."
        )
        basic_info.setWordWrap(True)
        layout.addWidget(basic_info)

        # Detailed kernel information
        detailed_info = QLabel(
            "Types of Kernels:\n\n"
            "1. Default Test Kernel:\n"
            "   • Pre-configured and ready to use\n"
            "   • Great for beginners and testing\n"
            "   • Limited functionality\n"
            "   • Safe and stable\n\n"
            "2. Custom Kernel:\n"
            "   • Full device functionality\n"
            "   • Specific to your device model\n"
            "   • Requires proper configuration\n"
            "   • More advanced setup\n\n"
            "3. Stock Samsung Kernel:\n"
            "   • Original device kernel\n"
            "   • Complete hardware support\n"
            "   • Model-specific features\n"
            "   • Requires extraction from device\n\n"
            "Common Kernel Files:\n"
            "• boot.img - Standard Android boot image\n"
            "• zImage - Compressed kernel image\n"
            "• Image - Raw kernel image\n\n"
            "Important Notes:\n"
            "• Always backup your kernel files\n"
            "• Match kernel architecture with device\n"
            "• Check kernel compatibility\n"
            "• Keep kernel parameters consistent"
        )
        detailed_info.setWordWrap(True)
        detailed_info.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(detailed_info)


class KernelPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Kernel Configuration")
        self.setSubTitle("Choose how you want to configure the kernel.")

        layout = QVBoxLayout()

        # Kernel options
        self.use_default = QCheckBox("Use default test kernel (Recommended for beginners)")
        self.use_default.setChecked(True)
        self.registerField("use_default_kernel", self.use_default)
        layout.addWidget(self.use_default)

        # Kernel file selection
        kernel_group = QHBoxLayout()
        kernel_label = QLabel("Custom kernel file (optional):")
        self.kernel_path = QLineEdit()
        self.kernel_path.setReadOnly(True)
        self.registerField("kernel_path", self.kernel_path)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_kernel)

        kernel_group.addWidget(kernel_label)
        kernel_group.addWidget(self.kernel_path)
        kernel_group.addWidget(browse_button)
        layout.addLayout(kernel_group)

        # Create scroll area for kernel information
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Add kernel info widget to scroll area
        kernel_info = KernelInfoWidget()
        scroll_area.setWidget(kernel_info)

        # Set fixed height for scroll area
        scroll_area.setMinimumHeight(300)
        scroll_area.setMaximumHeight(400)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

    def browse_kernel(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Kernel File",
            "",
            "Kernel Files (*.img *.gz *.zImage);;All Files (*.*)"
        )
        if path:
            self.kernel_path.setText(path)
            self.use_default.setChecked(False)


class NamePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Name and Device Model")
        self.setSubTitle(
            "Please specify a name for the new virtual machine and choose the model or use automatic detection.")

        layout = QVBoxLayout()

        # Name
        name_label = QLabel("Name:")
        self.name_edit = QLineEdit()
        self.registerField("name*", self.name_edit)

        # Automatic detection
        self.auto_detect = QCheckBox("Automatically detect model from dump")
        self.auto_detect.stateChanged.connect(self.toggle_model_selection)

        # Model
        model_layout = QHBoxLayout()
        model_label = QLabel("Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "Galaxy S10",
            "Galaxy S20",
            "Galaxy Note 10",
            "Galaxy S21",
            "Galaxy S22",
            "Other"
        ])
        self.registerField("model", self.model_combo, "currentText")
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)

        # Dump folder selection
        dump_layout = QHBoxLayout()
        self.dump_folder_edit = QLineEdit()
        self.dump_folder_edit.setReadOnly(True)
        dump_button = QPushButton("Select Dump Folder")
        dump_button.clicked.connect(self.select_dump_folder)
        dump_layout.addWidget(self.dump_folder_edit)
        dump_layout.addWidget(dump_button)

        # UI Version
        ui_label = QLabel("UI Version:")
        self.ui_combo = QComboBox()
        self.ui_combo.addItems([
            "One UI 4.0",
            "One UI 3.0",
            "One UI 2.0",
            "Samsung Experience 9.0",
            "TouchWiz"
        ])
        self.registerField("ui_version", self.ui_combo, "currentText")

        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.auto_detect)
        layout.addLayout(model_layout)
        layout.addLayout(dump_layout)
        layout.addWidget(ui_label)
        layout.addWidget(self.ui_combo)
        self.setLayout(layout)

    def toggle_model_selection(self, state):
        self.model_combo.setEnabled(not state)
        self.dump_folder_edit.setEnabled(state)

    def select_dump_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Dump Folder")
        if folder:
            self.dump_folder_edit.setText(folder)
            if self.auto_detect.isChecked():
                self.detect_model_from_dump(folder)

    def detect_model_from_dump(self, folder):
        try:
            model, ui_version = analyze_dump(folder)
            index = self.model_combo.findText(model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
            else:
                self.model_combo.setCurrentText("Other")

            ui_index = self.ui_combo.findText(ui_version)
            if ui_index >= 0:
                self.ui_combo.setCurrentIndex(ui_index)

            QMessageBox.information(self, "Auto-detection", f"Detected model: {model}\nUI version: {ui_version}")
        except Exception as e:
            QMessageBox.warning(self, "Auto-detection Failed", f"Could not detect model from dump: {str(e)}")


class MemoryPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Memory")
        self.setSubTitle("Please specify the amount of memory (RAM) for the virtual machine.")

        layout = QVBoxLayout()

        memory_label = QLabel("Memory size (MB):")
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(1024, 16384)
        self.memory_spin.setSingleStep(1024)
        self.memory_spin.setValue(2048)
        self.registerField("memory", self.memory_spin)

        recommended_label = QLabel("Recommended: 2048 MB or more")
        recommended_label.setStyleSheet("color: gray;")

        layout.addWidget(memory_label)
        layout.addWidget(self.memory_spin)
        layout.addWidget(recommended_label)
        self.setLayout(layout)


class StoragePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle("Virtual Hard Disk")
        self.setSubTitle("Configure the virtual hard disk for your device.")

        layout = QVBoxLayout()

        # Disk size
        size_label = QLabel("Disk size (MB):")
        self.size_spin = QSpinBox()
        self.size_spin.setRange(4096, 102400)  # 4GB to 100GB
        self.size_spin.setSingleStep(1024)
        self.size_spin.setValue(8192)  # 8GB default
        self.registerField("disk_size", self.size_spin)

        recommended_label = QLabel("Recommended: 8192 MB (8GB) or more")
        recommended_label.setStyleSheet("color: gray;")

        layout.addWidget(size_label)
        layout.addWidget(self.size_spin)
        layout.addWidget(recommended_label)
        self.setLayout(layout)


class NewVMWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Virtual Machine")

        # Add pages
        self.addPage(NamePage())
        self.addPage(MemoryPage())
        self.addPage(KernelPage())
        self.addPage(StoragePage())

        # Set window size
        self.setMinimumSize(600, 400)

    def accept(self):
        try:
            # Create VM configuration
            vm_config = {
                'name': self.field("name"),
                'model': self.field("model"),
                'ui_version': self.field("ui_version"),
                'memory': self.field("memory"),
                'use_default_kernel': self.field("use_default_kernel"),
                'kernel_path': self.field("kernel_path"),
                'disk_size': self.field("disk_size"),
                'dump_folder': self.field("dump_folder") if self.field("auto_detect") else None
            }

            # Save VM configuration (you'll implement this in main_window.py)
            self.parent().create_new_vm(vm_config)

            super().accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create VM: {str(e)}")

