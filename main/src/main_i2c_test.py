import master_mind
import json_edit

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
        print("7. Send - Time - Read")
        
        op = (int(input("| Digite a opcao: ")))
        if(op == 1):
            slot = int(input("|Slot: "))
            #port = int(input("|Port: "))
            #write =int(input("|Action: "))
            try:
                data = {
                    "id": "5",                 # ID da requisicao
                    "test":"Tensao 3.3V",      # Irrelevante ao firmware
                    "slot":slot,               # Chip Select SPI
                    "port_output":[1,1],       # Porta a ser usada
                    "debug": True}
                write = list(data.values())[3:]
                print(f"Enviando ao SLOT {slot}...")
                master_mind.send_i2c(slot, write)
                print(f"Lendo resposta SLOT {slot}...")
                response = master_mind.read_i2c(slot)
                print(f"Resposta SLOT {slot}:", response)
                
            except Exception as e:
                print(f"Modulo SLOT {slot} nao encontrado.")
            print()
        if(op == 2):
            master_mind.scan_i2c()
        if(op == 3):
            slot = 2 #int(input("|Slot: "))
            write = "check" #str(input("|CMD: "))
            try:
                print(f"Enviando ao SLOT {slot}...")
                master_mind.send_i2c(slot, write)
                print(f"Lendo resposta SLOT {slot}...")
                response = master_mind.read_i2c(slot)
                print(f"Resposta SLOT {slot}:", response)
            except Exception as e:
                print(f"Modulo SLOT {slot} nao encontrado.")
            print()
        if(op==4):
            slot = int(input("|Slot: "))
            master_mind.scan_i2c(slot)
        if(op==5):
            pass
        if(op == 6):
            slot = 2
            print(master_mind.send_check(slot))
        if(op == 7):
            slot = int(input("| SLOT: "))
            msg  = str(input("| Mensagem: "))
            time = int(input("| TIME: "))
            master_mind.send_time_read(slot,msg,time)
        print()
