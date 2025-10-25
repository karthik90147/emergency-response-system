from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import os

class EmergencyImageDetector:
    def __init__(self):
        # Load pre-trained YOLO model
        try:
            self.model = YOLO('yolov8n.pt')  # Nano model for faster inference
        except:
            self.model = None
    
    def detect_emergency_objects(self, image_path):
        """
        Detect emergency-related objects in image
        Returns: detection results as string
        """
        if not self.model or not os.path.exists(image_path):
            return "Image detection not available"
        
        try:
            # Run inference
            results = self.model(image_path, conf=0.25)
            
            # Emergency-related classes
            emergency_classes = {
                'person': 'MEDICAL',
                'car': 'ACCIDENT',
                'truck': 'ACCIDENT',
                'bus': 'ACCIDENT',
                'motorcycle': 'ACCIDENT',
                'fire hydrant': 'FIRE',
                'traffic light': 'ACCIDENT',
            }
            
            detections = []
            detected_types = set()
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = self.model.names[cls]
                    
                    if class_name in emergency_classes:
                        emergency_type = emergency_classes[class_name]
                        detected_types.add(emergency_type)
                        detections.append(f"{class_name} (confidence: {conf:.2f})")
            
            if detections:
                detection_str = "Detected: " + ", ".join(detections)
                return detection_str
            else:
                return "No specific emergency objects detected"
                
        except Exception as e:
            return f"Detection error: {str(e)}"
    
    def analyze_fire(self, image_path):
        """
        Simple color-based fire detection
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return False, 0.0
            
            # Convert to HSV
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Define range for fire colors (red, orange, yellow)
            lower_fire = np.array([0, 50, 50])
            upper_fire = np.array([35, 255, 255])
            
            # Create mask
            mask = cv2.inRange(hsv, lower_fire, upper_fire)
            
            # Calculate percentage of fire-colored pixels
            fire_percentage = (np.sum(mask > 0) / mask.size) * 100
            
            is_fire = fire_percentage > 5.0  # Threshold
            
            return is_fire, fire_percentage
        except:
            return False, 0.0
