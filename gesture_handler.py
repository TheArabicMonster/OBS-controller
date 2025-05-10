# gesture_handler.py
from obswebsocket import requests
import time
from config import VIDEO_SOURCE_NAME

# Gère les actions à effectuer selon le geste détecté
def handle_gesture(gesture, ws, last_action, gesture_cooldown):
    """Exécute une action OBS selon le geste détecté."""
    current_time = time.time()
    if not ws or current_time - last_action < gesture_cooldown:
        return last_action  # Pas d'action

    if gesture == "THUMB_UP":
        try:
            ws.call(requests.RestartMedia(sourceName=VIDEO_SOURCE_NAME))
            print("✓ Action OBS: Lecture vidéo")
        except Exception as e:
            print(f"❌ Erreur OBS: {e}")
        last_action = current_time
    elif gesture == "PEACE":
        try:
            ws.call(requests.SetCurrentScene("Scene 2"))
            print("✓ Action OBS: Changement vers Scene 2")
        except Exception as e:
            print(f"❌ Erreur OBS: {e}")
        last_action = current_time
    elif gesture == "SWIPE_LEFT":
        try:
            ws.call(requests.SetCurrentScene("Scene 2"))
            print("✓ Action OBS: Changement vers Scene 2 via swipe gauche")
        except Exception as e:
            print(f"❌ Erreur OBS: {e}")
        last_action = current_time
    elif gesture == "SWIPE_RIGHT":
        try:
            ws.call(requests.SetCurrentScene("Scene 1"))  # Retour à la scène principale
            print("✓ Action OBS: Changement vers Scene 1 via swipe droit")
        except Exception as e:
            print(f"❌ Erreur OBS: {e}")
        last_action = current_time
    # Ajoute ici d'autres actions pour d'autres gestes
    return last_action
