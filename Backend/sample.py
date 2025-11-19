import cv2
import os
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _resolve_auth_path(*parts: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *parts)


def capture_samples():
    try:
        cascade_path = _resolve_auth_path('haarcascade_frontalface_default.xml')
        if not os.path.exists(cascade_path):
            logger.error("Cascade file not found")
            return

        detector = cv2.CascadeClassifier(cascade_path)
        if detector.empty():
            logger.error("Failed to load cascade classifier")
            return

        # Initialize camera with retry mechanism
        max_retries = 3
        for attempt in range(max_retries):
            cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            if not cam.isOpened():
                logger.warning(f"Camera initialization attempt {attempt + 1} failed")
                time.sleep(1)
                continue
            break
        else:
            logger.error("Failed to initialize camera after multiple attempts")
            return

        cam.set(3, 640)
        cam.set(4, 480)

        face_id = input("Enter a Numeric user ID (0-9): ")
        try:
            face_id = int(face_id)
            if face_id < 0 or face_id > 9:
                raise ValueError
        except ValueError:
            logger.error("Invalid user ID. Please enter a number between 0 and 9")
            cam.release()
            return

        samples_path = _resolve_auth_path('samples')
        os.makedirs(samples_path, exist_ok=True)

        logger.info("Taking samples, look at camera...")
        count = 0
        max_samples = 100

        while count < max_samples:
            ret, img = cam.read()
            if not ret:
                logger.warning("Failed to capture image")
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6)

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                count += 1
                
                filename = os.path.join(samples_path, f"face.{face_id}.{count}.jpg")
                cv2.imwrite(filename, gray[y:y+h, x:x+w])
                
                cv2.imshow('image', img)

            k = cv2.waitKey(100) & 0xff
            if k == 27:
                break

        logger.info(f"Samples taken: {count}")
        
    except Exception as e:
        logger.error(f"Error in capture_samples: {str(e)}")
    finally:
        if 'cam' in locals() and cam.isOpened():
            cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_samples()