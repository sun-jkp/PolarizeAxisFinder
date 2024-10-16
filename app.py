import sys
import cv2
import numpy as np
import configparser
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QSlider, QFormLayout, QSpinBox, QHBoxLayout, QFrame, QGroupBox
from PyQt5.QtGui import QImage, QPixmap, QFont
from camera import IDSCamera
from impl import Imgpr
from utils import *
from version import __version__

# Config file path
CONFIG_FILE = 'settings.ini'

class VideoStreamWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Create the image label for video stream
        self.image_label = QLabel()
        self.image_label.setFrameShape(QFrame.Box)
        self.image_label.setLineWidth(1)
        self.image_label.setStyleSheet("border: 2px solid #4CAF50;")

        # Status labels
        self.camera_status_label = QLabel('Camera Status: Not Connected')
        self.camera_status_label.setFont(QFont("Century Gothic", 12))
        self.debug_label = QLabel('Debug: OFF')
        self.debug_label.setFont(QFont("Century Gothic", 12))
        self.motor_status_label = QLabel('Motor Status: Idle')
        self.motor_status_label.setFont(QFont("Century Gothic", 12))
        self.program_status_label = QLabel('Program Status: Ready')
        self.program_status_label.setFont(QFont("Century Gothic", 12))
        self.ink_angle_label = QLabel('Ink angle: None')
        self.ink_angle_label.setFont(QFont("Century Gothic", 12))
        self.polar_angle_label = QLabel('Polarize angle: None')
        self.polar_angle_label.setFont(QFont("Century Gothic", 12))
        self.diff_angle_label = QLabel('Different angles: None')
        self.diff_angle_label.setFont(QFont("Century Gothic", 12))

        # Create buttons
        self.start_button = QPushButton('Start Detection')
        self.check_params_button = QPushButton('Check Parameters')
        self.check_polar_angle_button = QPushButton('Check Angle')
        self.check_ink_line_button = QPushButton('Check Line Stamp')
        self.clear_button = QPushButton('Clear All')
        self.debug_button = QPushButton('Debug')
        self.settings_button = QPushButton('Settings')

        # Style buttons
        self.start_button.setStyleSheet(self.get_button_style())
        self.check_params_button.setStyleSheet(self.get_button_style())
        self.settings_button.setStyleSheet(self.get_button_style())
        self.check_polar_angle_button.setStyleSheet(self.get_button_style()) 
        self.check_ink_line_button.setStyleSheet(self.get_button_style())
        self.clear_button.setStyleSheet(self.get_button_style())
        self.debug_button.setStyleSheet(self.get_button_style()) 

        # Layout for buttons and status
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.check_params_button)
        button_layout.addWidget(self.check_polar_angle_button)
        button_layout.addWidget(self.check_ink_line_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.settings_button)
        button_layout.addWidget(self.debug_button)
        button_layout.addStretch()

        # Layout for status labels
        status_layout = QVBoxLayout()
        status_layout.addWidget(self.camera_status_label)
        status_layout.addWidget(self.debug_label)
        status_layout.addWidget(self.motor_status_label)
        status_layout.addWidget(self.program_status_label)
        status_layout.addWidget(self.polar_angle_label)
        status_layout.addWidget(self.ink_angle_label)
        status_layout.addWidget(self.diff_angle_label)
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
        
        # Create the image label for video stream
        self.setting_label = QLabel()
        self.setting_label.setFrameShape(QFrame.Box)
        self.setting_label.setLineWidth(2)
        self.setting_label.setStyleSheet("border: 2px solid #4CAF50;")

        # Status labels
        self.detect_lens_params_label = QLabel('Detect Lens Parameter')
        self.canny_edge_label = QLabel('Candy Edge Parameter')
        self.houghlines_label = QLabel('Hough Line Parameter')
        self.houghlines_p_label = QLabel('Hough Line P Parameter')
        # self.program_status_label = QLabel('Program Status: Ready')
        # self.ink_angle_label = QLabel('Ink angle: None')
        # self.polar_angle_label = QLabel('Polarize angle: None')
        # self.diff_angle_label = QLabel('Different angles: None')

        self.min_dist = QSpinBox()
        self.min_dist.setMaximum(1000)
        self.min_dist.setValue(50)
        self.min_dist.setFont(QFont("Arial", 12))
        
        self.param1 = QSpinBox()
        self.param1.setMaximum(300)
        self.param1.setValue(50)
        self.param1.setFont(QFont("Arial", 12))
        
        self.param2 = QSpinBox()
        self.param2.setMaximum(300)
        self.param2.setValue(50)
        self.param2.setFont(QFont("Arial", 12))
        
        self.min_radius = QSpinBox()
        self.min_radius.setMaximum(1000)
        self.min_radius.setValue(50)
        self.min_radius.setFont(QFont("Arial", 12))
        
        self.max_radius = QSpinBox()
        self.max_radius.setMaximum(1000)
        self.max_radius.setValue(50)
        self.max_radius.setFont(QFont("Arial", 12))
        
        self.threshold1 = QSpinBox()
        self.threshold1.setMaximum(255)
        self.threshold1.setValue(50)
        self.threshold1.setFont(QFont("Arial", 12))
        
        self.threshold2 = QSpinBox()
        self.threshold2.setMaximum(255)
        self.threshold2.setValue(50)
        self.threshold2.setFont(QFont("Arial", 12))
        
        self.houghlines_p_threshold = QSpinBox()
        self.houghlines_p_threshold.setMaximum(255)
        self.houghlines_p_threshold.setValue(50)
        self.houghlines_p_threshold.setFont(QFont("Arial", 12))

        self.houghlines_p_min_line_length = QSpinBox()
        self.houghlines_p_min_line_length.setMaximum(255)
        self.houghlines_p_min_line_length.setValue(50)
        self.houghlines_p_min_line_length.setFont(QFont("Arial", 12))

        self.houghlines_p_max_line_gap = QSpinBox()
        self.houghlines_p_max_line_gap.setMaximum(255)
        self.houghlines_p_max_line_gap.setValue(10)
        self.houghlines_p_max_line_gap.setFont(QFont("Arial", 12))
        
        self.houghlines_threshold = QSpinBox()
        self.houghlines_threshold.setMaximum(255)
        self.houghlines_threshold.setValue(50)
        self.houghlines_threshold.setFont(QFont("Arial", 12))

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
        layout.addRow(self.detect_lens_params_label)
        layout.addRow('HoughCircle Min Dist', self.min_dist)
        layout.addRow('HoughCircle Param1', self.param1)
        layout.addRow('HoughCircle Param2', self.param2)
        layout.addRow('HoughCircle Min Radius', self.min_radius)
        layout.addRow('HoughCircle Max Radius', self.max_radius)
        layout.addRow(self.canny_edge_label)
        layout.addRow('Candy Edge Th1', self.threshold1)
        layout.addRow('Candy Edge Th2', self.threshold2)
        layout.addRow(self.houghlines_p_label)
        layout.addRow('Hough Line P Th', self.houghlines_p_threshold)
        layout.addRow('Hough Line P Min Line Length', self.houghlines_p_min_line_length)
        layout.addRow('Hough Line P Max Line Gap', self.houghlines_p_max_line_gap)
        layout.addRow(self.houghlines_label)
        layout.addRow('Hough Line Th', self.houghlines_threshold)
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
        self.angle_run = False
        self.check_ink = False
        self._center = None
        self._radius = None
        self.lens_mask_inv = None
        self.ink_angle = None
        self.polar_angle = None
        self.last_frame = None
        self.last_frame_bgr = None
        self.debug_enable = False
        self.lens_detected = False
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
        self.video_stream_widget.check_params_button.clicked.connect(self.check_parameters)
        self.video_stream_widget.check_polar_angle_button.clicked.connect(self.check_polar_angle)
        self.video_stream_widget.check_ink_line_button.clicked.connect(self.check_ink_line)
        self.video_stream_widget.debug_button.clicked.connect(self.debug)
        # self.video_stream_widget.clear_button.clicked.connect(self.check_Angle)

        # Initialize timer for updating video stream
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        self.run_camera()

    def debug(self):
        if(self.debug_enable):
            self.debug_enable = False
            self.video_stream_widget.debug_label.setText('Debug: OFF')
        else:
            self.debug_enable = True
            self.video_stream_widget.debug_label.setText('Debug: ON')
    def check_polar_angle(self):
        img_polar = self.polarization_capture()
        angle = self.polarization_angle(img_polar=img_polar, roi=self.lens_mask_inv)
        # self.compare_angle()
        self.video_stream_widget.polar_angle_label.setText(f'Polarize angle: {angle}')
    
    def check_ink_line(self):
        self.check_polar_angle()
        self.check_ink = True
            
    def check_parameters(self):
        print("Current Parameters:", self.parameters)
        
    def polarization_capture(self):
        
        try:
            self.angle_run = True
            # Stop any previous camera acquisitions
            self.camera.stop_acquisition()
            # self.camera.disable_intensity() 
            self.camera.enable_polarize_angle()
            # # Start acquisition
            self.camera.alloc_and_announce_buffers()
            self.camera.start_acquisition()
            
            # Capture the polarization image frame
            polarization_img = self.camera.capture_frame()
            self.img_polar =  polarization_img
            self.camera.stop_acquisition()
            self.camera.enable_intensity()
            self.camera.alloc_and_announce_buffers()
            self.camera.start_acquisition()
            self.angle_run = False
            self.timer.start(30)
            return polarization_img
        
        except Exception as e:
            # Handle exceptions like timeouts or attribute errors
            print(f"Exception occurred: {str(e)}")
            return None
            
    def polarization_angle(self, img_polar, roi):
        roi_img = self.set_roi_lens(img_polar, roi)
        # Calculate the histogram
        histogram = cv2.calcHist([roi_img], [0], None, [256], [0, 256])
        histogram[255] = 0
        # Find the intensity value with the highest frequency
        highest_intensity = np.argmax(histogram)
        # Get the frequency of that intensity
        highest_frequency = histogram[highest_intensity]
        top_indices = np.argsort(histogram, axis=0)[-10:][::-1]
        # Print the top 3 intensity values and their frequencies
        for i, idx in enumerate(top_indices, 1):
            intensity_value = idx[0]
            frequency = histogram[intensity_value][0]
            print(f"Top {i}: Intensity value = {intensity_value}, Frequency = {frequency}")
        # print(f'top 5 histogram: {histogram[0]}, {histogram[0]}, {histogram[0]}, {histogram[0]}, {histogram[0]}')
        # print(f"The intensity value with the highest frequency, excluding 255, is: {highest_intensity}")
        # print(f"The frequency of this intensity is: {highest_frequency[0]}")
        self.polar_angle = highest_intensity
        return highest_intensity
    
    def adjust_offset_angle(self, angle, offset):
        return np.abs(angle-offset)
    
    def compare_angle(self, polar_angle, ink_angle, offset=90):
        _ink_angle = self.adjust_offset_angle(ink_angle, offset)
        return round(np.abs(polar_angle - _ink_angle), 2)
            
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
        self.parameters['hc_min_dist'] = self.settings_widget.min_dist.value()
        self.parameters['hc_p1'] = self.settings_widget.param1.value()
        self.parameters['hc_p2'] = self.settings_widget.param2.value()
        self.parameters['hc_min_r'] = self.settings_widget.min_radius.value()
        self.parameters['hc_max_r'] = self.settings_widget.max_radius.value()
        self.parameters['e_th1'] = self.settings_widget.threshold1.value()
        self.parameters['e_th2'] = self.settings_widget.threshold2.value()
        self.parameters['hlp_th'] = self.settings_widget.houghlines_p_threshold.value()
        self.parameters['hlp_min_l'] = self.settings_widget.houghlines_p_min_line_length.value()
        self.parameters['hlp_max_g'] = self.settings_widget.houghlines_p_max_line_gap.value()
        self.parameters['hl_th'] = self.settings_widget.houghlines_threshold.value()

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
                'hc_min_dist': int(config.get('Settings', 'min_dist', fallback='350')),
                'hc_p1': int(config.get('Settings', 'hc_p1', fallback='100')),
                'hc_p2': int(config.get('Settings', 'hc_p2', fallback='60')),
                'hc_min_r': int(config.get('Settings', 'hc_min_r', fallback='125')),
                'hc_max_r': int(config.get('Settings', 'hc_max_r', fallback='200')),
                'e_th1': int(config.get('Settings', 'e_th1', fallback='0')),
                'e_th2': int(config.get('Settings', 'e_th2', fallback='75')),
                'hlp_th': int(config.get('Settings', 'hlp_th', fallback='100')),
                'hlp_min_l': int(config.get('Settings', 'hlp_min_l', fallback='100')),
                'hlp_max_g': int(config.get('Settings', 'hlp_max_g', fallback='100')),
                'hl_th': int(config.get('Settings', 'hl_th', fallback='100'))
            }

            # Update settings widget with loaded values
            self.settings_widget.min_dist.setValue(self.parameters['hc_min_dist'])
            self.settings_widget.param1.setValue(self.parameters['hc_p1'])
            self.settings_widget.param2.setValue(self.parameters['hc_p2'])
            self.settings_widget.min_radius.setValue(self.parameters['hc_min_r'])
            self.settings_widget.max_radius.setValue(self.parameters['hc_max_r'])
            self.settings_widget.threshold1.setValue(self.parameters['e_th1'])
            self.settings_widget.threshold2.setValue(self.parameters['e_th2'])
            self.settings_widget.houghlines_p_threshold.setValue(self.parameters['hlp_th'])
            self.settings_widget.houghlines_p_min_line_length.setValue(self.parameters['hlp_min_l'])
            self.settings_widget.houghlines_p_max_line_gap.setValue(self.parameters['hlp_max_g'])
            self.settings_widget.houghlines_threshold.setValue(self.parameters['hl_th'])

        except Exception as e:
            print(f"Failed to load settings: {e}")
            # Set default values if loading fails
            self.parameters = {
                'hc_min_dist': 350,
                'hc_p1': 100,
                'hc_p2': 60,
                'hc_min_r': 125,
                'hc_max_r': 200,
                'e_th1': 0,
                'e_th2': 75,
                'hlp_th': 100,
                'hlp_min_l': 100,
                'hlp_max_g': 100,
                'hl_th': 100
            }

    def save_to_config_file(self):
        # Create a config parser object
        config = configparser.ConfigParser()

        # Add settings section
        config.add_section('Settings')
        config.set('Settings', 'hc_min_dist', str(self.parameters['hc_min_dist']))
        config.set('Settings', 'hc_p1', str(self.parameters['hc_p1']))
        config.set('Settings', 'hc_p2', str(self.parameters['hc_p2']))
        config.set('Settings', 'hc_min_r', str(self.parameters['hc_min_r']))
        config.set('Settings', 'hc_max_r', str(self.parameters['hc_max_r']))
        config.set('Settings', 'e_th1', str(self.parameters['e_th1']))
        config.set('Settings', 'e_th2', str(self.parameters['e_th2']))
        config.set('Settings', 'hlp_th', str(self.parameters['hlp_th']))
        config.set('Settings', 'hlp_min_l', str(self.parameters['hlp_min_l']))
        config.set('Settings', 'hlp_max_g', str(self.parameters['hlp_max_g']))
        config.set('Settings', 'hl_th', str(self.parameters['hl_th']))

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
        
        # if not self.camera.enable_polarize_angle():
        #     self.video_stream_widget.camera_status_label.setText('Camera Status: enable mode error')
        #     return
        
        if not self.camera.enable_intensity():
            self.video_stream_widget.camera_status_label.setText('Camera Status: enable mode error')
            return
        
        # if not self.camera.mode_setting():
        #     self.video_stream_widget.camera_status_label.setText('Camera Status: mode setting error')
        #     return

        if not self.camera.config_image():
            self.video_stream_widget.camera_status_label.setText('Camera Status: config error')
            return
        
        if not self.camera.set_roi(414, 298, 480, 480):
            self.video_stream_widget.camera_status_label.setText('Camera Status: set roi failed')
            return

        if not self.camera.alloc_and_announce_buffers():
            self.video_stream_widget.camera_status_label.setText('Camera Status: alloc and announce buffer error')
            return
        
        if not self.camera.start_acquisition():
            self.video_stream_widget.camera_status_label.setText('Camera Status: start acquisition error')
            return
        
        self.video_stream_widget.camera_status_label.setText('Camera Status: Ready')
        self.timer.start(30)

    def get_image(self):
        if(not self.angle_run):
            self.last_frame = self.camera.capture_frame()
        
        return self.last_frame
    
    def set_roi_lens(self, img, roi):
        roi_img = cv2.bitwise_or(img, roi)
        return roi_img
        
    def check_lens_roi(self, img):
        
        # circles = self.img_processing.detect_circle(img, mis_dist=350, p1=100, p2=60, min_radius=125, max_radius=200)
        circles = self.img_processing.detect_circle(img, mis_dist=self.settings_widget.min_dist.value(), 
                                                    p1=self.settings_widget.param1.value(),
                                                    p2=self.settings_widget.param2.value(),
                                                    min_radius=self.settings_widget.min_radius.value(),
                                                    max_radius=self.settings_widget.max_radius.value())
        lens_mask_inv = np.ones(img.shape, dtype=np.uint8)*255
        _center = None
        _radius = None
        status = ''
        if(circles is not None):
            if len(circles[0]) == 1:
                circles = np.uint16(np.around(circles))
                ct_th = 5
                r_th = 2
                for i in circles[0, :]:
                    _center = (i[0], i[1])
                    _radius = i[2]
                    if(self._center is not None and self._radius is not None):
                        # if(np.square((self._center[0]-i[0]**2) + (self._center[1]-i[1])**2) > ct_th):
                        if(abs(self._center[0] - i[0])>ct_th and abs(self._center[1] - i[1])>ct_th):
                            # if(abs(self._radius-i[2])> r_th):
                            self._center = _center
                            self._radius = _radius
                    else:
                        self._center = _center
                        self._radius = _radius
                    cv2.circle(lens_mask_inv, self._center, self._radius-20, 0, -1)
                status = D_LENS_STATUS.SUCCESS
            else:
                self._center = None
                self._radius = None
                _center = None
                _radius = None
                lens_mask_inv = None
                status = D_LENS_STATUS.FOUND_MORE_ONE
        else:
            self._center = None
            self._radius = None
            _center = None
            _radius = None
            lens_mask_inv = None
            status = D_LENS_STATUS.NOT_FOUND
            
        self.lens_mask_inv = lens_mask_inv
        return {'center': self._center, 'radius': self._radius, 'lens_roi': lens_mask_inv,'status': status}
    
    def detect_line_ink(self, img, roi):
        roi_img = self.set_roi_lens(img, roi)
        edges = self.img_processing.canny(roi_img, th1=self.settings_widget.threshold1.value(),
                                        th2=self.settings_widget.threshold2.value())
        lines = self.img_processing.detect_lines(edges, th=self.settings_widget.houghlines_threshold.value())
        if(self.debug_enable):
            img_copy = cv2.cvtColor(self.last_frame, cv2.COLOR_GRAY2BGR)
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    cv2.line(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.imshow('debug edge', edges)
            cv2.imshow('debug lines', img_copy)
            
        status = None
        ink_angle = None
        if(lines is not None):
            clusters = self.img_processing.group_lines(lines, angle_threshold=5, dist_threshold=100)
            averaged_lines = [self.img_processing.average_line(cluster) for cluster in clusters]
            closest_line = min(averaged_lines, key=lambda line: self.img_processing.distance_from_center(line, self._center))
            # x1, y1, x2, y2 = closest_line[0]
            ink_angle = self.img_processing.calculate_angle_from_axis2(closest_line)
            status = INK_L_STATUS.SUCCESS
        else:
            status = INK_L_STATUS.NOT_FOUND
            
        return {'ink_angle': ink_angle, 'status': status}

    def update_frame(self):
        #gray images
        img = self.get_image()
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        self.last_frame_bgr = img_bgr
        result = self.check_lens_roi(img)
        
        if(result['status'] == D_LENS_STATUS.SUCCESS):
            center = result['center']
            radius = result['radius']
            cv2.circle(img_bgr, center, 1, (0, 100, 100), 1)
            cv2.circle(img_bgr, center, radius, (255, 0, 255), 1)
            self.lens_detected = True
        else:
            self.lens_detected = False
            
        if(self.check_ink or self.debug_enable):
            result_ink = self.detect_line_ink(img, result['lens_roi'])
            self.ink_angle = result_ink['ink_angle']
            if(result_ink['status'] == INK_L_STATUS.SUCCESS):
                # img_bgr = self.img_processing.draw_line_through_circle(img_bgr, center=self._center, radius=self._radius+30, angle_degrees=result_ink['ink_angle'])
                self.video_stream_widget.ink_angle_label.setText(f'Ink angle: {self.adjust_offset_angle(result_ink['ink_angle'], 90)}')

                if(self.polar_angle is not None and result_ink['ink_angle'] is not None):
                    diff_angle = self.compare_angle(self.polar_angle, result_ink['ink_angle'])
                    self.video_stream_widget.diff_angle_label.setText(f'Different angles: {diff_angle}')
            else:
                self.video_stream_widget.ink_angle_label.setText('Ink angle: Not Found')
            self.check_ink = False
            
        if(self.ink_angle is not None and self.lens_detected):
            img_bgr = self.img_processing.draw_line_through_circle(img_bgr, center=self._center, radius=self._radius+30, angle_degrees=self.ink_angle)
            
        img_resize = self.img_processing.resize(img_bgr)
        
        bytes_per_line = 3 * img_resize.shape[1]
        q_img = QImage(img_resize.data, img_resize.shape[1], img_resize.shape[0], bytes_per_line, QImage.Format_RGB888)
        self.video_stream_widget.image_label.setPixmap(QPixmap.fromImage(q_img))

    def closeEvent(self, event):
        self.camera.dispose()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle(f'LensPolar Inspector - Version {__version__}')
    window.show()
    sys.exit(app.exec_())
