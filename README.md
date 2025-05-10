# Reconnaissance de gestes pour contrôle OBS

## Prérequis
- Windows
- OBS Studio avec Websocket activé
- Python 3.10.9 (impératif, mediapipe ne fonctionne pas avec d'autres versions récentes)

## Installation

1. **Installer Python 3.10.9**
   - Télécharger depuis : https://www.python.org/downloads/release/python-3109/
   - Pendant l'installation, cocher "Add Python to PATH".

2. **Créer un environnement virtuel**
   ```powershell
   py -3.10 -m venv venv310
   .\venv310\Scripts\Activate.ps1
   ```

3. **Installer les dépendances**
   ```powershell
   pip install mediapipe opencv-python obs-websocket-py
   ```

4. **Configurer OBS**
   - Créer une source média dans OBS avec le nom indiqué dans `config.py` (par défaut : `China credit`).
   - Activer le plugin Websocket dans OBS (généralement via le menu Outils > Websocket Server Settings).

5. **Lancer le script**
   ```powershell
   python hand_to_obs.py
   ```

## Personnalisation
- Modifiez `config.py` pour adapter les paramètres caméra, OBS, ou vidéo.
- Ajoutez ou modifiez des gestes dans `gesture_translator.py`.
- Ajoutez ou modifiez des actions dans `gesture_handler.py`.

## Dépannage
- Si mediapipe ne s'installe pas, vérifiez que vous utilisez bien Python 3.10.9.
- Si la caméra ne fonctionne pas, essayez de changer `CAMERA_ID` dans `config.py`.
- Si OBS n'est pas contrôlé, vérifiez la connexion Websocket et le nom de la source.
