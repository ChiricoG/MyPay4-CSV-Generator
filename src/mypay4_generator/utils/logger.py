# SPDX-License-Identifier: EUPL-1.2
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logging() -> str:
    """Configura il logging dell'applicazione."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        # Risale alla root del progetto dal pacchetto src/mypay4_generator/utils
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    log_path = os.path.join(base_dir, "mypay4_generator.log")
    use_json = os.environ.get("MYPAY4_LOG_JSON", "0") == "1"

    if use_json:
        fmt = '{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","msg":%(message)r}'
    else:
        fmt = "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s"

    handler = RotatingFileHandler(
        log_path,
        maxBytes=1 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%dT%H:%M:%S"))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    if os.environ.get("MYPAY4_DEBUG", "0") == "1":
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        root_logger.addHandler(ch)
        root_logger.setLevel(logging.DEBUG)

    return log_path

def _global_exception_handler(exc_type, exc_value, exc_tb, log_path):
    """Handler globale per eccezioni non gestite."""
    import traceback
    from tkinter import messagebox
    if issubclass(exc_type, KeyboardInterrupt):
        return
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logging.getLogger().critical("Eccezione non gestita:\n%s", tb_str)
    try:
        messagebox.showerror(
            "Errore imprevisto",
            f"Si è verificato un errore imprevisto:\n\n{exc_value}\n\n"
            f"Il dettaglio è stato salvato nel file di log:\n{log_path}"
        )
    except:
        pass
