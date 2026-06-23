# Stealth AI Coding Assistant

A stealth AI coding assistant designed to provide answers via screen and audio capture while remaining hidden from screen recording and screen sharing software (like Zoom, OBS, MS Teams, etc.).

## Features
- **Invisible Overlay:** Uses the Windows `SetWindowDisplayAffinity` (`WDA_EXCLUDEFROMCAPTURE`) API to remain completely un-capturable by screen recorders.
- **Global Hotkeys:** Control the app in the background while focusing on other windows.
- **AI Integration:** Uses Gemini (for audio/image processing) and Claude (for image/text processing).
- **Settings UI:** Configure your API keys, model, prompts, and custom shortcuts through a sleek user interface.

## Prerequisites
- Windows OS (due to specific Window APIs used).
- Python 3.10+ installed.

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd StealthAI
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Build the `.exe`
To compile the application into a standalone executable that runs without a console window, run the included build script:

```powershell
.\build.bat
```

*(Alternatively, you can run the command directly: `pyinstaller --noconsole --onefile --hidden-import="mss" --hidden-import="keyboard" --hidden-import="sounddevice" --hidden-import="soundfile" --name "StealthAI" main.py`)*

The built executable will be located in the `dist` directory.

## Usage
1. Run the `StealthAI.exe` from the `dist` folder.
2. Check your system tray for the app icon, right click and select **Settings**.
3. Input your Gemini or Claude API key and customize your hotkeys.
4. Use the hotkeys to instantly capture your screen and audio, and wait for the overlay to provide the AI's response.
