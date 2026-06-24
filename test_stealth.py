import unittest
import sys
from PyQt6.QtWidgets import QApplication
from ui import OverlayUI
from main import HotkeySignals

app = QApplication(sys.argv)

class TestStealthAI(unittest.TestCase):
    def test_overlay_ui_attributes(self):
        """Test that OverlayUI has all required methods and widgets."""
        overlay = OverlayUI()
        self.assertTrue(hasattr(overlay, 'update_progress'), "OverlayUI is missing update_progress")
        self.assertTrue(hasattr(overlay, 'show_message'), "OverlayUI is missing show_message")
        self.assertIsNotNone(overlay.progress_bar, "OverlayUI is missing progress_bar")
        self.assertIsNotNone(overlay.progress_label, "OverlayUI is missing progress_label")
        
    def test_hotkey_signals(self):
        """Test that HotkeySignals has the new update_progress signal."""
        signals = HotkeySignals()
        self.assertTrue(hasattr(signals, 'update_progress'), "HotkeySignals is missing update_progress")
        self.assertTrue(hasattr(signals, 'update_overlay'), "HotkeySignals is missing update_overlay")

    def test_progress_bar_updates(self):
        """Test that calling update_progress updates the UI elements safely."""
        overlay = OverlayUI()
        overlay.update_progress(50, "Testing progress...")
        self.assertEqual(overlay.progress_bar.value(), 50)
        self.assertEqual(overlay.progress_label.text(), "Testing progress...")
        
        # Test completion hides elements
        overlay.update_progress(100, "Done")
        self.assertFalse(overlay.progress_bar.isVisible())

if __name__ == '__main__':
    unittest.main()
