# SPDX-License-Identifier: EUPL-1.2
import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import date
from ..core.constants import COLORS as C, DSR_TYPES, FIELD_MAP, SECTIONS
from ..core.xml_engine import build_bilancio_xml, parse_bilancio_xml
from ..utils.helpers import center_on_parent, to_float, is_float
from .widgets import Tooltip, make_entry

# ─── EDITOR BILANCIO XML ──────────────────────────────────────────────────────
class BilancioEditor(tk.Toplevel):
    def __init__(self, parent, xml_str="", importo_dovuto=""):
        super().__init__(parent)
        self.title("Editor Bilancio XML")
        self.configure(bg=C["bg"])
        self.geometry("840x660")
        center_on_parent(self, parent)
        self.resizable(True, True)
        self.grab_set()

        self.result_xml = None
        self.importo_dovuto = importo_dovuto
        self.capitoli = parse_bilancio_xml(xml_str) or [self._empty_cap()]
        self._cap_vars = []
        
        self._build_ui()
        self._render_all()
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.wait_window()

    @staticmethod
    def _empty_cap():
        return {"codCapitolo": "", "codUfficio": "",
                "accertamenti": [{"codAccertamento": "", "importo": ""}]}

    def _build_ui(self):
        hdr = tk.Frame(self, bg=C["accent"], height=54)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Struttura Bilancio XML  —  Editor Visuale",
                 bg=C["accent"], fg="white",
                 font=("Helvetica", 13, "bold")).pack(side="left", padx=18, pady=14)
        if self.importo_dovuto:
            tk.Label(hdr, text=f"Importo da coprire: EUR {self.importo_dovuto}",
                     bg=C["accent"], fg="white",
                     font=("Helvetica", 10, "bold")).pack(side="right", padx=18)

        desc_bar = tk.Frame(self, bg=C["surface2"], pady=7, padx=14)
        desc_bar.pack(fill="x")
        tk.Label(desc_bar,
                 text="Aggiungi capitoli e accertamenti con i pulsanti. "
                      "La somma degli importi degli accertamenti DEVE corrispondere all'importoDovuto. "
                      "L'XML viene generato automaticamente.",
                 bg=C["surface2"], fg=C["muted"],
                 font=("Helvetica", 9), wraplength=800, justify="left").pack(side="left")

        outer = tk.Frame(self, bg=C["bg"])
        outer.pack(fill="both", expand=True, padx=8, pady=6)

        self.canvas = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(self.canvas, bg=C["bg"])
        self._wid  = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._wid, width=e.width))
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        def _on_mousewheel(e):
            try:
                if self.canvas.winfo_exists():
                    self.canvas.yview_scroll(int(-1*(e.delta/120)), "units")
            except:
                pass
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)

        bot = tk.Frame(self, bg=C["surface"], pady=7)
        bot.pack(fill="x")

        tk.Button(bot, text="  Aggiungi Capitolo", bg=C["accent"], fg="white", font=("Helvetica", 10, "bold"),
                  relief="flat", cursor="hand2", padx=14, pady=5, command=self._add_cap).pack(side="left", padx=12)

        tk.Button(bot, text="  Anteprima XML", bg=C["surface2"], fg=C["xml_tag"], font=("Helvetica", 10),
                  relief="flat", cursor="hand2", padx=12, pady=5, command=self._preview).pack(side="left", padx=4)

        self.total_var = tk.StringVar(value="Totale: EUR 0.00")
        self.total_lbl = tk.Label(bot, textvariable=self.total_var, bg=C["surface"], fg=C["success"], font=("Helvetica", 10, "bold"))
        self.total_lbl.pack(side="right", padx=18)

        btns = tk.Frame(self, bg=C["bg"], pady=10)
        btns.pack(fill="x", side="bottom")

        tk.Button(btns, text="  Conferma e genera XML", bg=C["success"], fg="white", font=("Helvetica", 11, "bold"),
                  relief="flat", cursor="hand2", padx=18, pady=8, command=self._confirm).pack(side="right", padx=16)

        tk.Button(btns, text="  Annulla", bg=C["danger"], fg="white", font=("Helvetica", 11, "bold"),
                  relief="flat", cursor="hand2", padx=18, pady=8, command=self._cancel).pack(side="right", padx=4)

        tk.Button(btns, text="  Svuota tutto", bg=C["surface2"], fg=C["muted"], font=("Helvetica", 10),
                  relief="flat", cursor="hand2", padx=14, pady=8, command=self._clear).pack(side="left", padx=16)

    def _render_all(self):
        for w in self.inner.winfo_children(): w.destroy()
        self._cap_vars = []
        for ci, cap in enumerate(self.capitoli): self._render_cap(ci, cap)
        self._update_total()

    def _render_cap(self, ci, cap_data):
        frame = tk.LabelFrame(self.inner, text=f"  Capitolo {ci + 1}  ", bg=C["surface3"], fg=C["accent"],
                             font=("Helvetica", 10, "bold"), bd=1, relief="groove", labelanchor="nw")
        frame.pack(fill="x", padx=10, pady=(8, 2), ipadx=6, ipady=6)
        cv = {"frame": frame, "accs": [], "accs_frame": None}
        row_hdr = tk.Frame(frame, bg=C["surface3"])
        row_hdr.pack(fill="x", pady=4, padx=4)
        tk.Label(row_hdr, text="Cod. Capitolo *:", bg=C["surface3"], fg=C["text"],
                 font=("Helvetica", 9, "bold"), width=16, anchor="w").pack(side="left")
        v_cod = tk.StringVar(value=cap_data.get("codCapitolo", ""))
        e_cod = make_entry(row_hdr, v_cod, width=20)
        e_cod.pack(side="left", padx=(0, 20))
        Tooltip(e_cod, "Codice del capitolo d'entrata. Obbligatorio.")
        tk.Label(row_hdr, text="Cod. Ufficio:", bg=C["surface3"], fg=C["text"],
                 font=("Helvetica", 9), width=12, anchor="w").pack(side="left")
        v_uff = tk.StringVar(value=cap_data.get("codUfficio", ""))
        e_uff = make_entry(row_hdr, v_uff, width=20)
        e_uff.pack(side="left", padx=(0, 20))
        Tooltip(e_uff, "Codice ufficio (opzionale).")
        tk.Button(row_hdr, text="Rimuovi capitolo", bg=C["danger"], fg="white", font=("Helvetica", 8),
                  relief="flat", cursor="hand2", padx=8, pady=2, command=lambda i=ci: self._remove_cap(i)).pack(side="right")
        v_cod.trace_add("write", lambda *_: self._update_total())
        v_uff.trace_add("write", lambda *_: self._update_total())
        cv["codCapitolo"] = v_cod; cv["codUfficio"] = v_uff
        tk.Frame(frame, bg=C["border"], height=1).pack(fill="x", padx=6, pady=4)
        col_h = tk.Frame(frame, bg=C["surface2"])
        col_h.pack(fill="x", padx=6, pady=(0, 2))
        for txt, w in [("Cod. Accertamento (opzionale)", 28), ("Importo  *", 14), ("", 8)]:
            tk.Label(col_h, text=txt, bg=C["surface2"], fg=C["muted"], font=("Helvetica", 8, "bold"), width=w, anchor="w").pack(side="left", padx=2)
        accs_f = tk.Frame(frame, bg=C["surface3"])
        accs_f.pack(fill="x", padx=6)
        cv["accs_frame"] = accs_f
        for acc in cap_data.get("accertamenti", [{"codAccertamento": "", "importo": ""}]): self._render_acc(cv, acc)
        tk.Button(frame, text="  Aggiungi Accertamento", bg=C["surface2"], fg=C["accent"], font=("Helvetica", 9),
                  relief="flat", cursor="hand2", padx=8, pady=3, command=lambda _cv=cv: self._add_acc(_cv)).pack(anchor="w", padx=8, pady=4)
        self._cap_vars.append(cv)

    def _render_acc(self, cv, acc_data):
        row = tk.Frame(cv["accs_frame"], bg=C["surface3"])
        row.pack(fill="x", pady=2)
        v_cod = tk.StringVar(value=acc_data.get("codAccertamento", ""))
        e1 = make_entry(row, v_cod, width=28)
        e1.pack(side="left", padx=(0, 8))
        v_imp = tk.StringVar(value=acc_data.get("importo", ""))
        e_imp = make_entry(row, v_imp, width=14, fg=C["xml_val"], font=("Consolas", 10, "bold"))
        e_imp.pack(side="left", padx=(0, 8))
        v_imp.trace_add("write", lambda *_: self._update_total())
        Tooltip(e_imp, "Importo con punto come separatore decimale. Es: 100.00\nObbligatorio.")
        tk.Button(row, text="x", bg=C["surface2"], fg=C["danger"], font=("Helvetica", 9, "bold"),
                  relief="flat", cursor="hand2", padx=6, pady=1, command=lambda r=row, _cv=cv, vi=v_imp, vc=v_cod: self._remove_acc(r, _cv, vi, vc)).pack(side="left")
        cv["accs"].append({"codAccertamento": v_cod, "importo": v_imp, "row": row})

    def _add_cap(self):
        self.capitoli = self._collect(); self.capitoli.append(self._empty_cap()); self._render_all()

    def _remove_cap(self, idx):
        if len(self.capitoli) == 1: messagebox.showinfo("Info", "Deve rimanere almeno un capitolo.", parent=self); return
        self.capitoli = self._collect(); self.capitoli.pop(idx); self._render_all()

    def _add_acc(self, cv): self._render_acc(cv, {"codAccertamento": "", "importo": ""})

    def _remove_acc(self, row_widget, cv, _vi, _vc):
        if len(cv["accs"]) == 1: messagebox.showinfo("Info", "Ogni capitolo deve avere almeno un accertamento.", parent=self); return
        cv["accs"] = [a for a in cv["accs"] if a["row"] is not row_widget]
        row_widget.destroy(); self._update_total()

    def _clear(self): self.capitoli = [self._empty_cap()]; self._render_all()

    def _collect(self):
        result = []
        for cv in self._cap_vars:
            cap = {"codCapitolo": cv["codCapitolo"].get().strip(), "codUfficio": cv["codUfficio"].get().strip(),
                   "accertamenti": [{"codAccertamento": a["codAccertamento"].get().strip(), "importo": a["importo"].get().strip()} for a in cv["accs"]]}
            result.append(cap)
        return result

    def _update_total(self):
        data = self._collect(); total = sum(to_float(a.get("importo"), silent=True) or 0.0 for cap in data for a in cap.get("accertamenti", []))
        msg = f"Totale accertamenti: EUR {total:.2f}"; color = C["success"]
        target = to_float(self.importo_dovuto, silent=True)
        if target is not None:
            if abs(total - target) > 0.001: color = C["danger"]; msg += f"  !!  atteso EUR {target:.2f}"
            else: msg += "  OK"
        self.total_var.set(msg); self.total_lbl.configure(fg=color)

    def _preview(self):
        xml = build_bilancio_xml(self._collect()); pretty = xml.replace("><", ">\n<")
        win = tk.Toplevel(self); win.title("Anteprima XML generato"); win.configure(bg=C["xml_bg"]); win.geometry("660x420")
        center_on_parent(win, self); win.grab_set()
        tk.Label(win, text="XML compresso", bg=C["xml_bg"], fg=C["muted"], font=("Helvetica", 9)).pack(anchor="w", padx=12, pady=(10, 2))
        frm = tk.Frame(win, bg=C["xml_bg"]); frm.pack(fill="both", expand=True, padx=12, pady=6)
        txt = tk.Text(frm, bg=C["xml_bg"], fg=C["xml_tag"], font=("Consolas", 10), wrap="none", relief="flat")
        vsb = ttk.Scrollbar(frm, orient="vertical", command=txt.yview); hsb = ttk.Scrollbar(win, orient="horizontal", command=txt.xview)
        txt.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set); vsb.pack(side="right", fill="y"); hsb.pack(side="bottom", fill="x"); txt.pack(fill="both", expand=True)
        txt.insert("1.0", pretty); txt.configure(state="disabled")
        warn = len(xml) > 4096
        tk.Label(win, text=f"Lunghezza XML: {len(xml)} caratteri (limite: 4096){' !! TROPPO LUNGO !!' if warn else ''}",
                 bg=C["xml_bg"], fg=C["danger"] if warn else C["muted"], font=("Helvetica", 8)).pack(anchor="w", padx=12, pady=4)
        tk.Button(win, text="Chiudi", bg=C["surface2"], fg="white", relief="flat", command=win.destroy).pack(pady=8)

    def _confirm(self):
        data = self._collect(); errors = []
        for i, cap in enumerate(data):
            if not cap["codCapitolo"]: errors.append(f"Capitolo {i+1}: codCapitolo e' obbligatorio.")
            for j, acc in enumerate(cap["accertamenti"]):
                if not acc["importo"]: errors.append(f"Capitolo {i+1}, Accertamento {j+1}: importo obbligatorio.")
                elif not is_float(acc["importo"]): errors.append(f"Capitolo {i+1}, Accertamento {j+1}: importo non numerico.")
                elif float(acc["importo"]) <= 0: errors.append(f"Capitolo {i+1}, Accertamento {j+1}: importo deve essere > 0.")
        target = to_float(self.importo_dovuto, silent=True)
        if target is not None:
            total = sum(to_float(a.get("importo"), silent=True) or 0.0 for cap in data for a in cap.get("accertamenti", []))
            if abs(total - target) > 0.001: errors.append(f"Somma accertamenti (EUR {total:.2f}) != importo dovuto (EUR {target:.2f}).")
        if errors: messagebox.showerror("Errori nel bilancio", "\n".join(errors), parent=self); return
        xml = build_bilancio_xml(data)
        if len(xml) > 4096: messagebox.showerror("Errore", f"XML troppo lungo ({len(xml)} car., max 4096).", parent=self); return
        self.result_xml = xml; self.destroy()

    def _cancel(self): self.result_xml = None; self.destroy()

# ─── HELPER DSR ───────────────────────────────────────────────────────────────
class DSREditor(tk.Toplevel):
    def __init__(self, parent, current="", title="Dati Specifici Riscossione"):
        super().__init__(parent)
        self.title(title); self.configure(bg=C["bg"]); self.geometry("580x330")
        center_on_parent(self, parent); self.resizable(False, False); self.grab_set()
        self.result = None; self.tipo_var = tk.StringVar(); self.codice_var = tk.StringVar(); self.preview_var = tk.StringVar(value="—")
        self._build_ui(current); self.wait_window()

    def _build_ui(self, current):
        hdr = tk.Frame(self, bg=C["accent"], height=48); hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="  Helper Dati Specifici Riscossione", bg=C["accent"], fg="white", font=("Helvetica", 12, "bold")).pack(side="left", padx=16, pady=12)
        body = tk.Frame(self, bg=C["bg"], padx=24, pady=18); body.pack(fill="both", expand=True)
        tk.Label(body, text="Formato: <tipo>/<codice>", bg=C["bg"], fg=C["muted"], font=("Helvetica", 9)).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 14))
        tk.Label(body, text="Tipo contabilita':", bg=C["bg"], fg=C["text"], font=("Helvetica", 10, "bold")).grid(row=1, column=0, sticky="w", pady=6)
        combo = ttk.Combobox(body, textvariable=self.tipo_var, values=[d[1] for d in DSR_TYPES], state="readonly", width=48)
        combo.grid(row=1, column=1, sticky="w", padx=10); combo.bind("<<ComboboxSelected>>", self._update_preview)
        tk.Label(body, text="Codice contabilita':", bg=C["bg"], fg=C["text"], font=("Helvetica", 10, "bold")).grid(row=2, column=0, sticky="w", pady=6)
        e = make_entry(body, self.codice_var, width=38)
        e.grid(row=2, column=1, sticky="w", padx=10); self.codice_var.trace_add("write", self._update_preview)
        Tooltip(e, "Min 3, max 138 caratteri senza spazi.")
        tk.Label(body, text="Valore generato:", bg=C["bg"], fg=C["text"], font=("Helvetica", 10, "bold")).grid(row=3, column=0, sticky="w", pady=(16, 4))
        tk.Label(body, textvariable=self.preview_var, bg=C["surface"], fg=C["xml_val"], font=("Consolas", 13, "bold"), padx=12, pady=7, anchor="w").grid(row=3, column=1, sticky="ew", padx=10)
        body.columnconfigure(1, weight=1)
        if current:
            m = re.match(r"^([0129])/(.*)", current)
            if m:
                t, c = m.group(1), m.group(2)
                for d in DSR_TYPES:
                    if d[0] == t: self.tipo_var.set(d[1]); break
                self.codice_var.set(c); self._update_preview()
        btn_f = tk.Frame(self, bg=C["bg"], pady=10); btn_f.pack(fill="x", side="bottom")
        tk.Button(btn_f, text="  Conferma", bg=C["success"], fg="white", font=("Helvetica", 10, "bold"), command=self._confirm).pack(side="right", padx=16)
        tk.Button(btn_f, text="  Annulla", bg=C["danger"], fg="white", font=("Helvetica", 10, "bold"), command=self.destroy).pack(side="right", padx=4)

    def _update_preview(self, *_):
        tipo_char = next((d[0] for d in DSR_TYPES if d[1] == self.tipo_var.get()), "")
        codice = self.codice_var.get().strip()
        self.preview_var.set(f"{tipo_char}/{codice}" if tipo_char and codice else "—")

    def _confirm(self):
        tipo_char = next((d[0] for d in DSR_TYPES if d[1] == self.tipo_var.get()), ""); codice = self.codice_var.get().strip()
        if not tipo_char: messagebox.showerror("Errore", "Seleziona il tipo contabilita'.", parent=self); return
        if not codice or len(codice) < 3 or len(codice) > 138 or re.search(r"\s", codice):
            messagebox.showerror("Errore", "Codice non valido (3-138 car., no spazi).", parent=self); return
        self.result = f"{tipo_char}/{codice}"; self.destroy()

# ─── EDITOR RIGA ──────────────────────────────────────────────────────────────
class RowEditor(tk.Toplevel):
    def __init__(self, parent, row_data=None, title="Nuova riga"):
        super().__init__(parent)
        self.title(title); self.configure(bg=C["bg"]); self.geometry("940x840")
        center_on_parent(self, parent); self.resizable(True, True); self.grab_set()
        self.result = None; self.vars = {}; self._row = row_data or {}
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.wait_window()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=C["accent"], height=54)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Editor Riga Dovuto", bg=C["accent"], fg="white", font=("Helvetica", 14, "bold")).pack(side="left", padx=20, pady=14)
        
        bf = tk.Frame(self, bg=C["bg"], pady=12)
        bf.pack(fill="x", side="bottom")
        tk.Button(bf, text="  Salva riga", bg=C["success"], fg="white", font=("Helvetica", 11, "bold"), relief="flat", cursor="hand2", padx=20, pady=8, command=self._save).pack(side="right", padx=16)
        tk.Button(bf, text="  Annulla", bg=C["danger"], fg="white", font=("Helvetica", 11, "bold"), relief="flat", cursor="hand2", padx=20, pady=8, command=self._cancel).pack(side="right", padx=4)
        tk.Button(bf, text="  Pulisci tutto", bg=C["surface2"], fg=C["muted"], font=("Helvetica", 10), relief="flat", cursor="hand2", padx=14, pady=8, command=self._clear).pack(side="left", padx=16)
        
        leg = tk.Frame(bf, bg=C["bg"]); leg.pack(side="left", padx=20)
        tk.Label(leg, text="  Obbligatorio", fg=C["req"], bg=C["bg"], font=("Helvetica", 8)).pack(side="left", padx=4)
        tk.Label(leg, text="  Opzionale", fg=C["opt"], bg=C["bg"], font=("Helvetica", 8)).pack(side="left", padx=4)

        vsb = ttk.Scrollbar(self, orient="vertical")
        canvas = tk.Canvas(self, bg=C["bg"], highlightthickness=0, yscrollcommand=vsb.set)
        vsb.configure(command=canvas.yview); vsb.pack(side="right", fill="y"); canvas.pack(side="left", fill="both", expand=True)
        
        inner = tk.Frame(canvas, bg=C["bg"])
        wid = canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        def _on_mw(e):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(e.delta/120)), "units")
            except:
                pass
        canvas.bind_all("<MouseWheel>", _on_mw)
        
        sec_icons = {
            "Dati Pagatore":         "  Dati Pagatore",
            "Dati Dovuto":           "  Dati Dovuto",
            "Ente Secondario (1_4)": "  Ente Secondario (tracciato 1_4)",
            "Azione":                "  Azione",
        }
        for sec_label, field_names in SECTIONS:
            sec = tk.LabelFrame(inner, text=f"  {sec_icons.get(sec_label, sec_label)}  ", bg=C["surface3"], fg=C["accent"], font=("Helvetica", 10, "bold"), bd=1, relief="groove", labelanchor="nw")
            sec.pack(fill="x", padx=14, pady=(12, 0), ipadx=6, ipady=6)
            for col in field_names:
                self._add_field(sec, col, *FIELD_MAP[col][1:])
        tk.Frame(inner, bg=C["bg"], height=20).pack()

    def _add_field(self, parent, col, label, required, ftype, note):
        rf = tk.Frame(parent, bg=C["surface3"]); rf.pack(fill="x", pady=3, padx=6)
        rf.columnconfigure(0, minsize=10); rf.columnconfigure(1, minsize=260); rf.columnconfigure(2, weight=1)
        
        tk.Label(rf, text="*" if required else " ", fg=C["req"] if required else C["opt"], bg=C["surface3"], font=("Helvetica", 9, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 2))
        lbl = tk.Label(rf, text=label, bg=C["surface3"], fg=C["text"], font=("Helvetica", 9, "bold" if required else "normal"), anchor="w")
        lbl.grid(row=0, column=1, sticky="w")
        
        existing = self._row.get(col, "")
        wf = tk.Frame(rf, bg=C["surface3"])
        wf.grid(row=0, column=2, sticky="w", padx=(4, 0))
        
        if ftype == "bilancio_xml":
            var = tk.StringVar(value=existing); self.vars[col] = var; pv = tk.StringVar()
            def _upd_pv(v=var, pv=pv):
                raw = v.get()
                pv.set(("XML: " + raw[:40] + "...") if len(raw) > 40 else ("XML: " + raw) if raw else "(vuoto)")
            var.trace_add("write", lambda *_: _upd_pv()); _upd_pv()
            tk.Label(wf, textvariable=pv, bg=C["xml_bg"], fg=C["xml_tag"], font=("Consolas", 8), anchor="w", width=34, relief="flat", padx=4).pack(side="left", padx=(0, 6))
            btn_ed = tk.Button(wf, text="  Editor Bilancio", bg=C["accent"], fg="white", font=("Helvetica", 9, "bold"), relief="flat", cursor="hand2", padx=8, pady=2, command=lambda v=var: self._open_bilancio(v))
            btn_ed.pack(side="left", padx=(0, 2))
            Tooltip(btn_ed, note)
            tk.Button(wf, text="x", bg=C["surface2"], fg=C["danger"], font=("Helvetica", 9), relief="flat", cursor="hand2", padx=6, pady=2, command=lambda v=var: v.set("")).pack(side="left")
        elif ftype == "dsr":
            var = tk.StringVar(value=existing); self.vars[col] = var
            e = make_entry(wf, var, width=24, fg=C["xml_val"])
            e.pack(side="left", padx=(0, 6))
            Tooltip(e, note + "\n\nPuoi digitare direttamente il valore oppure usare il pulsante 'Helper' per compilarlo guidato.")
            tk.Button(wf, text="  Helper", bg=C["accent"], fg="white", font=("Helvetica", 9, "bold"), relief="flat", cursor="hand2", padx=8, pady=2, command=lambda v=var, t=label: self._open_dsr(v, t)).pack(side="left")
        elif ftype == "combo_FG":
            var = tk.StringVar(value=existing); w = ttk.Combobox(wf, textvariable=var, values=["", "F", "G"], width=6, state="readonly"); w.pack(side="left"); self.vars[col] = var
            Tooltip(w, note)
        elif ftype == "combo_bool":
            var = tk.StringVar(value=existing); w = ttk.Combobox(wf, textvariable=var, values=["", "true", "false"], width=8, state="readonly"); w.pack(side="left"); self.vars[col] = var
            Tooltip(w, note)
        elif ftype == "combo_IMA":
            var = tk.StringVar(value=existing); w = ttk.Combobox(wf, textvariable=var, values=["", "I", "M", "A"], width=4, state="readonly"); w.pack(side="left"); self.vars[col] = var
            Tooltip(w, note)
        elif ftype == "date":
            var = tk.StringVar(value=existing or date.today().strftime("%Y-%m-%d")); w = make_entry(wf, var, width=13); w.pack(side="left"); self.vars[col] = var
            Tooltip(w, note)
        elif ftype == "decimal":
            var = tk.StringVar(value=existing); w = make_entry(wf, var, width=13, fg=C["warning"], font=("Consolas", 10, "bold")); w.pack(side="left"); self.vars[col] = var
            Tooltip(w, note)
        else:
            var = tk.StringVar(value=existing)
            is_long = col in ("causaleVersamento", "causaleVersamentoEnteSecondario")
            w = make_entry(wf, var, width=54 if is_long else 40)
            w.pack(side="left"); self.vars[col] = var
            Tooltip(w, note)

    def _open_bilancio(self, var):
        importo = self.vars.get("importoDovuto", tk.StringVar()).get(); ed = BilancioEditor(self, xml_str=var.get(), importo_dovuto=importo)
        if ed.result_xml is not None: var.set(ed.result_xml)

    def _open_dsr(self, var, title):
        ed = DSREditor(self, current=var.get(), title=title)
        if ed.result: var.set(ed.result)

    def _clear(self):
        for v in self.vars.values(): v.set("")

    def _save(self):
        row = {col: self.vars[col].get().strip() for col in self.vars}; from ..core.validators import validate_row
        errors = validate_row(row)
        if errors: messagebox.showerror("Errori di validazione", "Correggere i seguenti errori prima di proseguire:\n\n" + "\n".join(f"• {e}" for e in errors), parent=self); return
        self.result = row; self.destroy()

    def _cancel(self): self.result = None; self.destroy()
