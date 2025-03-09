import os
import json
import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QToolBar, QListWidget, QStackedWidget, QLabel,
                             QPushButton, QSplitter, QFrame, QTextEdit, QTabWidget, QMessageBox, QFileDialog)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt
from .vm_settings_widget import VMSettingsWidget
from .vm_list_widget import VMListWidget
from .vm_preview_widget import VMPreviewWidget
from .emulator_tab import EmulatorTab
from .settings_tab import SettingsTab
from qemu_controller import QEMUController
from config import CONFIG
from .wizard.new_vm_wizard import NewVMWizard
from .global_settings_dialog import GlobalSettingsDialog
from .font_manager import FontManager
from .documentation_widget import DocumentationWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SamsEmung - Samsung Smartphone Emulator")
        self.setGeometry(100, 100, 1200, 800)

        self.qemu_controller = QEMUController(CONFIG)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Create toolbar
        self.create_toolbar()

        # Create main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - VM List
        self.vm_list = VMListWidget()
        main_splitter.addWidget(self.vm_list)

        # Right panel - Settings and Preview
        right_panel = QSplitter(Qt.Orientation.Vertical)

        # Settings panel
        self.settings_widget = VMSettingsWidget(self.qemu_controller)
        right_panel.addWidget(self.settings_widget)

        # Preview panel
        self.preview_widget = VMPreviewWidget()
        right_panel.addWidget(self.preview_widget)

        # Add right panel to main splitter
        main_splitter.addWidget(right_panel)

        # Set stretch factors
        main_splitter.setStretchFactor(0, 1)  # VM List
        main_splitter.setStretchFactor(1, 3)  # Right panel

        main_layout.addWidget(main_splitter)

        # Connect signals
        self.vm_list.currentItemChanged.connect(self.on_vm_selected)
        self.settings_widget.vm_started.connect(self.preview_widget.update_preview)
        self.settings_widget.vm_stopped.connect(self.preview_widget.clear_preview)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        self.emulator_tab = EmulatorTab(self.qemu_controller)
        self.settings_tab = SettingsTab(self.qemu_controller)

        self.tab_widget.addTab(self.emulator_tab, "Emulator")
        self.tab_widget.addTab(self.settings_tab, "Settings")

        self.documentation_widget = DocumentationWidget()
        self.tab_widget.addTab(self.documentation_widget, "Documentation")

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)

        # Connect log signals
        self.emulator_tab.log_message.connect(self.log_message)
        self.settings_tab.log_message.connect(self.log_message)

        FontManager.load_fonts()

        self.setStyleSheet(f"""
            QWidget {{
                font-family: {FontManager.get_samsung_font()};
            }}
            QLabel {{
                font-size: 12px;
            }}
            QPushButton {{
                font-size: 14px;
            }}
        """)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Global Settings action
        global_settings_action = QAction(QIcon.fromTheme("preferences-system"), "Global Settings", self)
        global_settings_action.setStatusTip("Configure global emulator settings")
        global_settings_action.triggered.connect(self.open_global_settings)
        toolbar.addAction(global_settings_action)

        toolbar.addSeparator()

        # New VM action
        new_action = QAction(QIcon.fromTheme("document-new"), "New VM", self)
        new_action.setStatusTip("Create a new virtual machine")
        new_action.triggered.connect(self.on_new_vm)
        toolbar.addAction(new_action)

        # Add VM action
        add_action = QAction(QIcon.fromTheme("list-add"), "Add VM", self)
        add_action.setStatusTip("Add an existing virtual machine")
        add_action.triggered.connect(self.on_add_vm)
        toolbar.addAction(add_action)

        toolbar.addSeparator()

        # Start action
        start_action = QAction(QIcon.fromTheme("media-playback-start"), "Start", self)
        start_action.setStatusTip("Start virtual machine")
        start_action.triggered.connect(self.on_start)
        toolbar.addAction(start_action)

        # Stop action
        stop_action = QAction(QIcon.fromTheme("media-playback-stop"), "Stop", self)
        stop_action.setStatusTip("Stop virtual machine")
        stop_action.triggered.connect(self.on_stop)
        toolbar.addAction(stop_action)

        toolbar.addSeparator()

        # Add Kernel action
        add_kernel_action = QAction(QIcon.fromTheme("archive-insert"), "Add Kernel", self)
        add_kernel_action.setStatusTip("Add a kernel zip file")
        add_kernel_action.triggered.connect(self.on_add_kernel)
        toolbar.addAction(add_kernel_action)

        # Add TWRP Recovery action
        add_recovery_action = QAction(QIcon.fromTheme("drive-harddisk"), "Add TWRP Recovery", self)
        add_recovery_action.setStatusTip("Add a TWRP recovery image")
        add_recovery_action.triggered.connect(self.on_add_recovery)
        toolbar.addAction(add_recovery_action)

        # Create Dump action
        create_dump_action = QAction(QIcon.fromTheme("document-save"), "Create Dump", self)
        create_dump_action.setStatusTip("Create a dump file of the current emulator state")
        create_dump_action.triggered.connect(self.on_create_dump)
        toolbar.addAction(create_dump_action)

        # Documentation action
        doc_action = QAction(QIcon.fromTheme("help-contents"), "Documentation", self)
        doc_action.setStatusTip("Open documentation")
        doc_action.triggered.connect(self.show_documentation)
        toolbar.addAction(doc_action)

        toolbar.setMovable(False)
        toolbar.setFloatable(False)

    def open_global_settings(self):
        dialog = GlobalSettingsDialog(self)
        dialog.settings_updated.connect(self.on_global_settings_updated)
        dialog.exec()

    def on_global_settings_updated(self):
        # Reload QEMU controller with new settings
        self.qemu_controller = QEMUController(CONFIG)
        self.log_message("Global settings updated")

    def on_new_vm(self):
        wizard = NewVMWizard(self)
        wizard.exec()

    def create_new_vm(self, vm_config):
        try:
            # Create virtual disk
            logging.info(f"Creating virtual disk of size {vm_config['disk_size']}MB")
            vdisk_path = self.qemu_controller.create_virtual_disk(vm_config['disk_size'])

            # Update configuration
            vm_config['virtual_disk_path'] = vdisk_path
            vm_config['qcow2_path'] = vdisk_path

            # Add VM to list
            try:
                self.vm_list.add_vm(vm_config)
            except Exception as e:
                # Clean up virtual disk if VM creation fails
                if os.path.exists(vdisk_path):
                    try:
                        os.remove(vdisk_path)
                    except:
                        pass
                raise RuntimeError(f"Failed to add VM to list: {str(e)}")

            # Save VM configuration
            self.save_vm_config(vm_config)

            QMessageBox.information(
                self,
                "Success",
                f"Virtual machine '{vm_config['name']}' created successfully!"
            )

        except Exception as e:
            error_msg = str(e)
            logging.error(f"Failed to create virtual machine: {error_msg}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create virtual machine: {error_msg}"
            )

    def save_vm_config(self, vm_config):
        # Create VMs directory if it doesn't exist
        vms_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'vms')
        os.makedirs(vms_dir, exist_ok=True)

        # Save VM configuration to JSON file
        vm_file = os.path.join(vms_dir, f"{vm_config['name']}.json")
        with open(vm_file, 'w') as f:
            json.dump(vm_config, f, indent=2)

    def on_add_vm(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select VM Configuration",
            "",
            "VM Configuration (*.json);;All Files (*.*)"
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    vm_config = json.load(f)
                self.vm_list.add_vm(vm_config)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Virtual machine '{vm_config['name']}' added successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add virtual machine: {str(e)}"
                )

    def on_start(self):
        current_vm = self.vm_list.currentItem()
        if current_vm:
            try:
                vm_config = self.load_vm_config(current_vm.text())
                self.start_vm(vm_config)
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to start virtual machine: {str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Warning",
                "Please select a virtual machine first."
            )

    def on_stop(self):
        current_vm = self.vm_list.currentItem()
        if current_vm:
            try:
                self.qemu_controller.stop_emulator()
                self.preview_widget.clear_preview()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Virtual machine '{current_vm.text()}' stopped successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to stop virtual machine: {str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Warning",
                "Please select a virtual machine first."
            )

    def load_vm_config(self, vm_name):
        vm_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            '..',
            'vms',
            f"{vm_name}.json"
        )

        with open(vm_file, 'r') as f:
            return json.load(f)

    def start_vm(self, vm_config):
        # Update QEMU controller configuration
        self.qemu_controller.config.update({
            'virtual_disk_path': vm_config['virtual_disk_path'],
            'qcow2_path': vm_config.get('qcow2_path', vm_config['virtual_disk_path'])
        })

        cmd_line = self.qemu_controller.get_command_line(
            vm_config['model'],
            vm_config['ui_version'],
            vm_config['memory'],
            vm_config['kernel_zip'],
            vm_config['recovery_img']
        )
        self.log_message(f"Starting VM with command: {cmd_line}")

        # Start the VM
        self.qemu_controller.start_emulator(
            vm_config['model'],
            vm_config['ui_version'],
            vm_config['memory'],
            vm_config['kernel_zip'],
            vm_config['recovery_img']
        )

        # Update preview
        self.preview_widget.update_preview()

    def on_vm_selected(self, current, previous):
        if current:
            self.settings_widget.load_vm_settings(current.text())

    def log_message(self, message):
        self.log_output.append(message)

    def on_add_kernel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Kernel Zip File",
            "",
            "Zip Files (*.zip);;All Files (*.*)"
        )

        if file_path:
            try:
                kernel_path = self.qemu_controller.add_kernel(file_path)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Kernel zip added successfully: {os.path.basename(kernel_path)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add kernel zip: {str(e)}"
                )

    def on_add_recovery(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select TWRP Recovery Image",
            "",
            "Image Files (*.img);;All Files (*.*)"
        )

        if file_path:
            try:
                recovery_path = self.qemu_controller.add_twrp_recovery(file_path)
                QMessageBox.information(
                    self,
                    "Success",
                    f"TWRP recovery image added and modified successfully: {os.path.basename(recovery_path)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add TWRP recovery image: {str(e)}"
                )

    def on_create_dump(self):
        current_vm = self.vm_list.currentItem()
        if current_vm:
            try:
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Dump File",
                    "",
                    "Dump Files (*.dump);;All Files (*.*)"
                )

                if file_path:
                    dump_path = self.qemu_controller.create_dump_file(file_path)
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Dump file created successfully: {os.path.basename(dump_path)}"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create dump file: {str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Warning",
                "Please select a virtual machine first."
            )

    def show_documentation(self):
        self.tab_widget.setCurrentWidget(self.documentation_widget)

    def on_global_settings(self):
        dialog = GlobalSettingsDialog(self)
        dialog.exec()

    def show_kernel_recommendations(self):
        """Show recommended repositories for Samsung device emulation"""
        recommendations = (
            "Recommended GitHub repositories for Samsung device emulation:\n\n"
            "1. android-goldfish-3.4 - AOSP Goldfish kernel with Samsung modifications\n"
            "   https://github.com/samsung-msm8917/android_kernel_samsung_msm8917\n\n"
            "2. Samsung MSM8917 Kernel - Snapdragon platform kernel\n"
            "   https://github.com/LineageOS/android_kernel_samsung_msm8996\n\n"
            "3. LineageOS Samsung MSM8996 - Snapdragon 820 kernel\n"
            "   https://github.com/LineageOS/android_kernel_samsung_sdm845\n\n"
            "4. Samsung SDM845 Kernel - Snapdragon 845 platform\n"
            "   https://github.com/geiti94/android_kernel_samsung_universal7880\n\n"
            "These repositories contain kernel sources compatible with various Samsung devices.\n"
            "For Snapdragon devices, the MSM8996 and SDM845 kernels are recommended.\n\n"
            "Instructions:\n"
            "1. Clone the repository for your device's platform\n"
            "2. Build the kernel following the README instructions\n"
            "3. Use the resulting kernel image with this emulator"
        )

        msg = QMessageBox(self)
        msg.setWindowTitle("Samsung Device Emulation Resources")
        msg.setText(recommendations)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

