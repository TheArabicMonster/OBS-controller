🌍 **Language / Langue** :
[English](./README.en.md) | [Français](./README.md)

# Gesture Recognition for OBS Control

## Prerequisites
- Windows 10/11 (not tested on Linux or macOS)
- OBS Studio with WebSocket enabled (Tools -> WebSocket Server Settings -> enable "Enable WebSocket server", uncheck "Use authentication" -> click "OK")
- Python 3.10.9 (required, MediaPipe doesn't work with other recent versions)
- A webcam

## Python Dependencies
- `opencv-python` : Video processing and camera access
- `mediapipe` : Hand gesture detection and recognition
- `obsws-python` : WebSocket communication with OBS Studio

## Installation

### Automatic Method (Recommended)

not available at the moment

### Manual Method

1. **Install Python 3.10.9**
   - Download from: https://www.python.org/downloads/release/python-3109/
   - During installation, check "Add Python to PATH"

2. **Create a virtual environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure OBS**
   - Create a media source in OBS with the name specified in `config.py` (default: `China credit`)
   - Create the scenes mentioned in `config.py` (default: `Scène 1` and `Scène 2`)
   - Enable the WebSocket plugin in OBS (as mentioned in the prerequisites section)

5. **Run the script**
   ```powershell
   python hand_to_obs.py
   ```

### Installation Verification

To verify that everything is properly installed:
```powershell
python test_installation.py
```

## Project Structure

```
OBS-controller/
├── hand_to_obs.py           # Main script
├── config.py                # Project configuration
├── gesture_translator.py    # Gesture detection and translation
├── gesture_handler.py       # Actions to perform for each gesture
├── requirements.txt         # Python dependencies list
├── setup.ps1               # PowerShell installation script
├── setup.bat               # Batch installation script
├── README.md               # French documentation
└── README.en.md            # English documentation
```

## Available Gestures
- **Open hand** : No action (neutral gesture)
- **Thumbs up** : Starts video playback
- **Peace sign** : No action (neutral gesture)
- **Swipe left** : Changes to the configured left swipe scene
- **Swipe right** : Changes to the configured right swipe scene

## Customization

### General Configuration (`config.py`)
- `CAMERA_ID` : Camera ID (0 for built-in webcam, 1 for external)
- `VIDEO_SOURCE_NAME` : Name of the media source in OBS
- `SWIPE_LEFT_SCENE` / `SWIPE_RIGHT_SCENE` : Scene names for swipes

### Gesture Detection Parameters (`config.py`)
- `GESTURE_CONFIRMATION_DURATION` : Duration (in seconds) a static gesture must be held to be validated (default: 0.1s)
- `GESTURE_DEBOUNCE_TIME` : Wait time (in seconds) before the same gesture can be triggered again (default: 0.3s)

### Adding New Gestures
- Modify `gesture_translator.py` to add detection logic
- Modify `gesture_handler.py` to define the actions to perform

## Troubleshooting

### Installation
- If the installation script fails, verify that Python 3.10.9 is properly installed and in PATH
- If PowerShell blocks execution: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Camera
- If camera doesn't work, try changing `CAMERA_ID` in `config.py`
- Close all applications using the camera (Teams, Zoom, browsers)
- Check Windows camera permissions: `ms-settings:privacy-webcam`
- Restart computer if necessary

### OBS
- Verify that OBS is running before the script
- Enable WebSocket: Tools > WebSocket Server Settings
- Check port (default: 4455) and password (if enabled in WebSocket server settings) in `config.py`
- Create the scenes and sources mentioned in `config.py`

### Gestures
- Adjust `GESTURE_CONFIRMATION_DURATION` and `GESTURE_DEBOUNCE_TIME` in `config.py`
- Ensure good lighting for detection
- Position yourself about 50-100cm from the camera
