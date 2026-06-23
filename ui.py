import ctypes
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QDialog, QLabel, QLineEdit, QComboBox, 
                             QPushButton, QFormLayout, QHBoxLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor, QPalette
from config import load_config, save_config

class OverlayUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Make the window invisible to screen capture
        try:
            hwnd = int(self.winId())
            # WDA_EXCLUDEFROMCAPTURE = 0x00000011
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x00000011)
        except Exception as e:
            print(f"Failed to set window display affinity: {e}")

        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 180);
                color: #00FF00;
                font-family: Consolas;
                font-size: 16px;
                border: 2px solid #555555;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.text_display)
        
    def show_message(self, text):
        self.text_display.setPlainText(text)
        self.show()

class SettingsDialog(QDialog):
    settings_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Stealth AI Settings")
        self.setFixedSize(400, 450)
        
        layout = QFormLayout(self)
        
        self.gemini_key = QLineEdit(self.config.get("gemini_api_key", ""))
        self.claude_key = QLineEdit(self.config.get("claude_api_key", ""))
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Gemini 1.5 Flash", "Gemini 1.5 Pro", "Claude 3.5 Sonnet"])
        self.model_combo.setCurrentText(self.config.get("selected_model", "Gemini 1.5 Flash"))
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlainText(self.config.get("system_prompt", ""))
        self.prompt_edit.setFixedHeight(80)
        
        self.hk_image = QLineEdit(self.config.get("hotkey_image", "ctrl+shift+1"))
        self.hk_audio = QLineEdit(self.config.get("hotkey_audio", "ctrl+shift+2"))
        self.hk_hide = QLineEdit(self.config.get("hotkey_hide", "ctrl+shift+3"))
        self.hk_settings = QLineEdit(self.config.get("hotkey_settings", "ctrl+shift+s"))
        
        layout.addRow("Gemini API Key:", self.gemini_key)
        layout.addRow("Claude API Key:", self.claude_key)
        layout.addRow("Model:", self.model_combo)
        layout.addRow("System Prompt:", self.prompt_edit)
        layout.addRow("Hotkey (Image):", self.hk_image)
        layout.addRow("Hotkey (Audio+Image):", self.hk_audio)
        layout.addRow("Hotkey (Hide Overlay):", self.hk_hide)
        layout.addRow("Hotkey (Settings):", self.hk_settings)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        
    def save_settings(self):
        self.config["gemini_api_key"] = self.gemini_key.text()
        self.config["claude_api_key"] = self.claude_key.text()
        self.config["selected_model"] = self.model_combo.currentText()
        self.config["system_prompt"] = self.prompt_edit.toPlainText()
        self.config["hotkey_image"] = self.hk_image.text()
        self.config["hotkey_audio"] = self.hk_audio.text()
        self.config["hotkey_hide"] = self.hk_hide.text()
        self.config["hotkey_settings"] = self.hk_settings.text()
        
        save_config(self.config)
        self.settings_saved.emit()
        self.accept()
