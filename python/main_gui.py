"""
python/main_gui.py
Smart Gym CP02 - FIAP
Interface gráfica principal com Tkinter.
"""

import tkinter as tk
import threading
import queue

import rfid_reader
import db_helper

# Importações opcionais (não travam a GUI se não estiverem instaladas)
try:
    import cv2
    import mediapipe as mp
    from PIL import Image, ImageTk
    CAMERA_DISPONIVEL = True
except ImportError:
    CAMERA_DISPONIVEL = False

# ------------------------------------------------------------------ #
# Constantes visuais
# ------------------------------------------------------------------ #
COR_BG        = "#1a1a2e"
COR_CARD      = "#16213e"
COR_ACENTO    = "#e94560"
COR_TEXTO     = "#eaeaea"
COR_TEXTO_SEC = "#a0a0b0"
COR_VERDE     = "#4caf50"
COR_AMARELO   = "#ffc107"

LARGURA_CAM = 520
ALTURA_CAM  = 380

# ------------------------------------------------------------------ #
# Módulo de câmera inline
# ------------------------------------------------------------------ #
_frame_queue: queue.Queue = queue.Queue(maxsize=2)
_stop_camera  = threading.Event()
_cam_thread   = None


def _camera_loop():
    mp_pose = mp.solutions.pose
    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=0,
    ) as pose:
        while not _stop_camera.is_set():
            ret, frame = cap.read()
            if not ret:
                continue
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)
            if results.pose_landmarks:
                mp_draw.draw_landmarks(
                    frame, results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                    mp_draw.DrawingSpec(color=(255, 0, 255), thickness=2),
                )
            if not _frame_queue.full():
                _frame_queue.put(frame)
    cap.release()


def iniciar_camera():
    global _cam_thread
    _stop_camera.clear()
    _cam_thread = threading.Thread(target=_camera_loop, daemon=True)
    _cam_thread.start()


def parar_camera():
    _stop_camera.set()
    if _cam_thread:
        _cam_thread.join(timeout=2)


# ------------------------------------------------------------------ #
# Aplicação principal
# ------------------------------------------------------------------ #
class SmartGymApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Gym Station — FIAP CP02")
        self.configure(bg=COR_BG)
        self.geometry("1100x680")
        self.resizable(False, False)

        self.aluno_atual  = None
        self.rep_sessao   = 0
        self.camera_ativa = False

        self._build_ui()

        # Inicia leitura RFID em background
        rfid_reader.iniciar()
        self._poll_rfid()

    # ---------------------------------------------------------------- #
    # UI
    # ---------------------------------------------------------------- #
    def _build_ui(self):
        # Barra superior
        tk.Frame(self, bg=COR_ACENTO, height=6).pack(fill="x")

        # Cabeçalho
        topo = tk.Frame(self, bg=COR_BG, pady=10)
        topo.pack(fill="x", padx=30)
        tk.Label(topo, text="⚡  SMART GYM STATION",
                 bg=COR_BG, fg=COR_ACENTO,
                 font=("Segoe UI", 22, "bold")).pack(side="left")
        self.lbl_status_topo = tk.Label(
            topo, text="●  AGUARDANDO LOGIN",
            bg=COR_BG, fg=COR_AMARELO,
            font=("Segoe UI", 13, "bold"))
        self.lbl_status_topo.pack(side="right")

        tk.Frame(self, bg=COR_CARD, height=2).pack(fill="x")

        # Corpo
        corpo = tk.Frame(self, bg=COR_BG)
        corpo.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Câmera ---
        cam_frame = tk.Frame(corpo, bg=COR_CARD,
                             width=LARGURA_CAM + 20,
                             height=ALTURA_CAM + 20)
        cam_frame.pack(side="left", padx=(0, 20))
        cam_frame.pack_propagate(False)

        self.lbl_camera = tk.Label(
            cam_frame,
            text="📷\n\nCâmera inativa\nFaça login com seu\ncartão RFID",
            bg=COR_CARD, fg=COR_TEXTO_SEC,
            font=("Segoe UI", 13), justify="center")
        self.lbl_camera.pack(expand=True)

        # --- Painel direito ---
        painel = tk.Frame(corpo, bg=COR_BG)
        painel.pack(side="left", fill="both", expand=True)

        # Card boas-vindas
        c1 = tk.Frame(painel, bg=COR_CARD, pady=18, padx=20)
        c1.pack(fill="x", pady=(0, 12))
        tk.Label(c1, text="BEM-VINDO(A)", bg=COR_CARD,
                 fg=COR_TEXTO_SEC, font=("Segoe UI", 10)).pack(anchor="w")
        self.lbl_nome = tk.Label(c1, text="—", bg=COR_CARD,
                                 fg=COR_TEXTO, font=("Segoe UI", 24, "bold"))
        self.lbl_nome.pack(anchor="w")
        self.lbl_exercicio = tk.Label(c1, text="", bg=COR_CARD,
                                      fg=COR_ACENTO, font=("Segoe UI", 13))
        self.lbl_exercicio.pack(anchor="w", pady=(4, 0))

        # Card repetições
        c2 = tk.Frame(painel, bg=COR_CARD, pady=18, padx=20)
        c2.pack(fill="x", pady=(0, 12))
        tk.Label(c2, text="REPETIÇÕES (SESSÃO)", bg=COR_CARD,
                 fg=COR_TEXTO_SEC, font=("Segoe UI", 10)).pack(anchor="w")
        self.lbl_reps = tk.Label(c2, text="—", bg=COR_CARD,
                                 fg=COR_VERDE, font=("Segoe UI", 48, "bold"))
        self.lbl_reps.pack(anchor="w")
        self.btn_rep = tk.Button(
            c2, text="+ Registrar Repetição",
            bg="#2a5c2a", fg=COR_TEXTO_SEC,
            font=("Segoe UI", 12, "bold"),
            relief="flat", padx=15, pady=8,
            cursor="arrow", state="disabled",
            command=self._registrar_rep)
        self.btn_rep.pack(anchor="w", pady=(10, 0))

        # Card status
        c3 = tk.Frame(painel, bg=COR_CARD, pady=18, padx=20)
        c3.pack(fill="x", pady=(0, 12))
        tk.Label(c3, text="STATUS DA ESTAÇÃO", bg=COR_CARD,
                 fg=COR_TEXTO_SEC, font=("Segoe UI", 10)).pack(anchor="w")
        self.lbl_status = tk.Label(
            c3, text="🔴  Aguardando Login",
            bg=COR_CARD, fg=COR_AMARELO,
            font=("Segoe UI", 14, "bold"))
        self.lbl_status.pack(anchor="w", pady=(6, 0))

        # Botões
        btn_row = tk.Frame(painel, bg=COR_BG)
        btn_row.pack(fill="x", pady=(0, 4))

        self.btn_demo = tk.Button(
            btn_row, text="[DEMO] Simular Cartão",
            bg=COR_CARD, fg=COR_TEXTO_SEC,
            font=("Segoe UI", 10), relief="flat",
            padx=12, pady=6, cursor="hand2",
            command=self._simular)
        self.btn_demo.pack(side="left")

        self.btn_logout = tk.Button(
            btn_row, text="Encerrar Sessão",
            bg="#5c1a1a", fg=COR_TEXTO_SEC,
            font=("Segoe UI", 11, "bold"),
            relief="flat", padx=15, pady=6,
            cursor="arrow", state="disabled",
            command=self._logout)
        self.btn_logout.pack(side="right")

        # Rodapé
        tk.Frame(self, bg=COR_CARD, height=2).pack(fill="x")
        tk.Label(self,
                 text="Smart Gym Station  •  Physical Computing CP02  •  FIAP 2026",
                 bg=COR_BG, fg=COR_TEXTO_SEC,
                 font=("Segoe UI", 10)).pack(pady=7)

    # ---------------------------------------------------------------- #
    # RFID polling
    # ---------------------------------------------------------------- #
    def _poll_rfid(self):
        try:
            while not rfid_reader.uid_queue.empty():
                uid = rfid_reader.uid_queue.get_nowait()
                self._processar_uid(uid)
        except Exception:
            pass
        self.after(200, self._poll_rfid)

    def _processar_uid(self, uid: str):
        aluno = db_helper.buscar_aluno_por_uid(uid)
        if aluno:
            db_helper.registrar_log(aluno["id"], uid)
            self._login(aluno)
        else:
            self.lbl_status.config(
                text=f"⚠  UID não cadastrado: {uid}", fg=COR_ACENTO)
            self.after(3000, self._reset_status_se_deslogado)

    def _reset_status_se_deslogado(self):
        if not self.aluno_atual:
            self.lbl_status.config(text="🔴  Aguardando Login", fg=COR_AMARELO)

    # ---------------------------------------------------------------- #
    # Login / Logout
    # ---------------------------------------------------------------- #
    def _login(self, aluno: dict):
        self.aluno_atual = aluno
        self.rep_sessao  = 0

        self.lbl_nome.config(text=aluno["nome"])
        self.lbl_exercicio.config(text=f"🏋  {aluno['exercicio']}")
        self.lbl_reps.config(text="0")
        self.lbl_status.config(text="🟢  Treino Ativo", fg=COR_VERDE)
        self.lbl_status_topo.config(text="●  TREINO ATIVO", fg=COR_VERDE)

        self.btn_rep.config(state="normal", bg=COR_VERDE,
                            fg="white", cursor="hand2")
        self.btn_logout.config(state="normal", bg=COR_ACENTO,
                               fg="white", cursor="hand2")

        if CAMERA_DISPONIVEL and not self.camera_ativa:
            self.camera_ativa = True
            iniciar_camera()
            self._atualizar_camera()
        elif not CAMERA_DISPONIVEL:
            self.lbl_camera.config(
                text="⚠️  Instale opencv-python\nmediapipe e Pillow\npara ativar a câmera",
                fg=COR_AMARELO)

    def _logout(self):
        self.aluno_atual = None
        self.rep_sessao  = 0

        self.lbl_nome.config(text="—")
        self.lbl_exercicio.config(text="")
        self.lbl_reps.config(text="—")
        self.lbl_status.config(text="🔴  Aguardando Login", fg=COR_AMARELO)
        self.lbl_status_topo.config(text="●  AGUARDANDO LOGIN", fg=COR_AMARELO)

        self.btn_rep.config(state="disabled", bg="#2a5c2a",
                            fg=COR_TEXTO_SEC, cursor="arrow")
        self.btn_logout.config(state="disabled", bg="#5c1a1a",
                               fg=COR_TEXTO_SEC, cursor="arrow")

        if self.camera_ativa:
            self.camera_ativa = False
            parar_camera()
            self.lbl_camera.config(
                image="",
                text="📷\n\nCâmera inativa\nFaça login com seu\ncartão RFID",
                fg=COR_TEXTO_SEC)
            self.lbl_camera.image = None

    # ---------------------------------------------------------------- #
    # Repetições
    # ---------------------------------------------------------------- #
    def _registrar_rep(self):
        if not self.aluno_atual:
            return
        self.rep_sessao += 1
        db_helper.incrementar_repeticoes(self.aluno_atual["id"])
        self.lbl_reps.config(text=str(self.rep_sessao))

    # ---------------------------------------------------------------- #
    # Câmera
    # ---------------------------------------------------------------- #
    def _atualizar_camera(self):
        if not self.camera_ativa:
            return
        try:
            if not _frame_queue.empty():
                frame = _frame_queue.get_nowait()
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb).resize(
                    (LARGURA_CAM, ALTURA_CAM), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.lbl_camera.config(image=photo, text="")
                self.lbl_camera.image = photo
        except Exception:
            pass
        self.after(33, self._atualizar_camera)

    # ---------------------------------------------------------------- #
    # Demo
    # ---------------------------------------------------------------- #
    _demo_uids = [
        "A1:B2:C3:D4",
        "E5:F6:G7:H8",
        "I9:J0:K1:L2",
        "M3:N4:O5:P6",
        "Q7:R8:S9:T0",
        "XX:00:00:XX",
    ]
    _demo_idx = 0

    def _simular(self):
        if self.aluno_atual:
            self._logout()
            return
        uid = self._demo_uids[self._demo_idx % len(self._demo_uids)]
        self._demo_idx += 1
        rfid_reader.simular_uid(uid)


# ------------------------------------------------------------------ #
if __name__ == "__main__":
    app = SmartGymApp()
    app.mainloop()
