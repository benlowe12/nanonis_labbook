# nanonis_labbook/main.py
# Entry point shared by:
#   - python -m nanonis_labbook  (via __main__.py)
#   - nanonis-labbook             (via pyproject.toml console_scripts)

import tkinter as tk
from .gui import LabbookApp


def run():
    root = tk.Tk()
    app = LabbookApp(root)
    root.mainloop()
