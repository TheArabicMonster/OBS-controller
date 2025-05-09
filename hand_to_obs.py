import cv2
import mediapipe as mp
from obswebsocket import obsws, requests
import time

# Paramètres OBS
host = "localhost"
port = 4444
password = ""  # Laissez vide si "Authentication" n'est pas activé, ou mettez le mot de passe exact d'OBS

# Paramètre de caméra
camera_id = 1  # 0=webcam intégrée, 1=webcam externe, 2=autre caméra, etc.

# Paramètres vidéo pour OBS
video_source_name = "China credit"  # Nom de votre source média dans OBS
video_path = r"C:\Users\chats\Videos\Social Credit meme.mp4"  # Chemin vers votre fichier vidéo

# Initialisation MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,               # Détecte jusqu'à 1 main
    min_detection_confidence=0.5,  # Seuil de confiance pour la détection
    min_tracking_confidence=0.5    # Seuil de confiance pour le suivi
)
mp_draw = mp.solutions.drawing_utils

# Connexion à OBS
try:
    print("Tentative de connexion à OBS...")
    ws = obsws(host, port, password)
    ws.connect()
    print("Connexion à OBS réussie!")
except Exception as e:
    print(f"Erreur de connexion à OBS: {e}")
    print("Le programme continuera sans contrôler OBS.")
    ws = None

# Ouverture de la caméra
cap = cv2.VideoCapture(camera_id)
last_action = 0
gesture_cooldown = 2  # Secondes entre deux actions

# Actions OBS
def play_video_in_obs():
    """Lance la lecture d'une vidéo dans OBS en redémarrant la source et s'assurant que l'audio est activé"""
    if not ws:
        print("Pas de connexion à OBS")
        return False
    
    try:
        # Vérifier si la source existe
        sources = ws.call(requests.GetSourcesList()).getSources()
        source_exists = any(s['name'] == video_source_name for s in sources)
        
        if not source_exists:
            print(f"Source '{video_source_name}' introuvable dans OBS")
            return False
        
        # S'assurer que l'audio de la source est activé et à un volume correct
        try:
            print("Configuration de l'audio...")
            # Récupérer les paramètres actuels
            source_settings = ws.call(requests.GetSourceSettings(sourceName=video_source_name)).getSourceSettings()
            
            # Vérifier si des paramètres audio existent et les modifier
            audio_settings = {
                'muted': False,  # S'assurer que la source n'est pas en sourdine
                'volume': 1.0,   # Volume à 100%
            }
            
            # Mettre à jour les paramètres si 'muted' existe
            if 'muted' in source_settings:
                source_settings['muted'] = False
            
            # Mettre à jour le volume si possible
            if 'volume' in source_settings:
                source_settings['volume'] = 1.0
            
            # Appliquer les paramètres mis à jour
            ws.call(requests.SetSourceSettings(
                sourceName=video_source_name,
                sourceSettings=source_settings
            ))
            
            # Essayer aussi de configurer les paramètres audio spécifiques si disponibles
            try:
                ws.call(requests.SetMute(source=video_source_name, mute=False))
                ws.call(requests.SetVolume(source=video_source_name, volume=1.0))
                print("Paramètres audio configurés: volume à 100% et source non muette")
            except Exception as e:
                print(f"Note: Configuration audio avancée non disponible: {e}")
                
        except Exception as e:
            print(f"Avertissement lors de la configuration audio: {e}")
        
        # Stratégie 1: Essayer de redémarrer le média
        try:
            print("Tentative de redémarrage du média...")
            ws.call(requests.RestartMedia(sourceName=video_source_name))
            print(f"✓ Média '{video_source_name}' redémarré")
            return True
        except Exception as e:
            print(f"Échec du redémarrage: {e}")
        
        # Stratégie 2: Désactiver puis réactiver la source pour forcer le redémarrage
        try:
            print("Tentative de réinitialisation par visibilité...")
            # Récupérer les scènes
            scenes = ws.call(requests.GetSceneList()).getScenes()
            
            # Pour chaque scène, vérifier si notre source est présente
            for scene in scenes:
                scene_name = scene['name']
                
                # Obtenir les items de la scène
                scene_items = ws.call(requests.GetSceneItemList(sceneName=scene_name)).getSceneItems()
                
                # Trouver notre source dans cette scène
                for item in scene_items:
                    if item.get('sourceName') == video_source_name:
                        print(f"Source trouvée dans la scène: {scene_name}")
                        
                        # Récupérer l'ID de l'élément
                        item_id = item.get('id')
                        
                        # Désactiver la source
                        ws.call(requests.SetSceneItemProperties(
                            scene=scene_name,
                            item=item_id,
                            visible=False
                        ))
                        print("Source désactivée")
                        
                        # Attendre un court instant
                        time.sleep(0.5)
                        
                        # Réactiver la source pour déclencher le redémarrage
                        ws.call(requests.SetSceneItemProperties(
                            scene=scene_name,
                            item=item_id,
                            visible=True
                        ))
                        print("Source réactivée - la vidéo devrait démarrer")
                        return True
            
            print("Source non trouvée dans les scènes actives")
            
        except Exception as e:
            print(f"Échec de la réinitialisation par visibilité: {e}")
        
        # Stratégie 3: Essayer de jouer en utilisant la méthode SetSourceSettings
        try:
            print("Tentative de lecture via paramètres...")
            settings = {
                'playing': True,
                'restart': True,  # Essayer de forcer le redémarrage
                'loop': False
            }
            ws.call(requests.SetSourceSettings(
                sourceName=video_source_name,
                sourceSettings=settings
            ))
            print("Paramètres de lecture appliqués")
        except Exception as e:
            print(f"Échec de la lecture via paramètres: {e}")
        
        return True
        
    except Exception as e:
        print(f"Erreur lors de la lecture de la vidéo: {e}")
        return False

def detect_gesture(landmarks):
    """Détecte des gestes spécifiques basés sur la position des points de la main"""
    # Exemple: pouce levé
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    
    # Pouce levé - Si le pouce est au-dessus de l'index
    if thumb_tip.y < index_tip.y:
        return "THUMB_UP"
    
    # Vous pouvez ajouter d'autres gestes ici
    # Par exemple, index et majeur levés (signe de paix)
    middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    if (index_tip.y < landmarks.landmark[mp_hands.HandLandmark.WRIST].y and 
        middle_tip.y < landmarks.landmark[mp_hands.HandLandmark.WRIST].y and
        thumb_tip.y > index_tip.y):
        return "PEACE"
    
    return None

try:
    while cap.isOpened():
        # Lecture de l'image de la caméra
        success, image = cap.read()
        if not success:
            print("Échec de la lecture depuis la caméra.")
            break

        # Flip horizontal pour une expérience de miroir plus naturelle
        image = cv2.flip(image, 1)
        
        # Conversion pour MediaPipe (BGR à RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        
        # Traitement de l'image avec MediaPipe
        results = hands.process(image_rgb)
        
        # Préparation pour dessiner
        image_rgb.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # Affichage du geste détecté
        gesture_text = "Aucun geste"
        
        # Analyse des résultats de détection de la main
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Dessiner les points et connexions de la main
                mp_draw.draw_landmarks(
                    image, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS
                )
                
                # Détecter le geste
                gesture = detect_gesture(hand_landmarks)
                if gesture:
                    gesture_text = f"Geste: {gesture}"
                    
                    # Actions OBS avec délai de refroidissement
                    current_time = time.time()
                    if ws and current_time - last_action > gesture_cooldown:
                        if gesture == "THUMB_UP":
                            try:
                                # Au lieu de changer de scène, on lance la vidéo
                                play_video_in_obs()
                                print("Action OBS: Lecture vidéo")
                            except Exception as e:
                                print(f"Erreur OBS: {e}")
                        elif gesture == "PEACE":
                            try:
                                ws.call(requests.SetCurrentScene("Scene 2"))
                                print("Action OBS: Changement vers Scene 2")
                            except Exception as e:
                                print(f"Erreur OBS: {e}")
                        last_action = current_time
        
        # Affichage du texte sur l'image
        cv2.putText(image, gesture_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Affichage de l'image
        cv2.imshow("Reconnaissance de gestes", image)
        
        # Quitter si 'q' est pressé
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"Erreur : {e}")

finally:
    # Nettoyage
    if cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    if ws:
        ws.disconnect()