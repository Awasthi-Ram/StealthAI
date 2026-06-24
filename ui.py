import ctypes
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, 
                             QWidget, QDialog, QLabel, QLineEdit, QComboBox, 
                             QPushButton, QFormLayout, QHBoxLayout, QProgressBar, QSlider)
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
                background-color: rgba(25, 25, 30, 230);
                color: #F8F8F2;
                font-family: 'Segoe UI', Consolas, sans-serif;
                font-size: 18px;
                line-height: 1.5;
                border: 2px solid #44475A;
                border-radius: 12px;
                padding: 15px;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(0,0,0,0);
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #6272A4;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        
        layout.addWidget(self.text_display)
        
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #F8F8F2; font-family: 'Segoe UI', sans-serif; font-size: 14px; font-weight: bold;")
        self.progress_label.hide()
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #44475A;
                border-radius: 5px;
                background-color: #282A36;
                height: 8px;
                max-height: 8px;
            }
            QProgressBar::chunk {
                background-color: #50FA7B;
                border-radius: 4px;
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        btn_layout = QHBoxLayout()
        self.settings_btn = QPushButton("⚙ Settings", self)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(68, 71, 90, 200);
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(68, 71, 90, 255);
            }
        """)
        
        self.quit_btn = QPushButton("Quit", self)
        self.quit_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 85, 85, 200);
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 85, 85, 255);
            }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.settings_btn)
        btn_layout.addWidget(self.quit_btn)
        layout.addLayout(btn_layout)
        
    def show_message(self, text):
        self.text_display.setPlainText(text)
        self.show()

    def update_progress(self, value, text):
        if value < 100:
            if not self.progress_bar.isVisible():
                self.progress_bar.show()
                self.progress_label.show()
            self.progress_bar.setValue(value)
            self.progress_label.setText(text)
        else:
            self.progress_bar.hide()
            self.progress_label.hide()
            
    def scroll_up(self):
        scrollbar = self.text_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.value() - 50)

    def scroll_down(self):
        scrollbar = self.text_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.value() + 50)

    def move_window(self, dx, dy):
        pos = self.pos()
        self.move(pos.x() + dx, pos.y() + dy)

class SettingsDialog(QDialog):
    settings_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Stealth AI Settings")
        self.setFixedSize(450, 720)
        
        layout = QFormLayout(self)
        
        self.backend_combo = QComboBox()
        self.backend_combo.addItems(["API", "Web"])
        self.backend_combo.setCurrentText(self.config.get("backend_mode", "API"))
        layout.addRow("Integration Mode:", self.backend_combo)
        
        self.gemini_key = QLineEdit(self.config.get("gemini_api_key", ""))
        self.claude_key = QLineEdit(self.config.get("claude_api_key", ""))
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Gemini 3.5 Flash", "Gemini 3.5 Pro", "Claude Sonnet 4.6"])
        self.model_combo.setCurrentText(self.config.get("selected_model", "Gemini 3.5 Flash"))
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlainText(self.config.get("system_prompt", ""))
        self.prompt_edit.setFixedHeight(80)
        
        self.hk_image = QLineEdit(self.config.get("hotkey_image", "ctrl+shift+1"))
        self.hk_audio = QLineEdit(self.config.get("hotkey_audio", "ctrl+shift+2"))
        self.hk_hide = QLineEdit(self.config.get("hotkey_hide", "ctrl+shift+3"))
        self.hk_settings = QLineEdit(self.config.get("hotkey_settings", "ctrl+shift+s"))
        self.hk_scroll_up = QLineEdit(self.config.get("hotkey_scroll_up", "ctrl+shift+up"))
        self.hk_scroll_down = QLineEdit(self.config.get("hotkey_scroll_down", "ctrl+shift+down"))
        self.hk_move_up = QLineEdit(self.config.get("hotkey_move_up", "alt+shift+up"))
        self.hk_move_down = QLineEdit(self.config.get("hotkey_move_down", "alt+shift+down"))
        self.hk_move_left = QLineEdit(self.config.get("hotkey_move_left", "alt+shift+left"))
        self.hk_move_right = QLineEdit(self.config.get("hotkey_move_right", "alt+shift+right"))
        self.hk_capture_add = QLineEdit(self.config.get("hotkey_capture_add", "ctrl+shift+4"))
        self.hk_process_buffer = QLineEdit(self.config.get("hotkey_process_buffer", "ctrl+shift+5"))
        
        layout.addRow("Gemini API Key:", self.gemini_key)
        layout.addRow("Claude API Key:", self.claude_key)
        layout.addRow("Model:", self.model_combo)
        layout.addRow("System Prompt:", self.prompt_edit)
        layout.addRow("Hotkey (Image):", self.hk_image)
        layout.addRow("Hotkey (Audio+Image):", self.hk_audio)
        layout.addRow("Hotkey (Hide Overlay):", self.hk_hide)
        layout.addRow("Hotkey (Settings):", self.hk_settings)
        layout.addRow("Hotkey (Scroll Up):", self.hk_scroll_up)
        layout.addRow("Hotkey (Scroll Down):", self.hk_scroll_down)
        layout.addRow("Hotkey (Move Up):", self.hk_move_up)
        layout.addRow("Hotkey (Move Down):", self.hk_move_down)
        layout.addRow("Hotkey (Move Left):", self.hk_move_left)
        layout.addRow("Hotkey (Move Right):", self.hk_move_right)
        layout.addRow("Hotkey (Capture+Add):", self.hk_capture_add)
        layout.addRow("Hotkey (Process Multiple):", self.hk_process_buffer)
        
        self.login_btn = QPushButton("Open Gemini Web Login")
        self.login_btn.clicked.connect(self.login_gemini)
        layout.addRow("Web Login:", self.login_btn)
        
        # Opacity slider
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        opacity_val = int(self.config.get("overlay_opacity", 0.9) * 100)
        self.opacity_slider.setValue(opacity_val)
        self.opacity_label = QLabel(f"{opacity_val}%")
        self.opacity_slider.valueChanged.connect(lambda v: self.opacity_label.setText(f"{v}%"))
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        layout.addRow("Overlay Opacity:", opacity_layout)
        
        # Connect toggle
        self.backend_combo.currentTextChanged.connect(self.toggle_backend_ui)
        self.toggle_backend_ui(self.backend_combo.currentText())
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        
    def toggle_backend_ui(self, mode):
        is_api = (mode == "API")
        layout = self.layout()
        
        self.gemini_key.setVisible(is_api)
        layout.labelForField(self.gemini_key).setVisible(is_api)
        self.claude_key.setVisible(is_api)
        layout.labelForField(self.claude_key).setVisible(is_api)
        self.model_combo.setVisible(is_api)
        layout.labelForField(self.model_combo).setVisible(is_api)
        
        self.login_btn.setVisible(not is_api)
        layout.labelForField(self.login_btn).setVisible(not is_api)

    def login_gemini(self):
        import threading
        from ai_client import login_gemini_web
        threading.Thread(target=login_gemini_web, daemon=True).start()
        
    def save_settings(self):
        self.config["backend_mode"] = self.backend_combo.currentText()
        self.config["gemini_api_key"] = self.gemini_key.text()
        self.config["claude_api_key"] = self.claude_key.text()
        self.config["selected_model"] = self.model_combo.currentText()
        self.config["system_prompt"] = self.prompt_edit.toPlainText()
        self.config["hotkey_image"] = self.hk_image.text()
        self.config["hotkey_audio"] = self.hk_audio.text()
        self.config["hotkey_hide"] = self.hk_hide.text()
        self.config["hotkey_settings"] = self.hk_settings.text()
        self.config["hotkey_scroll_up"] = self.hk_scroll_up.text()
        self.config["hotkey_scroll_down"] = self.hk_scroll_down.text()
        self.config["hotkey_move_up"] = self.hk_move_up.text()
        self.config["hotkey_move_down"] = self.hk_move_down.text()
        self.config["hotkey_move_left"] = self.hk_move_left.text()
        self.config["hotkey_move_right"] = self.hk_move_right.text()
        self.config["hotkey_capture_add"] = self.hk_capture_add.text()
        self.config["hotkey_process_buffer"] = self.hk_process_buffer.text()
        self.config["overlay_opacity"] = self.opacity_slider.value() / 100.0
        
        save_config(self.config)
        self.settings_saved.emit()
        self.accept()
