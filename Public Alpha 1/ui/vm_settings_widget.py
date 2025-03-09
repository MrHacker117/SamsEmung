from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QLabel,
                             QLineEdit, QSpinBox, QComboBox, QPushButton,
                             QFileDialog, QMessageBox, QGroupBox, QFormLayout,
                             QScrollArea)
from PyQt6.QtCore import pyqtSignal, Qt
from config import CONFIG


class KernelInfoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Create content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)

        # Add kernel information
        info_label = QLabel(
            "Kernel Information:\n\n"
            "Current Kernel: {kernel_path}\n"
            "Architecture: {arch}\n"
            "Version: {version}\n"
            "Build Date: {build_date}\n\n"
            "Parameters:\n{params}\n\n"
            "Boot Configuration:\n{boot_config}\n\n"
            "Device Tree:\n{device_tree}\n\n"
            "Notes:\n{notes}"
        )
        info_label.setWordWrap(True)
        content_layout.addWidget(info_label)

        # Add the content widget to scroll area
        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

        # Add update button
        update_button = QPushButton("Update Kernel Information")
        layout.addWidget(update_button)

    def update_info(self, kernel_info):
        # Update the kernel information display
        pass


class VMSettingsWidget(QWidget):
    vm_started = pyqtSignal()
    vm_stopped = pyqtSignal()

    def __init__(self, qemu_controller):
        super().__init__()
        self.qemu_controller = qemu_controller

        layout = QVBoxLayout(self)

        # Create tab widget
        self.tabs = QTabWidget()

        # Create tabs
        self.general_tab = self.create_general_tab()
        self.system_tab = self.create_system_tab()
        self.storage_tab = self.create_storage_tab()
        self.kernel_tab = self.create_kernel_tab()
        self.kernel_info_tab = KernelInfoTab()

        # Add tabs
        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.system_tab, "System")
        self.tabs.addTab(self.storage_tab, "Storage")
        self.tabs.addTab(self.kernel_tab, "Kernel")
        self.tabs.addTab(self.kernel_info_tab, "Kernel Info")

        layout.addWidget(self.tabs)

    def create_general_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        # Name
        self.name_edit = QLineEdit()
        layout.addRow("Name:", self.name_edit)

        # Model
        self.model_combo = QComboBox()
        self.model_combo.addItems(CONFIG['samsung_models'].keys())
        layout.addRow("Model:", self.model_combo)

        # UI Version
        self.ui_version_combo = QComboBox()
        self.ui_version_combo.addItems(CONFIG['touchwiz_versions'] + CONFIG['oneui_versions'])
        layout.addRow("UI Version:", self.ui_version_combo)

        return widget

    def create_system_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        # Memory
        self.memory_spin = QSpinBox()
        self.memory_spin.setRange(1024, 16384)
        self.memory_spin.setSingleStep(1024)
        self.memory_spin.setValue(2048)
        self.memory_spin.setSuffix(" MB")
        layout.addRow("Base Memory:", self.memory_spin)

        # Processors
        self.cpu_spin = QSpinBox()
        self.cpu_spin.setRange(1, 8)
        self.cpu_spin.setValue(2)
        layout.addRow("Processors:", self.cpu_spin)

        return widget

    def create_storage_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Virtual disk group
        disk_group = QGroupBox("Virtual Disk")
        disk_layout = QFormLayout(disk_group)

        self.disk_size_spin = QSpinBox()
        self.disk_size_spin.setRange(1, 100000)
        self.disk_size_spin.setValue(4096)
        self.disk_size_spin.setSuffix(" MB")
        disk_layout.addRow("Size:", self.disk_size_spin)

        self.disk_path_edit = QLineEdit()
        self.disk_path_edit.setReadOnly(True)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_disk)
        disk_layout.addRow("Path:", self.disk_path_edit)
        disk_layout.addRow("", browse_button)

        layout.addWidget(disk_group)
        return widget

    def create_kernel_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Kernel configuration group
        kernel_group = QGroupBox("Kernel Configuration")
        kernel_layout = QFormLayout(kernel_group)

        # Kernel type
        self.kernel_type_combo = QComboBox()
        self.kernel_type_combo.addItems(["Custom Kernel", "Stock Kernel", "Test Kernel"])
        kernel_layout.addRow("Kernel Type:", self.kernel_type_combo)

        # Kernel path
        self.kernel_path_edit = QLineEdit()
        self.kernel_path_edit.setReadOnly(True)
        browse_kernel_button = QPushButton("Browse...")
        browse_kernel_button.clicked.connect(self.browse_kernel)
        kernel_layout.addRow("Kernel Path:", self.kernel_path_edit)
        kernel_layout.addRow("", browse_kernel_button)

        # Kernel parameters
        self.kernel_params_edit = QLineEdit()
        self.kernel_params_edit.setPlaceholderText("console=ttyAMA0 root=/dev/vda")
        kernel_layout.addRow("Parameters:", self.kernel_params_edit)

        layout.addWidget(kernel_group)
        return widget

    def browse_disk(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Virtual Disk", "", "QCOW2 Images (*.qcow2);;All Files (*.*)")
        if path:
            self.disk_path_edit.setText(path)

    def browse_kernel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Kernel", "", "Kernel Files (*.img);;All Files (*.*)")
        if path:
            self.kernel_path_edit.setText(path)

    def load_vm_settings(self, vm_name):
        # Load VM settings from config
        self.name_edit.setText(vm_name)
        # Load other settings...

    def start_vm(self):
        try:
            model = self.model_combo.currentText()
            memory = self.memory_spin.value()
            kernel_path = self.kernel_path_edit.text()
            kernel_params = self.kernel_params_edit.text()

            if not kernel_path:
                raise ValueError("Please select a kernel file")

            # Update QEMU controller configuration
            self.qemu_controller.config.update({
                'boot_img_path': kernel_path,
                'kernel_params': kernel_params
            })

            # Start the VM
            self.qemu_controller.start_emulator(model, self.ui_version_combo.currentText(), memory)
            self.vm_started.emit()

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

