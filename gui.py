import dearpygui.dearpygui as dpg
import serial.tools.list_ports
import re
import os

# START = KO ===
# STOP = OK
# RESET = OK
# STEP = KO === UNNECESSARY?
# SET LIST = OK
# SET STROKE = OK
# RESET STROKE = OK
# GOTO = OK
# ADD POINT = OK
# DIRECT INPUT = OK
# UP = OK
# DOWN = OK
# REMOVE = KO === INDEX
# SPEED = OK
# FEEDBACK = OK
# TRACKING = OK


step = []
moving = False
list_data = []
global ser
global curr_list_elem
target_coords = []
plot_data_x = [0]
plot_data_y = [0]


######################################################################
# Default DPGUI callback function.                                   #
# sender - id or tag of the widget                                   #
# app_data - None or data passed from widget                         #
# user_data - data defined by user and sent when widget is activated #
######################################################################
# In short:
# Each DPGUI widget has it's id (or tag, if you defined it).
# You can edit the actions that will take place if certain widgent gets activated.
# For example, if sender is "stop" button, the programm sends a stop signal to the board.
def btn_callback(sender, app_data, user_data):
    global curr_list_elem

    ser.reset_input_buffer()

    if sender == "start":
        print("click")
    elif sender == "stop":
        command = "X\n"
        ser.write(command.encode())
    elif sender == "reset":
        command = "INITAXISORIGINS\n"
        ser.write(command.encode())
    elif sender == "step":
        step = dpg.get_value("input_step")
        print(step)
    elif sender == "list":
        step = dpg.get_value("input_step")
        list_data.extend(list_of_points(step[0], step[1]))
        dpg.configure_item("list_of_points", items=list_data)
        curr_list_elem = list_data[0]
    elif sender == "stroke":
        stroke = [dpg.get_value("input_stroke")[0], dpg.get_value("input_stroke")[1]]
        command = "SETSTROKE," + str(stroke[0]) + "," + str(stroke[1]) + os.linesep
        ser.write(command.encode())
    elif sender == "reset_stroke":
        command = "SETSTROKE,700,700" + os.linesep
        ser.write(command.encode())
    elif sender == "goto":
        coords = [dpg.get_value("input_coords")[0], dpg.get_value("input_coords")[1]]
        command = "GOTOPOSITION," + str(coords[0]) + "," + str(coords[1]) + os.linesep
        print(command)
        ser.write(command.encode())
    elif sender == "add_point":
        coords = [dpg.get_value("input_coords")[0], dpg.get_value("input_coords")[1]]
        new_point = str(coords[0]) + "," + str(coords[1])
        list_data.append(new_point)
        dpg.configure_item("list_of_points", items=list_data)
    elif sender == "direct_input":
        inp = re.findall("\d{1,3},\d{1,3}", dpg.get_value("input_from_string"))
        for i, val in enumerate(inp):
            x = val.split(",")
            print(x)
            if int(x[0]) > 700:
                x[0] = "700"
            if int(x[1]) > 700:
                x[1] = "700"
            print(x)
            inp[i] = x[0] + "," + x[1]
            print(inp)
        list_data.extend(inp)
        dpg.configure_item("list_of_points", items=list_data)
        # "100,100;200,430;asd;adasd;adas;100,300;600,800;"
    elif sender == "point_up":
        ind = list_data.index(curr_list_elem)
        list_data.insert(ind - 1, list_data.pop(ind))
        dpg.configure_item("list_of_points", items=list_data)
    elif sender == "point_down":
        ind = list_data.index(curr_list_elem)
        list_data.insert(ind + 1, list_data.pop(ind))
        dpg.configure_item("list_of_points", items=list_data)
    elif sender == "remove_point":
        ind = list_data.index(curr_list_elem)
        list_data.remove(curr_list_elem)
        curr_list_elem = list_data[0]
        dpg.configure_item("list_of_points", items=list_data)
    elif sender == "input_speed":
        spd = int(dpg.get_value("input_speed"))
        command = "SETSPEED," + str(spd) + os.linesep
        ser.write(command.encode())
    elif sender == "selected_point":
        current = list_data[dpg.get_value(sender)]
    elif sender == "list_of_points":
        curr_list_elem = app_data
        print(curr_list_elem)
    else:
        print(sender, app_data, user_data)

###########################################################
# Creates a set of points with given step on X and Y axis #
# Parameters: step on X and Y axis (int)                  #
# Returns an array of said points.                        #
###########################################################
def list_of_points(step_x, step_y):
    tab = []
    for y in range(0, 700, step_y):
        for x in range(0, 700, step_x):
            tab.append(str(x) + "," + str(y))
    return tab

################################
# Checks if robot is in motion #
# Returns boolean              #
################################
def no_motion(port):
    clear = False
    cpt = 0
    while not clear:
        try:
            port.reset_output_buffer()
            feedback = port.readline().decode('ascii')
            # REMOVE
            # time.sleep(0.1)
            if feedback == port.readline().decode('ascii'):
                cpt += 1
            if cpt > 3:
                clear = True
        except IndexError:
            pass


def series(port, tab):
    for i in tab:
        cmd = "GOTOPOSITION," + i + os.linesep
        port.reset_input_buffer()
        port.reset_output_buffer()
        port.write(cmd.encode())
        no_motion(port)


'''
def command_handler(port, cmd):
    # time.sleep(1)
    if "LIST" in cmd:
        points = ["120,50", "50,120", "66, 300", "700,700", "0,0"]
        series(port, points)
    if "STEP" in cmd:
        stepX = cmd.split(",", 3)[1]
        stepY = cmd.split(",", 3)[2]
        tab = list_of_points(int(stepX), int(stepY))
        series(port, tab)
    if "READ" in cmd:
        # port.reset_output_buffer()
        print(port.readline().decode('ascii'))
    else:
        # port.reset_input_buffer()
        port.write(cmd.encode())
        time.sleep(0.2)
'''

###################################################
# Find USB port to which the device is connected  #
# Parameter: serial number of the device (string) #
# Returns: port (string)                          #
###################################################
def find_port(snr):
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if snr in p.serial_number:
            return p.device
    raise IOError("Unable to find arduino with given SNR.")


def main():
    dpg.create_context()
    dpg.create_viewport(resizable=False, title="AMT")
    dpg.set_viewport_height(500)
    dpg.set_viewport_width(800)
    dpg.setup_dearpygui()

    connect = find_port('95530343434351A012C1')

    global ser
    ser = serial.Serial(connect, baudrate=115200, bytesize=serial.EIGHTBITS, timeout=1,write_timeout=3)
    if(ser.isOpen() == False):
        ser.open()

    command = ""

    ########################
    #    TAKING ORIGINS    #
    ########################
    '''
    while(True):
        command="INITAXISORIGINS\r\n"
        ser.write(command.encode())
        try:
            feedback=ser.readline().decode('ascii').split(',',15)
            print(feedback[1],feedback[2])
            if(float(feedback[3]) == 0):
                break
        except(IndexError):
            time.sleep(1)
            ser.write(command.encode())
    '''
    # CUSTOM BUTTON IMAGES
    width_1, height_1, channels_1, data_down = dpg.load_image("down.png")
    width_2, height_2, channels_2, data_up = dpg.load_image("up.png")
    width_3, height_3, channels_3, data_remove = dpg.load_image("cross.png")

    with dpg.texture_registry():
        btn_down = dpg.add_static_texture(width_1, height_1, data_down)
        btn_up = dpg.add_static_texture(width_2, height_2, data_up)
        btn_remove = dpg.add_static_texture(width_3, height_3, data_remove)

    #####################
    # START - INTERFACE #
    #####################

    with dpg.window(tag="W1"):
        # demo_layout=dpg.generate_uuid()
        with dpg.group(horizontal=True):
            with dpg.child_window(width=300, height=-40):
                with dpg.group(horizontal=False):
                    # BIG BUTTONS

                    with dpg.theme(tag="rounded_corners"):
                        with dpg.theme_component(dpg.mvButton):
                            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
                            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3, 3)

                    with dpg.group(horizontal=True):
                        dpg.add_button(tag="start", label="START", width=89, height=60, callback=btn_callback)
                        dpg.add_button(tag="stop", label="STOP", width=89, height=60, callback=btn_callback)
                        dpg.add_button(tag="reset", label="RESET", width=89, height=60, callback=btn_callback)
                        dpg.bind_item_theme("start", "rounded_corners")
                        dpg.bind_item_theme("stop", "rounded_corners")
                        dpg.bind_item_theme("reset", "rounded_corners")

                    # STEP AND STROKE
                    dpg.add_spacer(height=10)
                    with dpg.group(horizontal=True):
                        dpg.add_input_intx(tag="input_step", size=2, width=89, min_value=100, max_value=350,
                                           default_value=[100, 100, 0, 0], min_clamped=True, max_clamped=True)
                        dpg.add_button(tag="step", label="Set STEP", width=89, callback=btn_callback)
                        dpg.add_button(tag="list", label="Set LIST", width=89, callback=btn_callback)
                    with dpg.group(horizontal=True):
                        dpg.add_input_intx(tag="input_stroke", size=2, width=89, min_value=100, max_value=700,
                                           default_value=[100, 100, 0, 0], min_clamped=True, max_clamped=True)
                        dpg.add_button(tag="stroke", label="Set STROKE", width=89, callback=btn_callback)
                        dpg.add_button(tag="reset_stroke", label="Reset STROKE", width=89, callback=btn_callback)

                    # GOTO AND LIST
                    dpg.add_spacer(height=10)
                    with dpg.group(horizontal=True):
                        dpg.add_input_intx(tag="input_coords", size=2, width=89, min_value=0, max_value=700,
                                           default_value=[0, 0, 0, 0], min_clamped=True, max_clamped=True)
                        dpg.add_button(tag="goto", label="Go to XY", width=89, callback=btn_callback)
                        dpg.add_button(tag="add_point", label="Add Point", width=89, callback=btn_callback)

                    # DIRECT INPUT
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(tag="input_from_string", hint="Example: 100,100;200,200;...", width=186)
                        dpg.add_button(tag="direct_input", label="GET INPUT", width=89, callback=btn_callback)
                    # GOTO AND LIST
                    with dpg.group(label="List Boxes", horizontal=True):
                        with dpg.group():
                            dpg.add_listbox(list_data, tag="list_of_points", num_items=10, width=186,
                                            callback=btn_callback)
                        with dpg.group(label="INNER", horizontal=False):
                            dpg.add_image_button(btn_up, width=15, height=15, tag="point_up", callback=btn_callback)
                            dpg.add_image_button(btn_down, width=15, height=15, tag="point_down", callback=btn_callback)
                            dpg.add_image_button(btn_remove, width=15, height=15, tag="remove_point",
                                                 callback=btn_callback)
                            dpg.add_spacer(height=30)
                            with dpg.group(horizontal=True):
                                dpg.add_spacer(width=20, indent=-50)
                                dpg.add_knob_float(tag="input_speed", label="Speed", default_value=40, min_value=30,
                                                   max_value=100, callback=btn_callback)


            # TRACKING
            with dpg.child_window(autosize_x=True, height=-40):
                with dpg.plot(label="Current Position", width=-1, height=-1, crosshairs=False, no_mouse_pos=True,
                              pan_button=-1, no_box_select=True, no_highlight=True, drag_callback=None,
                              drop_callback=None):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="x")
                    dpg.set_axis_limits(dpg.last_item(), 0, 700)
                    with dpg.plot_axis(dpg.mvYAxis, label="y"):
                        dpg.set_axis_limits(dpg.last_item(), 0, 700)
                        dpg.add_scatter_series(plot_data_x, plot_data_y, tag="tracking")

        # ARDUINO FEEDBACK
        with dpg.child_window(autosize_y=True):
            dpg.add_input_text(tag="feedback", readonly=True, label="Feedback", width=-60)

    ###################
    # END - INTERFACE #
    ###################

    dpg.show_viewport()
    dpg.set_primary_window("W1", True)
    # dpg.start_dearpygui()
    cpt = 0
    while dpg.is_dearpygui_running():
        # insert here any code you would like to run in the render loop
        # you can manually stop by using stop_dearpygui()
        x = []
        y = []
        cpt += 1

        #print(cpt)
        if(cpt>20):
            try:
                feedback=ser.readline().decode('ascii')
                cpt=0
                x.append(float(feedback.split(',',15)[3]))
                y.append(float(feedback.split(',',15)[4]))
                dpg.set_value("feedback",feedback)  
                dpg.set_value("tracking", [x,y])
                x.clear()
                y.clear()
            except(IndexError,ValueError):
                pass
        dpg.render_dearpygui_frame()
    ser.close() #closing the port
    dpg.destroy_context()


if __name__ == "__main__":
    main()