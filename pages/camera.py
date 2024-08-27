import os
import cv2
import uuid
import tempfile
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QPushButton, QLabel, QFrame
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import QTimer, Qt

class CameraWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera Preview")
        self.setFixedSize(670, 600)  # Set the window size to be fixed and prevent resizing

        # Ensure the window is always on top
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Radio buttons in a horizontal layout with equal spacing
        radio_layout = QHBoxLayout()
        radio_layout.setAlignment(Qt.AlignCenter)  # Center the layout
        radio_layout.addStretch(1)  # Add space before the first radio button

        self.radio1 = QRadioButton("Camera 1")
        self.radio2 = QRadioButton("Camera 2")

        # Set font size and bold text
        font = QFont("Arial", 12, QFont.Bold)
        self.radio1.setFont(font)
        self.radio2.setFont(font)

        # Set bigger size for radio buttons
        self.radio1.setStyleSheet("QRadioButton { font-size: 16px; }")
        self.radio2.setStyleSheet("QRadioButton { font-size: 16px; }")

        self.radio1.setChecked(True)  # Default to Camera 1
        radio_layout.addWidget(self.radio1)
        radio_layout.addStretch(1)  # Add space between the radio buttons
        radio_layout.addWidget(self.radio2)
        radio_layout.addStretch(1)  # Add space after the second radio button

        main_layout.addLayout(radio_layout)

        # Create a fixed-size container for the camera preview or error message
        self.camera_container = QFrame(self)
        self.camera_container.setFrameShape(QFrame.StyledPanel)
        self.camera_container.setFixedSize(650, 500)  # Fixed size for the container
        self.camera_container.setLayout(QVBoxLayout())

        # Camera preview or message
        self.camera_label = QLabel(self.camera_container)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.camera_container.layout().addWidget(self.camera_label)

        main_layout.addWidget(self.camera_container)

        # Capture button centered
        capture_button_layout = QHBoxLayout()
        capture_button_layout.addStretch(1)  # Add space before the button
        self.capture_button = QPushButton("Capture", self)
        self.capture_button.clicked.connect(self.capture_image)
        self.capture_button.setFont(QFont("Arial", 14, QFont.Bold))
        self.capture_button.setStyleSheet("background-color: #007acc; color: white; padding: 10px; border-radius: 5px;")
        self.capture_button.setFixedSize(120, 40)  # Set fixed size for the button
        capture_button_layout.addWidget(self.capture_button)
        capture_button_layout.addStretch(1)  # Add space after the button
        main_layout.addLayout(capture_button_layout)

        # Initialize camera
        self.cap = None
        self.selected_camera = 0
        self.radio1.toggled.connect(self.select_camera)
        self.radio2.toggled.connect(self.select_camera)

        self.select_camera()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)  # 20ms interval for 50 FPS

    def select_camera(self):
        if self.radio1.isChecked():
            self.selected_camera = 0
        elif self.radio2.isChecked():
            self.selected_camera = 1

        if self.cap is not None:
            self.cap.release()

        # Use CAP_DSHOW for Windows
        self.cap = cv2.VideoCapture(self.selected_camera, cv2.CAP_DSHOW)

        # Check if the camera is opened successfully
        if not self.cap.isOpened():
            self.camera_label.setText("Camera not found.")
            self.camera_label.setStyleSheet("color: red;")  # Optional: Set text color to red
            self.capture_button.setEnabled(False)  # Disable the capture button
        else:
            self.camera_label.clear()  # Clear the label if camera is found
            self.capture_button.setEnabled(True)

    def update_frame(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, _ = frame.shape
                image = QImage(frame, width, height, width * 3, QImage.Format_RGB888)

                # Resize the image to fit the container
                scaled_image = QPixmap.fromImage(image).scaled(self.camera_container.size(), Qt.KeepAspectRatio)

                self.camera_label.setPixmap(scaled_image)
                self.camera_label.setText("")  # Clear text if camera is active

    def capture_image(self):
        if self.cap is not None and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Save the image with a random name in a temporary directory
                random_name = f"modal{uuid.uuid4().hex}.png"
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, random_name)
                cv2.imwrite(temp_file_path, frame)
                self.captured_filename = temp_file_path
                self.close()  # Close the window after capturing

    def closeEvent(self, event):
        if self.cap is not None:
            self.cap.release()
        self.timer.stop()  # Stop the timer before closing
        super().closeEvent(event)