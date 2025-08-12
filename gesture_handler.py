# gesture_handler.py
import time
from config import VIDEO_SOURCE_NAME, SWIPE_LEFT_SCENE, SWIPE_RIGHT_SCENE

# Gère les actions à effectuer selon le geste détecté
def handle_gesture(gesture, ws, last_action, gesture_cooldown):
    current_time = time.time()
    
    # Vérification du cooldown et de la connexion OBS
    if not ws or (last_action is not None and current_time - last_action < gesture_cooldown):
        return last_action

    action_taken = False
    new_scene_name = None
    action_description = ""

    # Gestion des gestes avec changement de scène
    if gesture == "SWIPE_LEFT":
        new_scene_name = SWIPE_LEFT_SCENE
        action_description = f"Changement vers {SWIPE_LEFT_SCENE} via swipe gauche"
    elif gesture == "SWIPE_RIGHT":
        new_scene_name = SWIPE_RIGHT_SCENE
        action_description = f"Changement vers {SWIPE_RIGHT_SCENE} via swipe droit"
        
    elif gesture == "THUMB_UP":
        try:
            #restart_on_activate rejoue la video si le geste est détecté une seconde fois
            ws.set_input_settings(VIDEO_SOURCE_NAME, {"restart_on_activate": True}, True)

            print("✓ Action OBS: Lecture vidéo")
            action_taken = True
        except Exception as e:
            print(f"❌ Erreur OBS (RestartMedia): {e}")

    elif gesture == "PEACE":
        print("✌️ Geste de paix détecté. Aucune action OBS.")
    elif gesture == "THUMB_DOWN":
        print("👎 Geste de pouce vers le bas détecté. Aucune action OBS.")
    elif gesture == "THUMB_LEFT":
        print("👈 Geste de pouce vers la gauche détecté. Aucune action OBS.")
    elif gesture == "THUMB_RIGHT":
        print("👉 Geste de pouce vers la droite détecté. Aucune action OBS.")
    elif gesture == "FIST":
        print("✊ Geste de poing fermé détecté. Aucune action OBS.")
    elif gesture == "OPEN_HAND":
        print("✋ Geste de main ouverte détecté. Aucune action OBS.")
    elif gesture == "WAVE":
        print("👋 Geste de vague détecté. Aucune action OBS.")
    elif gesture == "OK":
        print("👌 Geste OK détecté. Aucune action OBS.")

    # Exécution des changements de scène
    if new_scene_name:
        try:
            ws.set_current_program_scene(new_scene_name)
            print(f"✓ Action OBS: Changement vers la scène {new_scene_name}")
            action_taken = True
        except Exception as e:
            print(f"❌ Erreur OBS (SetCurrentScene): {e}")
    
    # Retour avec timestamp si action effectuée
    if action_taken:
        timestamp = time.strftime('%H:%M:%S', time.localtime(current_time))

        print(f"✓ Action OBS faite le {timestamp}: {action_description}")
        return current_time    
    return last_action
