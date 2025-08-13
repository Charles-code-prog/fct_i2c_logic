# fct_i2c_logic
Manual de uso das funções
### master_mind.py - código nível **FIRMWARE**
### **Escanear endereços I2C**
### `scan_i2c(slot=False)`

**Objetivo:**

- Escanear o barramento I²C para localizar dispositivos conectados.
- Definir o endereço I²C de uma placa.
- Salvar as informações encontradas em no arquivo `data/slots.json`
**Parâmetros:**

|Nome|Tipo|Padrão|Descrição|
|---|---|---|---|
|slot|bool/int|`False`|Se `False`, apenas lista dispositivos; se número, define endereço para a placa correspondente.|
### **Enviar mensagens via I2C:**
### `send_json(slot, msg, addr=False)`

**Objetivo:**
- Enviar dados no formato dicionário/lista/string para um dispositivo I²C específico.

**Parâmetros:**

| Nome | Tipo          | Padrão  | Descrição                                                                                 |
| ---- | ------------- | ------- | ----------------------------------------------------------------------------------------- |
| slot | int           | —       | Número do slot a ser ativado para comunicação.                                            |
| msg  | dict/list/str | —       | Dicionário/Lista/String Python que será convertido em JSON e enviado via I²C.             |
| addr | int/bool      | `False` | Endereço I²C do dispositivo; se `False`, usa o endereço configurado em `CS_ADDRSS[slot]`. |

### **Receber mensagem I2C**
### `read_json(slot, addr=False)`

**Objetivo:**
- Ler um objeto JSON de um dispositivo I²C especificado pelo slot.
- Receber dados em blocos (`CHUNK_SIZE`) até que a transmissão seja concluída.
- Retornar o JSON como string (decodificado de UTF-8).

**Parâmetros:**

| Nome | Tipo     | Padrão  | Descrição                                                             |
| ---- | -------- | ------- | --------------------------------------------------------------------- |
| slot | int      | —       | Índice do slot que identifica o dispositivo.                          |
| addr | int/bool | `False` | Endereço I²C manual. Se `False`, usa o endereço definido para o slot. |

**Retorno:**
- `str` — Conteúdo do JSON recebido.
- `None` — Se ocorrer erro na decodificação ou nenhum dado for recebido.

### **Enviar - Esperar - Receber**
### `send_time_read(slot,msg,time)`

* Envia uma **mensagem** para o **slot** escolhido e recebe e resposta depois de um determinado **tempo**.
**Parâmetros**

| Nome | Tipo         | Descrição                                 |
| ---- | ------------ | ----------------------------------------- |
| slot | int          | posição do card alvo da comunicação       |
| msg  | dic/list/str | mensagem a ser enviada                    |
| time | int          | tempo em segundos entre escrita e leitura |

### json_edit.py código nível **BACKEND**
### `ler_lista_enderecos()`
* Retorna em uma lista os endereços i2c salvos em `defaul_addrss.json`

### `atualizar_json_slot(slot,novos_dados)`
* Atualiza o ***slots.json*** com os dados extraídos por scan_i2c().

### `error_logger(slot, msg)`
* Insere uma mensagem de erro em um JSON
* Estrutura dos dados: 
	`addr_i2c, id_test, test_name, op, error = msg`
 