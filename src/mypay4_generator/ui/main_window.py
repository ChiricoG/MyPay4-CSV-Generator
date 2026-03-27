# SPDX-License-Identifier: EUPL-1.2
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import io
import csv
import zipfile
import random
import string
import copy
import logging
import sys
from datetime import datetime
from ..core.constants import COLORS as C, HEADER, _TRACCIATO_VERSIONS
from ..core.validators import validate_row
from ..utils.helpers import center_on_parent
from ..utils.logger import _global_exception_handler
from .widgets import load_logo, make_entry
from .dialogs import RowEditor
from .bulk_ops import BulkIncreaseDialog

log = logging.getLogger(__name__)

class MyPay4Generator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MyPay4 — CSV Generator")
        self.configure(bg=C["bg"])
        self.geometry("1280x740")
        self.minsize(920, 520)
        self.rows = []
        self.current_file = None
        self._logo_img = None
        
        # Exception Hook
        from ..utils.logger import setup_logging
        lp = setup_logging()
        sys.excepthook = lambda t, v, tb: _global_exception_handler(t, v, tb, lp)

        self._apply_style()
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _apply_style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview",
                    background=C["surface"], foreground=C["text"],
                    fieldbackground=C["surface"], rowheight=26,
                    font=("Consolas", 9))
        s.configure("Treeview.Heading",
                    background=C["surface2"], foreground=C["accent"],
                    font=("Helvetica", 9, "bold"), relief="flat")
        s.map("Treeview",
              background=[("selected", C["accent2"])],
              foreground=[("selected", "white")])
        for orient in ("Vertical", "Horizontal"):
            s.configure(f"{orient}.TScrollbar",
                        background=C["surface2"], troughcolor=C["bg"],
                        arrowcolor=C["muted"])

    def _build_ui(self):
        # Header Blue
        top = tk.Frame(self, bg=C["accent"], height=66)
        top.pack(fill="x")
        top.pack_propagate(False)

        logo_lbl = tk.Label(top, bg=C["accent"])
        logo_lbl.pack(side="left", padx=20, pady=8)
        self._logo_img = load_logo(max_width=140, max_height=46)
        if self._logo_img:
            logo_lbl.configure(image=self._logo_img)
        else:
            tk.Label(top, text="MyPay4", fg="white", font=("Arial", 20, "bold"), bg=C["accent"]).pack(side="left", padx=20)

        tk.Label(top, text="Generatore CSV", bg=C["accent"], fg="white", font=("Helvetica", 10)).pack(side="left", padx=(0, 20), pady=18)
        tk.Label(top, text="Gianmarco Chirico - deda.cle", bg=C["accent"], fg="#d0eefa", font=("Helvetica", 9)).pack(side="right", padx=20)

        # Toolbar
        tb = tk.Frame(self, bg=C["surface"], height=50, pady=7)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        actions = [
            ("Nuova riga",     C["success"],  self.add_row),
            ("Modifica",       C["accent"],   self.edit_row),
            ("Elimina",        C["danger"],   self.delete_row),
            ("Duplica",        C["warning"],  self.duplicate_row),
            ("Su",             C["btn_sec"],  self.move_up),
            ("Giu",            C["btn_sec"],  self.move_down),
            ("SEP", "", None),
            ("Apri CSV",       C["btn_sec"],  self.open_csv),
            ("Salva",          C["accent2"],  self.save_csv),
            ("Salva come...",  C["accent2"],  self.save_csv_as),
            ("SEP", "", None),
            ("Nuova sessione", C["btn_sec"],  self.new_session),
            ("SEP", "", None),
            ("Aumento importi", C["warning"], self.bulk_increase),
        ]
        for text, color, cmd in actions:
            if text == "SEP":
                tk.Frame(tb, bg=C["border"], width=1).pack(side="left", fill="y", padx=10, pady=4)
                continue
            tk.Button(tb, text=text, bg=color, fg="white", font=("Helvetica", 9, "bold"), relief="flat", cursor="hand2", padx=10, pady=4, command=cmd).pack(side="left", padx=2)

        # Info Ente
        info = tk.Frame(self, bg=C["surface2"], pady=5, padx=14)
        info.pack(fill="x")
        tk.Label(info, text="Codice IPA:", bg=C["surface2"], fg=C["muted"], font=("Helvetica", 9, "bold")).pack(side="left")
        self.var_ipa = tk.StringVar(value="R_PUGLIA")
        ipa_entry = make_entry(info, self.var_ipa, width=14)
        ipa_entry.pack(side="left", padx=(4, 18))
        self._fname_preview = tk.StringVar()
        self._update_fname_preview()
        self.var_ipa.trace_add("write", lambda *_: self._update_fname_preview())
        tk.Label(info, textvariable=self._fname_preview, bg=C["surface2"], fg=C["muted"], font=("Helvetica", 8)).pack(side="left")

        # Grid
        tf = tk.Frame(self, bg=C["bg"])
        tf.pack(fill="both", expand=True, padx=8, pady=8)

        vis = ["IUD", "tipoIdentificativoUnivoco", "anagraficaPagatore",
               "dataEsecuzionePagamento", "importoDovuto", "tipoDovuto",
               "causaleVersamento", "bilancio", "azione", "flagMultiBeneficiario"]
        widths = {
            "IUD": 110, "tipoIdentificativoUnivoco": 46,
            "anagraficaPagatore": 160, "dataEsecuzionePagamento": 100,
            "importoDovuto": 86, "tipoDovuto": 110,
            "causaleVersamento": 180, "bilancio": 70,
            "azione": 54, "flagMultiBeneficiario": 80,
        }

        self.tree = ttk.Treeview(tf, columns=vis, show="headings", selectmode="browse")
        for c in vis:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths.get(c, 90), minwidth=40)

        vsb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tf, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tf.rowconfigure(0, weight=1); tf.columnconfigure(0, weight=1)

        self.tree.bind("<Double-1>", lambda _: self.edit_row())
        self.tree.bind("<Delete>",   lambda _: self.delete_row())

        # Status Bar
        self.status_var = tk.StringVar(value="Pronto.  Premi 'Nuova riga' per iniziare.")
        tk.Label(self, textvariable=self.status_var, bg=C["surface"], fg=C["muted"], font=("Helvetica", 9), anchor="w", padx=16, pady=6).pack(fill="x", side="bottom")

    def add_row(self):
        e = RowEditor(self, title="Nuova riga dovuto")
        if e.result:
            self.rows.append(e.result)
            self._refresh()
            self._st(f"Riga aggiunta. Totale: {len(self.rows)}")
            log.info("Riga aggiunta — IUD=%s  Totale righe: %d", e.result.get("IUD", ""), len(self.rows))

    def edit_row(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        e = RowEditor(self, row_data=self.rows[idx], title=f"Modifica riga {idx+1}")
        if e.result:
            self.rows[idx] = e.result
            self._refresh()
            self._st(f"Riga {idx+1} aggiornata.")
            log.info("Riga %d modificata — IUD=%s", idx + 1, e.result.get("IUD", ""))

    def delete_row(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        if messagebox.askyesno("Conferma", f"Eliminare la riga {idx+1}?"):
            iud = self.rows[idx].get("IUD", "")
            self.rows.pop(idx)
            self._refresh()
            self._st(f"Riga eliminata. Totale: {len(self.rows)}")
            log.info("Riga %d eliminata — IUD=%s  Totale righe: %d", idx + 1, iud, len(self.rows))

    def duplicate_row(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        new_row = copy.deepcopy(self.rows[idx])
        self.rows.insert(idx + 1, new_row)
        self._refresh()
        self.tree.selection_set(self.tree.get_children()[idx + 1])
        self._st(f"Riga {idx+1} duplicata in posizione {idx+2}.")
        log.info("Riga %d duplicata in posizione %d — IUD=%s", idx + 1, idx + 2, new_row.get("IUD", ""))

    def move_up(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        if idx > 0:
            self.rows[idx], self.rows[idx-1] = self.rows[idx-1], self.rows[idx]
            self._refresh(); self.tree.selection_set(self.tree.get_children()[idx-1])

    def move_down(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        if idx < len(self.rows)-1:
            self.rows[idx], self.rows[idx+1] = self.rows[idx+1], self.rows[idx]
            self._refresh(); self.tree.selection_set(self.tree.get_children()[idx+1])

    def new_session(self):
        if self.rows and not messagebox.askyesno("Nuova sessione", "Perdere le modifiche non salvate?"): return
        self.rows, self.current_file = [], None; self._refresh(); self._st("Nuova sessione.")

    def _update_fname_preview(self):
        ipa = self.var_ipa.get().strip().upper() or "ENTE"
        self._fname_preview.set(f"→  {ipa}-<ID>_<data>_<hhmmss>-1_4.csv")

    def _fname(self):
        ipa = self.var_ipa.get().strip().upper() or "ENTE"
        rand = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{ipa}-{rand}_{ts}-1_4.csv"

    @staticmethod
    def _detect_version(fieldnames):
        cols = [c.strip() for c in fieldnames]
        if "flagMultiBeneficiario" in cols: return "1_4"
        if "flgGeneraIuv" in cols: return "1_3"
        if "bilancio" in cols: return "1_2"
        return "1_1"

    def open_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV/ZIP", "*.csv;*.zip"), ("Tutti i file", "*.*")])
        if not path: return
        try:
            content = None
            if path.lower().endswith(".zip"):
                with zipfile.ZipFile(path, "r") as z:
                    for name in z.namelist():
                        if name.lower().endswith(".csv"):
                            content = z.read(name).decode("utf-8")
                            break
                if not content: raise Exception("Nessun file CSV trovato nello ZIP.")
            else:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

            f = io.StringIO(content)
            reader = csv.DictReader(f, delimiter=";")
            raw_rows = list(reader)
            detected_cols = reader.fieldnames or []
            
            if not raw_rows:
                messagebox.showwarning("File vuoto", "Nessuna riga trovata.")
                return

            version = self._detect_version(detected_cols)
            normalized = []
            for row in raw_rows:
                norm = {col: "" for col in HEADER}
                for col in HEADER:
                    if col in row: norm[col] = row[col] or ""
                normalized.append(norm)

            self.rows = normalized
            self.current_file = None
            
            # Auto-rilevamento IPA dal nome
            parts = os.path.splitext(os.path.basename(path))[0].split("-")
            if parts:
                self.var_ipa.set(parts[0].upper())
            
            self._update_fname_preview()
            self._refresh()

            if version != "1_4":
                messagebox.showinfo("Tracciato convertito", f"File importato in formato {version}.\nCampi inizializzati a vuoto. Salvataggio avverrà in 1_4.")

            self._st(f"Aperto (tracciato {version} → 1_4): {os.path.basename(path)}  ({len(self.rows)} righe)")
            self.title(f"MyPay4 — {os.path.basename(path)}  |  CSV Generator")
            log.info("File aperto — %s  versione: %s", path, version)
        except Exception as e:
            log.error("Errore apertura — %s: %s", path, str(e), exc_info=True)
            messagebox.showerror("Errore apertura", str(e))

    def save_csv(self):
        if not self.rows: return
        if not self.current_file: self.save_csv_as(); return
        self._write(self.current_file)

    def save_csv_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=self._fname())
        if path: self.current_file = path; self._write(path)

    def _write(self, path):
        try:
            # Validazione preventiva
            err_rows = []
            for i, row in enumerate(self.rows):
                errs = validate_row(row)
                if errs:
                    err_rows.append(f"Riga {i+1} (IUD: {row.get('IUD', '?')}): " + "; ".join(errs))
            
            if err_rows:
                msg = (f"Sono stati riscontrati {len(err_rows)} record con errori di validazione.\n"
                       f"Il file generato potrebbe essere rifiutato da MyPay.\n\n"
                       f"Esempi di errori:\n" + "\n".join(err_rows[:5]))
                if len(err_rows) > 5: msg += f"\n... e altri {len(err_rows)-5} errori."
                msg += "\n\nVuoi procedere comunque con il salvataggio?"
                if not messagebox.askyesno("Errori di validazione", msg): return

            csv_name = os.path.basename(path)
            buf = io.StringIO()
            w = csv.DictWriter(buf, fieldnames=HEADER, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            w.writeheader()
            for row in self.rows:
                w.writerow({col: row.get(col, "") for col in HEADER})
            
            zip_path = os.path.splitext(path)[0] + ".zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.writestr(csv_name, buf.getvalue().encode("utf-8"))
            
            self._st(f"Salvato: {os.path.basename(zip_path)}  ({len(self.rows)} righe)")
            self.title(f"MyPay4 — {csv_name}  |  CSV Generator")
            log.info("File salvato — %s  (%d righe)", zip_path, len(self.rows))
            
            messagebox.showinfo(
                "Salvataggio completato",
                f"File salvato correttamente:\n"
                f"  • {os.path.basename(zip_path)}\n\n"
                f"IMPORTANTE\n"
                f"Effettuare l'upload del file .zip sul sistema MyPay.\n"
                f"Non occorre spacchettare l'archivio per effettuare il caricamento."
            )
        except Exception as e:
            log.error("Errore salvataggio — %s: %s", path, str(e), exc_info=True)
            messagebox.showerror("Errore salvataggio", str(e))

    def bulk_increase(self):
        if not self.rows: return
        BulkIncreaseDialog(self)
        self._refresh()

    def _refresh(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        vis = ["IUD", "tipoIdentificativoUnivoco", "anagraficaPagatore",
               "dataEsecuzionePagamento", "importoDovuto", "tipoDovuto",
               "causaleVersamento", "bilancio", "azione", "flagMultiBeneficiario"]
        for i, row in enumerate(self.rows):
            vals = [("[XML]" if row.get(c) else "") if c == "bilancio" else row.get(c, "") for c in vis]
            self.tree.insert("", "end", values=vals, tags=("even" if i % 2 == 0 else "odd",))
        self.tree.tag_configure("even", background=C["surface"])
        self.tree.tag_configure("odd",  background=C["surface2"])
        fname = os.path.basename(self.current_file) if self.current_file else "(non salvato)"
        self._st(f"Righe nel flusso: {len(self.rows)}  |  File: {fname}")

    def _st(self, msg): self.status_var.set(msg)

    def _on_close(self):
        if self.rows and not messagebox.askyesno("Uscita", "Hai righe non salvate. Uscire comunque?"): return
        self.destroy()
