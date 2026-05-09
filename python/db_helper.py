"""
python/db_helper.py
Smart Gym CP02 - FIAP
Funções utilitárias para acesso ao banco SQLite.
"""

import sqlite3
import os

# Caminho para o banco (relativo à raiz do projeto)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "smart_gym.db")


def _connect():
    return sqlite3.connect(DB_PATH)


def buscar_aluno_por_uid(uid: str) -> dict | None:
    """Retorna dict com dados do aluno ou None se não encontrado."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nome, exercicio, repeticoes FROM alunos WHERE uid_rfid = ?",
        (uid.upper(),),
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "nome": row[1], "exercicio": row[2], "repeticoes": row[3]}
    return None


def registrar_log(aluno_id: int, uid: str):
    """Registra horário de acesso do aluno no banco."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO log_acesso (aluno_id, uid_rfid) VALUES (?, ?)",
        (aluno_id, uid.upper()),
    )
    conn.commit()
    conn.close()


def incrementar_repeticoes(aluno_id: int):
    """Incrementa o contador de repetições do aluno."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE alunos SET repeticoes = repeticoes + 1 WHERE id = ?",
        (aluno_id,),
    )
    conn.commit()
    conn.close()


def obter_repeticoes(aluno_id: int) -> int:
    """Retorna o total de repetições registradas para o aluno."""
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("SELECT repeticoes FROM alunos WHERE id = ?", (aluno_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0
