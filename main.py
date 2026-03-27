# SPDX-License-Identifier: EUPL-1.2
import sys
import os
import traceback
import logging
from tkinter import messagebox

# Aggiunge la cartella 'src' al path per permettere l'importazione di mypay4_generator
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from mypay4_generator.utils.logger import setup_logging
from mypay4_generator.ui.main_window import MyPay4Generator

log = logging.getLogger(__name__)

def global_exception_handler(exc_type, exc_value, exc_tb):
    """Handler globale per eccezioni non gestite."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log.critical("Eccezione non gestita:\n%s", tb_str)
    try:
        messagebox.showerror(
            "Errore imprevisto",
            f"Si è verificato un errore imprevisto:\n\n{exc_value}"
        )
    except: pass

def main():
    log_path = setup_logging()
    sys.excepthook = global_exception_handler
    
    log.info("MyPay4 CSV Generator modularizzato avviato.")
    try:
        app = MyPay4Generator()
        app.mainloop()
    except Exception as e:
        log.error("Errore fatale in mainloop: %s", e, exc_info=True)
    finally:
        log.info("Chiusura applicazione.")

if __name__ == "__main__":
    main()
