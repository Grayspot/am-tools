import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
for port in ports:
    print(port.serial_number)

def find_port(serial_number):
    for port in serial.tools.list_ports.comports():
        if port.serial_number == serial_number:
            return serial.Serial(port.device)
    raise IOError("Unable to find arduino with given SNR.")

connect = find_port(serial_number='SNR goes here.')

ser = serial.Serial(connect, baudrate = 9600, timeout = 1)

while (1):
    arduinoData = ser.readline().decode('ascii')
    print(arduinoData)