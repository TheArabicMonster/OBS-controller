# gesture_translator.py
import mediapipe as mp

mp_hands = mp.solutions.hands

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

    # Critère strict pour le pouce levé :
    # 1. Le pouce est au-dessus de l'index
    # 2. Les autres doigts sont repliés (tip sous le MCP)
    if (
        thumb_tip.y < index_mcp.y and
        index_tip.y > index_mcp.y and
        middle_tip.y > middle_mcp.y and
        ring_tip.y > ring_mcp.y and
        pinky_tip.y > pinky_mcp.y
    ):
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
