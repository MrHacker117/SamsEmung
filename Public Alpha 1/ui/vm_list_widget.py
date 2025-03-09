from PyQt6.QtWidgets import (QListWidget, QListWidgetItem, QMenu, QMessageBox)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal
import os


class VMListWidget(QListWidget):
    vm_deleted = pyqtSignal(str)  # Signal emitted when VM is deleted

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(200)
        self.setMaximumWidth(300)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def add_vm(self, vm_config):
        """Add a new VM to the list"""
        item = QListWidgetItem(vm_config['name'])
        item.setData(Qt.ItemDataRole.UserRole, vm_config)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.addItem(item)
        self.setCurrentItem(item)
        return item

    def show_context_menu(self, position):
        item = self.itemAt(position)
        if item is None:
            return

        menu = QMenu()
        delete_action = menu.addAction("Delete VM")
        action = menu.exec(self.mapToGlobal(position))

        if action == delete_action:
            self.delete_vm(item)

    def delete_vm(self, item):
        vm_name = item.text()
        reply = QMessageBox.question(
            self,
            "Delete Virtual Machine",
            f"Are you sure you want to delete '{vm_name}'?\nThis will delete all associated files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Get VM config to find associated files
            vm_config = item.data(Qt.ItemDataRole.UserRole)

            # Delete virtual disk if it exists
            if 'virtual_disk_path' in vm_config and os.path.exists(vm_config['virtual_disk_path']):
                try:
                    os.remove(vm_config['virtual_disk_path'])
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Warning",
                        f"Could not delete virtual disk: {str(e)}"
                    )

            # Delete VM config file
            try:
                config_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
                    'vms',
                    f"{vm_name}.json"
                )
                if os.path.exists(config_path):
                    os.remove(config_path)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Warning",
                    f"Could not delete config file: {str(e)}"
                )

            # Remove from list
            self.takeItem(self.row(item))
            self.vm_deleted.emit(vm_name)

