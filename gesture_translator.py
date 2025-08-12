# gesture_translator.py
import mediapipe as mp
import time
import config

mp_hands = mp.solutions.hands

# Ajout d'un historique pour le suivi du mouvement de la main (POUR LES SWIPES UNIQUEMENT)
gesture_history = {
    'swipe_x': [],
    'swipe_t': []
}

# Variables globales pour les landmarks de la main (évite la redondance)
thumb_tip = None
thumb_mcp = None
thumb_pip = None
thumb_ip = None
index_tip = None
index_mcp = None
index_pip = None
middle_tip = None
middle_mcp = None
middle_pip = None
ring_tip = None
ring_mcp = None
ring_pip = None
pinky_tip = None
pinky_mcp = None
pinky_pip = None
wrist = None

def _extract_landmarks(landmarks):
    """Extrait tous les landmarks nécessaires et les stocke dans les variables globales"""
    global thumb_tip, thumb_mcp, thumb_pip, thumb_ip
    global index_tip, index_mcp, index_pip
    global middle_tip, middle_mcp, middle_pip
    global ring_tip, ring_mcp, ring_pip
    global pinky_tip, pinky_mcp, pinky_pip
    global wrist
    
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_mcp = landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    thumb_pip = landmarks.landmark[mp_hands.HandLandmark.THUMB_PIP]
    thumb_ip = landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    
    index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_mcp = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    index_pip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    
    middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_mcp = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    middle_pip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
    
    ring_tip = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_mcp = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    ring_pip = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
    
    pinky_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    pinky_mcp = landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    pinky_pip = landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
    
    wrist = landmarks.landmark[mp_hands.HandLandmark.WRIST]

# État global pour la confirmation et le debounce des gestes STATIQUES et SWIPES

# Variable qui stocke le geste actuellement en cours de validation
# Contient le nom du geste détecté (ex: "THUMB_UP", "PEACE", "OPEN_HAND") 
# ou None si aucun geste n'est en cours de confirmation
# Sert à vérifier si le même geste est maintenu sur plusieurs frames consécutives
_gesture_candidate = None

# Timestamp (temps en secondes) du moment où le geste candidat a été détecté pour la première fois
# Permet de mesurer combien de temps le geste a été maintenu de manière stable
# Utilisé avec GESTURE_CONFIRMATION_DURATION pour confirmer qu'un geste est volontaire
_gesture_candidate_start_time = 0

# Stocke le dernier geste qui a été effectivement retourné/validé par la fonction
# Permet d'éviter de renvoyer le même geste plusieurs fois de suite (système de debounce)
# Contient le nom du geste (ex: "SWIPE_LEFT", "THUMB_UP") ou None
_last_returned_gesture = None

# Timestamp du moment où le dernier geste validé a été retourné
# Utilisé avec GESTURE_DEBOUNCE_TIME pour empêcher la répétition trop rapide du même geste
# Assure qu'il y a un délai minimum entre deux détections du même geste
_last_returned_gesture_time = 0

# Fonction utilitaire pour détecter une main ouverte comme l'émoji ->🖐️ (tous les doigts étendus et écartés)
def is_hand_open():
    """Utilise les variables globales des landmarks pour détecter une main ouverte"""
    
    # List des doigts écartés
    fingers_spread = []
    # Liste des doigts étendus
    fingers_extended = []
    
    # Vérifier que tous les doigts sont correctement étendus (progression MCP → PIP → TIP vers le haut)
    # Pour chaque doigt: base (MCP) < milieu (PIP) < pointe (TIP) avec marges de sécurité
    fingers_extended.append(
        index_mcp.y < index_pip.y - 0.01 and  # Base < Milieu avec marge 1% de la taille de l'écran
        index_pip.y < index_tip.y - 0.01 and  # Milieu < Pointe avec marge 1%
        index_tip.y < index_mcp.y - 0.03      # Vérification globale: pointe bien au-dessus de la base (3%)
    )
    fingers_extended.append(
        middle_mcp.y < middle_pip.y - 0.01 and
        middle_pip.y < middle_tip.y - 0.01 and
        middle_tip.y < middle_mcp.y - 0.03
    )
    fingers_extended.append(
        ring_mcp.y < ring_pip.y - 0.01 and
        ring_pip.y < ring_tip.y - 0.01 and
        ring_tip.y < ring_mcp.y - 0.03
    )
    fingers_extended.append(
        pinky_mcp.y < pinky_pip.y - 0.01 and
        pinky_pip.y < pinky_tip.y - 0.01 and
        pinky_tip.y < pinky_mcp.y - 0.03
    )
    
    # Pour le pouce -> vérifier qu'il est écarté latéralement (distance horizontale du poignet)
    # abs() = valeur absolue, supprime le signe négatif pour mesurer la distance pure sans prendre en compte l'agencement des doigts
    thumb_spread = abs(thumb_tip.x - wrist.x) > 0.08  # Pouce écarté horizontalement

    # Tous les doigts doivent être correctement étendus
    all_fingers_extended = all(fingers_extended) and thumb_spread

    return all_fingers_extended

# Détection et traduction des gestes de la main
def detect_gesture(landmarks):
    
    global _gesture_candidate, _gesture_candidate_start_time
    global _last_returned_gesture, _last_returned_gesture_time

    # Initialiser les variables globales des landmarks
    _extract_landmarks(landmarks)

    now = time.time()
    raw_detected_gesture = None
    #Geste brut/raw = un geste détecté qui n'a pas encore été confirmé (pas maintenu assez longtemps par exemple)

    # Vérifier les gestes dynamiques (SWIPE) si la main est ouverte
    if is_hand_open():
        palm_center_x = (wrist.x + index_mcp.x + pinky_mcp.x) / 3
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
            abs(index_pip.y - landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].y) < 0.03 and
            abs(middle_pip.y - landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP].y) < 0.03 and
            abs(ring_pip.y - landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP].y) < 0.03 and
            abs(pinky_pip.y - landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP].y) < 0.03
        )
        if thumb_vertical_degree and thumb_above_fingers and fingers_horizontal:
            raw_detected_gesture = "THUMB_UP"
        else:
            # Critères pour PEACE (Signe de paix)
            index_up = index_tip.y < index_mcp.y - 0.05
            middle_up = middle_tip.y < middle_mcp.y - 0.05
            ring_down = ring_tip.y > ring_mcp.y
            pinky_down = pinky_tip.y > pinky_mcp.y
            
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
