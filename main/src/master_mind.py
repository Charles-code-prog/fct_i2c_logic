import time
import json
from smbus2 import SMBus, i2c_msg
import lgpio
import atexit
import json_edit

# Abre o chip GPIO padrao (geralmente /dev/gpiochip0 ? id 0)
HANDLE = lgpio.gpiochip_open(0)

# Lista dos pinos chip select (BCM)
CHIP_SELECTS = [16,17,27,22,5,6,26,21,20] #primeiro pino nao direciona a nenhum CARD

for slot, CS in enumerate(CHIP_SELECTS):
    if slot != 0:
        lgpio.gpio_claim_output(HANDLE, CHIP_SELECTS[slot])
        lgpio.gpio_write(HANDLE, CHIP_SELECTS[slot], 1)
        
        

def ativar_chip_select(slot):
    lgpio.gpio_write(HANDLE, CHIP_SELECTS[slot], 0)


def desativar_chip_select():
    for pin in CHIP_SELECTS:
        lgpio.gpio_write(HANDLE, pin, 1)


I2C_BUS = 1
bus = SMBus(I2C_BUS)
CS_ADDRSS = json_edit.ler_lista_enderecos()
CHUNK_SIZE = 28

def update_i2c_addr():
    CS_ADDRSS = json_edit.ler_lista_enderecos()

def busca_addr_i2c(slot):
    #ativar_chip_select(slot)
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
        send_i2c(slot,f"addrss;{CS_ADDRSS[slot]}",endereco_antigo)

def send_check(slot, addr = False):
    addr = CS_ADDRSS[slot] if addr is False else int(addr,16)
    send_i2c(slot,"check",addr)
    response = read_i2c(slot,addr).split(";")
    return response
    
def update_slot_json(slot,response=False):
    if response is False:
        novos_dados = False
    else:
        novos_dados = {
        "present": True,
        "addrss":CS_ADDRSS[slot],
        "name":response[0], 
        "firmware":response[1],
        "type":response[2],
        "ports":response[3], 
        "temperature": response[4],
        "voltage":response[5]
        }
    json_edit.atualizar_slot_json(slot, novos_dados)
    
#----------------------------------------------------------------------------------------------
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
        else:
            update_slot_json(slot)
        desativar_chip_select()

def send_i2c(slot, msg, addr= False):
    update_i2c_addr()
    addr = CS_ADDRSS[slot] if addr is False else addr
    json_str = json.dumps(msg)
    json_bytes = json_str.encode('utf-8')
    index = 0
    ativar_chip_select(slot)
    try:
        while index < len(json_bytes):
            chunk = json_bytes[index:index + CHUNK_SIZE]
            header = [0x01 if index + CHUNK_SIZE < len(json_bytes) else 0x00]
            msg = i2c_msg.write(addr, header + list(chunk))
            bus.i2c_rdwr(msg)
            index += CHUNK_SIZE
            time.sleep(0.01)
    except Exception as e:
        print(f"erro de comunicaÃ§ao com slot {slot}")
    finally:    
        desativar_chip_select()

def read_i2c(slot, addr = False):
    update_i2c_addr()
    json_bytes = bytearray()
    addr = CS_ADDRSS[slot] if addr is False else addr
    ativar_chip_select(slot)
    try:
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
    except Exception as e:
        print(f"erro de resposta com slot {slot}")
    finally:
        desativar_chip_select()
    try:
        json_str = json_bytes.decode('utf-8')
        return json_str
    except Exception as e:
        print("Erro ao decodificar JSON:", e)
        return None
        
def send_time_read(slot,msg,tempo):
    send_i2c(slot,msg)
    time.sleep(tempo)
    resposta = read_i2c(slot)
    return resposta
#----------------------------------------------------------------------------------------------
#scan_i2c()
# Registro automatico ao sair
@atexit.register
def fechar_gpio():
    print("Fechando GPIO...")
    lgpio.gpiochip_close(HANDLE)
