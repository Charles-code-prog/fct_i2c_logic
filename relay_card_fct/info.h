#include "pico/stdlib.h"
#include "hardware/adc.h"

char nomePCB[] = "Relay";
char firmware_v[] = "0.1";
char boardType[] = "OUT"; // IN ou IOUT
char numero_de_portas[] = "8";

float lerTemperaturaRP2040() {
  adc_init();                     // Inicializa o ADC
  adc_set_temp_sensor_enabled(true);  // Habilita sensor interno
  adc_select_input(4);           // Canal 4 = sensor interno

  uint16_t leitura = adc_read();  // Lê valor de 0–4095

  // Conversão baseada no datasheet do RP2040:
  // T = 27 - (ADC - 0.706)/0.001721
  const float conversao = 3.3f / (1 << 12);  // 3.3V / 4096
  float voltagem = leitura * conversao;
  float temperatura = 27.0f - (voltagem - 0.706f) / 0.001721f;

  return temperatura;
}

float lerAlimentacaoRP2040(){
  analogReadResolution(12); // ADC de 12 bits

  int leitura = analogRead(29); // GPIO 29 → canal 4 → leitura da referência interna de 0.9V

  // Estimar a tensão de alimentação (Vdd)
  float vRefInterna = 0.9; // volts
  float vdd = (vRefInterna * 4096.0) / leitura;
  return vdd;
}