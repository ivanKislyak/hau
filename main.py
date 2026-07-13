from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import customtkinter as ctk
from pathlib import Path
import sqlite3
from datetime import date
# noinspection PyPackageRequirements
from TkToolTip import ToolTip
from PIL import Image, ImageTk
import json
from logic import to_number, calc_tiered_payment, commas_to_dots
import locale

# Current version
c_version = '(0.7)'

# DB
BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "data" / "hau.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"
ICONS_PATH = BASE_DIR / "assets" / "icons"
LANG_PATH = BASE_DIR / "lang.json"

DB_PATH.parent.mkdir(exist_ok=True)

with sqlite3.connect(DB_PATH) as db_sql_conn:
    with open(SCHEMA_PATH, 'r', encoding='utf-8', newline='') as sql_script:
        db_cursor = db_sql_conn.cursor()
        db_cursor.executescript(sql_script.read())

# Useful dicts
needed_columns = {
    'gas': 2,
    'water': 3,
    'electricity': 4,
    'heating': 5,
    'garbage': 6,
    'housing_main': 7
}

def choose_lang() -> None | str:
    choose_lang_conn = sqlite3.connect(DB_PATH)
    choose_lang_cursor = choose_lang_conn.cursor()
    choose_lang_cursor.execute("""SELECT * FROM user_settings""")
    u_settings = choose_lang_cursor.fetchone()

    chosen_lang = u_settings[1] if u_settings else None

    if not chosen_lang:
        try:
            locale.setlocale(locale.LC_ALL, '')
            system_lang, _ = locale.getlocale()
        except locale.Error:
            system_lang = None

        if system_lang and system_lang.startswith('ru'):
            return 'ru'
        elif system_lang and system_lang.startswith('kk'):
            return 'kz'
        else:
            return 'en'
    else:
        return chosen_lang

# Available languages: en, ru, kz
with open(LANG_PATH, "r", encoding="utf-8") as f:
    C_LANG = json.load(f)

def lang_u(key: str, **kwargs) -> str:
    text = C_LANG.get(choose_lang(), C_LANG["en"]).get(key, C_LANG["en"].get(key, key))
    return text.format(**kwargs)

# App
root = tk.Tk()
root.title(lang_u("app.title", version=c_version))
root.iconbitmap(default=str(ICONS_PATH / "hau_logo.ico"))
root.configure(bg="white")
root.minsize(750, 380)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

width, height = 750, 300
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - width) // 2
y = (screen_height - height) // 2
root.geometry(f"{width}x{height}+{x}+{y}")

def return_image(img_name: str, i_width: int, i_height: int) -> ImageTk.PhotoImage:
    return ImageTk.PhotoImage(Image.open(ICONS_PATH / img_name).resize((i_width, i_height)))

pencil_img = return_image('pencil1.png', 20, 20)
trash_img = return_image('trash.png', 20, 20)
house_img = return_image('house.png', 25, 20)
apartment_img = return_image("apartment.png", 15, 22)
settings_img = return_image("settings.png", 20, 19)
settings_w_img = return_image("settings_w_r.png", 20, 19)
settings_wt_img = return_image("settings_wt_r.png", 20, 19)
infinity_img = return_image("infinity.png", 22, 13)
return_img = return_image("return.png", 20, 20)
profile_img = return_image("profile_settings.png", 16, 20)

# Colors
dp_sea = '#11384D'
white = '#FFFFFF'
black = '#000000'
war_fg = '#edc651'
war_bd = '#c29e32'
war_text = '#4f4114'

# Fonts
base18 = ("Helvetica", 18)
base_bold18 = ("Helvetica", 18, 'bold')
base16 = ("Helvetica", 16)
base_bold16 = ("Helvetica", 16, 'bold')
base14 = ("Helvetica", 14)
base_bold14 = ("Helvetica", 14, 'bold')
base12 = ("Helvetica", 12)
base_bold12 = ("Helvetica", 12, 'bold')
base10 = ("Helvetica", 10)
base_bold10 = ("Helvetica", 10, 'bold')

# Styles
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
    background=white,
)
root.option_add('*TCombobox*Listbox.font', ("Helvetica", 16))
root.option_add('*TCombobox*Listbox.justify', 'center')

style.configure(
    "CustomHelvetica.TRadiobutton",
    fieldbackground=white,
    foreground=black,
    background=white,
    font=base14
)
style.configure(
    "CustomDHelvetica.TRadiobutton",
    fieldbackground=white,
    foreground='gray67',
    background=white,
    font=base14
)
style.configure('Fancy.TEntry',
                font=base16,
                foreground=black,
                fieldbackground=white,
                padding=3,
                )

# Useful notes
note_for_tiered = lang_u("tooltip.tiered_note")

# Useful variables
separator = '|'
pos_inf = float('inf')

# Main frame
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

canvas_fr.columnconfigure(0, weight=1)

def resize_canvas_frame(event):
    main_canvas.itemconfigure(canvas_window, width=event.width)

main_canvas.bind("<Configure>", resize_canvas_frame)

def on_mouse_wheel(event):
    main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

root.bind("<MouseWheel>", on_mouse_wheel)
root.bind('<Down>', on_mouse_wheel)

# Main functions
def close_window(_event, window):
    window.destroy()

def setting_rates(entry: ttk.Entry | tk.Entry, n_btn: ttk.Button | tk.Button, n_pr_id: int, cursor: sqlite3.Cursor, entry_buttons_dict: dict, war_label) -> None:
    """
    Updates the tariff settings button icon depending on the entry value
    and the tariff saved in the database.

    If the entry is empty, the button gets the default settings icon.
    If the entry has a value and a tariff is configured, the button gets
    the configured-rate icon.
    If the entry has a value but no tariff is configured, the button gets
    the warning-rate icon.

    Also shows or hides the warning label depending on whether at least
    one value entry has no configured tariff.

    Args:
        entry: Entry widget containing the current utility value.
        n_btn: Settings button related to this entry.
        n_pr_id: Property ID used to find the tariff row in the database.
        cursor: SQLite cursor used to read tariff information.
        entry_buttons_dict: Dictionary where keys are entries and values are
            their related settings buttons.
        war_label: Label shown when at least one value has no configured tariff.

    Returns:
        None"""

    ToolTip(war_label, msg=lang_u("tooltip.no_rate"), delay=1.0)
    cursor.execute("""SELECT * FROM tariffs WHERE pr_id = ?""", (n_pr_id,))
    text_inside = entry.get()
    needed_row = entry.grid_info()['row']
    result = cursor.fetchone()
    w_img = True

    if not text_inside:
        n_btn.configure(image=settings_img)
        n_btn.image_name = 'settings_img'
    elif text_inside and result:
        if text_inside and result[needed_row - 1] is not None and str(result[needed_row - 1]) != '0':
            n_btn.configure(image=settings_w_img)
            n_btn.image_name = 'settings_w_img'
        else:
            n_btn.configure(image=settings_wt_img)
            n_btn.image_name = 'settings_wt_img'

    elif text_inside and not result:
        n_btn.configure(image=settings_wt_img)
        n_btn.image_name = 'settings_wt_img'

    for entry_b, btn_b in entry_buttons_dict.items():
        if btn_b.image_name == 'settings_wt_img':
            w_img = False

    if not w_img:
        war_label.grid(row=11, column=1, columnspan=2, sticky='es', padx=10, pady=(15, 5))
    else:
        war_label.grid_remove()

def confirm_rate_info(v: StringVar, s_entry, c_frame, tariff_frm, tariff_top, n_pr_id: int, conn, cursor, value_h, up_entry: ttk.Entry | tk.Entry, up_btn, entry_buttons_dict: dict, war_label) -> None:
    """
    Validates and saves tariff information for the selected utility value.

    Supports two tariff types:
    - Flat: one fixed rate per unit.
    - Tiered: multiple rate values taken from entry widgets inside c_frame.

    The function checks that all required fields are filled in and contain
    numeric values. After validation, it inserts a new tariff row or updates
    the existing one in the database.

    After saving, it refreshes the related settings button icon and closes
    the tariff configuration window.

    Args:
        v: StringVar containing the selected tariff type.
        s_entry: Entry widget with the flat rate value.
        c_frame: Frame containing tiered rate entry widgets.
        tariff_frm: Parent frame used for error message boxes.
        tariff_top: Top-level tariff window that will be closed after saving.
        n_pr_id: Property ID used to save the tariff for the correct property.
        conn: SQLite connection used to commit database changes.
        cursor: SQLite cursor used to read and write tariff information.
        value_h: Name prefix used to build the tariff column name.
        up_entry: Entry widget whose related settings button should be updated.
        up_btn: Settings button that should be refreshed after saving.
        entry_buttons_dict: Dictionary where keys are entries and values are
            their related settings buttons.
        war_label: Label shown when at least one value has no configured tariff.

    Returns:
        None"""

    insert_value = None

    if v.get() == 'Flat':
        insert_value = s_entry.get()

        if not insert_value:
            messagebox.showerror(lang_u("dialog.error_title"), lang_u("error.all_fields_required"), parent=tariff_frm)
            return None
        try:
            float(insert_value)
        except ValueError:
            messagebox.showerror(lang_u("dialog.error_title"), lang_u("error.enter_numeric"), parent=tariff_frm)
            return None

    elif v.get() == 'Tiered':
        insert_value = [
            str(pos_inf) if er_ch.get() == lang_u("rate.remaining") else er_ch.get().replace(',', '.', 1)
            for er_ch in c_frame.winfo_children()
            if isinstance(er_ch, ttk.Entry)
        ]

        for val in insert_value:
            if not val:
                messagebox.showerror(lang_u("dialog.error_title"), lang_u("error.all_fields_required"), parent=tariff_frm)
                return None
            try:
                float(val)
            except ValueError:
                messagebox.showerror(lang_u("dialog.error_title"), lang_u("error.enter_numeric"), parent=tariff_frm)
                return None

        insert_value = separator.join(insert_value)

    cursor.execute("""SELECT * FROM tariffs WHERE pr_id = ?""", (n_pr_id,))
    info_ab_t = cursor.fetchall()
    change_v = f'{value_h}_t'

    if not info_ab_t:
        cursor.execute(f"""INSERT INTO tariffs (pr_id, {change_v}) VALUES (?, ?)""", (n_pr_id, insert_value))
        conn.commit()
    else:
        cursor.execute(f"""UPDATE tariffs set {change_v} = ? WHERE pr_id = ?""", (insert_value, n_pr_id))
        conn.commit()

    setting_rates(up_entry, up_btn, n_pr_id, cursor, entry_buttons_dict, war_label)
    return tariff_top.destroy()

def rest_counting(btn, cc_frame):
    btn_row = btn.grid_info().get('row')

    if not getattr(btn, "is_infinite", False):
        btn.configure(image=return_img)
        setattr(btn, "is_infinite", True)

        for ch in cc_frame.winfo_children():
            info = ch.grid_info()

            if info.get('row') == btn_row:
                if isinstance(ch, (tk.Label, ttk.Label)) and ch.cget('text') == lang_u("rate.next"):
                    ch.config(text='')

                if isinstance(ch, ttk.Entry) and info.get('column') == 2:
                    ch.delete(0, tk.END)
                    ch.grid(column=1, columnspan=2, sticky='e')
                    ch.configure(width=8)
                    ch.insert(0, lang_u("rate.remaining"))

    else:
        btn.configure(image=infinity_img)
        setattr(btn, "is_infinite", False)

        for ch in cc_frame.winfo_children():
            info = ch.grid_info()

            if info.get('row') == btn_row:
                if isinstance(ch, (tk.Label, ttk.Label)) and ch.cget('text') == '':
                    ch.config(text=lang_u("rate.next"))

                if isinstance(ch, ttk.Entry) and info.get('column') == 1:
                    ch.delete(0, tk.END)
                    ch.grid(column=2, columnspan=1)
                    ch.configure(width=3)

def check_for_new_user():
    check_conn = sqlite3.connect(DB_PATH)
    check_cursor = check_conn.cursor()
    check_cursor.execute("""SELECT * FROM user_settings""")
    settings_values = check_cursor.fetchone()

    if not settings_values:
        return False
    else:
        return True

def set_lang(lang_v, label, btn):
    set_lang_conn = sqlite3.connect(DB_PATH)
    set_lang_cursor = set_lang_conn.cursor()

    if check_for_new_user():
        set_lang_cursor.execute("""UPDATE user_settings set language = ?""", (lang_v,))
        set_lang_conn.commit()

    else:
        set_lang_cursor.execute("""INSERT INTO user_settings (language) VALUES (?)""", (lang_v,))
        set_lang_conn.commit()

    label.configure(text=lang_u("onboarding.choose_language"))
    btn.configure(text=lang_u("button.next"))
    btn.grid(column=0, row=4)

def choose_username_frame():
    for ch in canvas_fr.winfo_children():
        ch.destroy()

    main_label = ttk.Label(canvas_fr, text=lang_u("onboarding.welcome"), font=base_bold18, foreground=dp_sea,
                           justify='center')
    main_label.configure(background=white)
    main_label.grid(column=0, row=0, pady=(75, 0))

    ask_label = ttk.Label(canvas_fr, text=lang_u("onboarding.ask_name"), font=base16, foreground=black,
                           justify='left')
    ask_label.configure(background=white)
    ask_label.grid(column=0, row=1, pady=(20, 5))

    name_entry = ttk.Entry(canvas_fr, style='Fancy.TEntry', font=base16)
    name_entry.grid(column=0, row=2, pady=(10, 5))
    name_entry.bind("<Return>", lambda e: choose_lang_frame(name_entry.get()))

    ask_label = ttk.Label(canvas_fr, text=lang_u("onboarding.leave_this_blank"), font=base14, foreground='#A9A9A9',
                           justify='left')
    ask_label.configure(background=white)
    ask_label.grid(column=0, row=3, pady=5)

    next_btn_to_language = ttk.Button(canvas_fr, text=lang_u("button.next"), command=lambda: choose_lang_frame(name_entry.get()),
                              style='CustomHelvetica.TButton')
    next_btn_to_language.configure(text=lang_u("button.next"))
    next_btn_to_language.grid(column=0, row=4)

def choose_lang_frame(name_entry_v: str):
    choose_l_conn = sqlite3.connect(DB_PATH)
    choose_l_cursor = choose_l_conn.cursor()
    choose_l_cursor.execute("""INSERT INTO user_settings (name) VALUES (?)""", (name_entry_v,))
    choose_l_conn.commit()

    for ch in canvas_fr.winfo_children():
        ch.destroy()

    cl = StringVar()

    main_label = ttk.Label(canvas_fr, text=lang_u("onboarding.choose_language"), font=base_bold18, foreground=dp_sea,
                           justify='center')
    main_label.configure(background=white)
    main_label.grid(column=0, row=0, pady=(75, 0))

    eng_r_btn = ttk.Radiobutton(canvas_fr, text='English', style='CustomHelvetica.TRadiobutton',
                                variable=cl, value='en', command=lambda v=cl: set_lang(v.get(), main_label, next_btn))
    eng_r_btn.grid(column=0, row=1, padx=5, pady=5)

    ru_r_btn = ttk.Radiobutton(canvas_fr, text='Русский', style='CustomHelvetica.TRadiobutton',
                               variable=cl, value='ru', command=lambda v=cl: set_lang(v.get(), main_label, next_btn))
    ru_r_btn.grid(column=0, row=2, padx=5, pady=5)

    kz_r_btn = ttk.Radiobutton(canvas_fr, text='Қазақ', style='CustomHelvetica.TRadiobutton',
                               variable=cl, value='kz', command=lambda v=cl: set_lang(v.get(), main_label, next_btn))
    kz_r_btn.grid(column=0, row=3, padx=5, pady=5)

    next_btn = ttk.Button(canvas_fr, text=lang_u("button.next"), command=choose_currency,
                              style='CustomHelvetica.TButton')

def choose_currency():
    currency_dict = {
        lang_u('combobox.currency_usd'): 'usd',
        lang_u('combobox.currency_rub'): 'rub',
        lang_u('combobox.currency_kzt'): 'kzt',
        lang_u('combobox.currency_other'): 'other',
    }

    for ch in canvas_fr.winfo_children():
        ch.destroy()

    main_label = ttk.Label(canvas_fr, text=lang_u("onboarding.preferred_currency"), font=base_bold18, foreground=dp_sea,
                           justify='center')
    main_label.configure(background=white)
    main_label.grid(column=0, row=0, pady=(75, 0))

    ask_label = ttk.Label(canvas_fr, text=lang_u("onboarding.currency_tooltip"), font=base14, foreground=black,
                           justify='left')
    ask_label.configure(background=white)
    ask_label.grid(column=0, row=1, pady=(20, 5))

    currency_types = [lang_u('combobox.currency_usd'), lang_u('combobox.currency_rub'), lang_u('combobox.currency_kzt'),
                      lang_u('combobox.currency_other')]

    currency_type = ttk.Combobox(canvas_fr, values=currency_types, style='CustomHelvetica.TCombobox',
                                 font=base18, state='readonly', justify='center')
    currency_type.grid(column=0, row=2, pady=10, columnspan=3)

    try:
        locale.setlocale(locale.LC_ALL, '')
        system_lang, _ = locale.getlocale()
    except locale.Error:
        system_lang = None

    if system_lang and system_lang.startswith('ru'):
        currency_type.current(1)
    elif system_lang and system_lang.startswith('kk'):
        currency_type.current(2)
    else:
        currency_type.current(0)

    next_btn_to_language = ttk.Button(canvas_fr, text=lang_u("button.next"), command=lambda: set_currency_data(currency_dict[currency_type.get()]),
                              style='CustomHelvetica.TButton')
    next_btn_to_language.configure(text=lang_u("button.next"))
    next_btn_to_language.grid(column=0, row=4)

def set_currency_data(currency_type: str):
    choose_l_conn = sqlite3.connect(DB_PATH)
    choose_l_cursor = choose_l_conn.cursor()
    choose_l_cursor.execute("""UPDATE user_settings set currency = ?""", (currency_type,))
    choose_l_conn.commit()

    return refresh_cards()

def save_us_info(name_info: str, lang_info: str, currency_info: str, u_set_tl: Toplevel):
    save_us_conn = sqlite3.connect(DB_PATH)
    save_us_cursor = save_us_conn.cursor()
    save_us_cursor.execute("""UPDATE user_settings set (name, language, currency) = (?, ?, ?)""", (name_info, lang_info, currency_info))
    save_us_conn.commit()
    u_set_tl.destroy()
    refresh_cards()

def open_user_settings():
    u_set = Toplevel(root)
    u_set.focus_force()
    u_set.title(lang_u("window.settings.title", version=c_version))
    u_set.minsize(500, 450)
    u_set.configure(bg=white)
    u_set.columnconfigure(0, weight=1)
    u_set.rowconfigure(0, weight=1)

    u_set_width, u_set_height = 500, 450
    u_set_screen_width = u_set.winfo_screenwidth()
    u_set_screen_height = u_set.winfo_screenheight()
    u_set_x = (u_set_screen_width - u_set_width) // 2
    u_set_y = (u_set_screen_height - u_set_height) // 2
    u_set.geometry(f"{u_set_width}x{u_set_height}+{u_set_x}+{u_set_y}")

    currency_dict = {
        lang_u('combobox.currency_usd'): 'usd',
        lang_u('combobox.currency_rub'): 'rub',
        lang_u('combobox.currency_kzt'): 'kzt',
        lang_u('combobox.currency_other'): 'other',
    }

    language_dict = {
        'English': 'en',
        'Русский': 'ru',
        'Қазақ': 'kz',

    }

    open_us_conn = sqlite3.connect(DB_PATH)
    open_us_cursor = open_us_conn.cursor()
    open_us_cursor.execute("""SELECT * FROM user_settings""")
    user_info = open_us_cursor.fetchone()

    us_frm = tk.Frame(u_set, bg=white)
    us_frm.grid(row=0, column=0)

    u_set_label = ttk.Label(us_frm, text=lang_u("settings.main_label"), font=base_bold18, foreground=dp_sea,
                           justify='center')
    u_set_label.configure(background=white)
    u_set_label.grid(row=0, column=0, padx=5, pady=5, columnspan=2)

    u_set_name_l = ttk.Label(us_frm, text=lang_u("settings.name_label"), font=base16, foreground=black, background=white,
                           justify='center')
    u_set_name_l.grid(row=1, column=0, padx=5, pady=5)

    u_set_name_entry = ttk.Entry(us_frm, font=base14, foreground=black, background=white)
    u_set_name_entry.insert(0, user_info[0])
    u_set_name_entry.grid(row=1, column=1, padx=5, pady=5)

    u_set_lang_l = ttk.Label(us_frm, text=lang_u("settings.lang_label"), font=base16, foreground=black, background=white,
                           justify='center')
    u_set_lang_l.grid(row=2, column=0, padx=5, pady=5)

    language_types = ['English', 'Русский', 'Қазақ']

    language_type = ttk.Combobox(us_frm, values=language_types, style='CustomHelvetica.TCombobox',
                                 font=base18, state='readonly', justify='center')
    language_type.grid(row=2, column=1, pady=10)

    current_language = 0

    if user_info[1] == 'ru':
        current_language = 1
    elif user_info[1] == 'kz':
        current_language = 2

    language_type.current(current_language)

    u_set_currency_l = ttk.Label(us_frm, text=lang_u("settings.currency_label"), font=base16, foreground=black, background=white,
                           justify='center')
    u_set_currency_l.grid(row=3, column=0, padx=5, pady=5)

    currency_types = [lang_u('combobox.currency_usd'), lang_u('combobox.currency_rub'), lang_u('combobox.currency_kzt'),
                      lang_u('combobox.currency_other')]

    currency_type = ttk.Combobox(us_frm, values=currency_types, style='CustomHelvetica.TCombobox',
                                 font=base18, state='readonly', justify='center')
    currency_type.grid(row=3, column=1, pady=10)

    current_currency = 3

    if user_info[2] == 'usd':
        current_currency = 0
    elif user_info[2] == 'rub':
        current_currency = 1
    elif user_info[2] == 'kzt':
        current_currency = 2

    currency_type.current(current_currency)

    save_us_btn = ttk.Button(us_frm, text='Save', style='CustomHelvetica.TButton', command=lambda: save_us_info(u_set_name_entry.get(), language_dict[language_type.get()], currency_dict[currency_type.get()], u_set))
    save_us_btn.grid(row=4, column=0, columnspan=2, pady=10)

# Loading real estate listings on the home screen
def refresh_cards() -> None:
    """
    Refreshes the property cards on the main screen.

    Removes all existing widgets from the cards container, loads properties
    and their current utility values from the database, and rebuilds the UI
    cards for each property.

    If no properties are found, shows an empty-state message and a button
    for adding the first property.

    Side effects:
        - Destroys and recreates widgets inside canvas_fr.
        - Reads data from the SQLite database.
        - Creates property cards with utility values and action buttons.
        - Binds the Return key to the new_property function.
        - Shows a confirmation dialog before deleting a property.

    Returns:
        None
    """

    for ch in canvas_fr.winfo_children():
        ch.destroy()

    with sqlite3.connect(DB_PATH) as sql_conn:
        cursor = sql_conn.cursor()
        cursor.execute("""SELECT * FROM properties""")

        user_settings_btn = ttk.Button(canvas_fr, image=profile_img, style='CustomHelvetica.TButton', command=open_user_settings)
        user_settings_btn.grid(column=0, row=0, sticky='e', columnspan=2, padx=(10, 25), pady=(15, 0))

        if not check_for_new_user():
            choose_username_frame()
        else:
            if not cursor.fetchall():
                main_label = ttk.Label(canvas_fr, text=lang_u("main.no_properties"), font=base_bold18, foreground=dp_sea, justify='center')
                main_label.configure(background=white)
                main_label.grid(column=0, row=0, pady=(75, 5))

                lets_add_btn = ttk.Button(canvas_fr, text=lang_u("main.lets_add"), command=new_property, style='CustomHelvetica.TButton')
                lets_add_btn.grid(column=0, row=1)

                root.bind("<Return>", new_property)
            else:
                cursor.execute("""SELECT * FROM user_settings""")
                user_name_value = lang_u("label.welcome_name", name=cursor.fetchone()[0])

                user_settings_btn = ttk.Label(canvas_fr, text=user_name_value, font=base16, background=white)
                user_settings_btn.grid(column=0, row=0, sticky='w', columnspan=2, padx=(25, 10), pady=(15, 0))

                main_label = ttk.Label(canvas_fr, text=lang_u("main.your_properties"), font=base_bold18, foreground=dp_sea)
                main_label.configure(background=white)
                main_label.grid(column=0, row=1, sticky=NS)

                # Cards of properties
                with sqlite3.connect(DB_PATH) as sql_conn3:
                    cursor = sql_conn3.cursor()
                    cursor.execute("""SELECT * FROM properties""")
                    card_row = 2

                    for properties in cursor.fetchall():
                        cursor.execute("""SELECT * FROM hau_values WHERE hau_v_id = ?""", (properties[3],))
                        hau_values = cursor.fetchall()
                        card_fr = tk.Frame(canvas_fr, relief="solid", background='white', border=1, pady=10)
                        card_fr.grid(column=0, row=card_row, padx=5, pady=5)
                        card_fr.grid_columnconfigure(0, minsize=400)
                        card_fr.configure(width=400)

                        name_lb = ttk.Label(card_fr, text=properties[1], style='CustomHelvetica14.TLabel', justify='center', image=house_img if properties[2] == 2 else apartment_img, compound="left")
                        name_lb.grid(row=0, column=0, columnspan=3, pady=3)

                        type_text = lang_u("property.category_flat") if properties[2] == 1 else lang_u("property.category_house")

                        type_lb = ttk.Label(card_fr, text=type_text, style='CustomHelvetica14.TLabel')
                        type_lb.grid(row=1, column=0, sticky=W, padx=(10, 0))

                        utility_names = [lang_u("utility.gas"), lang_u("utility.water"), lang_u("utility.electricity"), lang_u("utility.heating"), lang_u("utility.garbage"), lang_u("utility.housing_main")]
                        req_values = hau_values[0][2:]
                        rcount = 2

                        for name, value in zip(utility_names, req_values):
                            if value:
                                txt = f'{name}: {value}'
                                ttk.Label(card_fr, text=txt, style='CustomHelvetica14.TLabel').grid(row=rcount, column=0, sticky=W, padx=(10, 0))
                                rcount += 1

                        cursor.execute("""SELECT * FROM hau_values WHERE hau_v_id = ?""", (hau_values[0][0],))
                        res = lang_u("property.last_update", date=cursor.fetchone()[-1])
                        Label(card_fr, text=res, bg=white, fg='grey').grid(row=rcount, column=0, sticky=W, padx=(10, 0), pady=(15, 0))

                        if not properties[4]:
                            cursor.execute("""SELECT * FROM tariffs WHERE pr_id = ?""",
                                           (properties[0],))
                            tariff_row = cursor.fetchone()

                            if tariff_row is None:
                                tariffs = (0, 0, 0, 0, 0, 0)
                            else:
                                tariffs = tariff_row[2:]

                            cursor.execute("""SELECT * FROM hau_values WHERE pr_id = ? ORDER BY hau_v_id DESC""",
                                           (properties[0],))
                            values = cursor.fetchall()
                            current_values = values[0][2:8]

                            try:
                                prev_values = values[1][2:8]
                            except IndexError:
                                prev_values = (0, 0, 0, 0, 0, 0)

                            calc_res = 0

                            for cv, pv, t in zip(current_values, prev_values, tariffs):
                                cv = to_number(cv)
                                pv = to_number(pv)
                                t = to_number(t)

                                units = (cv if pv else 0) - pv

                                if units <= 0 or not t:
                                    continue

                                if isinstance(t, (int, float)):
                                    calc_res += units * t
                                else:
                                    calc_res += calc_tiered_payment(units, t)

                            cursor.execute("""SELECT * FROM user_settings""")
                            currency_from_db = cursor.fetchone()[2]

                            currency_to_locale = {
                                'kzt': 'kk',
                                'rub': 'ru',
                                'usd': 'us'
                            }

                            if currency_from_db.lower() != 'other':
                                try:
                                    locale.setlocale(locale.LC_ALL, currency_to_locale[currency_from_db])
                                    calc_res = locale.currency(calc_res, grouping=True)
                                except locale.Error:
                                    pass

                            calc_res_lbl = Label(card_fr, text=lang_u("property.payment", amount=calc_res) if calc_res else None, bg=white, fg='green', font=base14)
                            calc_res_lbl.grid(row=rcount, column=2, sticky=E, padx=(0, 10), pady=(15, 0))

                        def del_pr(pr_id):
                            am = messagebox.askquestion(lang_u("dialog.delete_title"), lang_u("dialog.delete_message"))
                            if am == 'yes':
                                yes_del(pr_id)

                        new_hau_v = ttk.Button(card_fr, style='CustomHelvetica.TButton', command=lambda vp=properties[0]: redact_pr(vp), image=pencil_img, compound="center")
                        new_hau_v.grid(column=2, row=(rcount // 2)-1, sticky='e', padx=(0, 20))
                        new_hau_v.configure(width=2)
                        ToolTip(new_hau_v, msg=lang_u("tooltip.update_values"), delay=1.0)

                        del_pr_btn = ttk.Button(card_fr, style='CustomHelvetica.TButton', command=lambda vp=properties[0]: del_pr(vp), image=trash_img)
                        del_pr_btn.grid(column=2, row=(rcount // 2)+1, sticky='e', padx=(0, 20))
                        del_pr_btn.configure(width=2)
                        ToolTip(del_pr_btn, msg=lang_u("tooltip.delete_property"), delay=1.0)

                        card_row +=1

                lets_add_btn = ttk.Button(canvas_fr, text=lang_u("main.add_more"), command=new_property, style='CustomHelvetica.TButton')
                lets_add_btn.grid(column=0, row=card_row, sticky=NS, pady=10, padx=10)

                root.bind('<Return>', new_property)

def redact_pr(pr_id):
    red_conn = sqlite3.connect(DB_PATH)
    r_cursor = red_conn.cursor()

    r_cursor.execute("""SELECT * FROM properties WHERE id = ?""", (pr_id,))
    pr_info = r_cursor.fetchone()

    r_cursor.execute("""SELECT * FROM hau_values WHERE hau_v_id = ?""", (pr_info[-2],))
    hau_v_info = r_cursor.fetchone()
    red_conn.commit()

    red_pr = Toplevel(root)
    red_pr.focus_force()
    red_pr.title(lang_u("window.edit_property.title", property_name=pr_info[1]))
    red_pr.minsize(500, 450)
    red_pr.configure(bg=white)
    red_pr.columnconfigure(0, weight=1)
    red_pr.rowconfigure(0, weight=1)

    rpr_width, rpr_height = 500, 450
    rpr_screen_width = red_pr.winfo_screenwidth()
    rpr_screen_height = red_pr.winfo_screenheight()
    rpr_x = (rpr_screen_width - rpr_width) // 2
    rpr_y = (rpr_screen_height - rpr_height) // 2
    red_pr.geometry(f"{rpr_width}x{rpr_height}+{rpr_x}+{rpr_y}")

    pr_name, pr_type = pr_info[1:3]
    pr_gas, pr_water, pr_electro, pr_heating, pr_garbage, pr_housing_main, pr_date = hau_v_info[2:]

    str_var = StringVar(value=pr_name)
    str_var.set(pr_name)

    red_property_frm = tk.Frame(red_pr, bg=white)
    red_property_frm.grid(row=0, column=0)

    def tariff_for(value_h, up_entry, up_btn):
        r_tariff_top = tk.Toplevel(root)
        r_tariff_top.focus_force()
        r_tariff_top.title(lang_u("window.edit_tariff.title", version=c_version, utility=value_h))
        r_tariff_top.configure(bg="white")
        r_tariff_top.minsize(250, 200)
        r_tariff_top.columnconfigure(0, weight=1)
        r_tariff_top.rowconfigure(0, weight=1)

        r_tariff_top.geometry(f"{rpr_width}x{rpr_height}+{rpr_x}+{rpr_y}")

        tariff_frm = tk.Frame(r_tariff_top, bg=white)
        tariff_frm.grid(row=0, column=0)

        s_lbl = tk.Label(tariff_frm, text=lang_u("rate.rate_per_unit"), bg=white, fg=black, font=base14)
        s_lbl.grid(row=1, column=0, padx=5, pady=5, sticky='nw')

        s_entry = ttk.Entry(tariff_frm, font=base14, foreground=black, background=white, width=5)
        s_entry.grid(row=1, column=1, padx=(5, 50), pady=5)

        c_frame = Frame(tariff_frm, bg='white')
        c_frame.grid(row=3, columnspan=5)

        c_lbl = tk.Label(c_frame, text=lang_u("rate.first"), bg=white, fg=black, font=base14)
        c_lbl.grid(row=0, column=1, padx=5, pady=5)

        c_entry = ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3)
        c_entry.grid(row=0, column=2)

        c2_lbl = tk.Label(c_frame, text=lang_u("rate.units_cost"), bg=white, fg=black, font=base14)
        c2_lbl.grid(row=0, column=3, padx=5, pady=5)

        c2_entry = ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3)
        c2_entry.grid(row=0, column=4)

        c3_lbl = tk.Label(c_frame, text=lang_u("rate.next"), bg=white, fg=black, font=base14)
        c3_lbl.grid(row=1, column=1, padx=5, pady=5)

        c3_entry = ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3)
        c3_entry.grid(row=1, column=2)

        c4_lbl = tk.Label(c_frame, text=lang_u("rate.units_cost"), bg=white, fg=black, font=base14)
        c4_lbl.grid(row=1, column=3, padx=5, pady=5)

        c4_entry = ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3)
        c4_entry.grid(row=1, column=4)

        r_cursor.execute("""SELECT * FROM tariffs WHERE pr_id = ?""", (pr_id,))
        result_get_v = r_cursor.fetchone()
        red_conn.commit()

        row_t = 2

        infinity_btn = ttk.Button(c_frame, image=infinity_img, style='CustomHelvetica.TButton')
        setattr(infinity_btn, "is_infinite", False)
        infinity_btn.configure(command=lambda: rest_counting(infinity_btn, c_frame))

        ToolTip(infinity_btn, msg=lang_u("tooltip.remaining_rate"), delay=1.0)

        def del_cur(del_btn):
            nonlocal row_t

            r = int(del_btn.grid_info()['row'])

            for child in list(c_frame.winfo_children()):
                child_info = child.grid_info()

                if child_info.get('row') == row_t - 1:
                    if isinstance(child, tk.Label) and child.cget('text') == '':
                        child.config(text=lang_u("rate.next"))

                    if isinstance(child, ttk.Entry) and child_info.get('column') == 1:
                        child.delete(0, tk.END)
                        child.grid(column=2, columnspan=1)
                        child.configure(width=3)

                    if getattr(infinity_btn, "is_infinite", True):
                        infinity_btn.configure(image=infinity_img)
                        setattr(infinity_btn, "is_infinite", False)

                child_info = child.grid_info()

                if not child_info:
                    continue

                child_row = int(child_info['row'])

                if child_row == r:
                    if child is infinity_btn:
                        child.grid_forget()
                    elif child is c_btn:
                        continue
                    else:
                        child.destroy()
                elif child_row > r:
                    child.grid_configure(row=child_row - 1)

            row_t -= 1

            c_btn.grid_configure(row=row_t)

            if row_t > 2:
                infinity_btn.grid(row=row_t - 1, column=0, padx=5, pady=5)
            else:
                infinity_btn.grid_forget()

        def add_more(btn):
            nonlocal row_t
            cur_row = row_t

            for child in c_frame.winfo_children():
                child_info = child.grid_info()

                if child_info.get('row') == cur_row - 1:
                    if isinstance(child, tk.Label) and child.cget('text') == '':
                        child.config(text=lang_u("rate.next"))

                    if isinstance(child, ttk.Entry) and child_info.get('column') == 1:
                        child.delete(0, tk.END)
                        child.grid(column=2, columnspan=1)
                        child.configure(width=3)

                    if getattr(infinity_btn, "is_infinite", True):
                        infinity_btn.configure(image=infinity_img)
                        setattr(infinity_btn, "is_infinite", False)

            infinity_btn.grid(row=cur_row, column=0, padx=5, pady=5)
            tk.Label(c_frame, text=lang_u("rate.next"), bg=white, fg=black, font=base14).grid(row=cur_row, column=1, padx=5, pady=5)
            ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3).grid(row=cur_row, column=2)
            tk.Label(c_frame, text=lang_u("rate.units_cost"), bg=white, fg=black, font=base14).grid(row=cur_row, column=3, padx=5, pady=5)
            ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3).grid(row=cur_row, column=4)

            del_btn = ttk.Button(c_frame, text='X', style='CustomHelvetica.TButton', width=2)
            del_btn.configure(command=lambda b=del_btn: del_cur(b))
            del_btn.grid(row=cur_row, column=5, padx=5, pady=5)

            row_t += 1
            btn.grid_configure(row=row_t)

        vs = StringVar()
        vs.set('Flat')

        confirm_rate_btn = ttk.Button(tariff_frm, style='CustomHelvetica.TButton', text=lang_u("rate.confirm"),
                                      command=lambda v=vs: confirm_rate_info(v, s_entry, c_frame, tariff_frm, r_tariff_top, pr_id, red_conn, r_cursor, value_h, up_entry, up_btn, entry_buttons, war_label))
        confirm_rate_btn.grid(row=5, column=0, columnspan=3, sticky='ew', pady=(10, 5), padx=5)

        c_btn = ttk.Button(c_frame, style='CustomHelvetica.TButton', text=lang_u("main.add_more"))
        c_btn.grid(row=row_t, column=1, columnspan=4, sticky='ew', pady=(10, 5))
        c_btn.configure(command=lambda b=c_btn: add_more(b))

        def flat_or_tiered(v):
            value = v.get()

            if value == 'Flat':
                s_entry.configure(state='enabled')
                s_lbl.configure(fg=black)
                tiered_rate.configure(style='CustomDHelvetica.TRadiobutton')
                flat_rate.configure(style='CustomHelvetica.TRadiobutton')

                for d_child in c_frame.winfo_children():
                    try:
                        d_child['state'] = 'disabled'
                    except KeyError:
                        pass

            elif value == 'Tiered':
                s_entry.config(state="disabled")
                s_lbl.configure(fg='gray67')
                flat_rate.configure(style='CustomDHelvetica.TRadiobutton')
                tiered_rate.configure(style='CustomHelvetica.TRadiobutton')

                for n_child in c_frame.winfo_children():
                    try:
                        n_child['state'] = 'normal'
                    except KeyError:
                        pass

        flat_rate = ttk.Radiobutton(tariff_frm, text=lang_u("rate.flat_rate"), style='CustomHelvetica.TRadiobutton', variable=vs, value='Flat', command=lambda v=vs: flat_or_tiered(v))
        flat_rate.grid(column=0, row=0, padx=5, pady=5, sticky='w')

        tiered_rate = ttk.Radiobutton(tariff_frm, text=lang_u("rate.tiered_rate"), style='CustomHelvetica.TRadiobutton', variable=vs, value='Tiered', command=lambda v=vs: flat_or_tiered(v))
        tiered_rate.grid(column=0, row=2, padx=5, pady=5, sticky='w')

        ToolTip(tiered_rate, msg=note_for_tiered, delay=1.0)

        s_entry.configure(state='enabled')
        s_lbl.configure(fg=black)
        tiered_rate.configure(style='CustomDHelvetica.TRadiobutton')
        flat_rate.configure(style='CustomHelvetica.TRadiobutton')

        if result_get_v:
            if result_get_v[needed_columns[value_h]]:
                if not separator in result_get_v[needed_columns[value_h]]:
                    vs.set('Flat')
                    s_entry.insert(0, result_get_v[needed_columns[value_h]])
                else:
                    vs.set('Tiered')

                    separated_values = result_get_v[needed_columns[value_h]].split(separator)

                    while len([w for w in c_frame.winfo_children() if isinstance(w, ttk.Entry)]) < len(separated_values):
                        add_more(c_btn)

                    entries = sorted(
                        [w for w in c_frame.winfo_children() if isinstance(w, ttk.Entry)],
                        key=lambda w: (int(w.grid_info()['row']), int(w.grid_info()['column']))
                    )

                    for widget, separated_value in zip(entries, separated_values):
                        if separated_value == str(pos_inf):
                            widget.insert(0, lang_u("rate.remaining"))

                            row = widget.grid_info().get('row')

                            for ch in c_frame.winfo_children():
                                info = ch.grid_info()

                                if info.get('row') == row:
                                    if isinstance(ch, (tk.Label, ttk.Label)) and ch.cget('text') == lang_u("rate.next"):
                                        ch.config(text='')

                                    if isinstance(ch, ttk.Entry) and info.get('column') == 2:
                                        ch.grid(column=1, columnspan=2, sticky='e')
                                        ch.configure(width=8)

                            infinity_btn.grid(row=row, column=0, padx=5, pady=5)
                            infinity_btn.configure(image=return_img)
                            setattr(infinity_btn, "is_infinite", True)

                        else:
                            widget.insert(0, separated_value)

        flat_or_tiered(vs)

    property_types = [lang_u('property.type_flat'), lang_u('property.type_house')]
    property_type = ttk.Combobox(red_property_frm, values=property_types, style='CustomHelvetica.TCombobox',
                                 font=base18, state='readonly', justify='center')
    property_type.grid(column=0, row=0, pady=10, columnspan=3)
    property_type.current(pr_type-1)

    name_frm = tk.Frame(red_property_frm, bg=white)
    name_frm.grid(row=1, column=0, sticky='w')

    rpr_name_label = ttk.Label(name_frm, text=lang_u("property.name"), style='CustomHelvetica.TLabel')
    rpr_name_label.grid(column=0, row=0, padx=(10, 0))
    ttk.Label(name_frm, text='*', foreground='red', background='white', font=("Helvetica", 14)).grid(column=1, row=0)

    rpr_name_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_name_entry.grid(column=1, row=1, sticky="e")
    rpr_name_entry.insert(0, pr_name)

    fill_info = ttk.Label(red_property_frm, text=lang_u("property.fill_current_values"), font=("Helvetica", 14, 'bold'),
                          foreground='darkgrey', background='white')
    fill_info.grid(column=0, row=2, columnspan=2, sticky="w", padx=10)

    rpr_gas_label = ttk.Label(red_property_frm, text=lang_u("utility.gas"), style='CustomHelvetica.TLabel')
    rpr_gas_label.grid(column=0, row=3, sticky="w", padx=10)

    rpr_gas_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_gas_entry.grid(column=1, row=3, sticky="e")
    rpr_gas_entry.insert(0, pr_gas if pr_gas else '')
    rpr_gas_entry.focus_force()

    rpr_gas_btn = ttk.Button(red_property_frm, width=3, image=settings_img, command=lambda: tariff_for('gas', rpr_gas_entry, rpr_gas_btn), text='*')
    rpr_gas_btn.grid(column=2, row=3, sticky="e", padx=10)
    rpr_gas_btn.image_name = 'settings_img'

    rpr_water_label = ttk.Label(red_property_frm, text=lang_u("utility.water"), style='CustomHelvetica.TLabel')
    rpr_water_label.grid(column=0, row=4, sticky="w", padx=10)

    rpr_water_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_water_entry.grid(column=1, row=4, sticky="e")
    rpr_water_entry.insert(0, pr_water if pr_water else '')

    rpr_water_btn = ttk.Button(red_property_frm, width=3, image=settings_img, command=lambda: tariff_for('water', rpr_water_entry, rpr_water_btn))
    rpr_water_btn.grid(column=2, row=4, sticky="e", padx=10)
    rpr_water_btn.image_name = 'settings_img'

    rpr_electricity_label = ttk.Label(red_property_frm, text=lang_u("utility.electricity"), style='CustomHelvetica.TLabel')
    rpr_electricity_label.grid(column=0, row=5, sticky="w", padx=10)

    rpr_electricity_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_electricity_entry.grid(column=1, row=5, sticky="e")
    rpr_electricity_entry.insert(0, pr_electro if pr_electro else '')

    rpr_electricity_btn = ttk.Button(red_property_frm, width=3, image=settings_img,
                                     command=lambda: tariff_for('electricity', rpr_electricity_entry, rpr_electricity_btn))
    rpr_electricity_btn.grid(column=2, row=5, sticky="e", padx=10)
    rpr_electricity_btn.image_name = 'settings_img'

    rpr_heating_label = ttk.Label(red_property_frm, text=lang_u("utility.heating"), style='CustomHelvetica.TLabel')
    rpr_heating_label.grid(column=0, row=6, sticky="w", padx=10)

    rpr_heating_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_heating_entry.grid(column=1, row=6, sticky="e")
    rpr_heating_entry.insert(0, pr_heating if pr_heating else '')

    rpr_heating_btn = ttk.Button(red_property_frm, width=3, image=settings_img,
                                 command=lambda: tariff_for('heating', rpr_heating_entry, rpr_heating_btn))
    rpr_heating_btn.grid(column=2, row=6, sticky="e", padx=10)
    rpr_heating_btn.image_name = 'settings_img'

    rpr_garbage_label = ttk.Label(red_property_frm, text=lang_u("utility.garbage"), style='CustomHelvetica.TLabel')
    rpr_garbage_label.grid(column=0, row=7, sticky="w", padx=10)

    rpr_garbage_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_garbage_entry.grid(column=1, row=7, sticky="e")
    rpr_garbage_entry.insert(0, pr_garbage if pr_garbage else '')

    rpr_garbage_btn = ttk.Button(red_property_frm, width=3, image=settings_img, command=lambda: tariff_for('garbage', rpr_garbage_entry, rpr_garbage_btn))
    rpr_garbage_btn.grid(column=2, row=7, sticky="e", padx=10)
    rpr_garbage_btn.image_name = 'settings_img'

    rpr_housing_main_label = ttk.Label(red_property_frm, text=lang_u("utility.housing_main"), style='CustomHelvetica.TLabel')
    rpr_housing_main_label.grid(column=0, row=8, sticky="w", padx=10)

    rpr_housing_main_entry = ttk.Entry(red_property_frm, font=base14, foreground=black, background=white)
    rpr_housing_main_entry.grid(column=1, row=8, sticky="e")
    rpr_housing_main_entry.insert(0, pr_housing_main if pr_housing_main else '')

    rpr_housing_main_btn = ttk.Button(red_property_frm, width=3, image=settings_img, command=lambda: tariff_for('housing_main', rpr_housing_main_entry, rpr_housing_main_btn))
    rpr_housing_main_btn.grid(column=2, row=8, sticky="e", padx=10)
    rpr_housing_main_btn.image_name = 'settings_img'

    # Updating rate buttons
    entry_buttons = {
        rpr_gas_entry: rpr_gas_btn,
        rpr_water_entry: rpr_water_btn,
        rpr_electricity_entry: rpr_electricity_btn,
        rpr_heating_entry: rpr_heating_btn,
        rpr_garbage_entry: rpr_garbage_btn,
        rpr_housing_main_entry: rpr_housing_main_btn
    }

    war_label = ctk.CTkLabel(
        red_property_frm,
        text=lang_u("rate.unfilled_warning"),
        fg_color=war_fg,
        text_color=war_text,
        corner_radius=8,
        font=base_bold14,
        border_color=war_bd,
        border_width=2
    )

    for entry, e_btn in entry_buttons.items():
        entry.bind(
            "<KeyRelease>",
            lambda e, ent=entry, b=e_btn: setting_rates(ent, b, pr_id, r_cursor, entry_buttons, war_label)
        )
        setting_rates(entry, e_btn, pr_id, r_cursor, entry_buttons, war_label)

    def update_values():
        # Checking Values
        if not rpr_name_entry.get():
            return messagebox.showerror(lang_u("dialog.error_title"), lang_u("error.name_required"), parent=red_property_frm)

        w_list = [rpr_gas_entry.get(), rpr_water_entry.get(), rpr_electricity_entry.get(), rpr_heating_entry.get(),
                  rpr_garbage_entry.get(), rpr_housing_main_entry.get()]
        v_list = [v for v in w_list if v != '']

        for v in commas_to_dots(v_list):
            try:
                float(v)
            except ValueError:
                return messagebox.showerror(lang_u("dialog.error_title"), lang_u("error.enter_numeric"), parent=red_property_frm)

        new_values = []
        for v in commas_to_dots(w_list):
            try:
                new_values.append(float(v))
            except ValueError:
                new_values.append(0)

        # Updating Values
        r_cursor.execute("""SELECT gas, water, electricity, heating, garbage, housing_main FROM hau_values WHERE pr_id = ? ORDER BY hau_v_id DESC""", (pr_id,))

        prev_values = []

        for v in r_cursor.fetchone():
            try:
                prev_values.append(float(v))
            except ValueError:
                prev_values.append(0)
            except TypeError:
                prev_values.append(0)

        red_conn.commit()

        for pv, nv in zip(prev_values, new_values):
            if nv < pv:
                return messagebox.showerror(lang_u("dialog.error_title"), lang_u("error.new_values_lower"), parent=red_property_frm)

        r_cursor.execute("""INSERT INTO hau_values (pr_id, gas, water, electricity, heating, garbage, housing_main, date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                         (pr_id, *new_values, str(date.today())))
        red_conn.commit()

        r_cursor.execute("""SELECT * FROM hau_values WHERE pr_id = ? ORDER BY hau_v_id DESC""", (pr_id,))
        hau_v_id = r_cursor.fetchone()[0]
        r_cursor.execute("""UPDATE properties set (hau_v_id, name, type_id) = (?, ?, ?) WHERE id = ?""",
                         (hau_v_id, rpr_name_entry.get(), property_type.current() + 1, pr_id))
        red_conn.commit()

        red_pr.destroy()
        return refresh_cards()

    rpr_update_values_btn = ttk.Button(red_property_frm, text=lang_u("button.update_values"), command=update_values, style='CustomHelvetica.TButton')
    rpr_update_values_btn.grid(column=0, columnspan=2, row=12, sticky=N, pady=(40, 0))

    red_pr.bind("<Control-Z>", lambda e, w=red_pr: close_window(e, w))
    red_pr.bind("<Control-z>", lambda e, w=red_pr: close_window(e, w))
    red_pr.bind("<Return>", lambda e: update_values())

############ ADDING PROPERTY ###############
def new_property(_event=None):
    add_property = Toplevel(root)
    add_property.focus_force()
    add_property.title(lang_u("window.add_property.title", version=c_version))
    add_property.configure(bg="white")
    add_property.minsize(500, 450)
    add_property.columnconfigure(0, weight=1)
    add_property.rowconfigure(0, weight=1)

    pr_width, pr_height = 500, 450
    pr_screen_width = add_property.winfo_screenwidth()
    pr_screen_height = add_property.winfo_screenheight()
    pr_x = (pr_screen_width - pr_width) // 2
    pr_y = (pr_screen_height - pr_height) // 2
    add_property.geometry(f"{pr_width}x{pr_height}+{pr_x}+{pr_y}")

    add_property_frm = tk.Frame(add_property, bg=white)
    add_property_frm.grid(row=0, column=0)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT seq FROM sqlite_sequence WHERE name='properties'")
    row = cursor.fetchone()
    next_pr_id = (row[0] + 1) if row else 1

    def tariff_for(value_h, up_entry, up_btn):
        tariff_top = tk.Toplevel(root)
        tariff_top.focus_force()
        tariff_top.title(lang_u("window.edit_tariff.title", version=c_version, utility=value_h))
        tariff_top.configure(bg="white")
        tariff_top.minsize(250, 200)
        tariff_top.columnconfigure(0, weight=1)
        tariff_top.rowconfigure(0, weight=1)

        tariff_top.geometry(f"{pr_width}x{pr_height}+{pr_x}+{pr_y}")

        tariff_frm = tk.Frame(tariff_top, bg=white)
        tariff_frm.grid(row=0, column=0)

        s_lbl = tk.Label(tariff_frm, text=lang_u("rate.rate_per_unit"), bg=white, fg=black, font=base14)
        s_lbl.grid(row=1, column=0, padx=5, pady=5, sticky='nw')

        s_entry = ttk.Entry(tariff_frm, font=base14, foreground=black, background=white, width=5)
        s_entry.grid(row=1, column=1, padx=(5, 50), pady=5)

        c_frame = Frame(tariff_frm, bg='white')
        c_frame.grid(row=3, columnspan=5)

        c_lbl = tk.Label(c_frame, text=lang_u("rate.first"), bg=white, fg=black, font=base14)
        c_lbl.grid(row=0, column=1, padx=5, pady=5)

        c_entry = ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3)
        c_entry.grid(row=0, column=2)

        c2_lbl = tk.Label(c_frame, text=lang_u("rate.units_cost"), bg=white, fg=black, font=base14)
        c2_lbl.grid(row=0, column=3, padx=5, pady=5)

        c2_entry = ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3)
        c2_entry.grid(row=0, column=4)

        c3_lbl = tk.Label(c_frame, text=lang_u("rate.next"), bg=white, fg=black, font=base14)
        c3_lbl.grid(row=1, column=1, padx=5, pady=5)

        c3_entry = ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3)
        c3_entry.grid(row=1, column=2)

        c4_lbl = tk.Label(c_frame, text=lang_u("rate.units_cost"), bg=white, fg=black, font=base14)
        c4_lbl.grid(row=1, column=3, padx=5, pady=5)

        c4_entry = ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3)
        c4_entry.grid(row=1, column=4)

        cursor.execute("""SELECT * FROM tariffs WHERE pr_id = ?""", (next_pr_id,))
        result_get_v = cursor.fetchone()

        row_t = 2

        infinity_btn = ttk.Button(c_frame, image=infinity_img, style='CustomHelvetica.TButton')
        setattr(infinity_btn, "is_infinite", False)
        infinity_btn.configure(command=lambda: rest_counting(infinity_btn, c_frame))

        ToolTip(infinity_btn, msg=lang_u("tooltip.remaining_rate"), delay=1.0)

        def del_cur(del_btn):
            nonlocal row_t

            r = int(del_btn.grid_info()['row'])

            for ch in list(c_frame.winfo_children()):
                info_grid = ch.grid_info()

                if info_grid.get('row') == row_t - 1:
                    if isinstance(ch, tk.Label) and ch.cget('text') == '':
                        ch.config(text=lang_u("rate.next"))

                    if isinstance(ch, ttk.Entry) and info_grid.get('column') == 1:
                        ch.delete(0, tk.END)
                        ch.grid(column=2, columnspan=1)
                        ch.configure(width=3)

                    if getattr(infinity_btn, "is_infinite", True):
                        infinity_btn.configure(image=infinity_img)
                        setattr(infinity_btn, "is_infinite", False)

                info_grid = ch.grid_info()

                if not info_grid:
                    continue

                row_grid = int(info_grid['row'])

                if row_grid == r:
                    if ch is infinity_btn:
                        ch.grid_forget()
                    elif ch is c_btn:
                        continue
                    else:
                        ch.destroy()
                elif row_grid > r:
                    ch.grid_configure(row = row_grid - 1)

            row_t -= 1

            c_btn.grid_configure(row=row_t)

            if row_t > 2:
                infinity_btn.grid(row=row_t - 1, column=0, padx=5, pady=5)
            else:
                infinity_btn.grid_forget()

        def add_more(btn):
            nonlocal row_t
            cur_row = row_t

            for ch in c_frame.winfo_children():
                info = ch.grid_info()

                if info.get('row') == cur_row-1:
                    if isinstance(ch, tk.Label) and ch.cget('text') == '':
                        ch.config(text=lang_u("rate.next"))

                    if isinstance(ch, ttk.Entry) and info.get('column') == 1:
                        ch.delete(0, tk.END)
                        ch.grid(column=2, columnspan=1)
                        ch.configure(width=3)

                    if getattr(infinity_btn, "is_infinite", True):
                        infinity_btn.configure(image=infinity_img)
                        setattr(infinity_btn, "is_infinite", False)

            infinity_btn.grid(row=cur_row, column=0, padx=5, pady=5)
            tk.Label(c_frame, text=lang_u("rate.next"), bg=white, fg=black, font=base14).grid(row=cur_row, column=1, padx=5, pady=5)
            ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3).grid(row=cur_row, column=2)
            tk.Label(c_frame, text=lang_u("rate.units_cost"), bg=white, fg=black, font=base14).grid(row=cur_row, column=3, padx=5, pady=5)
            ttk.Entry(c_frame, font=base14, foreground=black, background=white, width=3).grid(row=cur_row, column=4)

            del_btn = ttk.Button(c_frame, text='X', style='CustomHelvetica.TButton', width=2)
            del_btn.configure(command=lambda b=del_btn: del_cur(b))
            del_btn.grid(row=cur_row, column=5, padx=5, pady=5)

            row_t += 1
            btn.grid_configure(row=row_t)

        vs = StringVar()
        vs.set('Flat')

        confirm_rate_btn = ttk.Button(tariff_frm, style='CustomHelvetica.TButton', text=lang_u("rate.confirm"),
                                      command=lambda v=vs: confirm_rate_info(v, s_entry, c_frame, tariff_frm, tariff_top, next_pr_id, conn, cursor, value_h, up_entry, up_btn, entry_buttons, war_label))
        confirm_rate_btn.grid(row=5, column=0, columnspan=4, sticky='ew', pady=(10, 5), padx=5)

        c_btn = ttk.Button(c_frame, style='CustomHelvetica.TButton', text=lang_u("main.add_more"))
        c_btn.grid(row=row_t, column=1, columnspan=4, sticky='ew', pady=(10, 5))
        c_btn.configure(command=lambda b=c_btn: add_more(b))

        def flat_or_tiered(v):
            value = v.get()

            if value == 'Flat':
                s_entry.configure(state='enabled')
                s_lbl.configure(fg=black)
                tiered_rate.configure(style='CustomDHelvetica.TRadiobutton')
                flat_rate.configure(style='CustomHelvetica.TRadiobutton')

                for d_child in c_frame.winfo_children():
                    try:
                        d_child['state'] = 'disabled'
                    except KeyError:
                        pass

            elif value == 'Tiered':
                s_entry.config(state="disabled")
                s_lbl.configure(fg='gray67')
                flat_rate.configure(style='CustomDHelvetica.TRadiobutton')
                tiered_rate.configure(style='CustomHelvetica.TRadiobutton')

                for n_child in c_frame.winfo_children():
                    try:
                        n_child['state'] = 'normal'
                    except KeyError:
                        pass

        flat_rate = ttk.Radiobutton(tariff_frm, text=lang_u("rate.flat_rate"), style='CustomHelvetica.TRadiobutton', variable=vs, value='Flat', command=lambda v=vs: flat_or_tiered(v))
        flat_rate.grid(column=0, row=0, padx=5, pady=5, sticky='w')

        tiered_rate = ttk.Radiobutton(tariff_frm, text=lang_u("rate.tiered_rate"), style='CustomHelvetica.TRadiobutton', variable=vs, value='Tiered', command=lambda v=vs: flat_or_tiered(v))
        tiered_rate.grid(column=0, row=2, padx=5, pady=5, sticky='w')

        ToolTip(tiered_rate, msg=note_for_tiered, delay=1.0)

        s_entry.configure(state='enabled')
        s_lbl.configure(fg=black)
        tiered_rate.configure(style='CustomDHelvetica.TRadiobutton')
        flat_rate.configure(style='CustomHelvetica.TRadiobutton')

        if result_get_v:
            if result_get_v[needed_columns[value_h]]:
                if not separator in result_get_v[needed_columns[value_h]]:
                    vs.set('Flat')
                    s_entry.insert(0, result_get_v[needed_columns[value_h]])

                else:
                    vs.set('Tiered')

                    separated_values = result_get_v[needed_columns[value_h]].split(separator)

                    while len([w for w in c_frame.winfo_children()
                               if isinstance(w, ttk.Entry)]) < len(separated_values):
                        add_more(c_btn)

                    entries = [w for w in c_frame.winfo_children() if isinstance(w, ttk.Entry)]

                    for widget, separated_value in zip(entries, separated_values):
                        if separated_value == str(pos_inf):
                            infinity_btn.grid(row=widget.grid_info()['row'], column=0, padx=5, pady=5)
                            rest_counting(infinity_btn, c_frame)
                        else:
                            widget.insert(0, separated_value)

        flat_or_tiered(vs)

    property_types = [lang_u('property.type_flat'), lang_u('property.type_house')]
    property_type = ttk.Combobox(add_property_frm, values=property_types, style='CustomHelvetica.TCombobox', font=base18, state='readonly', justify='center')
    property_type.grid(column=0, row=0, pady=10, columnspan=3)
    property_type.current(0)

    name_frm = tk.Frame(add_property_frm, bg=white)
    name_frm.grid(row=1, column=0, sticky='w')

    pr_name = ttk.Label(name_frm, text=lang_u("property.name"), style='CustomHelvetica.TLabel')
    pr_name.grid(column=0, row=0, padx=10)
    ttk.Label(name_frm, text='*', foreground='red', background='white', font=("Helvetica", 14)).grid(column=1, row=0)

    pr_name_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_name_entry.grid(column=1, row=1, sticky="e")
    pr_name_entry.focus_force()

    fill_info = ttk.Label(add_property_frm, text=lang_u("property.fill_current_values"), font=("Helvetica", 14, 'bold'), foreground='darkgrey', background='white')
    fill_info.grid(column=0, row=2, columnspan=2, sticky="w", padx=10)

    pr_gas = ttk.Label(add_property_frm, text=lang_u("utility.gas"), style='CustomHelvetica.TLabel')
    pr_gas.grid(column=0, row=3, sticky="w", padx=10)

    pr_gas_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_gas_entry.grid(column=1, row=3, sticky="e")

    pr_gas_btn = ttk.Button(add_property_frm, width=3, image=settings_img, command=lambda: tariff_for('gas', pr_gas_entry, pr_gas_btn))
    pr_gas_btn.grid(column=2, row=3, sticky="e", padx=10)
    pr_gas_btn.image_name = 'settings_img'

    pr_water = ttk.Label(add_property_frm, text=lang_u("utility.water"), style='CustomHelvetica.TLabel')
    pr_water.grid(column=0, row=4, sticky="w", padx=10)

    pr_water_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_water_entry.grid(column=1, row=4, sticky="e")

    pr_water_btn = ttk.Button(add_property_frm, width=3, image=settings_img, command=lambda: tariff_for('water', pr_water_entry, pr_water_btn))
    pr_water_btn.grid(column=2, row=4, sticky="e", padx=10)
    pr_water_btn.image_name = 'settings_img'

    pr_electricity = ttk.Label(add_property_frm, text=lang_u("utility.electricity"), style='CustomHelvetica.TLabel')
    pr_electricity.grid(column=0, row=5, sticky="w", padx=10)

    pr_electricity_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_electricity_entry.grid(column=1, row=5, sticky="e")

    pr_electricity_btn = ttk.Button(add_property_frm, width=3, image=settings_img, command=lambda: tariff_for('electricity', pr_electricity_entry, pr_electricity_btn))
    pr_electricity_btn.grid(column=2, row=5, sticky="e", padx=10)
    pr_electricity_btn.image_name = 'settings_img'

    pr_heating = ttk.Label(add_property_frm, text=lang_u("utility.heating"), style='CustomHelvetica.TLabel')
    pr_heating.grid(column=0, row=6, sticky="w", padx=10)

    pr_heating_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_heating_entry.grid(column=1, row=6, sticky="e")

    pr_heating_btn = ttk.Button(add_property_frm, width=3, image=settings_img, command=lambda: tariff_for('heating', pr_heating_entry, pr_heating_btn))
    pr_heating_btn.grid(column=2, row=6, sticky="e", padx=10)
    pr_heating_btn.image_name = 'settings_img'

    pr_garbage = ttk.Label(add_property_frm, text=lang_u("utility.garbage"), style='CustomHelvetica.TLabel')
    pr_garbage.grid(column=0, row=7, sticky="w", padx=10)

    pr_garbage_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_garbage_entry.grid(column=1, row=7, sticky="e")

    pr_garbage_btn = ttk.Button(add_property_frm, width=3, image=settings_img, command=lambda: tariff_for('garbage', pr_garbage_entry, pr_garbage_btn))
    pr_garbage_btn.grid(column=2, row=7, sticky="e", padx=10)
    pr_garbage_btn.image_name = 'settings_img'

    pr_housing_main_label = ttk.Label(add_property_frm, text=lang_u("utility.housing_main"), style='CustomHelvetica.TLabel')
    pr_housing_main_label.grid(column=0, row=8, sticky="w", padx=10)

    pr_housing_main_entry = ttk.Entry(add_property_frm, font=base14, foreground=black, background=white)
    pr_housing_main_entry.grid(column=1, row=8, sticky="e")

    pr_housing_main_btn = ttk.Button(add_property_frm, width=3, image=settings_img, command=lambda: tariff_for('housing_main', pr_housing_main_entry, pr_housing_main_btn))
    pr_housing_main_btn.grid(column=2, row=8, sticky="e", padx=10)
    pr_housing_main_btn.image_name = 'settings_img'

    # Updating rate buttons
    entry_buttons = {
        pr_gas_entry: pr_gas_btn,
        pr_water_entry: pr_water_btn,
        pr_electricity_entry: pr_electricity_btn,
        pr_heating_entry: pr_heating_btn,
        pr_garbage_entry: pr_garbage_btn,
        pr_housing_main_entry: pr_housing_main_btn
    }

    war_label = ctk.CTkLabel(
        add_property_frm,
        text=lang_u("rate.unfilled_warning"),
        fg_color=war_fg,
        text_color=war_text,
        corner_radius=8,
        font=base_bold14,
        border_color=war_bd,
        border_width=2
    )

    for entry, e_btn in entry_buttons.items():
        entry.bind(
            "<KeyRelease>",
            lambda e, ent=entry, b=e_btn: setting_rates(ent, b, next_pr_id, cursor, entry_buttons, war_label)
        )
        setting_rates(entry, e_btn, next_pr_id, cursor, entry_buttons, war_label)

    def add_record():
        # Checking Values
        if not pr_name_entry.get():
            return messagebox.showerror(lang_u("dialog.error_title"), lang_u("error.name_required"), parent=add_property_frm)

        w_list = [pr_gas_entry.get(), pr_water_entry.get(), pr_electricity_entry.get(), pr_heating_entry.get(),
                  pr_garbage_entry.get(), pr_housing_main_entry.get()]
        v_list = [v for v in w_list if v != '']

        for v in commas_to_dots(v_list):
            try:
                float(v)
            except ValueError:
                return messagebox.showerror(lang_u("dialog.error_title"), lang_u("error.enter_numeric"), parent=add_property_frm)

        # Adding Values
        with sqlite3.connect(DB_PATH) as add_sql_conn:
            add_cursor = add_sql_conn.cursor()
            add_cursor.execute("""INSERT INTO hau_values (gas, water, electricity, heating, garbage, housing_main, date, pr_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                               (*commas_to_dots(w_list), str(date.today()), next_pr_id))

        def lat_hau_id() -> int:
            with sqlite3.connect(DB_PATH) as whid_add_sql_conn:
                whid_cursor = whid_add_sql_conn.cursor()
                whid_cursor.execute("SELECT * FROM hau_values ORDER BY hau_v_id DESC")
                return whid_cursor.fetchone()[0]

        with sqlite3.connect(DB_PATH) as pr_add_sql_conn:
                add_cursor = pr_add_sql_conn.cursor()
                add_cursor.execute("""INSERT INTO properties (name, type_id, hau_v_id) VALUES (?, ?, ?)""",
                                   (pr_name_entry.get(), property_type.current() + 1, lat_hau_id()))

        conn.commit()
        add_property.destroy()
        return refresh_cards()

    add_pr_btn = ttk.Button(add_property_frm, width=15, text=lang_u("button.add_property"), style='CustomHelvetica.TButton', command=add_record)
    add_pr_btn.grid(column=0, row=12, columnspan=3, sticky='N', padx=5, pady=20)

    add_property.bind("<Control-Z>", lambda e, w=add_property: close_window(e, w))
    add_property.bind("<Control-z>", lambda e, w=add_property: close_window(e, w))
############ END OF ADDING PROPERTY ###############

def yes_del(pr_id):
    with sqlite3.connect(DB_PATH) as sql_del_info:
        sql_del_info.execute("PRAGMA foreign_keys = ON")

        cur = sql_del_info.cursor()
        cur.execute("""DELETE FROM properties WHERE id=?""", (pr_id,))
    refresh_cards()

if __name__ == '__main__':
    refresh_cards()
    root.mainloop()