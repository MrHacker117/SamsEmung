from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QTabWidget


class DocumentationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        tab_widget = QTabWidget()

        # General Documentation
        general_doc = QTextBrowser()
        general_doc.setOpenExternalLinks(True)
        general_doc.setHtml(self.get_general_documentation())
        tab_widget.addTab(general_doc, "General")

        # Kernel Documentation
        kernel_doc = QTextBrowser()
        kernel_doc.setOpenExternalLinks(True)
        kernel_doc.setHtml(self.get_kernel_documentation())
        tab_widget.addTab(kernel_doc, "Kernel")

        layout.addWidget(tab_widget)

    def get_general_documentation(self):
        return """
        <h1>SamsEmung Emulator Documentation</h1>
        <p>Welcome to the SamsEmung Emulator, a tool for emulating Samsung devices using QEMU.</p>
        <h2>Getting Started</h2>
        <ol>
            <li>Set up QEMU path in the Global Settings</li>
            <li>Create a new Virtual Machine</li>
            <li>Configure the VM settings</li>
            <li>Start the emulator</li>
        </ol>
        <h2>Features</h2>
        <ul>
            <li>Emulate various Samsung device models</li>
            <li>Customize virtual hardware settings</li>
            <li>Test applications in a controlled environment</li>
        </ul>
        """

    def get_kernel_documentation(self):
        return """
        <h1>Kernel Documentation</h1>
        <p>The kernel is a crucial component of the emulated device. It acts as a bridge between the hardware and software.</p>
        <h2>Kernel Types</h2>
        <ul>
            <li><strong>Stock Kernel:</strong> The original kernel provided by Samsung for the device.</li>
            <li><strong>Custom Kernel:</strong> A modified version of the kernel, often with additional features or optimizations.</li>
            <li><strong>Test Kernel:</strong> A simplified kernel used for testing and development purposes.</li>
        </ul>
        <h2>Kernel Selection</h2>
        <p>When setting up your virtual machine, you can choose between using a default test kernel or providing a custom kernel file. For the most accurate emulation, it's recommended to use the stock kernel for your target device.</p>
        <h2>Kernel Parameters</h2>
        <p>Kernel parameters can be set in the VM settings to customize the kernel's behavior. Common parameters include:</p>
        <ul>
            <li><code>console=ttyAMA0</code>: Redirect console output to the first serial port</li>
            <li><code>root=/dev/vda</code>: Specify the root filesystem device</li>
            <li><code>androidboot.hardware=qemu</code>: Indicate to Android that it's running on QEMU</li>
        </ul>
        """

