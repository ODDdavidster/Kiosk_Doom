import os
import subprocess as sp
from pathlib import Path
import tkinter as tk

run_config = "classic.bat"
MP_name = "Classic"

PARENT_PATH = Path(__file__).parent
ASSETS_PATH = PARENT_PATH / "assets" / "frame0"

def relative_to_assets(file: str) -> Path:
    return ASSETS_PATH / Path(file)

#a Function used to test if the init was done first. 
def init_test():
    try:
        with open('engines/wads/doom_complete.pk3') as file:
            print("this file does exist")
    except:
        print('Please Run "install.py" before running this program')
        input()
        exit()
        return 0
    print("This program has been inisialized")
    return 1

#these are functions that ChatGPT made. I asked it how I would go about diabling all buttons so I wouldn't
#have to write alot of the same code. loops. loops are how to do it. However I would just be rewriting all
#the code to do the same thing so The following two functions are 100% gpt generated TwT I need a life
def disable_buttons(window):
    # Iterate over all widgets in the window
    for widget in window.winfo_children():
        # Check if the widget is a button
        if isinstance(widget, tk.Button):
            # Disable the button
            widget.config(state=tk.DISABLED)

def disable_button(widget):
    widget.config(state=tk.DISABLED)

def enable_buttons(window):
    # Iterate over all widgets in the window
    for widget in window.winfo_children():
        # Check if the widget is a button
        if isinstance(widget, tk.Button):
            # Enable the button
            widget.config(state=tk.NORMAL)
#GPT Code end


def run_game():
    print(os.listdir("configs"))
    if run_config == "classic.bat":
        def run_doom(mes = 1): #runs a spasific version of classic doom
            doom_pick.destroy()
            os.chdir("configs")
            #Runs the batch file with the argument for whitch doom
            sp.Popen(f'{run_config} -{mes}', shell=True)
            # Exit the Python script
            window.destroy()
            exit()
    
        doom_pick = tk.Toplevel(window)
        doom_pick.title("")
        doom_pick.geometry('200x300+500+325')
        
        question = tk.Label(doom_pick,text="Doom 1 or 2?")
        temp_button1 = tk.Button(
            doom_pick,
            text='DOOM',
            image = DOOM_image,
            borderwidth=0,
            height=100,
            width=200,
            command=lambda: run_doom(1)
            )
        temp_button2 = tk.Button(
            doom_pick, 
            image=DOOM2_image,
            text="DOOM2",
            borderwidth=0,
            height=100,
            width=200,
            command=lambda: run_doom(2)
            )
        question.grid(row=0)
        temp_button1.grid(row=1)
        temp_button2.grid(row=2)

        print(relative_to_assets("button_3.png"))
    elif run_config in os.listdir("configs"):
        os.chdir("configs")
        #Runs the batch file with the argument for whitch doom
        sp.Popen(f'{run_config}', shell=True)
        # Exit the Python script
        window.destroy()
        exit()
#this code is so gross looking. tomorrow is gonna be clean up day.

def kill_menu(menu_name):
    #kill what ever tkinter gui is in the preamiter
    menu_name.destroy()


def make_config_list():
    con_button_list = []
    #make the buttons baced on the configs directory
    for i in os.listdir('configs'):
        if i.endswith('.bat'):
            button = tk.Button(
                #sugjested by GPT. I know... I know...
                config_list,  
                text=i[:-4],  # Remove the '.bat' extension from the filename
                command=lambda f=i: assign_run_config(f) #f=i is important so that it recalls the variable each time it changes.
            )
            con_button_list.append(button)
    return con_button_list


#this will asign the config then kill the window
def assign_run_config(file):
    global run_config, MP_name
    run_config = file
    MP_name = file[:-4]
    print(f'MP_name: {MP_name}\nrun_config: {run_config}')
    MP_text.config(text=f"MOD PACK: {MP_name} Doom")
    kill_menu(config_list)
    enable_buttons(window)

def show_configs():
    global config_list 
    disable_buttons(window)
    config_list = tk.Toplevel(window)
    config_list.wm_overrideredirect(True)
    config_list.geometry('+500+325')
    buttons = make_config_list()
    for idx, button in enumerate(buttons):
        button.grid(row=idx, column=0)

def make_config():
    disable_buttons(window)
    os.chdir('configs')
    config_name = input("Please input a name for this config >_")
    with open(f'{config_name}.ini','w') as t_file:
        pass
    with open(f'{config_name}.bat','w') as t_file:
        t_file.write(f'''
                    @echo off\n
                    copy "{config_name}.ini" ..\engines\gzdoom\ \n
                    cd ..\engines\ \n
                    copy wads\DOOM.WAD gzdoom\ \n
                    cd gzdoom\ \n
                    gzdoom.exe -iwad DOOM.WAD -file "%cd%\..\wads\doom_complete.pk3" -config "{config_name}.ini" \n
                    del DOOM.WAD\n
                    exit
                     ''')
    os.chdir('..')
    enable_buttons(window)

def use_password(): #This isn't a proper password thing. Just enough to keep grubby kids off the settings.
    pass_window = tk.Toplevel(window)
    pass_window.geometry("406x539")
    disable_buttons(window)
    pass_entery = tk.Entry(pass_window)
    pass_entery.place()


def make_config_window():
    config_window = tk.Toplevel(window)
    config_window.geometry("406x539")
    config_window.configure(bg = "#FFFFFF")
    config_window.protocol("WM_DELETE_WINDOW", lambda: [enable_buttons(window), config_window.destroy()])

    canvas = tk.Canvas(
        config_window,
        bg = "#FFFFFF",
        height = 539,
        width = 406,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    canvas.place(x = 0, y = 0)
    canvas.create_rectangle(
        17.0,
        115.0,
        257.0,
        519.0,
        fill="#D9D9D9",
        outline="")

    config_button_image_1 = tk.PhotoImage(file=relative_to_assets("switch_off.png"))
    config_button_1 = tk.Button(
        config_window,
        image=config_button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_1 clicked"),
        relief="flat"
    )
    config_button_1.place(
        x=284.0,
        y=49.0,
        width=104.0,
        height=34.0
    )

    button_image_2 = tk.PhotoImage(
        file=relative_to_assets("button_2.png"))
    button_2 = tk.Button(
        config_window,
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_2 clicked"),
        relief="flat"
    )
    button_2.place(
        x=285.0,
        y=431.0,
        width=104.0,
        height=34.0
    )

    button_image_3 = tk.PhotoImage(
        file=relative_to_assets("button_3.png"))
    button_3 = tk.Button(
        config_window,
        image=button_image_3,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_3 clicked"),
        relief="flat"
    )
    button_3.place(
        x=285.0,
        y=485.0,
        width=104.0,
        height=34.0
    )

    entry_1 = tk.Entry(
        config_window,
        bd=0,
        bg="#D9D9D9",
        fg="#000716",
        highlightthickness=0
    )
    entry_1.place(
        x=17.0,
        y=49.0,
        width=240.0,
        height=32.0
    )

    canvas.create_text(
        17.0,
        34.0,
        anchor="nw",
        text="Modpack Name:",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        284.0,
        34.0,
        anchor="nw",
        text="Has spasific Maps?",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        320.0,
        100.0,
        anchor="nw",
        text="IWAD",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        150.0,
        9.0,
        anchor="nw",
        text="New Modpack",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        17.0,
        100.0,
        anchor="nw",
        text="What mods (click in launch order):",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_rectangle(
        284.0,
        115.0,
        388.0,
        271.0,
        fill="#FF0000",
        outline="")

    button_image_4 = tk.PhotoImage(
        file=relative_to_assets("button_4.png"))
    button_4 = tk.Button(
        config_window,
        image=button_image_4,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_4 clicked"),
        relief="flat"
    )
    button_4.place(
        x=284.0,
        y=115.0,
        width=104.0,
        height=50.0
    )

    canvas.create_rectangle(
        284.0,
        219.0,
        388.0,
        271.0,
        fill="#FFFFFF",
        outline="")

    button_image_5 = tk.PhotoImage(
        file=relative_to_assets("button_5.png"))
    button_5 = tk.Button(
        config_window,
        image=button_image_5,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: print("button_5 clicked"),
        relief="flat"
    )
    button_5.place(
        x=284.0,
        y=166.0,
        width=104.0,
        height=52.0
    )
    config_window.resizable(False, False)





#main Menu made with a genorator. (add Credit later seems to have disapeared)

window = tk.Tk()

window.geometry("1280x720+0+0")
window.configure(bg="#FFFFFF")
window.title('Kiosk DOOM')
window.iconbitmap('assets\KioskDoomlogo.ico')

canvas = tk.Canvas(
    window,
    bg="#FFFFFF",
    height=720,
    width=1280,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)

canvas.place(x=0, y=0)

image_image_1 = tk.PhotoImage(
    file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(
    640.0,
    360.0,
    image=image_image_1
)

image_image_2 = tk.PhotoImage(
    file=relative_to_assets("image_2.png"))
image_2 = canvas.create_image(
    639.0,
    200.0,
    image=image_image_2
)

button_image_1 = tk.PhotoImage(
    file=relative_to_assets("button_1.png"))
button_1 = tk.Button(
    image=button_image_1,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: make_config_window(),
    relief="flat"
)

# this is one of the main fetures and I can't get it to function. 
# Given I have until thrusday to make this decent I have to cut it for now

# config window button
# button_1.place(
#     x=36.0,
#     y=640.0,
#     width=54.0,
#     height=54.0
# )

# This button runs the game with the current running config
button_image_2 = tk.PhotoImage(
    file=relative_to_assets("button_2.png"))
button_2 = tk.Button(
    image=button_image_2,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: run_game(),
    relief="flat"
)
button_2.place(
    x=506.0,
    y=332.0,
    width=268.0,
    height=55.0
)

#This is the configeration button
button_image_3 = tk.PhotoImage(
    file=relative_to_assets("button_3.png"))
button_3 = tk.Button(
    image=button_image_3,
    borderwidth=0,
    highlightthickness=0,
    command=lambda: show_configs(),
    relief="flat"
)
button_3.place(
    x=506.0,
    
    y=416.0,
    width=268.0,
    height=55.0
)
MP_text = tk.Label(text=f"MOD PACK: {MP_name} Doom")
MP_text.place(
    x=506.0,
    y=500.0,
    width=268.0,
    height=70.0
)

#the images for the classic doom setting. Which is special becuase we launch a who nother program for some dumb reason
DOOM_image = tk.PhotoImage(file='assets/doom_button_200.png')
DOOM2_image = tk.PhotoImage(file='assets/doom2_button_200.png')

#The main window being displayed. 

#To check for inicialzation
if init_test() == 1:
    window.resizable(False, False)
    window.mainloop()
else:
    input("Something went supper wrong. Somehow...")
    exit()

