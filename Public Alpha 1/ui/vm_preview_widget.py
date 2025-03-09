from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QPixmap, QPainter, QColor, QLinearGradient
from PyQt6.QtCore import Qt, QSize


class VMPreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create frame for preview
        preview_frame = QFrame()
        preview_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Sunken)
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: #000000;
                border: 1px solid #666666;
                border-radius: 5px;
            }
        """)

        preview_layout = QVBoxLayout(preview_frame)

        # Preview label with gradient background
        self.preview_label = PreviewLabel()
        preview_layout.addWidget(self.preview_label)

        # Status label
        self.status_label = QLabel("Powered Off")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
                padding: 5px;
            }
        """)

        layout.addWidget(preview_frame)
        layout.addWidget(self.status_label)

    def update_preview(self):
        self.preview_label.set_running(True)
        self.status_label.setText("Running")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00ff00;
                font-size: 12px;
                padding: 5px;
            }
        """)

    def clear_preview(self):
        self.preview_label.set_running(False)
        self.status_label.setText("Powered Off")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
                padding: 5px;
            }
        """)


class PreviewLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.running = False
        self.setMinimumSize(320, 240)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_display()

    def set_running(self, running):
        self.running = running
        self.update_display()

    def update_display(self):
        size = self.size()
        pixmap = QPixmap(size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.running:
            # Draw running preview
            gradient = QLinearGradient(0, 0, 0, size.height())
            gradient.setColorAt(0, QColor("#1a1a1a"))
            gradient.setColorAt(1, QColor("#000000"))
            painter.fillRect(0, 0, size.width(), size.height(), gradient)

            # Draw "device screen"
            painter.setPen(Qt.GlobalColor.white)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Samsung Device\nRunning")
        else:
            # Draw powered off preview
            gradient = QLinearGradient(0, 0, 0, size.height())
            gradient.setColorAt(0, QColor("#2d2d2d"))
            gradient.setColorAt(1, QColor("#1a1a1a"))
            painter.fillRect(0, 0, size.width(), size.height(), gradient)

            # Draw device outline
            painter.setPen(QColor("#666666"))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "Samsung Device\nPowered Off")

        painter.end()
        self.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

