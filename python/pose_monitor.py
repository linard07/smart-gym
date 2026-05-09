"""
python/pose_monitor.py
Smart Gym CP02 - FIAP
Módulo de monitoramento de postura com MediaPipe.
Roda em thread separada e expõe o frame anotado via fila.
"""

import threading
import queue
import cv2
import mediapipe as mp

# Fila thread-safe para passar frames anotados para a GUI
frame_queue: queue.Queue = queue.Queue(maxsize=2)

_stop_event = threading.Event()
_thread: threading.Thread | None = None


def _capture_loop():
    mp_pose = mp.solutions.pose
    mp_draw = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ) as pose:
        while not _stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                continue

            # Converte BGR -> RGB para o MediaPipe
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            # Desenha esqueleto se detectado
            if results.pose_landmarks:
                mp_draw.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                    mp_draw.DrawingSpec(color=(255, 0, 255), thickness=2),
                )

            # Envia frame para a GUI (descarta o anterior se a fila estiver cheia)
            if not frame_queue.full():
                frame_queue.put(frame)

    cap.release()


def iniciar():
    """Inicia a captura em thread separada."""
    global _thread
    _stop_event.clear()
    _thread = threading.Thread(target=_capture_loop, daemon=True)
    _thread.start()


def parar():
    """Para a captura de câmera."""
    _stop_event.set()
    if _thread:
        _thread.join(timeout=2)
