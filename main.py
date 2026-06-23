import sys
import keyboard
import threading
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from ui import OverlayUI, SettingsDialog
from config import load_config
from capture import capture_screen, record_audio, cleanup_audio
from ai_client import process_with_ai

class HotkeySignals(QObject):
    trigger_image = pyqtSignal()
    trigger_audio = pyqtSignal()
    trigger_hide = pyqtSignal()
    trigger_settings = pyqtSignal()

class StealthAIApp:
    def __init__(self):
        self.app = QApplication(sys.sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.config = load_config()
        self.signals = HotkeySignals()
        
        self.overlay = OverlayUI()
        self.settings_dialog = None
        
        # Connect signals
        self.signals.trigger_image.connect(self.on_image_trigger)
        self.signals.trigger_audio.connect(self.on_audio_trigger)
        self.signals.trigger_hide.connect(self.on_hide_trigger)
        self.signals.trigger_settings.connect(self.open_settings)
        
        self.setup_tray()
        self.register_hotkeys()
        
    def setup_tray(self):
        # Create a dummy icon since we don't have an image file yet
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.black)
        self.tray_icon = QSystemTrayIcon(QIcon(pixmap), self.app)
        
        menu = QMenu()
        settings_action = menu.addAction("Settings")
        settings_action.triggered.connect(self.open_settings)
        
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
        
    def register_hotkeys(self):
        keyboard.unhook_all()
        keyboard.add_hotkey(self.config.get("hotkey_image", "ctrl+shift+1"), lambda: self.signals.trigger_image.emit())
        keyboard.add_hotkey(self.config.get("hotkey_audio", "ctrl+shift+2"), lambda: self.signals.trigger_audio.emit())
        keyboard.add_hotkey(self.config.get("hotkey_hide", "ctrl+shift+3"), lambda: self.signals.trigger_hide.emit())
        keyboard.add_hotkey(self.config.get("hotkey_settings", "ctrl+shift+s"), lambda: self.signals.trigger_settings.emit())

    def update_hotkeys(self):
        self.config = load_config()
        self.register_hotkeys()
        
    def open_settings(self):
        if not self.settings_dialog:
            self.settings_dialog = SettingsDialog()
            self.settings_dialog.settings_saved.connect(self.update_hotkeys)
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()

    def on_hide_trigger(self):
        self.overlay.hide()

    def on_image_trigger(self):
        self.overlay.show_message("Capturing screen and analyzing...")
        # Run in thread to not block UI
        threading.Thread(target=self._process_image_task).start()
        
    def _process_image_task(self):
        img = capture_screen()
        if img:
            res = process_with_ai(image=img)
            self.overlay.show_message(res)
        else:
            self.overlay.show_message("Failed to capture screen.")

    def on_audio_trigger(self):
        self.overlay.show_message("Recording audio (5s) and capturing screen...")
        threading.Thread(target=self._process_audio_task).start()
        
    def _process_audio_task(self):
        img = capture_screen()
        audio_path = record_audio(duration=5)
        if img and audio_path:
            self.overlay.show_message("Processing with AI...")
            res = process_with_ai(image=img, audio_path=audio_path)
            self.overlay.show_message(res)
            cleanup_audio(audio_path)
        else:
            self.overlay.show_message("Failed to capture screen or audio.")

    def quit_app(self):
        keyboard.unhook_all()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = StealthAIApp()
    app.run()
