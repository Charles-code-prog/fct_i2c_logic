#include "hardware/watchdog.h"
#include <EEPROM.h>

const int CS_Pin = 17;
int led = LED_BUILTIN; 

void receiveEvent(int howMany);
void sendEvent();
//-----------------------------------
void initEEPROM();
void salvarEnderecoI2C(byte endereco);
byte lerEnderecoI2C();
void mostrarMenu();
void default_reset();

#define EEPROM_TAM 512
#define EEPROM_ADDR_I2C 0

//-----------------------------------
//#define I2C_ADDRESS 0x08  
byte I2C_ADDRESS;
#define CHUNK_SIZE 28     

String jsonToSend = "";
bool readyToSend = false;
int sendIndex = 0;
bool i2c_actived = true;

#ifndef BRIDGE_H
#define BRIDGE_H
  extern bool ler_cmd;
  extern char cmd[50];         // declaração, sem alocar espaço
  void receiveEvent(int howMany);
#endif

//--------------------------------------------------------------------------------------
void i2c_cicle(){
  int CS_State = digitalRead(CS_Pin);

  if (CS_State == LOW) {

    if(i2c_actived){

      Wire.begin(I2C_ADDRESS);
      Wire.onReceive(receiveEvent);
      Wire.onRequest(sendEvent);

      digitalWrite(led, HIGH);

      Serial.println("CS selecionado.");
    }

    i2c_actived = false;
    
  } else {
    Wire.end();
    i2c_actived = true;
    digitalWrite(led, LOW);
  }
}

void receiveEvent(int howMany) {
  if (digitalRead(CS_Pin) == LOW) {
      Wire.begin(I2C_ADDRESS);
      if (howMany < 1) return;
      byte header = Wire.read();
      char buffer[howMany];     
      int i = 0;
      while (Wire.available() && i < howMany - 1) {
        buffer[i++] = Wire.read();
      }
      buffer[i] = '\0';

      static String receivedData = "";
      receivedData += buffer;

      if (header == 0x00) {
        Serial.print("JSON completo recebido do Master: ");
        Serial.println(receivedData);
        strcpy(cmd,receivedData.c_str());
        ler_cmd = true;
        receivedData = "";
        readyToSend = true;
      }
  }
}

//--------------------------------------------------------------------------------------
void sendEvent() {
  if (digitalRead(CS_Pin) == LOW) {
    Wire.begin(I2C_ADDRESS);
    if (!readyToSend) {
      Wire.write(0x00);  
      return;
    }

    int remaining = jsonToSend.length() - sendIndex;
    byte header = (remaining > CHUNK_SIZE) ? 0x01 : 0x00;

    Wire.write(header);

    for (int i = 0; i < CHUNK_SIZE && sendIndex < jsonToSend.length(); i++, sendIndex++) {
      Wire.write(jsonToSend[sendIndex]);
    }
    jsonToSend = " ";
    if (header == 0x00) {
      sendIndex = 0;
      readyToSend = false;
    }
  }
}

//-------------------------------------

void initEEPROM() {
  EEPROM.begin(EEPROM_TAM);
}

void salvarEnderecoI2C(byte endereco) {
  EEPROM.put(0, endereco);      // escreve na RAM
  if (EEPROM.commit()) {
    Serial.print("Endereço I2C salvo: 0x");
    Serial.println(endereco, HEX);
  } else {
    Serial.println("Erro ao salvar endereço na EEPROM");
  }
}

byte lerEnderecoI2C() {
  byte endereco;
  EEPROM.get(0, endereco);
  if (endereco < 0x08 || endereco > 0x77) {
    return 0x30; // valor padrão se inválido
  }
  return endereco;
}

void default_reset() {
  watchdog_enable(1, 1);  // ativa watchdog com timeout mínimo
  while (1);              // trava o código até o reset ocorrer
}