from tkinter import *
from tkinter import ttk
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "hau.db"
DB_PATH.parent.mkdir(exist_ok=True)
conn = sqlite3.connect(DB_PATH)

c_version = '(0.1)'

root = Tk()
root.title("Hau " + c_version)
root.iconbitmap("assets/icons/hau_logo.ico")

mainframe = ttk.Frame(root, padding=(10, 10, 10, 10))
mainframe.grid(column=0, row=0)

width, height = 250, 100
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width - width) // 2
y = (screen_height - height) // 2

root.geometry(f"{width}x{height}+{x}+{y}")

meters = StringVar()
ttk.Label(mainframe, textvariable=meters).grid(column=2, row=2)

ttk.Button(mainframe, text="Calculate").grid(column=3, row=3, sticky=W)

ttk.Label(mainframe, text="").grid(column=3, row=1, sticky=W)
ttk.Label(mainframe, text="").grid(column=1, row=2, sticky=E)
ttk.Label(mainframe, text="").grid(column=3, row=2, sticky=W)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
mainframe.columnconfigure(2, weight=1)
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)
#
# feet_entry.focus()
# root.bind("<Enter>", calculate)
root.bind('Enter')
root.mainloop()
