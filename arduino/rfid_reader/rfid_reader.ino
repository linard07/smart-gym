/*
 * Smart Gym - Leitura RFID via ESP32/Arduino
 * CP02 - Physical Computing (IoT & IoB) - FIAP
 *
 * Hardware:
 *  - ESP32 (ou Arduino Uno/Mega)
 *  - Módulo RFID RC522
 *
 * Conexões RC522 -> ESP32:
 *  SDA  -> GPIO 5
 *  SCK  -> GPIO 18
 *  MOSI -> GPIO 23
 *  MISO -> GPIO 19
 *  RST  -> GPIO 27
 *  3.3V -> 3.3V
 *  GND  -> GND
 *
 * Bibliotecas necessárias:
 *  - MFRC522 by GithubCommunity (v1.4.10+)
 */

#include <SPI.h>
#include <MFRC522.h>

// Pinos do RC522
#define SS_PIN  10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  Serial.println("READY");  // Sinal para o Python saber que está pronto
}

void loop() {
  // Aguarda novo cartão
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  // Monta UID como string hexadecimal
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
    if (i < rfid.uid.size - 1) uid += ":";
  }
  uid.toUpperCase();

  // Envia pelo Serial no formato esperado pelo Python
  Serial.println("UID:" + uid);

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  delay(1500);  // Evita leitura dupla
}
