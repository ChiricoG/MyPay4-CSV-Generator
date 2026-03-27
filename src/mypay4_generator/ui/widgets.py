# SPDX-License-Identifier: EUPL-1.2
import os
import sys
import logging
import tkinter as tk
from ..core.constants import COLORS as C

try:
    from PIL import Image, ImageTk 
    PIL_OK = True
except ImportError:
    PIL_OK = False

log = logging.getLogger(__name__)

def load_logo(max_width: int = 140, max_height: int = 50) -> "ImageTk.PhotoImage | None":
    """Carica il logo MyPay4."""
    if not PIL_OK: return None
    if getattr(sys, "frozen", False):
        # Supporto per PyInstaller --onefile (_MEIPASS) o cartella esterna
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        # Sviluppo: cerca la cartella assets nella radice del progetto
        # widgets.py -> ui -> mypay4_generator -> src -> radice (4 livelli)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    logo_path = os.path.join(base_dir, "assets", "logo_mypay4.png")
    if not os.path.isfile(logo_path): return None

    try:
        img = Image.open(logo_path).convert("RGBA")
        img.thumbnail((max_width, max_height), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception as exc:
        log.warning("Impossibile caricare il logo: %s", exc)
        return None

def make_entry(parent, textvariable, width=22, font=("Consolas", 10), fg=None):
    if fg is None: fg = C["input_fg"]
    return tk.Entry(
        parent, textvariable=textvariable, width=width,
        bg=C["input_bg"], fg=fg, insertbackground=C["accent"],
        relief="flat", font=font, highlightthickness=2,
        highlightbackground=C["input_border"], highlightcolor=C["accent"]
    )

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.win = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, _=None):
        x = self.widget.winfo_rootx() + 24
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        self.win = tk.Toplevel(self.widget)
        self.win.wm_overrideredirect(True)
        self.win.wm_geometry(f"+{x}+{y}")
        tk.Label(self.win, text=self.text, wraplength=400,
                 bg=C["accent2"], fg="white", font=("Consolas", 9),
                 padx=10, pady=7, justify="left").pack()

    def _hide(self, _=None):
        if self.win: self.win.destroy(); self.win = None
