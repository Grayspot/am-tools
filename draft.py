import serial.tools.list_ports
import time
import os

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
                x=float(i.split(",")[0])
                y=float(i.split(",")[1])
                cmd="GOTOPOSITION,"+i+os.linesep
                port.reset_input_buffer()
                port.reset_output_buffer()
                port.write(cmd.encode())
                
                clear = False
                cpt = 0
                while not clear:
                    try:
                        port.reset_output_buffer()
                        feedback=port.readline().decode('ascii')
                        time.sleep(0.1)
                        if(feedback==port.readline().decode('ascii')):
                            cpt+=1
                        
                        if(cpt>3):
                            clear = True     
                    except(IndexError):
                        pass
    if "READ" in cmd:
        #port.reset_output_buffer()
        print(port.readline().decode('ascii'))
    else:
        #port.reset_input_buffer()
        port.write(cmd.encode())
        time.sleep(0.2)


def find_port(snr):
    ports = list(serial.tools.list_ports.comports())
    for p in ports :
        if snr in p.serial_number:
            return p.device
    raise IOError("Unable to find arduino with given SNR.")



def main():
    connect = find_port('95530343434351A012C1')
            
    ser = serial.Serial(connect, baudrate=115200, bytesize=serial.EIGHTBITS, timeout=1,write_timeout=3)
    if(ser.isOpen() == False):
        ser.open()

    command=""

    ########################
    #    TAKING ORIGINS    #
    ########################

    while(True):
        command="INITAXISORIGINS"+os.linesep
        ser.write(command.encode())
        time.sleep(0.5)
        try:
            feedback=ser.readline().decode('ascii').split(',',15)
            print(feedback[3],feedback[4])
            if(float(feedback[3]) == 0):
                break
        except(IndexError):
            ser.write(command.encode())


    #test = "PEPEGA,GAPEPE,HUEHUE"
    #print(test.split(',',3)[5])   


    ########################
    #       CMD LIST       #
    ########################
    # INITAXISORIGINS - OK
    # GOTOPOSITION,X,Y - OK
    # STOPMOTION - OK <--- type 'X' to stop motion
    # SETSPEED - OK
    # SETSTROKE - ???
    # BRKENGAGE - OK
    # BRKRELEASE - OK
    ########################

    while(command!="exit"):
        #os.system('cls' if os.name == 'nt' else 'clear') # <--- put this line in comm so that it doesn't clear the terminal

        ser.reset_input_buffer()
        command=input(">> ")
        if(command!="exit"):
            command=command+os.linesep
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            command_handler(ser,command)

    ser.close() #closing the port    

if __name__ == "__main__":
    main()