# NOTE: The project relies on ultralytics, cv2, numpy, and PIL. 
# Robust error handling is crucial for system stability.

import os

class EmergencyImageDetector:
    def __init__(self):
        self.model = None
        try:
            from ultralytics import YOLO
            # Load pre-trained YOLO model (assuming yolov8n.pt is available)
            self.model = YOLO('yolov8n.pt')  
            print("INFO: YOLOv8 model initialized successfully.")
        except ImportError:
            print("WARNING: ultralytics library not found. Image object detection disabled.")
        except Exception as e:
            print(f"ERROR: Failed to load YOLO model: {e}. Image object detection disabled.")
    
    def detect_emergency_objects(self, image_path):
        """
        Detect emergency-related objects in image using YOLO.
        Returns: Tuple of (detection results string, primary detected type).
        """
        if not self.model or not os.path.exists(image_path):
            return "Image detection unavailable (model not loaded or file missing).", 'OTHER'
        
        try:
            # Run inference
            results = self.model(image_path, conf=0.25)
            
            # Emergency-related classes (mapping object names to EMERGENCY_TYPE)
            emergency_classes = {
                'person': 'MEDICAL',
                'car': 'ACCIDENT',
                'truck': 'ACCIDENT',
                'bus': 'ACCIDENT',
                'motorcycle': 'ACCIDENT',
                'fire hydrant': 'FIRE',
                'traffic light': 'ACCIDENT',
                'bicycle': 'ACCIDENT'
            }
            
            detections = []
            detected_types = set() # To store unique types found
            
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = self.model.names[cls]
                    
                    if class_name in emergency_classes:
                        emergency_type = emergency_classes[class_name]
                        detected_types.add(emergency_type)
                        detections.append(f"{class_name} ({conf:.2f})")
            
            if detections:
                detection_str = "Detected: " + ", ".join(detections)
                
                # Prioritize ACCIDENT > MEDICAL for non-fire events
                if 'ACCIDENT' in detected_types:
                     primary_type = 'ACCIDENT'
                elif 'MEDICAL' in detected_types:
                     primary_type = 'MEDICAL'
                else:
                    primary_type = 'OTHER'
                    
                return detection_str, primary_type 

            else:
                return "No specific emergency objects detected.", 'OTHER'
                
        except Exception as e:
            # Catch errors that occur during the heavy inference process
            print(f"YOLO Inference Error: {e}")
            return "Detection inference error. Trusting text triage.", 'OTHER'
    
    def analyze_fire(self, image_path):
        """
        Simple color-based fire detection using OpenCV (cv2) and NumPy (np).
        Returns: (is_fire_bool, fire_percentage)
        """
        try:
            import cv2
            import numpy as np
            
            img = cv2.imread(image_path)
            if img is None:
                return False, 0.0
            
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            lower_fire = np.array([0, 50, 50])
            upper_fire = np.array([35, 255, 255])
            
            mask = cv2.inRange(hsv, lower_fire, upper_fire)
            fire_percentage = (np.sum(mask > 0) / mask.size) * 100
            
            is_fire = fire_percentage > 5.0
            
            return is_fire, fire_percentage
        except ImportError:
            # Catch error if cv2 or numpy are not available
            return False, 0.0
        except Exception as e:
            # Catch file read or processing errors
            return False, 0.0
