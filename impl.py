import cv2
import numpy as np
import matplotlib.pyplot as plt
import math


class Imgpr():
    
    def __init__(self):
        pass
    
    def canny(self, img, th1=0, th2=75):
        edges = cv2.Canny(img, th1, th2)
        return edges
    
    def detect_circle(self, img, mis_dist):
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1.5, mis_dist, param1 = 75, param2 = 80, minRadius = 300, maxRadius = 450)
        return circles

    def detect_lines_p(self, edges, th=100, min_l = 30, max_lg = 60):
        lines = cv2.HoughLinesP(edges, rho=1.0, theta=np.pi/180, threshold=th, minLineLength=min_l, maxLineGap=max_lg)
        return lines

    def detect_lines(self, edges, th=170):
        lines = cv2.HoughLines(edges, rho=1, theta=np.pi/180, threshold=th)

        output = list()
        if lines is not None:
            for line in lines:
                rho,theta = line[0]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))
                
                output.append([(x1, y1, x2, y2)])
            return output
        else:
            return None


    def line_to_params(self, line):
        """ Convert line endpoints to slope (m) and intercept (c). """
        x1, y1, x2, y2 = line[0]
        if x2 - x1 != 0:  # Avoid division by zero
            m = (y2 - y1) / (x2 - x1)
            c = y1 - m * x1
        else:
            m = np.inf
            c = x1  # Vertical line case
        return m, c

    def group_lines(self, lines, angle_threshold=np.pi/18, dist_threshold=10):
        """ Group lines based on angle and distance similarity. """
        clusters = []
        
        for line in lines:
            m, c = self.line_to_params(line)
            matched = False
            
            for cluster in clusters:
                avg_m, avg_c = cluster['avg_m'], cluster['avg_c']
                if abs(m - avg_m) < angle_threshold and abs(c - avg_c) < dist_threshold:
                    cluster['lines'].append(line)
                    cluster['avg_m'] = np.mean([self.line_to_params(l)[0] for l in cluster['lines']])
                    cluster['avg_c'] = np.mean([self.line_to_params(l)[1] for l in cluster['lines']])
                    matched = True
                    break
            
            if not matched:
                clusters.append({'lines': [line], 'avg_m': m, 'avg_c': c})
        
        return clusters

    def average_line(self, cluster):
        """ Calculate the average line from a cluster of lines. """
        x1_avg = np.mean([line[0][0] for line in cluster['lines']])
        y1_avg = np.mean([line[0][1] for line in cluster['lines']])
        x2_avg = np.mean([line[0][2] for line in cluster['lines']])
        y2_avg = np.mean([line[0][3] for line in cluster['lines']])
        
        return np.array([[int(x1_avg), int(y1_avg), int(x2_avg), int(y2_avg)]])

    def distance_from_center(self, line, center):
        """ Calculate the distance of the line's midpoint from the center. """
        x1, y1, x2, y2 = line[0]
        midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)
        return np.sqrt((midpoint[0] - center[0]) ** 2 + (midpoint[1] - center[1]) ** 2)

    def calculate_angle_from_axis(self, line):
        x1, y1, x2, y2 = line[0]
        
        # Calculate the slope (m)
        if x2 - x1 != 0:
            slope = (y2 - y1) / (x2 - x1)
            angle_radians = math.atan(slope)
        else:
            # The line is vertical
            angle_radians = np.pi / 2  # 90 degrees
        
        # Convert angle to degrees
        angle_degrees = math.degrees(angle_radians)
        
        # Ensure the angle is positive
        if angle_degrees < 0:
            angle_degrees += 180
        
        return angle_degrees

    def calculate_angle_from_axis2(self, line):
        x1, y1, x2, y2 = line[0]
        
        # Calculate the angle using atan2
        angle_radians = math.atan2(y2 - y1, x2 - x1)
        
        # Convert angle to degrees
        angle_degrees = math.degrees(angle_radians)
        
        # Ensure the angle is within the range [0, 180)
        if angle_degrees < 0:
            angle_degrees += 180
        
        return angle_degrees

    def draw_line_through_circle(self, image, center, radius, angle_degrees, bgr_color=(255, 0, 0)):
        cx, cy = center
        
        # Convert the angle from degrees to radians
        angle_radians = math.radians(angle_degrees)
        
        # Calculate the endpoints of the line
        x1 = int(cx + radius * math.cos(angle_radians))
        y1 = int(cy + radius * math.sin(angle_radians))
        x2 = int(cx - radius * math.cos(angle_radians))
        y2 = int(cy - radius * math.sin(angle_radians))
        
        # Draw the line on the image
        cv2.line(image, (x1, y1), (x2, y2), bgr_color, 2)
        
        return image
    
    def resize(self, img, w=None, h=None, percent = 0.8):
        if(w ==None and h==None):
            return cv2.resize(img, (int(img.shape[1] * 0.8), int(img.shape[0] * 0.8)))
        else:
            return cv2.resize(img, (int(w), int(h)))