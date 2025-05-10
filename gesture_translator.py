# gesture_translator.py
import mediapipe as mp
import time

mp_hands = mp.solutions.hands

# Ajout d'un historique pour le suivi du mouvement de la main
gesture_history = {
    'swipe_x': [],  # Liste des positions x du poignet
    'swipe_t': []  # Liste des timestamps associés
}

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
    wrist = landmarks.landmark[mp_hands.HandLandmark.WRIST]
    
    # Critères plus souples pour une main ouverte
    # Le pouce est ouvert si vers l'extérieur ou vers le haut
    thumb_open = (abs(thumb_tip.x - thumb_ip.x) > 0.05 or thumb_tip.y < thumb_ip.y)
    
    # Condition plus souple: la majorité des doigts doit être vers le haut
    fingers_up_count = sum(1 for tip, mcp in fingers if landmarks.landmark[tip].y < landmarks.landmark[mcp].y)
    most_fingers_up = fingers_up_count >= 3  # Au moins 3 doigts levés
    
    return most_fingers_up

# Détection et traduction des gestes de la main
def detect_gesture(landmarks):
    """Détecte des gestes spécifiques basés sur la position des points de la main."""
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    index_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_mcp = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_tip = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_mcp = landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_tip = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_mcp = landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_tip = landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    pinky_mcp = landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    wrist = landmarks.landmark[mp_hands.HandLandmark.WRIST]

    # Détection main ouverte + suivi du poignet pour swipe
    if is_hand_open(landmarks):
        now = time.time()
        # Utiliser le centre de la paume pour un suivi plus précis
        palm_center_x = (wrist.x + index_mcp.x + pinky_mcp.x) / 3
        
        # Ajouter la position actuelle à l'historique
        gesture_history['swipe_x'].append(palm_center_x)
        gesture_history['swipe_t'].append(now)
        
        # On garde les 5 dernières positions
        if len(gesture_history['swipe_x']) > 5:
            gesture_history['swipe_x'].pop(0)
            gesture_history['swipe_t'].pop(0)
              # Si la main a glissé de droite à gauche
        if len(gesture_history['swipe_x']) == 5:
            dx = gesture_history['swipe_x'][0] - gesture_history['swipe_x'][-1]
            dt = gesture_history['swipe_t'][-1] - gesture_history['swipe_t'][0]
            speed = abs(dx / dt) if dt > 0 else 0
            direction = "DROITE->GAUCHE" if dx > 0 else "GAUCHE->DROITE"            # Détection du swipe dans les deux directions
            if dt < 1.0 and speed > 0.5:  # Timing et vitesse minimale requis
                if dx > 0.30:  # Droite vers gauche (dx positif)
                    print(f"Swipe {direction} détecté")
                    gesture_history['swipe_x'].clear()
                    gesture_history['swipe_t'].clear()
                    return "SWIPE_LEFT"
                elif dx < -0.30:  # Gauche vers droite (dx négatif)
                    print(f"Swipe {direction} détecté")
                    gesture_history['swipe_x'].clear()
                    gesture_history['swipe_t'].clear()
                    return "SWIPE_RIGHT"
        return "OPEN_HAND"
    else:
        gesture_history['swipe_x'].clear()
        gesture_history['swipe_t'].clear()

    # Critères plus stricts pour le pouce levé :
    # 1. Le pouce doit être clairement au-dessus des autres doigts
    # 2. Les autres doigts doivent être clairement repliés (bien plus bas)
    # 3. Le pouce doit être orienté vers le haut (y vraiment plus petit)
    thumb_mcp = landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
      # Calcul de l'orientation du pouce - plus souple
    thumb_vertical = (thumb_tip.y < thumb_ip.y)  # Pouce orienté vers le haut
    
    # Vérification que le pouce est au-dessus des autres doigts - seuil plus bas
    thumb_clearly_up = thumb_tip.y < index_mcp.y - 0.05  # Réduit à 5% au lieu de 10%
    
    # Vérification que les autres doigts sont repliés - critère plus souple
    fingers_clearly_down = (
        index_tip.y > index_mcp.y and
        middle_tip.y > middle_mcp.y and
        ring_tip.y > ring_mcp.y and
        pinky_tip.y > pinky_mcp.y
    )
    
    if thumb_vertical and thumb_clearly_up and fingers_clearly_down:
        return "THUMB_UP"

    # Signe de paix (index et majeur levés, autres doigts repliés)
    if (
        index_tip.y < index_mcp.y and
        middle_tip.y < middle_mcp.y and
        ring_tip.y > ring_mcp.y and
        pinky_tip.y > pinky_mcp.y and
        thumb_tip.y > thumb_ip.y
    ):
        return "PEACE"

    # Ajoute ici d'autres gestes personnalisés
    return None
