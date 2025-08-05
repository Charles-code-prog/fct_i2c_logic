import json

# Caminho do arquivo
arquivo_json = "slots.json"

def read_json(caminho, slot_especifico=None):
    with open(caminho, "r") as f:
        data = json.load(f)

    # Se não for lista (erro no arquivo), aborta
    if not isinstance(data, list):
        print("Erro: o JSON precisa conter uma lista de objetos.")
        return

    encontrado = False
    for placa in data:
        if slot_especifico is None or placa["slot"] == slot_especifico:
            print(f"Slot: {placa['slot']}")
            print(f"Presente: {placa['present']}")
            print(f"Endereço I2C: {placa['addrss']}")
            print(f"Nome: {placa['name']}")
            print(f"Firmware: {placa['firmware']}")
            print(f"Portas: {placa['ports']}")
            print(f"Temperatura: {placa['temperature']} C")
            print("-" * 30)
            encontrado = True

    if not encontrado:
        print(f"Slot {slot_especifico} não encontrado.")


def atualizar_slot_json(caminho, slot_alvo, novos_dados):
    # 1. Carrega o JSON existente
    with open(caminho, "r") as f:
        dados = json.load(f)

    # 2. Atualiza o slot correspondente
    for slot in dados:
        if slot["slot"] == slot_alvo:
            slot.update(novos_dados)
            break

    # 3. Salva novamente o JSON com as alterações
    with open(caminho, "w") as f:
        json.dump(dados, f, indent=4)


def atualizar_endereco_slot(caminho_arquivo, slot, novo_endereco):
    try:
        # 1. Lê o conteúdo do arquivo JSON
        with open(caminho_arquivo, "r") as f:
            dados = json.load(f)

        # 2. Garante que há uma lista válida
        if "i2c_addresses" not in dados or not isinstance(dados["i2c_addresses"], list):
            print("Erro: Estrutura inválida no JSON.")
            return

        # 3. Verifica se o slot existe
        if slot < 0 or slot >= len(dados["i2c_addresses"]):
            print(f"Erro: Slot {slot} fora do intervalo.")
            return

        # 4. Atualiza o slot com o novo endereço
        dados["i2c_addresses"][slot] = novo_endereco

        # 5. Salva o arquivo novamente
        with open(caminho_arquivo, "w") as f:
            json.dump(dados, f, indent=4)

        print(f"Endereço do slot {slot} atualizado para {novo_endereco} com sucesso.")

    except Exception as e:
        print(f"Erro ao atualizar: {e}")


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
# atualizar_slot_json(arquivo_json,4,
#     novos_dados=
#     {
#     "present": False,
#     "addrss":None,
#     "name":None, 
#     "firmware":None,
#     "ports":None, 
#     "temperature": None
#     })  
#write_json(arquivo_json,2,True,"Volts Card 2.1",2.3,32,45.3)
#read_json(arquivo_json,1)