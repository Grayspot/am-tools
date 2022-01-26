__author__ = 'HAORAN ZHENG'
from tkinter  import *
from  tkinter  import ttk

#creation de gui
cccp = Tk()

#donner le titre de gui
cccp.title("Robot Command")

#determine le taille de fenetre
cccp.geometry("1300x850")

#change le coleur de font
cccp["bg"] = "WhiteSmoke"

#creer labels des texts
text1 = Message(cccp,width = 200,bd = 2,bg = "WhiteSmoke",text = "Ports disponibles")
text1.place(x = 5,y = 5)
'''
une fois que on utilise text1.pack(),le text1.place() ne fonctionne plus
'''

text2 = Message(cccp,width = 60,bd = 1,bg = "WhiteSmoke",text = "Port affect")
text2.place(x = 335,y = 5)

text_de_ports_disponibles = Text(cccp,bg = 'white',height = 11,width = 45)
text_de_ports_disponibles.place(x = 5,y = 25)

text_de_ports_affect = Text(cccp,bg = 'white',height = 1,width = 10)
text_de_ports_affect.place(x = 410,y = 10)

#fonction de button brade on off
def button_fonction_brake_on_off():
    pass

#fonction de button led on odd
def led_on_off():
    pass

#fonction de button take
def button_take():
    pass

#fonction de button Stop
def button_stop():
    pass

#fonction de button set stroke
def button_set_stroke():
    pass

#fonction de button set stroke
def button_set_stroke1():
    pass

#fonction de button set stroke
def button_set_speed():
    pass

action = Message(cccp,text = "Actions",bd = 1,bg = "WhiteSmoke",width = 70)
action.place(x = 340,y = 30)

button_brake = Button(cccp,relief = "raised",text = "Brake\n on/off",height = 6,bg = "gray",width = 6,command = button_fonction_brake_on_off)
button_brake.place(x = 340,y = 50)

button_LED_ON_OFF = Button(cccp,relief = "raised",text = "LED ON/OFF",height = 1,bg = "gray",width = 10,command = led_on_off)
button_LED_ON_OFF.place(x = 410,y = 50)

button_take = Button(cccp,relief = "raised",text = "Take",height = 1,bg = "Silver",width = 10,command = button_take)
button_take.place(x = 410,y = 92)

button_stop = Button(cccp,relief = "raised",text = "Stop",height = 1,bg = "orange",width = 10,command = button_stop)
button_stop.place(x = 410,y = 134)

button_set_stroke = Button(cccp,relief = "raised",text = "Set stroke",height = 1,bg = "Silver",width = 10,command = button_set_stroke)
button_set_stroke.place(x = 410,y = 176)

button_set_stroke1 = Button(cccp,relief = "raised",text = "Set stroke",height = 1,bg = "Silver",width = 10,command = button_set_stroke1)
button_set_stroke1.place(x = 410,y = 218)

button_set_speed = Button(cccp,relief = "raised",text = "Set speed",height = 1,bg = "Silver",width = 10,command = button_set_speed)
button_set_speed.place(x = 410,y = 260)

text1 = Message(cccp,width = 200,bd = 2,bg = "WhiteSmoke",text = "Ports a utiliser")
text1.place(x = 5,y = 180)

box_port_a_utiliser = ttk.Combobox(cccp)
box_port_a_utiliser.place(x = 120,y = 180)

deplacement = Message(cccp,text = "Deplacement",bd = 1,bg = "WhiteSmoke",width = 100)
deplacement.place(x = 5,y = 200)

x = Message(cccp,text = "Y",bd = 1,bg = "WhiteSmoke",width = 10)
x.place(x = 10,y = 225)

y = Message(cccp,text = "Z",bd = 1,bg = "WhiteSmoke",width = 10)
y.place(x = 10,y = 250)

x_spinbox = Spinbox(cccp,from_= 0.0,to = 700.0,increment = 0.1,width = 10)
x_spinbox.place(x = 35,y = 225)

y_spinbox = Spinbox(cccp,from_= 0.0,to = 700.0,increment = 0.1,width = 10)
y_spinbox.place(x = 35,y = 250)

button_go_to_yz = Button(cccp,relief = "raised",text = "Go to position YZ",height = 1,bg = "Silver",width = 20,command = button_set_speed)
button_go_to_yz.place(x = 140,y = 230)

set_stroke_spinbox = Spinbox(cccp,from_= 0.0,to = 700.0,increment = 0.1,width = 7)
set_stroke_spinbox.place(x = 340,y = 182)

set_stroke1_spinbox = Spinbox(cccp,from_= 0.0,to = 700.0,increment = 0.1,width = 7)
set_stroke1_spinbox.place(x = 340,y = 225)

set_speed_spinbox = Spinbox(cccp,from_= 0.0,to = 700.0,increment = 0.1,width = 7)
set_speed_spinbox.place(x = 340,y = 265)

flux = Message(cccp,text = "Flux du port",bd = 1,bg = "WhiteSmoke",width = 80)
flux.place(x = 5,y = 270)

entry_of_flux = Entry(cccp,width = 69)
entry_of_flux.place(x = 5,y = 295)

light1 = Canvas(cccp,height = 35,width = 35)
light1.create_rectangle(0,0,30,30)
light1.create_oval(5,5,25,25,fill = "red")
light1.place(x = 5,y = 330)

light2 = Canvas(cccp,height = 35,width = 35)
light2.create_rectangle(0,0,30,30)
light2.create_oval(5,5,25,25,fill = "red")
light2.place(x = 250,y = 330)

#les liste des points ou le robot y aller
liste_destination = []
points = []

#result_afficher = Text(cccp,bg = 'white',height = 16,width = 69)
#result_afficher.place(x = 5,y = 320)

w = Canvas(cccp, width=720, height=720)
w.place(x = 550,y = 25)

w.create_oval(7,720-7,14,720-14,fill = "red")#(0,0)
origine = Message(cccp,text = "(0,0)",bd = 1,bg = "WhiteSmoke",width = 40)
origine.place(x = 520,y = 740)

w.create_oval(707,720-7,714,720-14,fill = "red")#(700,0)
point_top_left = Message(cccp,text = "(0,700)",bd = 1,bg = "WhiteSmoke",width = 40)
point_top_left.place(x = 520,y = 5)

w.create_oval(7,20-7,14,20-14,fill = "red")#(0,700)
point_right_bot = Message(cccp,text = "(700,0)",bd = 1,bg = "WhiteSmoke",width = 40)
point_right_bot.place(x = 1250,y = 740)

w.create_oval(707,20-7,714,20-14,fill = "red")#(700,700)
w.create_line(10,710,10,10,fill = "blue",dash=(4,4))
w.create_line(10,10,710,10,fill = "blue",dash=(4,4))
w.create_line(10,710,710,710,fill = "blue",dash=(4,4))
w.create_line(710,710,710,10,fill = "blue",dash=(4,4))
#w.scale("all",0,0,0.8,0.8)


#Partie de creation de destinations


index_x = StringVar()
index_y = StringVar()
index_x.set(0)
index_y.set(0)

x_index = Message(cccp,text = "X",bd = 1,bg = "WhiteSmoke",width = 10)
x_index.place(x = 5,y = 370)

x_entry = Entry(cccp,width = 6,textvariable = index_x)
x_entry.place(x = 30,y = 370)

y_index = Message(cccp,text = "Y",bd = 1,bg = "WhiteSmoke",width = 10)
y_index.place(x = 150,y = 370)

y_entry = Entry(cccp,width = 6,textvariable = index_y)
y_entry.place(x = 170,y = 370)

frame = Frame(cccp)
frame.place(x = 5,y=430)

liste = Listbox(frame, height=3)

yscrollbar = Scrollbar(frame,orient = VERTICAL)
liste.config(yscrollcommand=yscrollbar.set)

yscrollbar.config(command=liste.yview)
yscrollbar.pack(side=RIGHT,fill = Y)

liste.pack()

#function of the create points of destination 
def dot():
    global w
    if index_x.get().isdigit and index_y.get().isdigit:
        x = int(x_entry.get())
        y = int(y_entry.get())
    liste_destination.append([x,y])
    liste.insert(END,[x,y])
    return w.create_oval(7+x,720-7-y,14+x,720-14-y,fill = "red")
    
#function of the add points button
def addPoints():
    points.append(dot())

button_add_point = Button(cccp,relief = "raised",text = "add_points",height = 1,bg = "orange",width = 12,
                          command = addPoints)
button_add_point.place(x = 340,y = 365)

#the function of the delete button
def delete_points():
    global w
    x = liste.index(ACTIVE)
    liste.delete(ACTIVE)
    w.delete(points[x])

def delete_all():
    global w
    liste.delete(0,END)
    for items in points:
        w.delete(items)

#bt = Button(cccp, text='delete', command=lambda x=liste:x.delete(ACTIVE))
bt = Button(cccp, text='delete',fg = "red" ,width = 10,command=delete_points)
bt.place(x = 250,y = 430)

bt = Button(cccp, text='delete_all',fg ="red",width = 10, command=delete_all)
bt.place(x = 250,y = 470)

cccp.mainloop()