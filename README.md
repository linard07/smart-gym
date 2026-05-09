# 🏋️ Smart Gym Station — CP02

> **Physical Computing (IoT & IoB) — FIAP 2026**  
> Checkpoint 02: Persistência de Dados e Interface Homem-Máquina (IHM)

---

## 👥 Equipe

| Nome | RM |
|------|----|
| Guilherme Linard | RM 555768 |
| Lucas Vasquez | RM 55159 |
| Ali Andrea | RM 558052 |

---

## 📋 Descrição do Projeto

O **Smart Gym Station** é um sistema embarcado que simula uma estação de treino inteligente. Ao aproximar o cartão RFID, o aluno é identificado no banco de dados e a interface exibe seu nome, exercício prescrito e contador de repetições. A câmera ativa o monitoramento de postura em tempo real via **MediaPipe Pose**, desenhando o esqueleto sobre o vídeo. Todos os acessos são registrados automaticamente no banco SQLite com data e hora.

**Fluxo completo:**
```
Cartão RFID → Arduino Uno → Serial (USB) → Python (db_helper) → SQLite → Tkinter GUI
                                                                   ↘ Câmera + MediaPipe
```

---

## 🗂️ Estrutura do Repositório

```
smart_gym/
├── arduino/
│   └── rfid_reader/
│       └── rfid_reader.ino       # Arduino Uno — leitura RFID RC522
├── database/
│   ├── setup_db.py               # Script de criação e seed do banco
│   └── smart_gym.db              # Banco SQLite gerado após setup
├── python/
│   ├── main_gui.py               # Interface gráfica principal (Tkinter)
│   ├── db_helper.py              # Funções de acesso ao SQLite
│   ├── rfid_reader.py            # Leitura serial do Arduino Uno
│   └── pose_monitor.py           # Captura de câmera + MediaPipe (thread)
├── requirements.txt
└── README.md
```

---

## 🗄️ Banco de Dados — Tabelas

### `alunos`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER PK | Identificador único auto-incrementado |
| `nome` | TEXT | Nome completo do aluno |
| `uid_rfid` | TEXT UNIQUE | UID do cartão RFID (ex.: `A1:B2:C3:D4`) |
| `exercicio` | TEXT | Exercício prescrito pelo personal |
| `repeticoes` | INTEGER | Total de repetições acumuladas |

### `log_acesso`
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `id` | INTEGER PK | Identificador único |
| `aluno_id` | INTEGER FK | Referência ao aluno |
| `uid_rfid` | TEXT | UID lido no acesso |
| `horario` | TEXT | Data/hora do acesso (`datetime('now','localtime')`) |

---

## 🔧 Hardware Utilizado

| Componente | Quantidade |
|------------|------------|
| Arduino Uno| 1 |
| Módulo RFID RC522 + cartões/tags | 1 + 2+ |
| Cabo USB para programação | 1 |
| Webcam USB (ou câmera embutida) | 1 |
| Jumpers macho-macho | 7 |
| Protoboard | 1 |

---

## 🔌 Diagrama de Conexões — RC522 ↔ Arduino Uno

```
RC522 Pin  │  Arduino Uno Pin
-----------│-----------------
SDA (SS)   │  Pino 10
SCK        │  Pino 13
MOSI       │  Pino 11
MISO       │  Pino 12
IRQ        │  (não usado)
GND        │  GND
RST        │  Pino 9
3.3V       │  3.3V
```

> ⚠️ **Atenção:** O RC522 opera em **3.3 V**. Não conecte ao pino de 5 V.

Diagrama visual: [Wokwi Simulation Link](https://wokwi.com/projects/463578516384126977)

---

## 📦 Bibliotecas e Dependências

### Arduino / ESP32
| Biblioteca | Versão | Finalidade |
|------------|--------|------------|
| MFRC522 | 1.4.10+ | Leitura do módulo RC522 |
| SPI | (built-in) | Comunicação SPI |

### Python
| Biblioteca | Versão | Finalidade |
|------------|--------|------------|
| `opencv-python` | ≥ 4.8 | Captura de vídeo |
| `mediapipe` | ≥ 0.10 | Detecção de pose / esqueleto |
| `pyserial` | ≥ 3.5 | Comunicação serial com Arduino |
| `Pillow` | ≥ 10.0 | Renderização de imagens no Tkinter |
| `sqlite3` | built-in | Banco de dados local |
| `tkinter` | built-in | Interface gráfica |

---

## 🚀 Instruções de Setup e Execução

### 1. Clone o repositório
```bash
git clone 
cd smart-gym-cp02
```

### 2. Crie e ative um ambiente virtual (recomendado)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instale as dependências Python
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados
```bash
python database/setup_db.py
```
Isso criará o arquivo `database/smart_gym.db` com 5 alunos de exemplo.

### 5. Grave o sketch no Arduino/ESP32
- Abra `arduino/rfid_reader/rfid_reader.ino` na Arduino IDE
- Instale a biblioteca **MFRC522** via *Sketch → Incluir Biblioteca → Gerenciar Bibliotecas*
- Selecione a placa correta (*Arduino Uno*)
- Faça o upload

### 6. Execute a interface gráfica
```bash
cd python
python main_gui.py
```

> 💡 **Sem hardware?** Clique no botão **[DEMO] Simular Cartão** na interface para testar sem Arduino conectado.

---

## 📝 UIDs dos Alunos de Exemplo

| Aluno | UID do Cartão | Exercício |
|-------|---------------|-----------|
| Carlos Mendes | `A1:B2:C3:D4` | Supino Reto |
| Ana Paula | `E5:F6:G7:H8` | Agachamento |
| Lucas Ferreira | `I9:J0:K1:L2` | Remada Curvada |
| Juliana Costa | `M3:N4:O5:P6` | Desenvolvimento |
| Rafael Souza | `Q7:R8:S9:T0` | Leg Press |

---

## 🎬 Vídeo Demonstrativo

🔗 [Link do vídeo](https://www.youtube.com/watch?v=QVYUDBO_6_U)

---

## 📊 Rubrica de Avaliação

| Critério | Pontos |
|----------|--------|
| Organização do código e repositório | 2 pts |
| Qualidade do vídeo explicativo | 2 pts |
| Qualidade técnica do README | 1 pt |
| Demonstração Hands-ON em aula | 5 pts |
| **Total** | **10 pts** |

---

*Projeto desenvolvido para a disciplina Physical Computing (IoT & IoB) — Engenharia de Software — FIAP 2026.*
