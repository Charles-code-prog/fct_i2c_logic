#include <Wire.h>
#include <ArduinoJson.h>
#include <string.h>
#include <ctype.h>
#include "Bridge.h"


void i2c_cicle();
//--------------------------------------------------------------------------------------
bool ler_cmd = false;
char cmd[50];
String Scmd = " ";
void Interpretador(char *cmd);
void default_check();
//--------------------------------------------------------------------------------------
void setup() {
  pinMode(CS_Pin, INPUT_PULLUP);
  pinMode(led, OUTPUT);

  EEPROM.begin(EEPROM_TAM);
  I2C_ADDRESS = lerEnderecoI2C();
  Wire.begin(I2C_ADDRESS);
  Wire.setClock(400000);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(sendEvent);
  Serial.begin(9600);

  // JsonDocument doc;
  // doc["id"] = 123;
  // doc["sensor"] = "temperature";
  // doc["value"] = 25.7;
  // doc["status"] = "OK";
  // serializeJson(doc, jsonToSend);
  digitalWrite(led, LOW);
  
  mostrarMenu();
}

//--------------------------------------------------------------------------------------
void loop() {
  // MENU
  //------------------------------------------------------------------------------------
  if (Serial.available()) {
    String linha = Serial.readStringUntil('\n');
    linha.trim();  // remove espaços e \r\n
    char opcao = linha[0];

    if (opcao == '1') {
      byte endereco = lerEnderecoI2C();
      Serial.print("\nEndereço I2C atual: 0x");
      Serial.println(endereco, HEX);
      mostrarMenu();
    }
    if (opcao == '2') {
      Serial.println("\nDigite o novo endereço I2C em hexadecimal (ex: 42): ");
      while (!Serial.available()) {}  // aguarda entrada
      String entrada = Serial.readStringUntil('\n');
      entrada.trim();

      int novoEndereco = strtol(entrada.c_str(), NULL, 16);
      if (novoEndereco >= 0x08 && novoEndereco <= 0x77) {
        salvarEnderecoI2C((byte)novoEndereco);
        default_reset();
      } else {
        Serial.println("Endereço inválido! Use de 08 a 77 (hex).");
      }
      mostrarMenu();
    }
    if (opcao == '3') {
      Serial.println("default_reset()");
      default_reset();
    }
    if (opcao == '4'){
      Serial.println("Check Info");
      default_check();
    }
    else {
      Serial.println("Opção inválida.");
      mostrarMenu();
    }

  }
  //--------------------------------------------------------------------------------------
  i2c_cicle();
  if(ler_cmd){
    Interpretador(cmd);
    memset(cmd, 0, sizeof(cmd));
  }
  ler_cmd = false;
}

void Interpretador(char *cmd) {
  // Comandos simples
  if (strstr(cmd, "reset")) {
    Serial.println("Reseta Card");
    default_reset();
  }

  if (strstr(cmd, "check")) {
    Serial.println("Check Info");
    default_check();
  }

  if (strstr(cmd, "addrss")) {
    Serial.println("Mudar Endereço I2C");
    char *pos = strchr(cmd, ';');  // Encontra o ';'
    if (pos != NULL) {
      pos++;  // Move para o caractere após o ';'
      Serial.println("Gravar novo endereço: ");
      int novoEndereco = atoi(pos);
      Serial.print(atoi(pos));
      if (novoEndereco >= 0x08 && novoEndereco <= 0x77) {
        salvarEnderecoI2C((byte)novoEndereco);
        default_reset();
      } else {
        Serial.println("\nEndereço inválido! Use de 08 a 77 (hex).");
      }
    } else {
      Serial.println("\nNúmero não válido");
    }
  }

  // Verifica se é comando estruturado tipo [[1,0],true]
  if (cmd[0] == '[' && cmd[1] == '[') {
    int pino = -1;
    int estado = -1;
    char debug_str[6] = {0};  // para "true" ou "false"

    int extraídos = sscanf(cmd, "[[%d,%d],%5[^]]", &pino, &estado, debug_str);
    if (extraídos == 3) {
      bool debug = (strcmp(debug_str, "true") == 0);

      Serial.print("Comando estruturado: pino=");
      Serial.print(pino);
      Serial.print(", estado=");
      Serial.print(estado);
      Serial.print(", debug=");
      Serial.println(debug ? "true" : "false");

      // aqui você pode aplicar:
      // digitalWrite(pino, estado);
      return;
    } else {
      Serial.println("Erro ao interpretar comando estruturado");
    }
  }

  // Se não bateu com nenhum tipo conhecido
  Serial.println("\nComando não reconhecido");
}

void mostrarMenu() {
  Serial.println("\n======== Menu I2C ========");
  Serial.println("1 - Ver endereço I2C atual");
  Serial.println("2 - Definir novo endereço I2C");
  Serial.println("3 - Resetar");
  Serial.println("4 - Check");
  Serial.println("==========================");
  Serial.print("Escolha: ");
}



