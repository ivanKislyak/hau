from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from pathlib import Path
import sqlite3
from datetime import date
from PIL import Image, ImageTk

# DB
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "hau.db"
DB_PATH.parent.mkdir(exist_ok=True)
DB_PATH = 'data/hau.db'
SCHEMA_PATH = 'schema.sql'
ICONS_PATH = 'assets/icons/'

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
root.minsize(500, 300)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

width, height = 500, 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - width) // 2
y = (screen_height - height) // 2
root.geometry(f"{width}x{height}+{x}+{y}")

def resize_img(img):
    return img.resize((20, 20))

pencil_img = ImageTk.PhotoImage(resize_img(Image.open(ICONS_PATH+'pencil1.png')))
trash_img = ImageTk.PhotoImage(resize_img(Image.open(ICONS_PATH+'trash.png')))

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

main_canvas = tk.Canvas(mainframe, bg='white', borderwidth=0, highlightthickness=0)
main_canvas.grid(column=0, row=0, sticky='nsew')
main_canvas.rowconfigure(0, weight=1)
main_canvas.columnconfigure(0, weight=1)

scrollbar = tk.Scrollbar(mainframe, orient="vertical", command=main_canvas.yview)
scrollbar.grid(row=0, column=1, sticky="ns")

main_canvas.configure(yscrollcommand=scrollbar.set)

canvas_fr = tk.Frame(main_canvas, bg='white', borderwidth=0)

canvas_fr.bind(
    "<Configure>",
    lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
)
canvas_window = main_canvas.create_window((0, 0), window=canvas_fr, anchor="nw")

def on_mouse_wheel(event):
    main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

root.bind("<MouseWheel>", on_mouse_wheel)
root.bind('<Down>', on_mouse_wheel)

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


def commas_to_dots(my_list):
    return [item.replace(',', '.', 1) for item in my_list]

def close_window(_event, window):
    window.destroy()

# Loading real estate listings on the home screen
def refresh_cards():
    for ch in canvas_fr.winfo_children():
        ch.destroy()
    with sqlite3.connect(DB_PATH) as sql_conn:
        cursor = sql_conn.cursor()
        cursor.execute("""SELECT * FROM properties""")

        if not cursor.fetchall():
            main_label = ttk.Label(canvas_fr, text="No properties found", font=base_bold18, foreground=dp_sea, justify='center')
            main_label.configure(background=white, width=25)
            main_label.grid(column=0, row=0, padx=(125, 0), pady=(75, 0))

            lets_add_btn = ttk.Button(canvas_fr, text="Let's add!", command=new_property, style='CustomHelvetica.TButton')
            lets_add_btn.grid(column=0, row=1)

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

                for properties in cursor.fetchall():
                    cursor.execute("""SELECT * FROM hau_values WHERE hau_v_id = ?""", (properties[3],))
                    hau_values = cursor.fetchall()
                    card_fr = tk.Frame(canvas_fr, relief="solid", background='white', border=1, pady=10)
                    card_fr.grid(column=0, row=a, padx=5, pady=5)
                    card_fr.grid_columnconfigure(0, minsize=400)
                    card_fr.configure(width=400)

                    name_lb = ttk.Label(card_fr, text=properties[1], style='CustomHelvetica14.TLabel', justify='center')
                    name_lb.grid(row=0, column=0, columnspan=3, pady=3)

                    type_text = 'Category: Flat' if properties[2] == 1 else 'Category: House'

                    type_lb = ttk.Label(card_fr, text=type_text, style='CustomHelvetica14.TLabel')
                    type_lb.grid(row=1, column=0, sticky=W, padx=(10, 0))

                    pastes = ['Gas', 'Water', 'Electricity', 'Heating', 'Garbage']
                    req_values = hau_values[0][2:]
                    rcount = 2

                    for name, value in zip(pastes, req_values):
                        if value:
                            txt = f'{name}: {value}'
                            ttk.Label(card_fr, text=txt, style='CustomHelvetica14.TLabel').grid(row=rcount, column=0, sticky=W, padx=(10, 0))
                            rcount += 1

                    cursor.execute("""SELECT * FROM hau_values WHERE hau_v_id = ?""", (hau_values[0][0],))
                    res = f'Last update: {cursor.fetchone()[-1]}'
                    Label(card_fr, text=res, bg=white, fg='grey').grid(row=rcount, column=0, sticky=W, padx=(10, 0), pady=(15, 0))

                    def del_pr(pr_id):
                        am = messagebox.askquestion('Are you sure?', 'Are you sure for deleting?')
                        if am == 'yes':
                            yes_del(pr_id)

                    new_hau_v = ttk.Button(card_fr, style='CustomHelvetica.TButton', command=lambda v=properties[0]: redact_pr(v), image=pencil_img, compound="center")
                    new_hau_v.grid(column=2, row=(rcount // 2)-1, sticky='e', padx=(0, 20))
                    new_hau_v.configure(width=2)

                    del_pr_btn = ttk.Button(card_fr, style='CustomHelvetica.TButton', command=lambda v=properties[0]: del_pr(v), image=trash_img)
                    del_pr_btn.grid(column=2, row=(rcount // 2)+1, sticky='e', padx=(0, 20))
                    del_pr_btn.configure(width=2)

                    a +=1

            lets_add_btn = ttk.Button(canvas_fr, text="Add more", command=new_property, style='CustomHelvetica.TButton')
            lets_add_btn.grid(column=0, row=a, sticky=NS, pady=10, padx=10)

            for child in mainframe.winfo_children():
                child.grid_configure(padx=5, pady=5)

            root.bind('<Return>', new_property)

def redact_pr(pr_id):
    red_conn = sqlite3.connect(DB_PATH)
    r_cursor = red_conn.cursor()

    r_cursor.execute("""SELECT * FROM properties WHERE id = ?""", (pr_id,))
    pr_info = r_cursor.fetchone()

    r_cursor.execute("""SELECT * FROM hau_values WHERE hau_v_id = ?""", (pr_info[-1],))
    hau_v_info = r_cursor.fetchone()

    red_conn.commit()
    red_pr = Toplevel(root)
    red_pr.focus_force()
    red_pr.title(f'Updating values for {pr_info[1]}')
    red_pr.minsize(200, 200)
    red_pr.configure(bg=white)

    rpr_width, rpr_height = 400, 400
    rpr_screen_width = red_pr.winfo_screenwidth()
    rpr_screen_height = red_pr.winfo_screenheight()
    rpr_x = (rpr_screen_width - rpr_width) // 2
    rpr_y = (rpr_screen_height - rpr_height) // 2
    red_pr.geometry(f"{rpr_width}x{rpr_height}+{rpr_x}+{rpr_y}")

    pr_name, pr_type = pr_info[1:3]
    pr_gas, pr_water, pr_electro, pr_heating, pr_garbage, pr_date = hau_v_info[2:]

    str_var = StringVar(value=pr_name)
    str_var.set(pr_name)

    red_property_frm = tk.Frame(red_pr, bg=white)
    red_property_frm.grid(row=0, column=0)

    property_types = ['Flat', 'House']
    property_type = ttk.Combobox(red_property_frm, values=property_types, style='CustomHelvetica.TCombobox',
                                 font=base18, state='readonly', justify='center')
    property_type.grid(column=0, row=0, pady=10, columnspan=3)
    property_type.current(pr_type-1)

    name_frm = tk.Frame(red_property_frm, bg=white)
    name_frm.grid(row=1, column=0, sticky='w')

    rpr_name_label = ttk.Label(name_frm, text='Name', style='CustomHelvetica.TLabel')
    rpr_name_label.grid(column=0, row=0, padx=(10, 0))
    ttk.Label(name_frm, text='*', foreground='red', background='white', font=("Helvetica", 14)).grid(column=1, row=0)

    rpr_name_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_name_entry.grid(column=1, row=1, sticky="e")
    rpr_name_entry.insert(0, pr_name)

    fill_info = ttk.Label(red_property_frm, text='Fill in the current values', font=("Helvetica", 14, 'bold'),
                          foreground='darkgrey', background='white')
    fill_info.grid(column=0, row=2, columnspan=2, sticky="w", padx=10)

    rpr_gas_label = ttk.Label(red_property_frm, text='Gas', style='CustomHelvetica.TLabel')
    rpr_gas_label.grid(column=0, row=3, sticky="w", padx=10)

    rpr_gas_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_gas_entry.grid(column=1, row=3, sticky="e")
    rpr_gas_entry.insert(0, pr_gas if pr_gas else '')
    rpr_gas_entry.focus_force()

    rpr_water_label = ttk.Label(red_property_frm, text='Water', style='CustomHelvetica.TLabel')
    rpr_water_label.grid(column=0, row=4, sticky="w", padx=10)

    rpr_water_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_water_entry.grid(column=1, row=4, sticky="e")
    rpr_water_entry.insert(0, pr_water if pr_water else '')

    rpr_electricity_label = ttk.Label(red_property_frm, text='Electricity', style='CustomHelvetica.TLabel')
    rpr_electricity_label.grid(column=0, row=5, sticky="w", padx=10)

    rpr_electricity_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_electricity_entry.grid(column=1, row=5, sticky="e")
    rpr_electricity_entry.insert(0, pr_electro if pr_electro else '')

    rpr_heating_label = ttk.Label(red_property_frm, text='Heating', style='CustomHelvetica.TLabel')
    rpr_heating_label.grid(column=0, row=6, sticky="w", padx=10)

    rpr_heating_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_heating_entry.grid(column=1, row=6, sticky="e")
    rpr_heating_entry.insert(0, pr_heating if pr_heating else '')

    rpr_heating_btn = ttk.Button(red_property_frm, text='⚙️', width=3)
    rpr_heating_btn.grid(column=2, row=6, sticky="e", padx=10)

    rpr_garbage_label = ttk.Label(red_property_frm, text='Garbage', style='CustomHelvetica.TLabel')
    rpr_garbage_label.grid(column=0, row=7, sticky="w", padx=10)

    rpr_garbage_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_garbage_entry.grid(column=1, row=7, sticky="e")
    rpr_garbage_entry.insert(0, pr_garbage if pr_garbage else '')

    rpr_garbage_btn = ttk.Button(red_property_frm, text='⚙️', width=3)
    rpr_garbage_btn.grid(column=2, row=7, sticky="e", padx=10)

    def update_values():
        # Checking Values
        if not rpr_name_entry.get():
            return messagebox.showerror('Error', 'The “Name” field is required', parent=red_property_frm)

        w_list = [rpr_gas_entry.get(), rpr_water_entry.get(), rpr_electricity_entry.get(), rpr_heating_entry.get(),
                  rpr_garbage_entry.get()]
        v_list = [v for v in w_list if v != '']

        for v in commas_to_dots(v_list):
            try:
                float(v)
            except ValueError:
                return messagebox.showerror('Error', 'Enter the numerical values', parent=red_property_frm)

        new_values = []
        for v in commas_to_dots(w_list):
            try:
                new_values.append(float(v))
            except ValueError:
                new_values.append(0)

        # Updating Values
        update_conn = sqlite3.connect(DB_PATH)
        u_cursor = update_conn.cursor()
        u_cursor.execute("""SELECT gas, water, electricity, heating, garbage FROM hau_values WHERE pr_id = ? ORDER BY hau_v_id DESC""", (pr_id,))

        prev_values = []
        for v in u_cursor.fetchone():
            try:
                prev_values.append(float(v))
            except ValueError:
                prev_values.append(0)

        for pv, nv in zip(prev_values, new_values):
            if nv < pv:
                return messagebox.showerror('Error', 'The new values must be greater than or equal to the previous ones', parent=red_property_frm)

        u_cursor.execute("""INSERT INTO hau_values (pr_id, gas, water, electricity, heating, garbage, date) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                         (pr_id, *new_values, str(date.today())))
        update_conn.commit()

        u_cursor.execute("""SELECT * FROM hau_values WHERE pr_id = ? ORDER BY hau_v_id DESC""", (pr_id,))
        u_cursor.execute("""UPDATE properties set hau_v_id = ? WHERE id = ?""", (u_cursor.fetchone()[0], pr_id))
        update_conn.commit()

        red_pr.destroy()
        return refresh_cards()

    rpr_update_values_btn = ttk.Button(red_property_frm, text='Update values', command=update_values, style='CustomHelvetica.TButton')
    rpr_update_values_btn.grid(column=0, columnspan=2, row=8, sticky=N, pady=(40, 0))

    red_pr.bind("<Control-Z>", lambda e, w=red_pr: close_window(e, w))
    red_pr.bind("<Control-z>", lambda e, w=red_pr: close_window(e, w))
    red_pr.bind("<Return>", lambda e: update_values())

############ ADDING PROPERTY ###############
def new_property(_event=None):
    add_property = Toplevel(root)
    add_property.focus_force()
    add_property.title("Hau " + c_version + ' - adding property')
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
    pr_name_entry.focus_force()

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

    def add_record():
        # Checking Values
        if not pr_name_entry.get():
            return messagebox.showerror('Error', 'The “Name” field is required', parent=add_property_frm)

        w_list = [pr_gas_entry.get(), pr_water_entry.get(), pr_electricity_entry.get(), pr_heating_entry.get(),
                  pr_garbage_entry.get()]
        v_list = [v for v in w_list if v != '']

        for v in commas_to_dots(v_list):
            try:
                float(v)
            except ValueError:
                return messagebox.showerror('Error', 'Enter the numerical values', parent=add_property_frm)

        # Adding Values
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT seq FROM sqlite_sequence WHERE name='properties'")
        row = cursor.fetchone()
        next_pr_id = (row[0] + 1) if row else 1

        with sqlite3.connect(DB_PATH) as add_sql_conn:
            add_cursor = add_sql_conn.cursor()
            add_cursor.execute("""INSERT INTO hau_values (gas, water, electricity, heating, garbage, date, pr_id) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                               (*commas_to_dots(w_list), str(date.today()), next_pr_id))

        def lat_hau_id() -> int:
            with sqlite3.connect(DB_PATH) as whid_add_sql_conn:
                whid_cursor = whid_add_sql_conn.cursor()
                whid_cursor.execute("SELECT * FROM hau_values ORDER BY hau_v_id DESC")
                return whid_cursor.fetchone()[0]

        with sqlite3.connect(DB_PATH) as pr_add_sql_conn:
                add_cursor = pr_add_sql_conn.cursor()
                add_cursor.execute("""INSERT INTO properties (name, type_id, hau_v_id) VALUES (?, ?, ?)""",
                                   (pr_name_entry.get(), 1 if property_type.get() == 'Flat' else 2, lat_hau_id()))

        conn.commit()
        add_property.destroy()
        return refresh_cards()

    add_pr_btn = ttk.Button(add_property_frm, width=10, text='+', style='CustomHelvetica.TButton', command=add_record)
    add_pr_btn.grid(column=0, row=8, columnspan=3, sticky='N', padx=5, pady=20)

    add_property.bind("<Control-Z>", lambda e, w=add_property: close_window(e, w))
    add_property.bind("<Control-z>", lambda e, w=add_property: close_window(e, w))

############ END OF ADDING PROPERTY ###############

def yes_del(pr_id):
    with sqlite3.connect(DB_PATH) as sql_del_info:
        cur = sql_del_info.cursor()
        cur.execute("""DELETE FROM properties WHERE id=?""", (pr_id,))
    refresh_cards()

if __name__ == '__main__':
    db()
    refresh_cards()
    root.mainloop()

