🌍 **Langue / Language** :
[Français](./README.md) | [English](./README.en.md)

# Reconnaissance de gestes pour contrôle OBS

## Prérequis
- Windows 10/11 (pas testé sur linux ni macOS)
- OBS Studio avec WebSocket activé (Outils -> Paramètres du serveur WebSocket -> activer "Activer le serveur WebSocket", décocher "Utiliser l'authentification" -> cliquer sur "OK")
- Python 3.10.9 (impératif, MediaPipe ne fonctionne pas avec d'autres versions récentes)
- Une webcam (btw)

## Dépendances Python
- `opencv-python` : Traitement vidéo et accès caméra
- `mediapipe` : Détection et reconnaissance des gestes de la main
- `obsws-python` : Communication WebSocket avec OBS Studio

## Installation

### Méthode automatique

pas d'installation automatique pour le moment

### Méthode manuelle

1. **Installer Python 3.10.9**
   - Télécharger depuis : https://www.python.org/downloads/release/python-3109/
   - Pendant l'installation, cocher "Add Python to PATH".

2. **Créer un environnement virtuel**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Installer les dépendances**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configurer OBS**
   - Créer une source média dans OBS avec le nom indiqué dans `config.py` (par défaut : `China credit`).
   - Créer les scènes mentionnées dans `config.py` (par défaut : `Scène 1` et `Scène 2`).
   - Activer le plugin Websocket dans OBS (comme mentionné dans le chapitre prérequis).

5. **Lancer le script**
   ```powershell
   python hand_to_obs.py
   ```

### Vérification de l'installation

Pour vérifier que tout est correctement installé :
```powershell
python test_installation.py
```

## Structure du projet

```
OBS-controller/
├── hand_to_obs.py           # Script principal
├── config.py                # Configuration du projet
├── gesture_translator.py    # Détection et traduction des gestes
├── gesture_handler.py       # Actions à effectuer pour chaque geste
├── requirements.txt         # Liste des dépendances Python
├── setup.ps1               # Script d'installation PowerShell
├── setup.bat               # Script d'installation Batch
├── README.md               # Documentation française
└── README.en.md            # Documentation anglaise
```

## Gestes disponibles
- **Main ouverte** : Pas d'action (geste neutre)
- **Pouce levé** : Démarre la lecture de la vidéo
- **Signe de paix** : Pas d'action (geste neutre)
- **Swipe gauche** : Change vers la scène configurée pour swipe gauche
- **Swipe droite** : Change vers la scène configurée pour swipe droite

## Personnalisation

### Configuration générale (`config.py`)
- `CAMERA_ID` : ID de la caméra (0 pour webcam intégrée, 1 pour externe)
- `VIDEO_SOURCE_NAME` : Nom de la source média dans OBS
- `SWIPE_LEFT_SCENE` / `SWIPE_RIGHT_SCENE` : Noms des scènes pour les swipes

### Paramètres de détection des gestes (`config.py`)
- `GESTURE_CONFIRMATION_DURATION` : Durée (en secondes) pendant laquelle un geste statique doit être maintenu pour être validé (défaut : 0.1s)
- `GESTURE_DEBOUNCE_TIME` : Temps d'attente (en secondes) avant de pouvoir redéclencher le même geste (défaut : 0.3s)

### Ajout de nouveaux gestes
- Modifiez `gesture_translator.py` pour ajouter la logique de détection
- Modifiez `gesture_handler.py` pour définir les actions à effectuer

## Dépannage

### Installation
- Si le script d'installation échoue, vérifiez que Python 3.10.9 est bien installé et dans le PATH
- Si PowerShell bloque l'exécution : `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Caméra
- Si la caméra ne fonctionne pas, essayez de changer `CAMERA_ID` dans `config.py`
- Fermez toutes les applications utilisant la caméra (Teams, Zoom, navigateurs)
- Vérifiez les permissions caméra Windows : `ms-settings:privacy-webcam`
- Redémarrez l'ordinateur si nécessaire

### OBS
- Vérifiez que OBS est lancé avant le script
- Activez le WebSocket : Outils > Paramètres du serveur WebSocket
- Vérifiez le port (défaut: 4455) et le mot de passe (si activé dans les paramètres du serveur WebSocket) dans `config.py`
- Créez les scènes et sources mentionnées dans `config.py`

### Gestes
- Ajustez `GESTURE_CONFIRMATION_DURATION` et `GESTURE_DEBOUNCE_TIME` dans `config.py`
- Assurez-vous d'avoir un bon éclairage pour la détection
- Positionnez-vous à environ 50-100cm de la caméra
