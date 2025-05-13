🌍 **Language / Langue** :
[English](./README.en.md) | [Français](./README.md)

# Gesture Recognition for OBS Control

## Prerequisites
- Windows
- OBS Studio with Websocket enabled
- Python 3.10.9 (required, mediapipe doesn't work with other recent versions)
- A webcam (btw)

## Installation

1. **Install Python 3.10.9**
- Download from: https://www.python.org/downloads/release/python-3109/
- During installation, check "Add Python to PATH".

2. **Create a virtual environment**
```powershell
py -3.10 -m venv venv310
.\venv310\Scripts\Activate.ps1
```

3. **Install dependencies**
```powershell
pip install mediapipe opencv-python obs-websocket-py
```

4. **Configure OBS**
- Create a media source in OBS with the name specified in `config.py` (default: `China credit`).
- Enable the Websocket plugin in OBS (usually via the Tools > Websocket Server Settings menu).

5. **Run the script**
```powershell
python hand_to_obs.py
```

## Customization
- Modify `config.py` to adapt the camera, OBS, or video settings add or modify gestures in `gesture_translator.py`.
- Add or modify actions in `gesture_handler.py`.

## Troubleshooting
- If mediapipe doesn't install, check that you're using Python 3.10.9.
- If the camera isn't working, try changing the `CAMERA_ID` in `config.py`.
- If OBS isn't being monitored, check the websocket connection and source name.
