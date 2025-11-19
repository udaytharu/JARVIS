import cv2
import numpy as np
from PIL import Image
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _resolve_auth_path(*parts: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *parts)


def Images_And_Labels(path):
    try:
        if not os.path.exists(path):
            logger.error(f"Sample path {path} does not exist")
            return [], []

        if not hasattr(cv2, 'face'):
            logger.error("OpenCV 'cv2.face' module not found. Install opencv-contrib-python.")
            return [], []

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        cascade_path = _resolve_auth_path("haarcascade_frontalface_default.xml")
        detector = cv2.CascadeClassifier(cascade_path)

        if detector.empty():
            logger.error("Failed to load cascade classifier")
            return [], []

        image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg')]
        face_samples = []
        ids = []

        for image_path in image_paths:
            try:
                gray_img = Image.open(image_path).convert('L')
                img_arr = np.array(gray_img, 'uint8')
                
                # Basic data augmentation
                flipped_img = cv2.flip(img_arr, 1)  # Horizontal flip
                bright_img = cv2.convertScaleAbs(img_arr, alpha=1.2, beta=10)  # Brightness adjustment
                
                id = int(os.path.split(image_path)[-1].split(".")[1])
                faces = detector.detectMultiScale(img_arr, scaleFactor=1.1, minNeighbors=6)

                for (x, y, w, h) in faces:
                    face_samples.append(img_arr[y:y+h, x:x+w])
                    face_samples.append(flipped_img[y:y+h, x:x+w])
                    face_samples.append(bright_img[y:y+h, x:x+w])
                    ids.extend([id] * 3)  # Add ID for each augmented image

            except Exception as e:
                logger.warning(f"Error processing image {image_path}: {str(e)}")
                continue

        return face_samples, ids

    except Exception as e:
        logger.error(f"Error in Images_And_Labels: {str(e)}")
        return [], []

def train_model():
    try:
        path = _resolve_auth_path('samples')
        logger.info("Starting face training process...")
        
        faces, ids = Images_And_Labels(path)
        
        if not faces or not ids:
            logger.error("No valid training data found")
            return False

        recognizer = cv2.face.LBPHFaceRecognizer_create(radius=1, neighbors=8, grid_x=8, grid_y=8)
        recognizer.train(faces, np.array(ids))

        trainer_dir = _resolve_auth_path('trainer')
        os.makedirs(trainer_dir, exist_ok=True)
        recognizer.write(os.path.join(trainer_dir, 'trainer.yml'))
        
        logger.info("Model trained successfully")
        return True

    except Exception as e:
        logger.error(f"Error in training: {str(e)}")
        return False

if __name__ == "__main__":
    train_model()