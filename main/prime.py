import time
import json
from smbus2 import SMBus, i2c_msg
import lgpio
import atexit
import json_edit

# Abre o chip GPIO padrao (geralmente /dev/gpiochip0 ? id 0)
HANDLE = lgpio.gpiochip_open(0)

# Lista dos pinos chip select (BCM)
CHIP_SELECTS = [16,17,27,22,5,6,26,21,20]

for slot, CS in enumerate(CHIP_SELECTS):
    if slot != 0:
        lgpio.gpio_claim_output(HANDLE, CHIP_SELECTS[slot])
        

def ativar_chip_select(slot):
    lgpio.gpio_write(HANDLE, CHIP_SELECTS[slot], 0)
    time.sleep(0.1)

def desativar_chip_select(slot):
    lgpio.gpio_write(HANDLE, CHIP_SELECTS[slot], 1)
    time.sleep(0.1)

I2C_BUS = 1
bus = SMBus(I2C_BUS)
CS_ADDRSS = json_edit.ler_lista_enderecos()
CHUNK_SIZE = 28

def update_i2c_addr():
    CS_ADDRSS = json_edit.ler_lista_enderecos()

def busca_addr_i2c(slot):
    for address in range(0x03, 0x78):  
        try:
            bus.write_byte(address, 0)  
            addr_atual = (hex(address))
            print(f"CS{slot}: {addr_atual}")
            return addr_atual
        except IOError:
            pass  
    print(f"CS{slot}: {None}")
    return None

def redefinir_endereco(slot, endereco_antigo): 
    update_i2c_addr()
    endereco_antigo = int(endereco_antigo, 16)
    if endereco_antigo != CS_ADDRSS[slot]:
        # Redefine o addrss_i2c
        write = f"addrss;{CS_ADDRSS[slot]}"
        print(f"-- Enviando {write} ao SLOT {slot}...")
        send_json(slot,f"addrss;{CS_ADDRSS[slot]}",endereco_antigo)

def send_check(slot,addr = False):
    addr = CS_ADDRSS[slot] if addr is False else int(addr,16)
    send_json(slot,"check",addr)
    response = read_json(slot,addr).split(";")
    return response
    
def update_slot_json(slot,response):
    json_edit.atualizar_slot_json(json_edit.arquivo_json_slots,slot,
    {
        "present": True,
        "addrss":CS_ADDRSS[slot],
        "name":response[0], 
        "firmware":response[1],
        "type":response[2],
        "ports":response[3], 
        "temperature": response[4],
        "voltage":response[5]
    })

def scan_i2c(barramento=False):
    update_i2c_addr()
    print("Escaneando enderecos I2C...")
    # Definir os slots a escanear
    if barramento is False:
        slots_to_scan = list(range(1, len(CHIP_SELECTS)))  # pula o Indice 0
    else:
        slots_to_scan = [barramento]

    for slot in slots_to_scan:
        ativar_chip_select(slot)
        addr = busca_addr_i2c(slot)
        if addr:
            response = send_check(slot,addr)
            print(response)
            update_slot_json(slot,response)
            redefinir_endereco(slot,addr)
        desativar_chip_select(slot)
        
#----------------------------------------------------------------------------------------------
def send_json(slot, msg, addr= False):
    update_i2c_addr()
    ativar_chip_select(slot)
    addr = CS_ADDRSS[slot] if addr is False else addr
    json_str = json.dumps(msg)
    json_bytes = json_str.encode('utf-8')
    index = 0
    print(json_str)
    while index < len(json_bytes):
        chunk = json_bytes[index:index + CHUNK_SIZE]
        header = [0x01 if index + CHUNK_SIZE < len(json_bytes) else 0x00]
        msg = i2c_msg.write(addr, header + list(chunk))
        bus.i2c_rdwr(msg)
        index += CHUNK_SIZE
        time.sleep(0.01)
    desativar_chip_select(slot)

def read_json(slot, addr = False):
    update_i2c_addr()
    ativar_chip_select(slot)
    json_bytes = bytearray()
    addr = CS_ADDRSS[slot] if addr is False else addr
    while True:
        read = i2c_msg.read(addr, CHUNK_SIZE + 1)
        bus.i2c_rdwr(read)
        buffer = list(read)

        filtered_buffer = [item for item in buffer if item != 0]
        if buffer[0] == 0:
            filtered_buffer.insert(0,0)

        if not filtered_buffer:
            print("Nenhum dado recebido.")
            break

        header = filtered_buffer[0]
        json_bytes.extend(filtered_buffer[1:])

        if header == 0x00:
            break

        time.sleep(0.01) 
    desativar_chip_select(slot)
    try:
        json_str = json_bytes.decode('utf-8')
        return json_str
    except Exception as e:
        print("Erro ao decodificar JSON:", e)
        return None

#----------------------------------------------------------------------------------------------

    
# Registro automatico ao sair
@atexit.register
def fechar_gpio():
    print("Fechando GPIO...")
    lgpio.gpiochip_close(HANDLE)

#----------------------------------------------------------------------------------------------
if __name__ == '__main__':
    while True:
        print("#### MENU I2C ####")
        print("1. Enviar JSON")
        print("2. Scanear enderecos/cards")
        print("3. Enviar comando: ")
        print("4. Escanear slot")
        print("5. Rodar Rotina")
        print("6. CHECK")
        
        op = (int(input("| Digite a opcao: ")))
        if(op == 1):
            slot = 1# int(input("|Slot: "))
            #port = int(input("|Port: "))
            #write =int(input("|Action: "))
            try:
                #time.sleep(1)
                ativar_chip_select(slot)
            
                data = {
                    "id": "5",                 # ID da requisicao
                    "test":"Tensao 3.3V",      # Irrelevante ao firmware
                    "slot":slot,          # Chip Select SPI
                    "port_output":[1,1],  # Porta a ser usada
                    "debug": True}
                write = list(data.values())[3:]
                print(f"Enviando ao SLOT {slot}...")
                send_json(bus,  slot, write)
                print(f"Lendo resposta SLOT {slot}...")
                response = read_json(slot)
                print(f"Resposta SLOT {slot}:", response)
                desativar_chip_select(slot)
                #time.sleep(1)
            except Exception as e:
                print(f"Modulo SLOT {slot} nao encontrado.")
            print()
        if(op == 2):
            scan_i2c()
        if(op == 3):
            slot = 2 #int(input("|Slot: "))
            write = "check" #str(input("|CMD: "))
            try:
                print(f"Enviando ao SLOT {slot}...")
                send_json(slot, write)
                print(f"Lendo resposta SLOT {slot}...")
                response = read_json(slot)
                print(f"Resposta SLOT {slot}:", response)
            except Exception as e:
                print(f"Modulo SLOT {slot} nao encontrado.")
            print()
        if(op==4):
            slot = int(input("|Slot: "))
            scan_i2c(slot)
        if(op==5):
            pass
        if(op == 6):
            slot = 2
            send_check(slot,CS_ADDRSS[slot])
        print()

