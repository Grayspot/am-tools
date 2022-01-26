import serial.tools.list_ports
import time
import os
from pprint import pprint

def list_of_points(stepX,stepY):
    tab = []
    for y in range(0,700,stepY):
        for x in range(0,700,stepX):
            tab.append(str(x)+","+str(y))
    return tab

def command_handler(port,cmd):
    time.sleep(1)
    if "STEP" in cmd:
            stepX=cmd.split(",",3)[1]
            stepY=cmd.split(",",3)[2]
            posX=0
            posY=0
            tab=list_of_points(int(stepX),int(stepY))
            for i in tab:
                cmd="GOTOPOSITION,"+i+os.linesep
                print(cmd)
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                port.write('\n'.encode())
                port.write(cmd.encode())
                input("MEASUREMENT DONE?")

            '''for y in range(0,700,int(stepY)):
                for x in range(0,700,int(stepX)):
                    time.sleep(1)
                    cmd="GOTOPOSITION,"+str(x)+","+str(y)+os.linesep
                    command_handler(ser,cmd)
                    while True:
                        try:
                            ser.reset_output_buffer()
                            feedback=ser.readline().decode('ascii')
                            if(posX==float(feedback.split(",",15)[3])): 
                                command_handler(ser,cmd)
                                break
                            posX=float(feedback.split(",",15)[3])
                            posY=float(feedback.split(",",15)[4])
                            print(posX,posY)
                        except(IndexError):
                            pass
                        print("WHILE\n")
                        if(posX>float(x)+0.3 or posX<float(x)-0.3): break
                    print("INNER FOR\n")
                print("OUTER FOR\n")'''
    if(cmd=="READ" and "STEP" not in cmd):
        port.reset_output_buffer()
        print(port.readline().decode('ascii'))
    else:
        port.reset_output_buffer()
        feedback=port.readline().decode('ascii')
        #while (feedback==port.readline().decode('ascii')):
            #print("stuck")
        port.write(cmd.encode())
            #time.sleep(0.5)
            #feedback=port.readline().decode('ascii')


def find_port(snr):
    ports = list(serial.tools.list_ports.comports())
    for p in ports :
        print(ports)
        if snr in p.serial_number:
            return p.device
    raise IOError("Unable to find arduino with given SNR.")

connect = find_port('95530343434351A012C1')
        
ser = serial.Serial(connect, baudrate=115200, bytesize=serial.EIGHTBITS, timeout=1,write_timeout=3)
if(ser.isOpen() == False):
    ser.open()

command=""

########################
#        CMD LIST      #
########################
# INITAXISORIGINS - OK
# GOTOPOSITION,X,Y - OK
# STOPMOTION - OK
# SETSPEED - OK
# SETSTROKE - ???
# BRKENGAGE - OK
# BRKRELEASE - OK
########################

list_of_points(150,150)

while(command!="exit"):
    #os.system('cls' if os.name == 'nt' else 'clear')
    #INITAXISORIGINS
    #GOTOPOSITION
    #ser.write('INITAXISORIGINS'.encode())

    ser.reset_input_buffer()
    time.sleep(1)
    command=input(">> ")
    if(command!="exit"):
        command=command+os.linesep
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        command_handler(ser,command)

        


ser.close()
# while (1):
#    arduinoData = ser.readline().decode('ascii')
#    print(arduinoData)