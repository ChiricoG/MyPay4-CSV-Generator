# SPDX-License-Identifier: EUPL-1.2
from .ui.main_window import MyPay4Generator
from .utils.logger import setup_logging
import sys
import logging
import traceback
from tkinter import messagebox

log = logging.getLogger(__name__)

def global_exception_handler(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log.critical("Eccezione non gestita:\n%s", tb_str)
    try:
        messagebox.showerror("Errore imprevisto", f"Si è verificato un errore:\n\n{exc_value}")
    except: pass

def main():
    setup_logging()
    sys.excepthook = global_exception_handler
    app = MyPay4Generator()
    app.mainloop()

if __name__ == "__main__":
    main()
