import json
import os

CONFIG_FILE = "settings.json"

DEFAULT_CONFIG = {
    "backend_mode": "API",
    "gemini_api_key": "",
    "claude_api_key": "",
    "selected_model": "Gemini 3.5 Flash",  # Options: Gemini 3.5 Flash, Gemini 3.5 Pro, Claude Sonnet 4.6
    "system_prompt": "You are an expert coding assistant. Solve the coding problem provided in the image/audio. Be extremely concise.",
    "hotkey_image": "ctrl+shift+1",
    "hotkey_audio": "ctrl+shift+2",
    "hotkey_hide": "ctrl+shift+3",
    "hotkey_settings": "ctrl+shift+s",
    "hotkey_scroll_up": "ctrl+shift+up",
    "hotkey_scroll_down": "ctrl+shift+down",
    "hotkey_move_up": "alt+shift+up",
    "hotkey_move_down": "alt+shift+down",
    "hotkey_move_left": "alt+shift+left",
    "hotkey_move_right": "alt+shift+right",
    "hotkey_capture_add": "ctrl+shift+4",
    "hotkey_process_buffer": "ctrl+shift+5",
    "overlay_opacity": 0.9
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            # Merge with defaults to ensure all keys exist
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")
