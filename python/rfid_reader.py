"""
python/rfid_reader.py
Smart Gym CP02 - FIAP
Lê UIDs enviados pelo Arduino/ESP32 via porta serial.
Roda em thread separada e coloca os UIDs em uma fila.
"""

import threading
import queue
import serial
import serial.tools.list_ports

# Fila thread-safe para UIDs recebidos
uid_queue: queue.Queue = queue.Queue()

_stop_event = threading.Event()
_thread: threading.Thread | None = None

# ------------------------------------------------------------------ #
# Configurações da porta serial
# ------------------------------------------------------------------ #
BAUD_RATE = 9600
TIMEOUT   = 1  # segundos


def detectar_porta() -> str | None:
    """Tenta detectar automaticamente a porta do Arduino/ESP32."""
    portas = serial.tools.list_ports.comports()
    for p in portas:
        desc = (p.description or "").lower()
        if any(k in desc for k in ("arduino", "esp32", "ch340", "cp210", "ftdi", "usb serial")):
            return p.device
    # Se não encontrar automaticamente, retorna None
    return None


def _read_loop(porta: str):
    try:
        ser = serial.Serial(porta, BAUD_RATE, timeout=TIMEOUT)
        print(f"[RFID] Conectado em {porta}")
        while not _stop_event.is_set():
            linha = ser.readline().decode("utf-8", errors="ignore").strip()
            if linha.startswith("UID:"):
                uid = linha[4:].strip()
                uid_queue.put(uid)
                print(f"[RFID] Cartão lido: {uid}")
        ser.close()
    except serial.SerialException as e:
        print(f"[RFID] Erro na porta serial: {e}")


def iniciar(porta: str | None = None):
    """Inicia a leitura serial em thread separada."""
    global _thread
    if porta is None:
        porta = detectar_porta()
    if porta is None:
        print("[RFID] Porta serial não encontrada. Modo simulação ativo.")
        return  # Sem hardware conectado, a GUI ainda funciona
    _stop_event.clear()
    _thread = threading.Thread(target=_read_loop, args=(porta,), daemon=True)
    _thread.start()


def parar():
    _stop_event.set()
    if _thread:
        _thread.join(timeout=2)


# ------------------------------------------------------------------ #
# Simulação de leitura (para testes sem hardware)
# ------------------------------------------------------------------ #
def simular_uid(uid: str):
    """Injeta um UID simulado na fila (uso em testes/demo)."""
    uid_queue.put(uid)
