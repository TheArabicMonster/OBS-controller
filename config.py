# config.py
# Paramètres importants du projet

# Paramètres OBS
HOST = "localhost"
PORT = 4455
PASSWORD = ""  # Laissez vide si "Authentication" n'est pas activé, ou mettez le mot de passe exact d'OBS

# Paramètre de caméra
CAMERA_ID = 1  # 0=webcam intégrée, 1=webcam externe, 2=autre caméra, etc.

# Paramètres vidéo pour OBS
VIDEO_SOURCE_NAME = "China credit"  # Nom de votre source média dans OBS
VIDEO_PATH = r"C:\Users\chats\Videos\Social Credit meme.mp4"  # Chemin vers votre fichier vidéo

# Paramètres de détection de gestes
GESTURE_CONFIRMATION_DURATION = 0.1  # Durée en secondes pour valider un geste statique
GESTURE_DEBOUNCE_TIME = 0.3  # Temps en secondes avant de pouvoir redéclencher le même geste

# Paramètres des scènes pour les gestes de swipe
SWIPE_LEFT_SCENE = "Scène 2"  # Scène à activer lors d'un swipe vers la gauche
SWIPE_RIGHT_SCENE = "Scène 1" # Scène à activer lors d'un swipe vers la droite
