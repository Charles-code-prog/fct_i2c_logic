import json
import os
from datetime import datetime

# Caminho do arquivo
base_dir = os.path.dirname(os.path.abspath(__file__))

# Funcaoo auxiliar para construir caminhos seguros para arquivos JSON
def caminho_json(rel_path):
    return os.path.join(base_dir, "..", rel_path)

# Caminhos absolutos dos arquivos JSON  
arquivo_json_slots       = caminho_json("data/slots.json")
arquivo_json_i2c_addrss  = caminho_json("data/default_addrss.json")
arquivo_json_rotina      = caminho_json("data/routine.json")
arquivo_json_results     = caminho_json("data/results.json")
arquivo_json_error       = caminho_json("data/error_register.json")

### SLOT
def read_json_slots(slot_especifico=None):
    caminho = arquivo_json_slots
    with open(caminho, "r") as f:
        data = json.load(f)

    # Se nao for lista (erro no arquivo), aborta
    if not isinstance(data, list):
        print("Erro: o JSON precisa conter uma lista de objetos.")
        return

    encontrado = False
    result = []
    for placa in data:
        if slot_especifico is None or placa["slot"] == slot_especifico:
            print(f"Slot: {placa['slot']}")
            print(f"Presente: {placa['present']}")
            print(f"Endereco I2C: {placa['addrss']}")
            print(f"Nome: {placa['name']}")
            print(f"Firmware: {placa['firmware']}")
            print(f"Type: {placa['type']}")
            print(f"Portas: {placa['ports']}")
            print(f"Temperatura: {placa['temperature']} C")
            print(f"Tensao de alimentaçao: {placa['voltage']} C")  
            print("-" * 30)
            encontrado = True

    if not encontrado:
        print(f"Slot {slot_especifico} nao encontrado.")

#read_json_slots(2)

def atualizar_slot_json(slot_alvo, novos_dados=False):
    # 1. Carrega o JSON existente
    caminho = arquivo_json_slots
    with open(caminho, "r") as f:
        dados = json.load(f)

    # 2. Atualiza o slot correspondente
    for slot in dados:
        if slot["slot"] == slot_alvo:
            if novos_dados:
                # Atualiza com os dados fornecidos
                slot.update(novos_dados)
            else:
                # Seta todos os campos (menos "slot") para None
                for chave in list(slot.keys()):
                    if chave != "slot":
                        slot[chave] = None
            break

    # 3. Salva novamente o JSON com as alteracoes
    with open(caminho, "w") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

### ADDRSS
def atualizar_endereco_slot(slot, novo_endereco):
    caminho_arquivo = arquivo_json_i2c_addrss
    try:
        # 1. Le o conteudo do arquivo JSON
        with open(caminho_arquivo, "r") as f:
            dados = json.load(f)

        # 2. Garante que ha uma lista valida
        if "i2c_addresses" not in dados or not isinstance(dados["i2c_addresses"], list):
            print("Erro: Estrutura invalida no JSON.")
            return

        # 3. Verifica se o slot existe
        if slot < 0 or slot >= len(dados["i2c_addresses"]):
            print(f"Erro: Slot {slot} fora do intervalo.")
            return

        # 4. Atualiza o slot com o novo endereao
        dados["i2c_addresses"][slot] = novo_endereco

        # 5. Salva o arquivo novamente
        with open(caminho_arquivo, "w") as f:
            json.dump(dados, f, indent=4)

        print(f"Endereco do slot {slot} atualizado para {novo_endereco} com sucesso.")

    except Exception as e:
        print(f"Erro ao atualizar: {e}")
        

def ler_lista_enderecos():
    try:
        with open(arquivo_json_i2c_addrss, "r") as f:
            dados = json.load(f)

        return dados.get("i2c_addresses", [])
    
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return []
    

### Rotinas
def gerenciar_rotina(rotina, deletar=False):
    rotinas = []
    caminho_arquivo = arquivo_json_rotina
    # 1. Le o conteudo existente
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, "r") as f:
            try:
                rotinas = json.load(f)
            except json.JSONDecodeError:
                print("Aviso: JSON malformado, criando novo.")

    id_alvo = rotina.get("id")
    if id_alvo is None:
        print("Erro: rotina precisa conter um campo 'id'.")
        return

    # 2. Verifica se o ID existe
    for i, r in enumerate(rotinas):
        if r.get("id") == id_alvo:
            if deletar:
                rotinas.pop(i)
                print(f"Rotina com id={id_alvo} deletada.")
            else:
                rotinas[i] = rotina
                print(f"Rotina com id={id_alvo} atualizada.")
            break
    else:
        if deletar:
            print(f"ID {id_alvo} nao encontrado. Nada foi deletado.")
        else:
            rotinas.append(rotina)
            print(f"Nova rotina com id={id_alvo} adicionada.")
    # 3. Salva o arquivo atualizado
    with open(caminho_arquivo, "w") as f:
        json.dump(rotinas, f, indent=4)


### GERAL
def obter_rotina_por_chave(caminho_arquivo, chave):
    try:
        with open(caminho_arquivo, "r") as f:
            rotinas = json.load(f)
        for rotina in rotinas:
            if rotina.get(chave):
                return rotina
        return None  # Se nao encontrar o ID
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return None
    

def contar_keys(caminho_json, separador):
    with open(caminho_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)  # <-- aqui usamos json.load() (sem 's')
    return sum(1 for item in dados if separador in item)


### ERROR
def error_logger(slot, msg):
    file_path = arquivo_json_error
    # Descompacta a lista
    addr_i2c, id_test, test_name, op, error = msg

    # Monta o registro no formato desejado
    registro = {
        "slot": slot,
        "addr_i2c": addr_i2c,
        "datetime": datetime.now().strftime("%H:%M:%S %d/%m/%y"),
        "id": id_test,
        "test": test_name,
        "op": op,
        "error": error
    }

    # Se o arquivo nao existir, cria uma lista nova
    if not os.path.exists(file_path):
        dados = []
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
            except json.JSONDecodeError:
                dados = []

    # Adiciona novo registro
    dados.append(registro)
    
    # Salva de volta
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# error_logger(
#     slot=1,
#     msg= [81, 5, "Tensão 3.3V", "read", "no response"]
# )

#atualizar_slot_json(arquivo_json_slots,1)
#print("Lista de enderecos: ",ler_lista_enderecos())
#print("Numero de teste por id: ",contar_keys(arquivo_json_rotina,"id"))
#print(contar_keys(arquivo_json_rotina,"id"))
        
# gerenciar_rotina(arquivo_json_rotina, 
#     {
#         "id": 1,
#         "test": "Verificar LED",
#         "slot": 1,
#         "port": [3, 0],
#         "debug": False
#     })

# gerenciar_rotina(arquivo_json_rotina, 
#     {
#         "id": 2,
#         "test": "Tensão 3.3V modificada",
#         "slot": 2,
#         "port": [2, 200],
#         "debug": False
#     })

#gerenciar_rotina({"id": 2}, deletar=True)
#atualizar_endereco_slot(slot=2, novo_endereco=0x61)

# atualizar_slot_json(arquivo_json, 1, 
#     novos_dados=
#     {
#     "present": True,
#     "addrss":"0x56",
#     "name":"Relay Cards 0.1", 
#     "firmware":0.1,
#     "ports":8, 
#     "temperature": 38.7
#     })

# atualizar_slot_json(4,
#     novos_dados=
#     {
#     "present": False,
#     "addrss":None,
#     "name":None, 
#     "firmware":None,
#     "ports":None, 
#     "temperature": None
#     })  
