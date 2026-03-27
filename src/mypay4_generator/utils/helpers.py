# SPDX-License-Identifier: EUPL-1.2
import tkinter as tk
import logging

log = logging.getLogger(__name__)

def center_on_parent(win: tk.Toplevel, parent: tk.Tk) -> None:
    """Centra la finestra win rispetto alla finestra parent."""
    win.update_idletasks()
    pw = parent.winfo_width()
    ph = parent.winfo_height()
    px = parent.winfo_rootx()
    py = parent.winfo_rooty()
    ww = win.winfo_width()
    wh = win.winfo_height()
    x  = px + (pw - ww) // 2
    y  = py + (ph - wh) // 2
    win.geometry(f"+{x}+{y}")

def to_float(val: object, silent: bool = False) -> float | None:
    """Converte un valore in float, gestendo virgole e casi limite."""
    if val is None:
        return None
    try:
        if isinstance(val, str):
            v_str = val.replace(",", ".").strip()
            return float(v_str)
        return float(val)
    except (ValueError, TypeError):
        if not silent:
            log.debug("Conversione float fallita per: %r", val)
        return None

def is_float(s: object) -> bool:
    """Verifica se s è convertibile in float."""
    return to_float(s, silent=True) is not None
