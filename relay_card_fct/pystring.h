#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

bool isValidFormat(char* str, char sep) {
    int len = strlen(str);
    return str[0] == sep && str[len - 1] == sep;
}

#define MAX_TOKENS 10       // Máximo de parâmetros que serão separados
#define MAX_TOKEN_LEN 20    // Tamanho máximo de cada parâmetro

char tokens[MAX_TOKENS][MAX_TOKEN_LEN];  // Armazena os tokens separados

char** split(char* str, char sep) {
  static char* tokenPtrs[MAX_TOKENS];  // Ponteiros para cada token
  int tokenIndex = 0;

  char* current = str;
  while (*current && tokenIndex < MAX_TOKENS) {
    // Aponta para o início do próximo token
    tokenPtrs[tokenIndex] = tokens[tokenIndex];
    int charIndex = 0;

    // Copia os caracteres até encontrar o separador ou fim
    while (*current && *current != sep && charIndex < MAX_TOKEN_LEN - 1) {
      tokens[tokenIndex][charIndex++] = *current++;
    }
    tokens[tokenIndex][charIndex] = '\0'; // Finaliza string

    tokenIndex++;

    // Pula o separador se ainda não terminou
    if (*current == sep) current++;
  }


  return tokenPtrs;
}


int count(char* str, char target) { //Contagem de caracteres especificados
    int total = 0;
    while (*str) {
        if (*str == target) {
            total++;
        }
        str++;
    }
    return total;
}


int calcular_checksum(char* array[], int tamanho) {
    int checksum = 0;

    for (int i = 0; i < tamanho; i++) {
        for (int j = 0; array[i][j] != '\0'; j++) {
            //printf("\n%d <- %c = %d",checksum, array[i][j],(unsigned char)array[i][j]);
            checksum += (unsigned char)array[i][j];
        }
    }

    return checksum % 256;
}

#define MAX_TAMANHO_ARRAY 20      // máximo de strings
#define MAX_NUM_LEN       12      // espaço por string

char valores[MAX_TAMANHO_ARRAY][MAX_NUM_LEN];  // onde os números em string serão armazenados
char* array[MAX_TAMANHO_ARRAY];                // ponteiros para cada string

int add_checksum(char* array[], int* count, int valor) {
  if (*count >= MAX_TAMANHO_ARRAY) {
    return 0; // erro: sem espaço
  }

  // converte valor para string diretamente no buffer estático
  snprintf(valores[*count], MAX_NUM_LEN, "%d", valor);
  array[*count] = valores[*count];  // aponta para a string convertida
  (*count)++;

  return 1; // sucesso
}
