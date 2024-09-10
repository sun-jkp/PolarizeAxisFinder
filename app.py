import sys
import cv2
import numpy as np
import configparser
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QSlider, QFormLayout, QSpinBox, QHBoxLayout, QFrame, QGroupBox
from PyQt5.QtGui import QImage, QPixmap, QFont
from camera import IDSCamera
from impl import Imgpr

# Config file path
CONFIG_FILE = 'settings.ini'

class VideoStreamWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create the image label for video stream
        self.image_label = QLabel()
        self.image_label.setFrameShape(QFrame.Box)
        self.image_label.setLineWidth(2)
        self.image_label.setStyleSheet("border: 2px solid #4CAF50;")

        # Status labels
        self.camera_status_label = QLabel('Camera Status: Not Connected')
        self.motor_status_label = QLabel('Motor Status: Idle')
        self.program_status_label = QLabel('Program Status: Ready')
        self.ink_angle_label = QLabel('Ink angle: None')
        self.polar_angle_label = QLabel('Polarize angle: None')

        # Create buttons
        self.start_button = QPushButton('Start Detection')
        self.check_button = QPushButton('Check Parameters')
        self.settings_button = QPushButton('Settings')

        # Style buttons
        self.start_button.setStyleSheet(self.get_button_style())
        self.check_button.setStyleSheet(self.get_button_style())
        self.settings_button.setStyleSheet(self.get_button_style())

        # Layout for buttons and status
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addStretch()

        # Layout for status labels
        status_layout = QVBoxLayout()
        status_layout.addWidget(self.camera_status_label)
        status_layout.addWidget(self.motor_status_label)
        status_layout.addWidget(self.program_status_label)
        status_layout.addStretch()

        # Create group box for buttons
        group_box = QGroupBox("Controls")
        group_box.setLayout(button_layout)
        group_box.setStyleSheet("QGroupBox { font-weight: bold; }")

        # Main layout: buttons and status on the left, video stream on the right
        main_layout = QHBoxLayout()
        main_layout.addWidget(group_box)
        main_layout.addLayout(status_layout)
        main_layout.addWidget(self.image_label)
        self.setLayout(main_layout)

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """

class SettingsWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create sliders and spin boxes for settings
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(255)
        self.threshold_slider.setValue(100)
        self.threshold_slider.setStyleSheet(self.get_slider_style())

        self.houghlinesp_min_line_length = QSpinBox()
        self.houghlinesp_min_line_length.setValue(50)
        self.houghlinesp_min_line_length.setFont(QFont("Arial", 12))

        self.houghlinesp_max_line_gap = QSpinBox()
        self.houghlinesp_max_line_gap.setValue(10)
        self.houghlinesp_max_line_gap.setFont(QFont("Arial", 12))

        self.houghcircle_param1 = QSpinBox()
        self.houghcircle_param1.setValue(100)
        self.houghcircle_param1.setFont(QFont("Arial", 12))

        self.houghcircle_param2 = QSpinBox()
        self.houghcircle_param2.setValue(30)
        self.houghcircle_param2.setFont(QFont("Arial", 12))

        # Create save and back buttons
        self.save_button = QPushButton('Save Settings')
        self.back_button = QPushButton('Back')

        self.save_button.setStyleSheet(self.get_button_style())
        self.back_button.setStyleSheet(self.get_button_style())

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.back_button)

        # Layout for the entire settings page
        layout = QFormLayout()
        layout.addRow('Threshold', self.threshold_slider)
        layout.addRow('HoughLinesP Min Line Length', self.houghlinesp_min_line_length)
        layout.addRow('HoughLinesP Max Line Gap', self.houghlinesp_max_line_gap)
        layout.addRow('HoughCircle Param1', self.houghcircle_param1)
        layout.addRow('HoughCircle Param2', self.houghcircle_param2)
        layout.addRow(button_layout)
        self.setLayout(layout)

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """

    def get_slider_style(self):
        return """
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #4CAF50;
            }
            QSlider::handle:horizontal {
                background: #45a049;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.img_processing = Imgpr()
                
        # Create main stack widget to switch between video stream and settings
        self.stacked_widget = QStackedWidget()
        self.video_stream_widget = VideoStreamWidget()
        self.settings_widget = SettingsWidget()

        self.stacked_widget.addWidget(self.video_stream_widget)
        self.stacked_widget.addWidget(self.settings_widget)

        # Main layout: stack widget contains pages
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        # Connect buttons to their actions
        self.video_stream_widget.settings_button.clicked.connect(self.show_settings_page)
        self.settings_widget.save_button.clicked.connect(self.save_settings)
        self.settings_widget.back_button.clicked.connect(self.show_video_stream_page)

        # Load settings from config file
        self.load_settings()

        # Connect button actions
        self.video_stream_widget.start_button.clicked.connect(self.start_detection)
        self.video_stream_widget.check_button.clicked.connect(self.check_parameters)

        # Initialize timer for updating video stream
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Initialize camera
        # self.cap = cv2.VideoCapture(0)
        # self.detection_enabled = False
        
        # Start camera stream immediately
        # self.timer.start(30)
        
        self.run_camera()

    def start_detection(self):
        self.detection_enabled = True
        self.video_stream_widget.program_status_label.setText('Program Status: Detecting')

    def check_parameters(self):
        print("Current Parameters:", self.parameters)

    def show_settings_page(self):
        self.stacked_widget.setCurrentWidget(self.settings_widget)

    def show_video_stream_page(self):
        self.stacked_widget.setCurrentWidget(self.video_stream_widget)

    def save_settings(self):
        # Update parameters from the settings widget
        self.parameters['threshold'] = self.settings_widget.threshold_slider.value()
        self.parameters['houghlinesp_min_line_length'] = self.settings_widget.houghlinesp_min_line_length.value()
        self.parameters['houghlinesp_max_line_gap'] = self.settings_widget.houghlinesp_max_line_gap.value()
        self.parameters['houghcircle_param1'] = self.settings_widget.houghcircle_param1.value()
        self.parameters['houghcircle_param2'] = self.settings_widget.houghcircle_param2.value()

        # Save parameters to config file
        self.save_to_config_file()

        # Switch back to video stream page
        self.show_video_stream_page()

    def load_settings(self):
        # Create a config parser object
        config = configparser.ConfigParser()

        # Check if the config file exists
        try:
            config.read(CONFIG_FILE)
            self.parameters = {
                'threshold': int(config.get('Settings', 'threshold', fallback='100')),
                'houghlinesp_min_line_length': int(config.get('Settings', 'houghlinesp_min_line_length', fallback='50')),
                'houghlinesp_max_line_gap': int(config.get('Settings', 'houghlinesp_max_line_gap', fallback='10')),
                'houghcircle_param1': int(config.get('Settings', 'houghcircle_param1', fallback='100')),
                'houghcircle_param2': int(config.get('Settings', 'houghcircle_param2', fallback='30'))
            }

            # Update settings widget with loaded values
            self.settings_widget.threshold_slider.setValue(self.parameters['threshold'])
            self.settings_widget.houghlinesp_min_line_length.setValue(self.parameters['houghlinesp_min_line_length'])
            self.settings_widget.houghlinesp_max_line_gap.setValue(self.parameters['houghlinesp_max_line_gap'])
            self.settings_widget.houghcircle_param1.setValue(self.parameters['houghcircle_param1'])
            self.settings_widget.houghcircle_param2.setValue(self.parameters['houghcircle_param2'])

        except Exception as e:
            print(f"Failed to load settings: {e}")
            # Set default values if loading fails
            self.parameters = {
                'threshold': 100,
                'houghlinesp_min_line_length': 50,
                'houghlinesp_max_line_gap': 10,
                'houghcircle_param1': 100,
                'houghcircle_param2': 30
            }

    def save_to_config_file(self):
        # Create a config parser object
        config = configparser.ConfigParser()

        # Add settings section
        config.add_section('Settings')
        config.set('Settings', 'threshold', str(self.parameters['threshold']))
        config.set('Settings', 'houghlinesp_min_line_length', str(self.parameters['houghlinesp_min_line_length']))
        config.set('Settings', 'houghlinesp_max_line_gap', str(self.parameters['houghlinesp_max_line_gap']))
        config.set('Settings', 'houghcircle_param1', str(self.parameters['houghcircle_param1']))
        config.set('Settings', 'houghcircle_param2', str(self.parameters['houghcircle_param2']))

        # Write to config file
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
            
    def run_camera(self):
        self.camera = IDSCamera()
        if not self.camera.open_camera():
            self.video_stream_widget.camera_status_label.setText('Camera Status: Not Connected')
            return
        
        if not self.camera.prepare_acquisition():
            self.video_stream_widget.camera_status_label.setText('Camera Status: prepare error')
            return
        
        if not self.camera.enable_polarize_angle():
            self.video_stream_widget.camera_status_label.setText('Camera Status: enable mode error')
            return
        
        if not self.camera.enable_intensity():
            self.video_stream_widget.camera_status_label.setText('Camera Status: enable mode error')
            return
        
        # if not self.camera.mode_setting():
        #     self.video_stream_widget.camera_status_label.setText('Camera Status: mode setting error')
        #     return

        if not self.camera.config_image():
            self.video_stream_widget.camera_status_label.setText('Camera Status: config error')
            return

        if not self.camera.alloc_and_announce_buffers():
            self.video_stream_widget.camera_status_label.setText('Camera Status: alloc and announce buffer error')
            return
        
        if not self.camera.start_acquisition():
            self.video_stream_widget.camera_status_label.setText('Camera Status: start acquisition error')
            return
        
        self.video_stream_widget.camera_status_label.setText('Camera Status: Ready')
        self.timer.start(30)

    def update_frame(self):
        #gray images
        img = self.camera.capture_frame()
        # print(img.shape)
        width = img.shape[1]
        height = img.shape[0]
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        circles = self.img_processing.detect_circle(img, img.shape[0]/8)
        mask = np.zeros_like(img)
        _center = None
        _radius = None
        # print(len(circles[0]))
        if len(circles[0]) == 1:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                _center = (i[0], i[1])
                _radius = i[2]
                cv2.circle(img_bgr, _center, 1, (0, 100, 100), 3)
                cv2.circle(img_bgr, _center, _radius, (255, 0, 255), 3)
                cv2.circle(mask, _center, _radius, (255, 0, 255), -1)
            
            masked_image = cv2.bitwise_and(img, mask)
            edges = self.img_processing.canny(masked_image)
            # lines = self.img_processing.detect_lines_p(edges, th=90)
            lines = self.img_processing.detect_lines(edges, th=90)
            if(lines is not None):
                clusters = self.img_processing.group_lines(lines, angle_threshold=5, dist_threshold=100)
                averaged_lines = [self.img_processing.average_line(cluster) for cluster in clusters]
                closest_line = min(averaged_lines, key=lambda line: self.img_processing.distance_from_center(line, _center))
                # x1, y1, x2, y2 = closest_line[0]
                ink_angle = self.img_processing.calculate_angle_from_axis2(closest_line)
                img_bgr = self.img_processing.draw_line_through_circle(img_bgr, center=_center, radius=_radius+30, angle_degrees=ink_angle)
        elif len(circles[0]) > 1:
            pass
        else:
            pass
        
        

        
        img_resize = self.img_processing.resize(img_bgr)
        
        bytes_per_line = 3 * img_resize.shape[1]
        q_img = QImage(img_resize.data, img_resize.shape[1], img_resize.shape[0], bytes_per_line, QImage.Format_RGB888)
        self.video_stream_widget.image_label.setPixmap(QPixmap.fromImage(q_img))

    def closeEvent(self, event):
        self.camera.dispose()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle('Modern UI Camera Stream with Detection')
    window.show()
    sys.exit(app.exec_())
