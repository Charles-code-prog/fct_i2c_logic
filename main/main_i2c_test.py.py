#MAIN Tester
import time
import json
from smbus2 import SMBus, i2c_msg
import RPi.GPIO as GPIO
import json_edit

GPIO.setwarnings(False)

I2C_BUS = 1
CS_ADDRSS = json_edit.ler_lista_enderecos()
CHUNK_SIZE = 28

GPIO.setmode(GPIO.BCM)       # Usa a numeracao BCM
CHIP_SELECTS = [18,17,27,22,5,6,26,21,20]

for CS in enumerate(CHIP_SELECTS): 
    if(CS[0] != 0):
        GPIO.setup(CS[1], GPIO.OUT)     # Declara CS como saidas
        GPIO.output(CS[1],GPIO.HIGH)

def scan_i2c():
    I2C_BUS = 1
    CS_ADDRSS = json_edit.ler_lista_enderecos()
    bus = SMBus(I2C_BUS)
    
    print("Escaneando enderecos I2C...")
    
    found_devices = []
    for CS in enumerate(CHIP_SELECTS):    
        if(CS[0] != 0):
            GPIO.output(CS[1],GPIO.LOW)
            slot = CS[0]
            for address in range(0x03, 0x78):  
                try:
                    bus.write_byte(address, 0)  
                    found_devices.append(hex(address))
                except IOError:
                    pass  
            
            if found_devices and slot!=0:
                print(f"CS{slot}: ",found_devices)
                if int(found_devices[0],16) != CS_ADDRSS[slot]:

                    actual_addrss = int(found_devices[0],16)
                    ## Serve pra atualizar "slots.json"
                    send_json(bus, actual_addrss, "check") ## CHECK
                    response = read_json(bus, actual_addrss) ## Respostas de CHECK
                    response = response.split(";")
                    json_edit.atualizar_slot_json(json_edit.arquivo_json, slot,                           
                        novos_dados=
                        {
                            "present": True,
                            "addrss":f"0x{CS_ADDRSS[slot]:02X}",
                            "name":f"{response[0]}", 
                            "firmware":f"{response[1]}",
                            "ports":f"{response[2]}", 
                            "temperature": f"{response[3]}"
                        })
                    
                    #Redefine o addrss_i2c
                    write = f"addrss;{CS_ADDRSS[slot]}"
                    print(f"Enviando {write} ao SLOT {slot}...")
                    send_json(bus, actual_addrss, write)
            else:
                print(f"CS{slot}: None")
                json_edit.atualizar_slot_json(json_edit.arquivo_json,slot,
                    novos_dados=
                    {
                        "present": False,
                        "addrss":None,
                        "name":None, 
                        "firmware":None,
                        "ports":None, 
                        "temperature": None
                    })  
            found_devices.clear()
            GPIO.output(CS[1],GPIO.HIGH)

def scan_i2c_slot(slot):
    CS_ADDRSS = json_edit.ler_lista_enderecos()
    I2C_BUS = 1
    bus = SMBus(I2C_BUS)
    
    print("Escaneando enderecos I2C...")
    
    found_devices = []
    GPIO.output(CHIP_SELECTS[slot],GPIO.LOW)
    
    for address in range(0x03, 0x78):  
        try:
            bus.write_byte(address, 0)  
            found_devices.append(hex(address))
        except IOError:
            pass  
    if found_devices :
        print(f"CS{slot}: ",found_devices)
        if int(found_devices[0],16) != CS_ADDRSS[slot]:
            actual_addrss = int(found_devices[0],16)
            ## Serve pra atualizar "slots.json"
            send_json(bus, actual_addrss, "check") ## CHECK
            response = read_json(bus, actual_addrss) ## Respostas de CHECK
            response = response.split(";")
            json_edit.atualizar_slot_json(json_edit.arquivo_json, slot,                           
                novos_dados=
                {
                    "present": True,
                    "addrss":f"0x{CS_ADDRSS[slot]:02X}",
                    "name":f"{response[0]}", 
                    "firmware":f"{response[1]}",
                    "ports":f"{response[2]}", 
                    "temperature": f"{response[3]}"
                })
            
            #Redefine o addrss_i2c
            write = f"addrss;{CS_ADDRSS[slot]}"
            print(f"Enviando {write} ao SLOT {slot}...")
            send_json(bus, actual_addrss, write)
    else:
        print(f"CS{slot}: None")
        json_edit.atualizar_slot_json(json_edit.arquivo_json,slot,
            novos_dados=
            {
                "present": False,
                "addrss":None,
                "name":None, 
                "firmware":None,
                "ports":None, 
                "temperature": None
            })  
    found_devices.clear()
    GPIO.output(CHIP_SELECTS[slot],GPIO.HIGH)


def send_json(bus, slot, data_dict):
    CS_ADDRSS = json_edit.ler_lista_enderecos()
    addr = CS_ADDRSS[slot]
    json_str = json.dumps(data_dict)
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

#----------------------------------------------------------------------------------------------
def read_json(bus, slot):
    json_bytes = bytearray()
    
    CS_ADDRSS = json_edit.ler_lista_enderecos()
    addr = CS_ADDRSS[slot]
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

    try:
        json_str = json_bytes.decode('utf-8')
        return json_str
    except Exception as e:
        print("Erro ao decodificar JSON:", e)
        return None


#----------------------------------------------------------------------------------------------
if __name__ == '__main__':
    #time.sleep(3)
    with SMBus(I2C_BUS) as bus:
        while True:
            print("#### MENU I2C ####")
            print("1. Enviar JSON")
            print("2. Scanear enderecos/cards")
            print("3. Enviar comando: ")
            print("4. Escanear slot")
            
            op = (int(input("Digite a opcao: ")))
            if(op == 1):
                slot = 2# int(input("|Slot: "))
                #port = int(input("|Port: "))
                #write =int(input("|Action: "))
                try:
                    #time.sleep(1)
                    GPIO.output(CHIP_SELECTS[slot],GPIO.LOW)
                
                    data = {
                        "id": "5",                 # ID da requisicao
                        "test":"Tensao 3.3V",      # Irrelevante ao firmware
                        "slot":slot,          # Chip Select SPI
                        "port_output":[1,1],  # Porta a ser usada
                        "debug": True}
                    valores = list(data.values())[3:]
                    print(f"Enviando ao SLOT {slot}...")
                    send_json(bus, slot, valores)
                    print(f"Lendo resposta SLOT {slot}...")
                    response1 = read_json(bus,slot)
                    print(f"Resposta SLOT {slot}:", response1)
                    GPIO.output(CHIP_SELECTS[slot],GPIO.HIGH)
                    #time.sleep(1)
                except Exception as e:
                    print(f"Modulo SLOT {slot} nao encontrado.")
                print()
            if(op == 2):
                scan_i2c()
            if(op == 3):
                slot = 1 #int(input("|Slot: "))
                write= "check" #str(input("|CMD: "))
                try:
                    #time.sleep(1)
                    GPIO.output(CHIP_SELECTS[slot] , GPIO.LOW)
                    print(f"Enviando ao SLOT {slot}...")
                    send_json(bus, slot, write)
                    print(f"Lendo resposta SLOT {slot}...")
                    response1 = read_json(bus,  slot)
                    print(f"Resposta SLOT {slot}:", response1)
                    GPIO.output(CHIP_SELECTS[slot] , GPIO.HIGH)
                    #time.sleep(1)
                except Exception as e:
                    print(f"Modulo SLOT {slot} nao encontrado.")
                print()
            if(op == 4):
                slot = int(input("|Slot: "))
                scan_i2c_slot(slot)

