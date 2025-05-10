# gesture_translator.py
import mediapipe as mp
import time
import config # Added import

mp_hands = mp.solutions.hands

# Ajout d'un historique pour le suivi du mouvement de la main (POUR LES SWIPES UNIQUEMENT)
gesture_history = {
    'swipe_x': [],
    'swipe_t': []
}

# État global pour la confirmation et le debounce des gestes STATIQUES et SWIPES
_gesture_candidate = None  # For static gestures
_gesture_candidate_start_time = 0 # For static gestures
_last_returned_gesture = None
_last_returned_gesture_time = 0

# Fonction utilitaire pour savoir si tous les doigts sont levés
def is_hand_open(landmarks):
    fingers = [
        (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP),
        (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP),
        (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_MCP),
        (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_MCP)
    ]
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    # wrist = landmarks.landmark[mp_hands.HandLandmark.WRIST] # Not directly used here
    
    # Critères plus souples pour une main ouverte
    # Le pouce est ouvert si vers l'extérieur ou vers le haut
    # thumb_open = (abs(thumb_tip.x - thumb_ip.x) > 0.05 or thumb_tip.y < thumb_ip.y) # This specific logic for thumb_open is not used for the general hand_open check
    
    # Condition plus souple: la majorité des doigts doit être vers le haut
    fingers_up_count = sum(1 for tip, mcp in fingers if landmarks.landmark[tip].y < landmarks.landmark[mcp].y)
    most_fingers_up = fingers_up_count >= 3  # Au moins 3 doigts levés
    
    return most_fingers_up

# Détection et traduction des gestes de la main
def detect_gesture(landmarks):
    """Détecte des gestes spécifiques basés sur la position des points de la main,
    avec confirmation de durée pour les gestes statiques et debounce global."""
    global _gesture_candidate, _gesture_candidate_start_time
    global _last_returned_gesture, _last_returned_gesture_time
    # gesture_history is implicitly global when modified

    now = time.time()
    raw_detected_gesture = None # The gesture identified in this frame before confirmation/debounce

    # Extraction des landmarks nécessaires
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_mcp = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_mcp = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_tip = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_mcp = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    pinky_mcp_lm = landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP] # Renamed to avoid conflict with function parameter if any
    wrist = landmarks.landmark[mp_hands.HandLandmark.WRIST]

    # --- Détection de Geste Brut ---
    # 1. Vérifier les gestes dynamiques (SWIPE) si la main est ouverte
    if is_hand_open(landmarks):
        palm_center_x = (wrist.x + index_mcp.x + pinky_mcp_lm.x) / 3
        gesture_history['swipe_x'].append(palm_center_x)
        gesture_history['swipe_t'].append(now)
        
        if len(gesture_history['swipe_x']) > 5:
            gesture_history['swipe_x'].pop(0)
            gesture_history['swipe_t'].pop(0)

        if len(gesture_history['swipe_x']) == 5: # Check for swipe if enough history
            dx = gesture_history['swipe_x'][0] - gesture_history['swipe_x'][-1]
            dt = gesture_history['swipe_t'][-1] - gesture_history['swipe_t'][0]
            speed = abs(dx / dt) if dt > 0 else 0
            
            # Conditions de swipe (vitesse et distance)
            if dt < 1.0 and speed > 0.5: 
                current_swipe_gesture = None
                if dx > 0.30:  # Droite vers gauche
                    current_swipe_gesture = "SWIPE_LEFT"
                elif dx < -0.30:  # Gauche vers droite
                    current_swipe_gesture = "SWIPE_RIGHT"
                
                if current_swipe_gesture:
                    gesture_history['swipe_x'].clear() # Clear history after detecting swipe
                    gesture_history['swipe_t'].clear()
                    _gesture_candidate = None # Reset static gesture candidate

                    # Appliquer le debounce pour les swipes
                    if (current_swipe_gesture != _last_returned_gesture or \
                        now - _last_returned_gesture_time >= config.GESTURE_DEBOUNCE_TIME):
                        _last_returned_gesture = current_swipe_gesture
                        _last_returned_gesture_time = now
                        return current_swipe_gesture
                    else:
                        return None # Swipe detected but in debounce period
        
        # Si ce n'est pas un swipe actif, la main ouverte est un geste statique potentiel
        raw_detected_gesture = "OPEN_HAND"
        # Ne pas vider gesture_history ici, car OPEN_HAND peut transitionner vers un swipe

    else: # Main non ouverte, vérifier autres gestes statiques
        gesture_history['swipe_x'].clear() # Si la main se ferme, le swipe est interrompu
        gesture_history['swipe_t'].clear()

        # 2. Vérifier les gestes statiques (THUMB_UP, PEACE, etc.)
        # Critères pour THUMB_UP (Pouce levé)
        thumb_vertical_degree = abs(thumb_tip.y - thumb_ip.y) > 0.04
        thumb_above_fingers = (
            thumb_tip.y < index_tip.y and 
            thumb_tip.y < middle_tip.y and
            thumb_tip.y < ring_tip.y and
            thumb_tip.y < pinky_tip.y
        )
        fingers_horizontal = (
            abs(landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y - 
                landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].y) < 0.03 and
            abs(landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y - 
                landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP].y) < 0.03 and
            abs(landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y - 
                landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP].y) < 0.03 and
            abs(landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y - 
                landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP].y) < 0.03
        )
        if thumb_vertical_degree and thumb_above_fingers and fingers_horizontal:
            raw_detected_gesture = "THUMB_UP"
        else:
            # Critères pour PEACE (Signe de paix)
            index_up = index_tip.y < index_mcp.y - 0.05
            middle_up = middle_tip.y < middle_mcp.y - 0.05
            ring_down = ring_tip.y > ring_mcp.y
            pinky_down = pinky_tip.y > pinky_mcp_lm.y
            
            fingers_v_shape = abs(index_tip.x - middle_tip.x) > 0.05
            
            thumb_behind_line = False # Default
            if abs(index_mcp.x - wrist.x) < 0.001: # Ligne verticale
                line_x = index_mcp.x
                thumb_behind_line = (thumb_ip.x < line_x) if wrist.x < index_mcp.x else (thumb_ip.x > line_x)
            else: # Ligne non verticale
                slope = (index_mcp.y - wrist.y) / (index_mcp.x - wrist.x)
                intercept = wrist.y - slope * wrist.x
                y_on_line = slope * thumb_ip.x + intercept
                if index_mcp.x > wrist.x: # Main gauche probable (vue de face, la gauche anatomique est à droite)
                    thumb_behind_line = thumb_ip.y > y_on_line 
                else: # Main droite probable
                    thumb_behind_line = thumb_ip.y < y_on_line
            
            if (index_up and middle_up and ring_down and pinky_down and 
                fingers_v_shape and thumb_behind_line):
                raw_detected_gesture = "PEACE"
            
            # ... (Ajouter ici d'autres logiques de détection de gestes statiques bruts) ...

    # --- Logique de Confirmation et Debounce pour les gestes STATIQUES ---
    if raw_detected_gesture: # Un geste statique potentiel a été détecté (OPEN_HAND, THUMB_UP, PEACE)
        if raw_detected_gesture == _gesture_candidate:
            # Le même candidat de geste est maintenu
            if (now - _gesture_candidate_start_time >= config.GESTURE_CONFIRMATION_DURATION):
                # Le geste est maintenu assez longtemps pour confirmation
                # Vérifier maintenant le debounce par rapport au dernier geste *retourné*
                if (raw_detected_gesture != _last_returned_gesture or \
                    now - _last_returned_gesture_time >= config.GESTURE_DEBOUNCE_TIME):
                    
                    _last_returned_gesture = raw_detected_gesture
                    _last_returned_gesture_time = now
                    # Le geste est confirmé et retourné.
                    return raw_detected_gesture
                # else: Geste confirmé par durée, mais en debounce car identique au dernier retourné récemment
            # else: Geste maintenu, mais pas encore assez longtemps pour confirmation
        else:
            # Nouveau candidat de geste statique, ou différent du précédent
            _gesture_candidate = raw_detected_gesture
            _gesture_candidate_start_time = now
            # Ne rien retourner ici, on commence juste à suivre ce nouveau candidat
    else:
        # Aucun geste statique brut détecté dans ce frame, réinitialiser le candidat
        _gesture_candidate = None
        _gesture_candidate_start_time = 0 # Réinitialiser le temps de début

    return None # Aucun geste (statique ou swipe) n'est confirmé et prêt à être retourné dans ce frame

    # ... (Le "return None" à la fin de la fonction originale pour les gestes non reconnus est maintenant géré par le flux ci-dessus)
