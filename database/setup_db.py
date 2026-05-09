"""
database/setup_db.py
Smart Gym CP02 - FIAP
Cria o banco SQLite e insere alunos de exemplo.
Execute este script uma vez antes de rodar a aplicação principal.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "smart_gym.db")


def criar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ------------------------------------------------------------------ #
    # Tabela de alunos
    # ------------------------------------------------------------------ #
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT    NOT NULL,
            uid_rfid    TEXT    NOT NULL UNIQUE,
            exercicio   TEXT    NOT NULL,
            repeticoes  INTEGER NOT NULL DEFAULT 0
        )
    """)

    # ------------------------------------------------------------------ #
    # Tabela de log de acesso
    # ------------------------------------------------------------------ #
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_acesso (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id    INTEGER NOT NULL,
            uid_rfid    TEXT    NOT NULL,
            horario     TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (aluno_id) REFERENCES alunos(id)
        )
    """)

    # ------------------------------------------------------------------ #
    # Dados de exemplo (INSERT OR IGNORE para não duplicar)
    # ------------------------------------------------------------------ #
    alunos_exemplo = [
        ("Carlos Mendes",   "A1:B2:C3:D4", "Supino Reto",       12),
        ("Ana Paula",       "E5:F6:G7:H8", "Agachamento",       15),
        ("Lucas Ferreira",  "I9:J0:K1:L2", "Remada Curvada",    10),
        ("Juliana Costa",   "M3:N4:O5:P6", "Desenvolvimento",   12),
        ("Rafael Souza",    "Q7:R8:S9:T0", "Leg Press",         20),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO alunos (nome, uid_rfid, exercicio, repeticoes) VALUES (?,?,?,?)",
        alunos_exemplo,
    )

    conn.commit()
    conn.close()
    print(f"[OK] Banco criado/atualizado em: {DB_PATH}")
    print("[OK] Alunos de exemplo inseridos.")


if __name__ == "__main__":
    criar_banco()
