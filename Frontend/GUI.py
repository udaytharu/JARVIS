from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, 
    QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, 
    QSizePolicy, QGraphicsDropShadowEffect, QScrollArea, QSlider, QShortcut
)
from PyQt5.QtGui import (
    QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, 
    QTextBlockFormat, QLinearGradient, QPalette, QBrush, QPen, QKeySequence
)
from PyQt5.QtCore import (
    Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect, 
    QThread, pyqtSignal, QPoint, QPropertyAnimation, QParallelAnimationGroup
)
from dotenv import dotenv_values
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from Backend.assistant_core import process_input
from Backend.utils import AnswerModifier, QueryModifier, TempDirectoryPath, GraphicDirectoryPath, SetAssistantStatus, GetAssistantStatus

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Jarvis")
current_dir = os.getcwd()
old_chat_message = ""

# Paths
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")

# Modern color scheme
COLORS = {
    'primary': '#1a1a2e',
    'secondary': '#16213e',
    'accent': '#0f3460',
    'highlight': '#e94560',
    'text': '#ffffff',
    'text_secondary': '#b0b0b0',
    'success': '#4CAF50',
    'warning': '#FF9800',
    'error': '#f44336'
}

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def ShowTextTOScreen(Text):
    """Display text on screen with error handling."""
    try:
        with open(os.path.join(TempDirPath, 'Responses.data'), "w", encoding='utf-8') as file:
            file.write(Text)
    except Exception as e:
        print(f"Error showing text to screen: {e}")

class ModernButton(QPushButton):
    """Modern styled button with hover effects."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #e94560;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #1a1a2e;
            }
        """)

class ModernTextEdit(QTextEdit):
    """Modern styled text edit with smooth scrolling."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTextEdit {
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 15px;
                color: white;
                font-size: 14px;
                padding: 15px;
                selection-background-color: #e94560;
            }
            QScrollBar:vertical {
                background-color: #1a1a2e;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #0f3460;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #e94560;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

class ChatSection(QWidget):
    """Enhanced chat section with modern design."""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Chat display area (increase size)
        self.chat_text_edit = ModernTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setMinimumHeight(250)  # Increased height
        self.chat_text_edit.setMaximumHeight(600)  # Allow it to grow more
        
        # Status label with modern styling
        self.status_label = QLabel("Ready! 🚀")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba(76, 175, 80, 0.1);
                border-radius: 10px;
                border: 2px solid #4CAF50;
            }
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        
        # Assistant animation (decrease gif size)
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none; background: transparent;")
        try:
            movie = QMovie(GraphicDirectoryPath('Jarvis.gif'))
            movie.setScaledSize(QSize(150, 150))  # Decreased gif size
            self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.gif_label.setMovie(movie)
            movie.start()
        except Exception:
            # Fallback if gif not found
            self.gif_label.setText("🤖")
            self.gif_label.setStyleSheet("font-size: 60px; color: #e94560;")
        self.gif_label.setAlignment(Qt.AlignCenter)
        
        # Layout arrangement
        layout.addWidget(self.chat_text_edit, 2)  # Give chat box more stretch
        layout.addWidget(self.status_label)
        layout.addWidget(self.gif_label, 0)  # Less stretch for gif
        
        # Setup timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_content)
        self.timer.start(100)  # Reduced frequency for better performance
        
    def setup_animations(self):
        """Setup smooth animations."""
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        
    def update_content(self):
        """Update chat content and status."""
        global old_chat_message
        
        # Update chat messages
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                if messages and messages != old_chat_message:
                    self.add_message(messages, COLORS['text'])
            old_chat_message = messages
        except Exception:
            pass
        
        # Update status
        try:
            status = GetAssistantStatus()
            if status != self.status_label.text():
                self.status_label.setText(status)
                self.update_status_color(status)
        except Exception:
            pass
    
    def update_status_color(self, status):
        """Update status label color based on status."""
        if "Ready" in status or "Available" in status:
            color = COLORS['success']
        elif "Listening" in status or "Processing" in status:
            color = COLORS['warning']
        elif "Sleeping" in status:
            color = COLORS['text_secondary']
        else:
            color = COLORS['highlight']
        
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba({color[1:3]}, {color[3:5]}, {color[5:7]}, 0.1);
                border-radius: 10px;
                border: 2px solid {color};
            }}
        """)
    
    def add_message(self, message, color):
        """Add message with smooth animation."""
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

        # Auto-scroll to bottom
        scrollbar = self.chat_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class ModernTopBar(QWidget):
    """Modern top bar with controls."""
    pinToggled = pyqtSignal(bool)  # Signal to toggle always-on-top
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_pinned = False
        self.setup_ui()
    def setup_ui(self):
        """Setup the top bar interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        # Title
        title = QLabel(f"{Assistantname} 2.0 AI Assistant ")
        title.setStyleSheet("""
            QLabel {
                color: #e94560;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        # Pin button
        self.pin_btn = ModernButton("📌")
        self.pin_btn.setFixedSize(40, 40)
        self.pin_btn.setCheckable(True)
        self.pin_btn.setStyleSheet("""
            QPushButton {
                background-color: #0f3460;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #4CAF50;
            }
            QPushButton:hover {
                background-color: #e94560;
            }
        """)
        self.pin_btn.clicked.connect(self.toggle_pin)
        # Control buttons
        self.minimize_btn = ModernButton("−")
        self.minimize_btn.setFixedSize(40, 40)
        self.minimize_btn.clicked.connect(self.parent().showMinimized)
        self.close_btn = ModernButton("×")
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border-radius: 20px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.close_btn.clicked.connect(self.parent().close)
        # Layout
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.pin_btn)
        layout.addWidget(self.minimize_btn)
        layout.addWidget(self.close_btn)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a2e;
                border-bottom: 2px solid #0f3460;
            }
        """)
    def toggle_pin(self):
        self.is_pinned = not self.is_pinned
        self.pin_btn.setChecked(self.is_pinned)
        self.pin_btn.setText("📌" if self.is_pinned else "📌")
        self.pinToggled.emit(self.is_pinned)

class MainWindow(QMainWindow):
    """Main application window with modern design."""
    def __init__(self):
        super().__init__()
        self.is_always_on_top = False
        self.setup_window()
        self.setup_ui()
    def setup_window(self):
        """Setup window properties."""
        self.setWindowTitle(f"{Assistantname} AI Voice Assistant")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Set window size
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() // 4, screen.height() // 4, 
                        screen.width() // 2, screen.height() // 2)
    def setup_ui(self):
        """Setup the main user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Top bar
        self.top_bar = ModernTopBar(self)
        self.top_bar.pinToggled.connect(self.toggle_always_on_top)
        layout.addWidget(self.top_bar)
        # Chat section
        self.chat_section = ChatSection()
        layout.addWidget(self.chat_section)
        # Developed by label
        self.dev_label = QLabel("Developed by uday-studio")
        self.dev_label.setAlignment(Qt.AlignCenter)
        self.dev_label.setStyleSheet("color: #b0b0b0; font-size: 15px; padding: 8px 0 8px 0;")
        layout.addWidget(self.dev_label)
        # Apply modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #16213e;
                border-radius: 20px;
                border: 2px solid #0f3460;
            }
        """)
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        central_widget.setGraphicsEffect(shadow)
    def toggle_always_on_top(self, enabled):
        self.is_always_on_top = enabled
        flags = Qt.FramelessWindowHint
        if enabled:
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
    def mousePressEvent(self, event):
        """Handle mouse press for window dragging."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for window dragging."""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        self.chat_section = ChatSection()
        layout.addWidget(self.chat_section)
        # --- Add input box and send button ---
        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type your message or command...")
        self.input_box.setMinimumHeight(32)
        self.send_button = QPushButton("Send")
        self.send_button.setMinimumHeight(32)
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        # Loading indicator
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #00ff00; font-size: 12px;")
        layout.addWidget(self.status_label)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        # Connect send button and input
        self.send_button.clicked.connect(self.handle_send)
        self.input_box.returnPressed.connect(self.handle_send)
        # Keyboard shortcuts
        self.input_box_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self.input_box_shortcut.activated.connect(self.focus_input_box)
        self.command_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        self.command_shortcut.activated.connect(self.open_command_dialog)
    def focus_input_box(self):
        self.input_box.setFocus()
    def open_command_dialog(self):
        from PyQt5.QtWidgets import QInputDialog
        cmd, ok = QInputDialog.getText(self, "Generate Command", "Enter command:")
        if ok and cmd.strip():
            self.input_box.setText(cmd)
            self.input_box.setFocus()
    def handle_send(self):
        text = self.input_box.text().strip()
        if not text:
            return
        self.status_label.setText("Processing...")
        self.input_box.setDisabled(True)
        self.send_button.setDisabled(True)
        def run_backend():
            import io, sys
            old_stdout = sys.stdout
            sys.stdout = mystdout = io.StringIO()
            try:
                result, image_paths = process_input(text)
            except Exception as e:
                result, image_paths = f"Error: {e}", []
            finally:
                sys.stdout = old_stdout
            return result, image_paths
        from PyQt5.QtCore import QThread, pyqtSignal, QObject
        class Worker(QObject):
            finished = pyqtSignal(str, list)
            def run(self):
                result, image_paths = run_backend()
                self.finished.emit(result, image_paths)
        self.worker = Worker()
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(self.on_backend_finished)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
    def on_backend_finished(self, result, image_paths):
        # Show text result
        for line in result.split('\n'):
            self.chat_section.addMessage(line, 'cyan')
        # Show images inline if any
        if image_paths:
            from PyQt5.QtGui import QPixmap
            for img_path in image_paths:
                if os.path.exists(img_path):
                    img_label = QLabel()
                    pixmap = QPixmap(img_path)
                    img_label.setPixmap(pixmap.scaled(200, 200))
                    self.chat_section.layout().addWidget(img_label)
        self.status_label.setText("")
        self.input_box.clear()
        self.input_box.setDisabled(False)
        self.send_button.setDisabled(False)
        self.input_box.setFocus()
        self.thread.quit()
        self.thread.wait()

def GraphicalUserInterface():
    """Initialize and run the graphical user interface."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName(f"{Assistantname} AI Assistant")
    app.setApplicationVersion("2.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start the application
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()