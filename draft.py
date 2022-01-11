import serial.tools.list_ports
import os

def find_port(serial_number):
    for port in serial.tools.list_ports.comports():
        if port.serial_number == serial_number:
            return serial.Serial(port.device)
    raise IOError("Unable to find arduino with given SNR.")

connect = find_port(serial_number='95530343434351A012C1')
print(connect)

ser = serial.Serial(connect.port, baudrate=115200)
if(ser.isOpen() == False):
    ser.open()

cmd=""

while(cmd!="exit"):
    os.system('cls' if os.name == 'nt' else 'clear')
    #INITAXISORIGINS
    cmd=input(">> ")
    if(cmd!="exit"):
        ser.write(cmd.encode())
    arduinoData = ser.readline().decode('ascii')
    print(arduinoData)
    print("\n")

ser.close()
# while (1):
#    arduinoData = ser.readline().decode('ascii')
#    print(arduinoData)