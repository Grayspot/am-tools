import dearpygui.dearpygui as dpg
import serial.tools.list_ports
import re
import os

global ser              # serial port
global curr_list_elem   # current element in the listbox
global sequence         # boolean used to enable/disable automatic movement to the list of points
global tooltips         # boolean used to enable/disable tooltips

step = [100, 100]       # step value X,Y
moving = False          # boolean that indicated if the machine is moving
list_data = []          # list that contains all the coordinates
#  list_data_x = [0]       # <- can be used to trace a trajectory for robot's movement (see # TRAJECTORY)
#  list_data_y = [0]       #


######################################################################
# Default DPGUI callback function.                                   #
# sender - id or tag of the widget                                   #
# app_data - None or data passed from widget                         #
# user_data - data defined by user and sent when widget is activated #
######################################################################
# In short:
# Each DPGUI widget has an id (or tag, if you defined it manually).
# You can edit the actions that will take place if certain widget gets activated.
# For example, if sender is "stop" button, the program sends a stop signal to the board.
def btn_callback(sender, app_data, user_data):
    global curr_list_elem
    global sequence
    global tooltips
    global clear
    global ser

    # ser.reset_input_buffer()

    if sender == "start":
        sequence = True
        clear = True
        #for x in list_data:
        #    list_data_x.append(int(x.split(",")[0]))
        #    list_data_y.append(int(x.split(",")[1]))
        #    dpg.set_value("tracking_list",[list_data_x,list_data_y])
    elif sender == "stop":
        command = "X\n"
        ser.write(command.encode())
    elif sender == "reset":
        command = "INITAXISORIGINS\n"
        ser.write(command.encode())
    elif sender == "clear_list":
        list_data.clear()
        dpg.configure_item("list_of_points", items=list_data)
    elif sender == "list":
        step = dpg.get_value("input_step")
        list_data.extend(list_of_points(step[0], step[1]))
        dpg.configure_item("list_of_points", items=list_data)
        curr_list_elem = list_data[0]
    elif sender == "stroke":
        stroke = [dpg.get_value("input_stroke")[0], dpg.get_value("input_stroke")[1]]
        dpg.set_axis_limits("x_axis", -50, stroke[0]+50)
        dpg.set_axis_limits("y_axis", -50, stroke[1]+50)
        command = "SETSTROKE," + str(stroke[0]) + "," + str(stroke[1]) + os.linesep
        ser.write(command.encode())
    elif sender == "reset_stroke":
        dpg.set_axis_limits("x_axis", -50, 750)
        dpg.set_axis_limits("y_axis", -50, 750)
        command = "SETSTROKE,700,700" + os.linesep
        ser.write(command.encode())
    elif sender == "goto":
        coords = [dpg.get_value("input_coords")[0], dpg.get_value("input_coords")[1]]
        command = "GOTOPOSITION," + str(coords[0]) + "," + str(coords[1]) + os.linesep
        ser.write(command.encode())
    elif sender == "add_point":
        coords = [dpg.get_value("input_coords")[0], dpg.get_value("input_coords")[1]]
        new_point = str(coords[0]) + "," + str(coords[1])
        list_data.append(new_point)
        dpg.configure_item("list_of_points", items=list_data)
    elif sender == "direct_input":
        inp = re.findall("\d*,\d*", dpg.get_value("input_from_string"))
        for i, val in enumerate(inp):
            x = val.split(",")
            if int(x[0]) > 700:
                x[0] = "700"
            if int(x[1]) > 700:
                x[1] = "700"
            inp[i] = x[0] + "," + x[1]
        list_data.extend(inp)
        dpg.configure_item("list_of_points", items=list_data)
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
    elif sender == "tooltips":
        if tooltips:
            dpg.configure_item("tooltips", label="Enable Tooltips")
            destroy_tooltips()
            tooltips = False
        else:
            dpg.configure_item("tooltips", label="Disable Tooltips")
            build_tooltips()
            tooltips = True
    elif sender == "connection":
        ser = connection()
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


#########################################################
# Destroys tooltips when clicking on "Disable Tooltips" #
#########################################################
def destroy_tooltips():
    dpg.delete_item("tooltip_reset")
    dpg.delete_item("tooltip_start")
    dpg.delete_item("tooltip_stop")
    dpg.delete_item("tooltip_list")
    dpg.delete_item("tooltip_clear_list")
    dpg.delete_item("tooltip_stroke")
    dpg.delete_item("tooltip_reset_stroke")
    dpg.delete_item("tooltip_goto")
    dpg.delete_item("tooltip_add_point")
    dpg.delete_item("tooltip_direct_input")


###############################################################
# Builds tooltips when clicking on "Enable Tooltips" in menu  #
###############################################################
def build_tooltips():
    with dpg.tooltip("reset", tag="tooltip_reset"):
        dpg.add_text("Return to position 0,0.")
    with dpg.tooltip("start", tag="tooltip_start"):
        dpg.add_text("Start moving to coordinates from the list.")
    with dpg.tooltip("stop", tag="tooltip_stop"):
        dpg.add_text("Stops all motion.")
    with dpg.tooltip("list", tag="tooltip_list"):
        dpg.add_text("Generates a list with given X,Y step.")
    with dpg.tooltip("clear_list", tag="tooltip_clear_list"):
        dpg.add_text("Removes all points from the list.")
    with dpg.tooltip("stroke", tag="tooltip_stroke"):
        dpg.add_text("Limits working zone on 0-X,0-Y.")
    with dpg.tooltip("reset_stroke", tag="tooltip_reset_stroke"):
        dpg.add_text("Resets stroke to 700,700.")
    with dpg.tooltip("goto", tag="tooltip_goto"):
        dpg.add_text("Go to position X,Y.")
    with dpg.tooltip("add_point", tag="tooltip_add_point"):
        dpg.add_text("Adds point X,Y to the list of points.")
    with dpg.tooltip("direct_input", tag="tooltip_direct_input"):
        dpg.add_text("Transforms user-input into a list of coordinates.")


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
    raise IOError("Unable to find Arduino board with given SNR.")


###################################################
# Find USB port to which the device is connected  #
# Parameter: serial number of the device (string) #
# Returns: port (string)                          #
###################################################
def connection():
    connect = find_port('95530343434351A012C1')

    return serial.Serial(connect, baudrate=115200, bytesize=serial.EIGHTBITS, timeout=1, write_timeout=3)


#########################################################################################
# This function builds the actual interface of the application                          #
# The interface is container based.                                                     #
# The root container is the window.                                                     #
# It is split in 3 - control panel (left), tracking panel (right), feedback (bottom).   #
#########################################################################################
def build_interface():

    # Custom button images are loaded here
    width_1, height_1, channels_1, data_down = dpg.load_image("resources/down.png")
    width_2, height_2, channels_2, data_up = dpg.load_image("resources/up.png")
    width_3, height_3, channels_3, data_remove = dpg.load_image("resources/cross.png")

    with dpg.texture_registry():
        btn_down = dpg.add_static_texture(width_1, height_1, data_down)
        btn_up = dpg.add_static_texture(width_2, height_2, data_up)
        btn_remove = dpg.add_static_texture(width_3, height_3, data_remove)

    with dpg.window(tag="W1"):
        #
        # Menu bar is created here.
        #
        with dpg.menu_bar():
            with dpg.menu(label="Help"):
                dpg.add_menu_item(label="Reconnect", tag="connection", callback=btn_callback)
                dpg.add_menu_item(label="Enable Tooltips", tag="tooltips", callback=btn_callback)

        with dpg.group(horizontal=True):
            #
            # Left section of the GUI starts here.
            #
            with dpg.child_window(width=300, height=-40):
                with dpg.group(horizontal=False):
                    with dpg.theme(tag="rounded_corners"):
                        with dpg.theme_component(dpg.mvButton):
                            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 10)
                            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3, 3)

                    with dpg.group(horizontal=True):
                        dpg.add_button(tag="reset", label="RESET", width=89, height=60, callback=btn_callback)
                        dpg.add_button(tag="start", label="START", width=89, height=60, callback=btn_callback)
                        dpg.add_button(tag="stop", label="STOP", width=89, height=60, callback=btn_callback)
                        dpg.bind_item_theme("start", "rounded_corners")
                        dpg.bind_item_theme("stop", "rounded_corners")
                        dpg.bind_item_theme("reset", "rounded_corners")

                    dpg.add_spacer()
                    dpg.add_separator()
                    dpg.add_spacer()

                    with dpg.group(horizontal=True):
                        dpg.add_input_intx(tag="input_step", size=2, width=89, min_value=100, max_value=350,
                                           default_value=[100, 100, 0, 0], min_clamped=True, max_clamped=True)
                        dpg.add_button(tag="list", label="Set LIST", width=89, callback=btn_callback)
                        dpg.add_button(tag="clear_list", label="Clear LIST", width=89, callback=btn_callback)
                    with dpg.group(horizontal=True):
                        dpg.add_input_intx(tag="input_stroke", size=2, width=89, min_value=100, max_value=700,
                                           default_value=[100, 100, 0, 0], min_clamped=True, max_clamped=True)
                        dpg.add_button(tag="stroke", label="Set STROKE", width=89, callback=btn_callback)
                        dpg.add_button(tag="reset_stroke", label="Reset STROKE", width=89, callback=btn_callback)

                    dpg.add_spacer()
                    dpg.add_separator()
                    dpg.add_spacer()

                    with dpg.group(horizontal=True):
                        dpg.add_input_intx(tag="input_coords", size=2, width=89, min_value=0, max_value=700,
                                           default_value=[0, 0, 0, 0], min_clamped=True, max_clamped=True)
                        dpg.add_button(tag="goto", label="Go to XY", width=89, callback=btn_callback)
                        dpg.add_button(tag="add_point", label="Add Point", width=89, callback=btn_callback)

                    with dpg.group(horizontal=True):
                        dpg.add_input_text(tag="input_from_string", hint="Ex.: 100,100;200,200;...", width=186)
                        dpg.add_button(tag="direct_input", label="GET INPUT", width=89, callback=btn_callback)

                    with dpg.group(label="List Boxes", horizontal=True):
                        with dpg.group():
                            dpg.add_listbox(list_data, tag="list_of_points", num_items=10, width=186,
                                            callback=btn_callback)
                        with dpg.group( horizontal=False):
                            dpg.add_image_button(btn_up, width=15, height=15, tag="point_up", callback=btn_callback)
                            dpg.add_image_button(btn_down, width=15, height=15, tag="point_down", callback=btn_callback)
                            dpg.add_image_button(btn_remove, width=15, height=15, tag="remove_point",
                                                 callback=btn_callback)
                            dpg.add_spacer(height=30)
                            with dpg.group(horizontal=True):
                                dpg.add_spacer(width=20, indent=-50)
                                dpg.add_knob_float(tag="input_speed", label="Speed", default_value=40, min_value=30,
                                                   max_value=100, callback=btn_callback)

            #
            # Right section of the GUI starts here.
            #
            with dpg.child_window(autosize_x=True, height=-40):
                with dpg.plot(tag="tracking_plot", label="Current Position", width=-1, height=-1, crosshairs=False, no_mouse_pos=True,
                              pan_button=-1, no_box_select=True, no_highlight=True, drag_callback=None,
                              drop_callback=None):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="X", tag="x_axis")
                    dpg.set_axis_limits(dpg.last_item(), -50, 750)
                    with dpg.plot_axis(dpg.mvYAxis, label="Y", tag="y_axis"):
                        dpg.set_axis_limits(dpg.last_item(), -50, 750)
                        dpg.add_scatter_series([0], [0], tag="tracking")
                        
                        # Next line allows to draw a trajectory of the robots movements. But it requires some tinkering.
                        #dpg.add_line_series(list_data_x, list_data_y, tag="tracking_list") # TRAJECTORY

        #
        # Arduino board feedback
        #
        with dpg.child_window(autosize_y=True):
            dpg.add_input_text(tag="feedback", readonly=True, label="Feedback", width=-60)


def main():
    dpg.create_context()
    dpg.create_viewport(resizable=False, title="RCAMT")
    dpg.set_viewport_height(500)
    dpg.set_viewport_width(800)
    dpg.setup_dearpygui()

    global ser

    #
    # Connection with the Arduino board is established here.
    # Using serial module, we find an Arduino board with the serial number indicated below.
    # If the board is found - connection is established. Otherwise, an exception is thrown.
    #

    connect = find_port('95530343434351A012C1')

    ser = serial.Serial(connect, baudrate=115200, bytesize=serial.EIGHTBITS, timeout=1, write_timeout=3)
    if not ser.isOpen():
       ser.open()

    command = ""

    build_interface()

    dpg.show_viewport()
    dpg.set_primary_window("W1", True)

    global curr_list_elem  # current element in the listbox
    global sequence
    global tooltips

    global tooltips     # boolean used to enable/disable tooltips
    global sequence       # boolean used to enable/disable sequence mode
    global clear        # boolean used to indicate if the robot achieved the endpoint
    sequence = False
    tooltips = False

    cpt = 0
    cpt_list = 0

    #
    # Main loop of DPG
    #
    while dpg.is_dearpygui_running():

        x = []
        y = []
        cpt += 1
        
        if (cpt > 20):
            try:
                # FEEDBACK UPDATE
                ser.reset_input_buffer()
                feedback = ser.readline().decode('ascii')
                cpt = 0
                x.append(float(feedback.split(',', 15)[3]))
                y.append(float(feedback.split(',', 15)[4]))
                dpg.set_value("feedback", feedback)
                dpg.set_value("tracking", [x, y])
                x.clear()
                y.clear()

                # CHECK LIST CONDITION
                if sequence and list_data:
                    #
                    # The acoustic measurement starts here.
                    # You can add your code here.
                    #
                    if not clear:
                        #
                        # This entire section should be replaced.
                        # This condition is supposed to check if the microphone have finished recording.
                        # If it is the case -> clear = True
                        #
                        if feedback == ser.readline().decode('ascii'):
                            cpt_list += 1
                        if cpt_list > 15:
                            cpt_list = 0
                            clear = True
                    else:
                        command = "GOTOPOSITION," + list_data.pop(0) + "\n"
                        dpg.configure_item("list_of_points", items=list_data)
                        ser.write(command.encode())
                        clear = False
                        # 150,150;100,100;350,350;500,150;700,700;350,350
                else:
                    sequence = False
            except(IndexError, ValueError):
                pass
        
        dpg.render_dearpygui_frame()
    ser.close()  # closing the port
    dpg.destroy_context()


if __name__ == "__main__":
    main()
