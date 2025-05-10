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
            gesture_history['swipe_t'].pop(0)        # Si la main a glissé de droite à gauche
        if len(gesture_history['swipe_x']) == 5:
            dx = gesture_history['swipe_x'][0] - gesture_history['swipe_x'][-1]
            dt = gesture_history['swipe_t'][-1] - gesture_history['swipe_t'][0]
            speed = abs(dx / dt) if dt > 0 else 0
            direction = "DROITE->GAUCHE" if dx > 0 else "GAUCHE->DROITE"
            # Détection du swipe dans les deux directions
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
        gesture_history['swipe_t'].clear()    # Critères précis pour le pouce levé :
    # 1. Le pouce doit être vertical (orientation vers le haut)
    # 2. Le pouce doit être au-dessus des autres doigts
    # 3. Les autres doigts doivent être fermés et horizontaux
    
    thumb_mcp = landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    
    # 1. Vérification que le pouce est vertical (différence Y significative)
    thumb_vertical_degree = abs(thumb_tip.y - thumb_ip.y) > 0.04
    
    # 2. Vérification que le pouce est clairement au-dessus des autres doigts
    thumb_above_fingers = (
        thumb_tip.y < index_tip.y and 
        thumb_tip.y < middle_tip.y and
        thumb_tip.y < ring_tip.y and
        thumb_tip.y < pinky_tip.y
    )
    
    # 3. Vérification que les autres doigts sont fermés (horizontaux)
    # Pour des doigts horizontaux, la différence en Y entre les articulations est faible
    # et les bouts des doigts ne sont pas plus bas que leurs articulations MCP
    fingers_horizontal = (
        # L'index n'est pas vertical (différence Y faible entre PIP et DIP)
        abs(landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y - 
            landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP].y) < 0.03 and
        # Le majeur n'est pas vertical
        abs(landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y - 
            landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_DIP].y) < 0.03 and
        # L'annulaire n'est pas vertical
        abs(landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y - 
            landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP].y) < 0.03 and
        # L'auriculaire n'est pas vertical
        abs(landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y - 
            landmarks.landmark[mp_hands.HandLandmark.PINKY_DIP].y) < 0.03
    )
    
    if thumb_vertical_degree and thumb_above_fingers and fingers_horizontal:
        return "THUMB_UP"    # Signe de paix (index et majeur levés en V, autres doigts repliés, pouce derrière la ligne index-poignet)
    
    # Vérifier que l'index et le majeur sont clairement levés
    index_up = index_tip.y < index_mcp.y - 0.05  # Seuil augmenté pour s'assurer que le doigt est bien levé
    middle_up = middle_tip.y < middle_mcp.y - 0.05
    
    # Vérifier que l'annulaire et l'auriculaire sont repliés
    ring_down = ring_tip.y > ring_mcp.y
    pinky_down = pinky_tip.y > pinky_mcp.y
    
    # Vérifier que les doigts forment un "V" (suffisamment écartés)
    fingers_v_shape = abs(index_tip.x - middle_tip.x) > 0.05  # Écart minimal entre index et majeur
    
    # Points importants pour vérifier la position du pouce par rapport à la ligne poignet-index
    wrist = landmarks.landmark[mp_hands.HandLandmark.WRIST]  # Point du poignet
    
    # Calcul de l'équation de la ligne entre le poignet et la base de l'index (index_mcp)
    # Équation de ligne: y = mx + b
    # m = (y2 - y1) / (x2 - x1)
    # b = y1 - m * x1
    
    # Éviter la division par zéro
    if abs(index_mcp.x - wrist.x) < 0.001:
        # Ligne verticale, calcul différent
        line_x = index_mcp.x
        thumb_behind_line = (thumb_ip.x < line_x) if wrist.x < index_mcp.x else (thumb_ip.x > line_x)
    else:
        slope = (index_mcp.y - wrist.y) / (index_mcp.x - wrist.x)
        intercept = wrist.y - slope * wrist.x
        
        # Calcul du côté de la ligne où se trouve le pouce
        # On calcule y théorique sur la ligne pour le même x que le pouce
        y_on_line = slope * thumb_ip.x + intercept
        
        # Si on est à gauche de la main, le pouce est derrière si y_thumb > y_on_line
        # Si on est à droite de la main, le pouce est derrière si y_thumb < y_on_line
        # On peut utiliser index_mcp.x > wrist.x pour savoir si c'est main gauche ou droite
        if index_mcp.x > wrist.x:  # Main gauche probablement
            thumb_behind_line = thumb_ip.y > y_on_line
        else:  # Main droite probablement
            thumb_behind_line = thumb_ip.y < y_on_line
    
    if (index_up and middle_up and ring_down and pinky_down and fingers_v_shape and thumb_behind_line):
        return "PEACE"

    # Ajoute ici d'autres gestes personnalisés
    return None
