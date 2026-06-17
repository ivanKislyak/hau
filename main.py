from tkinter import *
import tkinter as tk
from tkinter import ttk
from pathlib import Path
import sqlite3
import os
import datetime

# DB
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "hau.db"
DB_PATH.parent.mkdir(exist_ok=True)
DB_PATH = 'data/hau.db'
SCHEMA_PATH = 'schema.sql'

def db():
    with sqlite3.connect(DB_PATH) as sql_conn:
        with open(SCHEMA_PATH, 'r', encoding='utf-8', newline='') as sql_script:
            cursor = sql_conn.cursor()
            cursor.executescript(sql_script.read())

# Current version
c_version = '(0.1)'

# App
root = tk.Tk()
root.title("Hau " + c_version)
root.iconbitmap(default="assets/icons/hau_logo.ico")
root.configure(bg="white")
root.minsize(380, 200)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

width, height = 500, 200
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - width) // 2
y = (screen_height - height) // 2
root.geometry(f"{width}x{height}+{x}+{y}")

# FGs
dp_sea = '#11384D'
white = '#FFFFFF'
black = '#000000'

# Fonts
base18 = ("Helvetica", 18)
base_bold18 = ("Helvetica", 18, 'bold')
base16 = ("Helvetica", 16)
base_bold16 = ("Helvetica", 16, 'bold')
base14 = ("Helvetica", 14)
base_bold14 = ("Helvetica", 14, 'bold')

mainframe = tk.Frame(root, bg='white')
mainframe.grid(column=0, row=0, sticky='nsew')
mainframe.grid_rowconfigure(0, weight=1)
mainframe.grid_columnconfigure(0, weight=1)

# Style
style = ttk.Style()
style.configure(
    "CustomHelvetica.TLabel",
    font=base18,
    foreground=black,
    background=white
)
style.configure(
    "CustomHelvetica14.TLabel",
    font=base14,
    foreground=black,
    background=white
)
style.configure(
    "CustomHelvetica.TButton",
    font=base_bold16,
    foreground=black,
    background=white
)
style.configure(
    "CustomHelvetica.TCombobox",
    fieldbackground=white,
    foreground=black,
    background=white
)

############ ADDING PROPERTY ###############
def new_property(_event=None):
    add_property = Toplevel(root)
    add_property.focus_force()
    add_property.title("Hau " + c_version + ' - adding property')
    #add_property.iconbitmap("assets/icons/hau_logo.ico")
    add_property.configure(bg="white")
    add_property.minsize(200, 200)
    add_property.columnconfigure(0, weight=1)

    pr_width, pr_height = 400, 400
    pr_screen_width = add_property.winfo_screenwidth()
    pr_screen_height = add_property.winfo_screenheight()
    pr_x = (pr_screen_width - pr_width) // 2
    pr_y = (pr_screen_height - pr_height) // 2
    add_property.geometry(f"{pr_width}x{pr_height}+{pr_x}+{pr_y}")

    add_property_frm = tk.Frame(add_property, bg=white)
    add_property_frm.grid(row=0, column=0)

    property_types = ['Flat', 'House']
    property_type = ttk.Combobox(add_property_frm, values=property_types, style='CustomHelvetica.TCombobox', font=base18, state='readonly', justify='center')
    property_type.grid(column=0, row=0, pady=10, columnspan=3)
    property_type.current(0)

    name_frm = tk.Frame(add_property_frm, bg=white)
    name_frm.grid(row=1, column=0, sticky='w')

    pr_name = ttk.Label(name_frm, text='Name', style='CustomHelvetica.TLabel')
    pr_name.grid(column=0, row=0, padx=10)
    ttk.Label(name_frm, text='*', foreground='red', background='white', font=("Helvetica", 14)).grid(column=1, row=0)

    pr_name_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_name_entry.grid(column=1, row=1, sticky="e")

    fill_info = ttk.Label(add_property_frm, text='Fill in the current values', font=("Helvetica", 14, 'bold'), foreground='darkgrey', background='white')
    fill_info.grid(column=0, row=2, columnspan=2, sticky="w", padx=10)

    pr_gas = ttk.Label(add_property_frm, text='Gas', style='CustomHelvetica.TLabel')
    pr_gas.grid(column=0, row=3, sticky="w", padx=10)

    pr_gas_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_gas_entry.grid(column=1, row=3, sticky="e")

    pr_water = ttk.Label(add_property_frm, text='Water', style='CustomHelvetica.TLabel')
    pr_water.grid(column=0, row=4, sticky="w", padx=10)

    pr_water_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_water_entry.grid(column=1, row=4, sticky="e")

    pr_electricity = ttk.Label(add_property_frm, text='Electricity', style='CustomHelvetica.TLabel')
    pr_electricity.grid(column=0, row=5, sticky="w", padx=10)

    pr_electricity_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_electricity_entry.grid(column=1, row=5, sticky="e")

    pr_heating = ttk.Label(add_property_frm, text='Heating', style='CustomHelvetica.TLabel')
    pr_heating.grid(column=0, row=6, sticky="w", padx=10)

    pr_heating_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_heating_entry.grid(column=1, row=6, sticky="e")

    pr_heating_btn = ttk.Button(add_property_frm, text='⚙️', width=3)
    pr_heating_btn.grid(column=2, row=6, sticky="e", padx=10)

    pr_garbage = ttk.Label(add_property_frm, text='Garbage', style='CustomHelvetica.TLabel')
    pr_garbage.grid(column=0, row=7, sticky="w", padx=10)

    pr_garbage_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_garbage_entry.grid(column=1, row=7, sticky="e")

    pr_garbage_btn = ttk.Button(add_property_frm, text='⚙️', width=3)
    pr_garbage_btn.grid(column=2, row=7, sticky="e", padx=10)

    add_pr_btn = ttk.Button(add_property_frm, width=10, text='+', style='CustomHelvetica.TButton')
    add_pr_btn.grid(column=0, row=8, columnspan=3, sticky='N', padx=5, pady=20)

    def close_window(_event):
        add_property.destroy()

    add_property.bind("<Control-Z>", close_window)
    add_property.bind("<Control-z>", close_window)

############ END OF ADDING PROPERTY ###############
main_canvas = tk.Canvas(mainframe, bg='white', borderwidth=0, highlightthickness=0)
main_canvas.grid(column=0, row=0, sticky='nsew')

canvas_fr = tk.Frame(main_canvas, bg='white', borderwidth=0)
canvas_fr.grid_columnconfigure(0, weight=1)
canvas_fr.grid_rowconfigure(0, weight=1)

canvas_window = main_canvas.create_window((0, 0), window=canvas_fr, anchor="nw")

scrollbar = tk.Scrollbar(mainframe, orient="vertical", command=main_canvas.yview)
scrollbar.grid(row=0, column=1, sticky="ns")

main_canvas.configure(yscrollcommand=scrollbar.set)

canvas_fr.bind(
    "<Configure>",
    lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
)

main_canvas.bind(
    "<Configure>",
    lambda e: main_canvas.itemconfigure(canvas_window, width=e.width)
)

# Loading real estate listings on the home screen
with sqlite3.connect(DB_PATH) as sql_conn:
    cursor = sql_conn.cursor()
    cursor.execute("""SELECT * FROM properties""")

    if not cursor.fetchall():
        main_label = ttk.Label(canvas_fr, text="No properties found", font=base_bold18, foreground=dp_sea)
        main_label.configure(background=white)
        main_label.grid(column=0, row=1, sticky=NS)

        lets_add_btn = ttk.Button(canvas_fr, text="Let's add!", command=new_property, style='CustomHelvetica.TButton')
        lets_add_btn.grid(column=0, row=2, sticky=NS)

        root.bind("<Return>", new_property)
    else:
        main_label = ttk.Label(canvas_fr, text="Your properties:", font=base_bold18, foreground=dp_sea)
        main_label.configure(background=white)
        main_label.grid(column=0, row=1, sticky=NS)

        # Cards of properties
        with sqlite3.connect(DB_PATH) as sql_conn3:
            cursor = sql_conn3.cursor()
            cursor.execute("""SELECT * FROM properties""")
            a = 2
            frame_w = mainframe.winfo_screenmmwidth() * 0.8
            for properties in cursor.fetchall():
                cursor.execute("""SELECT * FROM hau_values WHERE hau_v_id = ?""", (properties[3],))
                hau_values = cursor.fetchall()
                card_fr = tk.Frame(canvas_fr, relief="solid", background='white', width=frame_w, height=150, border=1, pady=10)
                card_fr.grid(column=0, row=a, padx=5, pady=5)
                card_fr.grid_propagate(False)
                name_lb = ttk.Label(card_fr, text=properties[1], style='CustomHelvetica14.TLabel', justify='center')
                name_lb.grid(row=0, column=0, columnspan=3)

                type_text = 'Category: Flat' if properties[0] == 1 else 'Category: House'

                type_lb = ttk.Label(card_fr, text=type_text, style='CustomHelvetica14.TLabel')
                type_lb.grid(row=1, column=0, sticky=W)

                gas_txt = f'Gas: {hau_values[0][1]}'
                gas_lb = ttk.Label(card_fr, text=gas_txt, style='CustomHelvetica14.TLabel')
                gas_lb.grid(row=2, column=0, sticky=W)

                a +=1

        lets_add_btn = ttk.Button(canvas_fr, text="Add more", command=new_property, style='CustomHelvetica.TButton')
        lets_add_btn.grid(column=0, row=a, sticky=NS, pady=10, padx=10)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        root.bind('<Return>', new_property)

if __name__ == '__main__':
    db()
    root.mainloop()

