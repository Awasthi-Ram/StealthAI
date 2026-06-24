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
    update_overlay = pyqtSignal(str)
    update_progress = pyqtSignal(int, str)
    trigger_scroll_up = pyqtSignal()
    trigger_scroll_down = pyqtSignal()
    trigger_move_up = pyqtSignal()
    trigger_move_down = pyqtSignal()
    trigger_move_left = pyqtSignal()
    trigger_move_right = pyqtSignal()
    trigger_capture_add = pyqtSignal()
    trigger_process_buffer = pyqtSignal()

class StealthAIApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.config = load_config()
        self.signals = HotkeySignals()
        self.image_buffer = []
        
        self.overlay = OverlayUI()
        self.settings_dialog = None
        
        # Connect signals
        self.signals.trigger_image.connect(self.on_image_trigger)
        self.signals.trigger_audio.connect(self.on_audio_trigger)
        self.signals.trigger_hide.connect(self.on_hide_trigger)
        self.signals.trigger_settings.connect(self.open_settings)
        self.signals.update_overlay.connect(self.overlay.show_message)
        self.signals.update_progress.connect(self.overlay.update_progress)
        self.signals.trigger_scroll_up.connect(self.overlay.scroll_up)
        self.signals.trigger_scroll_down.connect(self.overlay.scroll_down)
        self.signals.trigger_move_up.connect(lambda: self.overlay.move_window(0, -50))
        self.signals.trigger_move_down.connect(lambda: self.overlay.move_window(0, 50))
        self.signals.trigger_move_left.connect(lambda: self.overlay.move_window(-50, 0))
        self.signals.trigger_move_right.connect(lambda: self.overlay.move_window(50, 0))
        self.signals.trigger_capture_add.connect(self.on_capture_add)
        self.signals.trigger_process_buffer.connect(self.on_process_buffer)
        
        # Connect overlay buttons and opacity
        self.overlay.quit_btn.clicked.connect(self.quit_app)
        self.overlay.settings_btn.clicked.connect(self.open_settings)
        self.overlay.setWindowOpacity(self.config.get("overlay_opacity", 0.9))
        
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
        keyboard.add_hotkey(self.config.get("hotkey_image", "ctrl+shift+1"), lambda: self.signals.trigger_image.emit(), suppress=True)
        keyboard.add_hotkey(self.config.get("hotkey_audio", "ctrl+shift+2"), lambda: self.signals.trigger_audio.emit(), suppress=True)
        keyboard.add_hotkey(self.config.get("hotkey_hide", "ctrl+shift+3"), lambda: self.signals.trigger_hide.emit(), suppress=True)
        keyboard.add_hotkey(self.config.get("hotkey_settings", "ctrl+shift+s"), lambda: self.signals.trigger_settings.emit(), suppress=True)
        keyboard.add_hotkey(self.config.get("hotkey_scroll_up", "ctrl+alt+up"), lambda: self.signals.trigger_scroll_up.emit(), suppress=True)
        keyboard.add_hotkey(self.config.get("hotkey_scroll_down", "ctrl+alt+down"), lambda: self.signals.trigger_scroll_down.emit(), suppress=True)
        keyboard.add_hotkey(self.config.get("hotkey_move_up", "alt+shift+up"), lambda: self.signals.trigger_move_up.emit(), suppress=True)
        keyboard.add_hotkey(self.config.get("hotkey_move_down", "alt+shift+down"), lambda: self.signals.trigger_move_down.emit(), suppress=True)
        keyboard.add_hotkey(self.config.get("hotkey_move_left", "alt+shift+left"), lambda: self.signals.trigger_move_left.emit(), suppress=True)
        keyboard.add_hotkey(self.config.get("hotkey_move_right", "alt+shift+right"), lambda: self.signals.trigger_move_right.emit(), suppress=True)
        keyboard.add_hotkey(self.config.get("hotkey_capture_add", "ctrl+shift+4"), lambda: self.signals.trigger_capture_add.emit(), suppress=True)
        keyboard.add_hotkey(self.config.get("hotkey_process_buffer", "ctrl+shift+5"), lambda: self.signals.trigger_process_buffer.emit(), suppress=True)

    def update_hotkeys(self):
        self.config = load_config()
        self.register_hotkeys()
        self.overlay.setWindowOpacity(self.config.get("overlay_opacity", 0.9))
        
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
        threading.Thread(target=self._process_image_task).start()
        
    def _progress_cb(self, val, msg):
        self.signals.update_progress.emit(val, msg)
        
    def _process_image_task(self):
        img = capture_screen()
        if img:
            res = process_with_ai(images=[img], progress_cb=self._progress_cb)
            self.signals.update_overlay.emit(res)
            self.signals.update_progress.emit(100, "")
        else:
            self.signals.update_overlay.emit("Failed to capture screen.")

    def on_capture_add(self):
        img = capture_screen()
        if img:
            self.image_buffer.append(img)
            self.overlay.show_message(f"Captured image {len(self.image_buffer)}. Waiting for process command...")
        else:
            self.overlay.show_message("Failed to capture screen.")
            
    def on_process_buffer(self):
        if not self.image_buffer:
            self.overlay.show_message("No images in buffer. Capture some first.")
            return
        
        self.overlay.show_message(f"Processing {len(self.image_buffer)} images...")
        threading.Thread(target=self._process_buffer_task).start()
        
    def _process_buffer_task(self):
        res = process_with_ai(images=self.image_buffer, progress_cb=self._progress_cb)
        self.signals.update_overlay.emit(res)
        self.signals.update_progress.emit(100, "")
        self.image_buffer.clear()

    def on_audio_trigger(self):
        self.overlay.show_message("Recording audio (5s) and capturing screen...")
        threading.Thread(target=self._process_audio_task).start()
        
    def _process_audio_task(self):
        img = capture_screen()
        audio_path = record_audio(duration=5)
        if img and audio_path:
            self.signals.update_overlay.emit("Processing with AI...")
            res = process_with_ai(images=[img], audio_path=audio_path, progress_cb=self._progress_cb)
            self.signals.update_overlay.emit(res)
            self.signals.update_progress.emit(100, "")
            cleanup_audio(audio_path)
        else:
            self.signals.update_overlay.emit("Failed to capture screen or audio.")

    def quit_app(self):
        keyboard.unhook_all()
        self.app.quit()

    def run(self):
        self.overlay.show_message("StealthAI Running\nListening for hotkeys...\n(This overlay is invisible to screen capture)")
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app = StealthAIApp()
    app.run()
