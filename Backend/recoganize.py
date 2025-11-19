import cv2
import pyautogui as p
import logging
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def _resolve_auth_path(*parts: str) -> str:
    """Return an absolute path inside the `Backend/auth` directory."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *parts)


def AuthenticateFace():
    flag = 0  # Initialize flag
    try:
        # Validate file paths (use relative to repo)
        model_path = _resolve_auth_path('trainer', 'trainer.yml')
        cascade_path = _resolve_auth_path('haarcascade_frontalface_default.xml')
        
        if not os.path.exists(model_path) or not os.path.exists(cascade_path):
            logger.error("Model or cascade file not found")
            return flag

        if not hasattr(cv2, 'face'):
            logger.error("OpenCV 'cv2.face' module not found. Install opencv-contrib-python.")
            return flag

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(model_path)
        face_cascade = cv2.CascadeClassifier(cascade_path)

        if face_cascade.empty():
            logger.error("Failed to load cascade classifier")
            return flag

        font = cv2.FONT_HERSHEY_SIMPLEX
        # Map numeric IDs from your training data to display names. Ensure your face ID is 1.
        names = {1: 'User'}
        confidence_threshold = 70  # Adjusted confidence threshold

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
            return flag

        cam.set(3, 640)
        cam.set(4, 480)
        min_w = 0.1 * cam.get(3)
        min_h = 0.1 * cam.get(4)

        start_time = time.time()
        timeout = 30  # 30 seconds timeout

        while time.time() - start_time < timeout:
            ret, img = cam.read()
            if not ret:
                logger.warning("Failed to capture image")
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,  # Optimized for better detection
                minNeighbors=6,
                minSize=(int(min_w), int(min_h))
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

                if confidence < confidence_threshold:
                    display_name = names.get(id, f"ID {id}")
                    confidence = f"{round(100 - confidence)}%"
                    flag = 1
                else:
                    display_name = "unknown"
                    confidence = f"{round(100 - confidence)}%"
                    flag = 0

                cv2.putText(img, str(display_name), (x+5, y-5), font, 1, (255, 255, 255), 2)
                cv2.putText(img, str(confidence), (x+5, y+h-5), font, 1, (255, 255, 0), 1)

            cv2.imshow('camera', img)

            k = cv2.waitKey(10) & 0xff
            if k == 27 or flag == 1:
                break

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        if 'cam' in locals() and cam.isOpened():
            cam.release()
        cv2.destroyAllWindows()
    return flag