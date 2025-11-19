import cv2
import numpy as np
import time
import logging
import pyautogui
from typing import Optional, Tuple, List, Dict, Any
from PIL import Image
import pyperclip
import os

# Try to import mss for screen capture (optional)
try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    logging.warning("mss not available. Screen capture features will be disabled. Install with: pip install mss")

# Try to import pytesseract for OCR (optional)
try:
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logging.warning("pytesseract not available. OCR features will be disabled. Install with: pip install pytesseract")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure pyautogui safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


class RealTimeScreenAnalyzer:
    """Real-time screen analysis and observation for automation assistance."""
    
    def __init__(self):
        if not MSS_AVAILABLE:
            raise ImportError("mss module is not available. Please install it with: pip install mss")
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[0]  # Primary monitor
        self.screen_width = self.monitor["width"]
        self.screen_height = self.monitor["height"]
        logger.info(f"Screen analyzer initialized: {self.screen_width}x{self.screen_height}")
    
    def capture_screen(self, region: Optional[Dict[str, int]] = None) -> np.ndarray:
        """Capture screen or specific region."""
        try:
            if region:
                monitor = {
                    "top": region.get("top", 0),
                    "left": region.get("left", 0),
                    "width": region.get("width", self.screen_width),
                    "height": region.get("height", self.screen_height)
                }
            else:
                monitor = self.monitor
            
            img = np.array(self.sct.grab(monitor))
            # Convert BGRA to BGR for OpenCV compatibility
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            return frame
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None
    
    def get_screen_text(self, region: Optional[Dict[str, int]] = None) -> Tuple[bool, str]:
        """Extract text from screen using OCR."""
        if not OCR_AVAILABLE:
            return False, "OCR not available. Install pytesseract."
        
        try:
            frame = self.capture_screen(region)
            if frame is None:
                return False, "Failed to capture screen"
            
            # Convert to PIL Image for pytesseract
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Perform OCR
            text = pytesseract.image_to_string(pil_image)
            return True, text.strip()
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return False, str(e)
    
    def find_text_on_screen(self, search_text: str, region: Optional[Dict[str, int]] = None) -> List[Dict[str, Any]]:
        """Find text on screen and return locations."""
        if not OCR_AVAILABLE:
            return []
        
        try:
            frame = self.capture_screen(region)
            if frame is None:
                return []
            
            # Convert to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Get text with bounding boxes
            data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            # Search for the text
            matches = []
            search_lower = search_text.lower()
            
            for i, text in enumerate(data['text']):
                if search_lower in text.lower() and text.strip():
                    matches.append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': data['conf'][i]
                    })
            
            return matches
        except Exception as e:
            logger.error(f"Text search failed: {e}")
            return []
    
    def analyze_screen_content(self, region: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Analyze screen content and return structured information."""
        try:
            frame = self.capture_screen(region)
            if frame is None:
                return {"error": "Failed to capture screen"}
            
            analysis = {
                "screen_size": {"width": frame.shape[1], "height": frame.shape[0]},
                "has_text": False,
                "text_content": "",
                "detected_elements": [],
                "mouse_position": pyautogui.position()
            }
            
            # Extract text if OCR is available
            if OCR_AVAILABLE:
                success, text = self.get_screen_text(region)
                if success and text:
                    analysis["has_text"] = True
                    analysis["text_content"] = text
                    # Extract key phrases (buttons, labels, etc.)
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and len(line) > 2:
                            analysis["detected_elements"].append({
                                "type": "text",
                                "content": line
                            })
            
            # Detect buttons (rectangular regions with text)
            # This is a simple heuristic - can be enhanced with ML models
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            # Handle different OpenCV versions (3.x vs 4.x)
            try:
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            except ValueError:
                # OpenCV 3.x returns 3 values
                _, contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            button_candidates = []
            for contour in contours:
                try:
                    x, y, w, h = cv2.boundingRect(contour)
                    area = w * h
                    # Filter for button-like shapes (reasonable size and aspect ratio)
                    # Avoid division by zero
                    if h > 0 and 100 < area < 50000 and 0.2 < (w/h) < 5:
                        button_candidates.append({
                            "type": "button_candidate",
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                            "center": (x + w//2, y + h//2)
                        })
                except Exception as e:
                    logger.debug(f"Error processing contour: {e}")
                    continue
            
            analysis["detected_elements"].extend(button_candidates[:10])  # Limit to top 10
            
            return analysis
        except Exception as e:
            logger.error(f"Screen analysis failed: {e}")
            return {"error": str(e)}
    
    def click_on_text(self, search_text: str, region: Optional[Dict[str, int]] = None) -> Tuple[bool, str]:
        """Find and click on text on screen."""
        matches = self.find_text_on_screen(search_text, region)
        if not matches:
            return False, f"Text '{search_text}' not found on screen"
        
        # Click on the first match
        match = matches[0]
        center_x = match['x'] + match['width'] // 2
        center_y = match['y'] + match['height'] // 2
        
        try:
            pyautogui.click(center_x, center_y)
            logger.info(f"Clicked on '{search_text}' at ({center_x}, {center_y})")
            return True, f"Clicked on '{search_text}' at ({center_x}, {center_y})"
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False, str(e)
    
    def observe_and_respond(self, query: str, region: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Observe screen and provide response based on query."""
        try:
            analysis = self.analyze_screen_content(region)
            
            response = {
                "query": query,
                "screen_analysis": analysis,
                "suggestions": []
            }
            
            query_lower = query.lower()
            
            # Provide context-aware suggestions
            if "button" in query_lower or "click" in query_lower:
                buttons = [e for e in analysis.get("detected_elements", []) if e.get("type") == "button_candidate"]
                if buttons:
                    response["suggestions"].append(f"Found {len(buttons)} potential buttons on screen")
            
            if "text" in query_lower or "read" in query_lower:
                if analysis.get("has_text"):
                    text_preview = analysis.get("text_content", "")[:200]
                    response["suggestions"].append(f"Screen contains text: {text_preview}...")
            
            if "find" in query_lower:
                # Try to extract what to find from query
                words = query_lower.split()
                if len(words) > 1:
                    search_term = " ".join(words[words.index("find") + 1:]) if "find" in words else None
                    if search_term:
                        matches = self.find_text_on_screen(search_term, region)
                        if matches:
                            response["suggestions"].append(f"Found '{search_term}' at {len(matches)} location(s)")
                            response["matches"] = matches
            
            return response
        except Exception as e:
            logger.error(f"Observe and respond failed: {e}")
            return {"error": str(e)}
    
    def save_screenshot(self, filename: Optional[str] = None, region: Optional[Dict[str, int]] = None) -> Tuple[bool, str]:
        """Save screenshot to file."""
        try:
            frame = self.capture_screen(region)
            if frame is None:
                return False, "Failed to capture screen"
            
            if not filename:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            os.makedirs("Data", exist_ok=True)
            filepath = os.path.join("Data", filename)
            cv2.imwrite(filepath, frame)
            logger.info(f"Screenshot saved to {filepath}")
            return True, filepath
        except Exception as e:
            logger.error(f"Screenshot save failed: {e}")
            return False, str(e)
    
    def run_live_view(self, show_analysis: bool = False):
        """Run live screen view with optional analysis overlay."""
        logger.info("Starting live screen view. Press 'q' to exit, 's' to save screenshot.")
        
        while True:
            frame = self.capture_screen()
            if frame is None:
                break
            
            display_frame = frame.copy()
            
            # Add analysis overlay if requested
            if show_analysis and OCR_AVAILABLE:
                try:
                    # Draw mouse position
                    mouse_x, mouse_y = pyautogui.position()
                    cv2.circle(display_frame, (mouse_x, mouse_y), 10, (0, 255, 0), 2)
                    cv2.putText(display_frame, f"Mouse: ({mouse_x}, {mouse_y})", 
                              (mouse_x + 15, mouse_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                except Exception as e:
                    logger.debug(f"Analysis overlay failed: {e}")
            
            # Resize for display if too large
            height, width = display_frame.shape[:2]
            if width > 1920 or height > 1080:
                scale = min(1920/width, 1080/height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                display_frame = cv2.resize(display_frame, (new_width, new_height))
            
            cv2.imshow("Real-Time Screen Analyzer", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.save_screenshot()
                logger.info("Screenshot saved")
        
        cv2.destroyAllWindows()
        logger.info("Live view stopped")
    
    def __del__(self):
        """Cleanup."""
        try:
            if hasattr(self, 'sct'):
                self.sct.close()
        except Exception:
            pass


# Global instance
_screen_analyzer = None

def get_screen_analyzer() -> Optional[RealTimeScreenAnalyzer]:
    """Get or create global screen analyzer instance."""
    global _screen_analyzer
    if not MSS_AVAILABLE:
        logger.error("Cannot create screen analyzer: mss module not available")
        return None
    if _screen_analyzer is None:
        try:
            _screen_analyzer = RealTimeScreenAnalyzer()
        except Exception as e:
            logger.error(f"Failed to create screen analyzer: {e}")
            return None
    return _screen_analyzer


def analyze_screen(region: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """Convenience function to analyze screen."""
    analyzer = get_screen_analyzer()
    if analyzer is None:
        return {"error": "Screen analyzer not available. Please install mss: pip install mss"}
    return analyzer.analyze_screen_content(region)


def find_and_click_text(text: str, region: Optional[Dict[str, int]] = None) -> Tuple[bool, str]:
    """Convenience function to find and click text."""
    analyzer = get_screen_analyzer()
    if analyzer is None:
        return False, "Screen analyzer not available. Please install mss: pip install mss"
    return analyzer.click_on_text(text, region)


def observe_screen(query: str, region: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """Convenience function to observe screen and respond to query."""
    analyzer = get_screen_analyzer()
    if analyzer is None:
        return {"error": "Screen analyzer not available. Please install mss: pip install mss"}
    return analyzer.observe_and_respond(query, region)


def run_screen_capture():
    """Original function for backward compatibility."""
    analyzer = get_screen_analyzer()
    if analyzer is None:
        logger.error("Cannot run screen capture: mss module not available")
        return
    analyzer.run_live_view(show_analysis=False)


if __name__ == "__main__":
    # Test the screen analyzer
    if not MSS_AVAILABLE:
        print("ERROR: mss module is not available. Please install it with: pip install mss")
        exit(1)
    
    try:
        analyzer = RealTimeScreenAnalyzer()
        
        print("Testing screen analysis...")
        analysis = analyzer.analyze_screen_content()
        print(f"Screen analysis: {analysis}")
        
        print("\nStarting live view. Press 'q' to quit, 's' to save screenshot.")
        analyzer.run_live_view(show_analysis=True)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
