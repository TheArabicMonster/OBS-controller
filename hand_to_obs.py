import cv2
import mediapipe as mp
import obsws_python as obs
from config import HOST, PORT, PASSWORD, CAMERA_ID, VIDEO_SOURCE_NAME
from gesture_translator import detect_gesture
from gesture_handler import handle_gesture

# Connexion à OBS
try:
    print("Tentative de connexion à OBS...")
    ws = obs.ReqClient(host=HOST, port=PORT, password=PASSWORD)
    print("Connexion à OBS réussie!")
except Exception as e:
    print(f"Erreur de connexion à OBS: {e}")
    print("Le programme continuera sans contrôler OBS.")
    ws = None

# Ouverture de la caméra
cap = cv2.VideoCapture(CAMERA_ID)
last_action = 0
gesture_cooldown = 2  # Secondes entre deux actions

# Initialisation MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,               # Détecte jusqu'à 1 main
    min_detection_confidence=0.5,  # Seuil de confiance pour la détection
    min_tracking_confidence=0.5    # Seuil de confiance pour le suivi
)
mp_draw = mp.solutions.drawing_utils

try:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Échec de la lecture depuis la caméra.")
            break

        # Flip horizontal de l'image
        image = cv2.flip(image, 1)
        
        # Conversion pour MediaPipe (BGR à RGB)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_rgb.flags.writeable = False
        
        results = hands.process(image_rgb)

        # Convertie l'image de RGB à BGR
        image_rgb.flags.writeable = True
        image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
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
                    
                    # Exécute action et met à jour timestamp anti-spam
                    last_action = handle_gesture(gesture, ws, last_action, gesture_cooldown)
        
        # Affichage du geste sur l'image
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