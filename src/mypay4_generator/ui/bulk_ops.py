# SPDX-License-Identifier: EUPL-1.2
import tkinter as tk
from tkinter import ttk, messagebox
from ..core.constants import COLORS as C, DSR_TYPES
from ..core.xml_engine import build_bilancio_xml, parse_bilancio_xml
from ..utils.helpers import center_on_parent, to_float, is_float
from .widgets import Tooltip, make_entry

class BulkIncreaseDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Aumento massivo importi")
        self.configure(bg=C["bg"])
        self.geometry("660x820")
        center_on_parent(self, parent)
        self.resizable(False, True)
        self.grab_set()

        self.var_tipo = tk.StringVar(value="percentuale")
        self.lbl_val = tk.Label()

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.wait_window()

    def _build_ui(self):
        hdr = tk.Frame(self, bg=C["accent"], height=54)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Aumento massivo importi",
                 bg=C["accent"], fg="white",
                 font=("Helvetica", 13, "bold")).pack(side="left", padx=18, pady=14)

        sub = tk.Frame(self, bg=C["surface2"], pady=6, padx=16)
        sub.pack(fill="x")
        tk.Label(sub,
                 text="Applica un aumento percentuale o fisso a tutti gli importi del flusso corrente.",
                 bg=C["surface2"], fg=C["muted"],
                 font=("Helvetica", 9), justify="left").pack(anchor="w")

        outer = tk.Frame(self, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        vsb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        body = tk.Frame(canvas, bg=C["bg"], padx=24, pady=14)
        wid = canvas.create_window((0, 0), window=body, anchor="nw")
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(wid, width=e.width))
        body.bind("<Configure>",
                  lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        def _on_mw(e):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(e.delta/120)), "units")
            except:
                pass
        canvas.bind_all("<MouseWheel>", _on_mw)

        lf1 = tk.LabelFrame(body, text="  Tipo di aumento  ",
                            bg=C["surface3"], fg=C["accent"],
                            font=("Helvetica", 10, "bold"),
                            bd=1, relief="groove", labelanchor="nw")
        lf1.pack(fill="x", pady=(0, 14), ipadx=8, ipady=8)

        tk.Radiobutton(lf1, text="Percentuale  (%)",
                       variable=self.var_tipo, value="percentuale",
                       bg=C["surface3"], fg=C["text"], activebackground=C["surface3"],
                       selectcolor=C["surface3"],
                       font=("Helvetica", 10),
                       command=self._update_label).pack(anchor="w", padx=14, pady=(8, 2))
        tk.Radiobutton(lf1, text="Valore fisso  (€)",
                       variable=self.var_tipo, value="fisso",
                       bg=C["surface3"], fg=C["text"], activebackground=C["surface3"],
                       selectcolor=C["surface3"],
                       font=("Helvetica", 10),
                       command=self._update_label).pack(anchor="w", padx=14, pady=(0, 8))

        row_val = tk.Frame(lf1, bg=C["surface3"])
        row_val.pack(anchor="w", padx=14, pady=(4, 12))

        self.lbl_val = tk.Label(row_val, text="Percentuale di aumento (%):",
                                bg=C["surface3"], fg=C["text"],
                                font=("Helvetica", 10, "bold"), width=28, anchor="w")
        self.lbl_val.pack(side="left")

        self.var_val = tk.StringVar()
        val_entry = make_entry(row_val, self.var_val, width=14,
                                font=("Consolas", 12, "bold"), fg=C["warning"])
        val_entry.pack(side="left", padx=(10, 0))
        Tooltip(val_entry, "Inserisci un numero positivo.\nEs: 5 per il 5%, oppure 1.50 per €1,50")

        lf2 = tk.LabelFrame(body, text="  Gestione bilancio XML  ",
                            bg=C["surface3"], fg=C["accent"],
                            font=("Helvetica", 10, "bold"),
                            bd=1, relief="groove", labelanchor="nw")
        lf2.pack(fill="x", pady=(0, 14), ipadx=8, ipady=8)

        self.var_cap = tk.StringVar(value="preesistente")

        tk.Radiobutton(lf2, text="Aggiungi importi a un capitolo preesistente",
                       variable=self.var_cap, value="preesistente",
                       bg=C["surface3"], fg=C["text"], activebackground=C["surface3"],
                       selectcolor=C["surface3"],
                       font=("Helvetica", 10),
                       command=self._toggle_cap).pack(anchor="w", padx=14, pady=(10, 2))

        self.frame_A = tk.Frame(lf2, bg=C["surface2"], padx=16, pady=10)
        self.frame_A.pack(fill="x", padx=32, pady=(0, 8))
        tk.Label(self.frame_A, text="Codice capitolo da aggiornare:",
                 bg=C["surface2"], fg=C["text"], font=("Helvetica", 9, "bold")).grid(row=0, column=0, sticky="w", pady=4)
        self.var_cap_esistente = tk.StringVar()
        ent_cap_esistente = make_entry(self.frame_A, self.var_cap_esistente, width=24)
        ent_cap_esistente.grid(row=0, column=1, sticky="w", padx=(12, 0), pady=4)
        Tooltip(ent_cap_esistente, "Inserisci il codice del capitolo preesistente i cui importi\ndegli accertamenti devono essere aumentati.\nSe lasciato vuoto, tutti i capitoli verranno aggiornati.")
        tk.Label(self.frame_A, text="(vuoto = aggiorna tutti i capitoli)",
                 bg=C["surface2"], fg=C["muted"], font=("Helvetica", 8, "italic")).grid(row=1, column=1, sticky="w", padx=(12, 0))

        tk.Radiobutton(lf2, text="Elimina capitoli esistenti e sostituisci con nuovo capitolo",
                       variable=self.var_cap, value="sostituisci",
                       bg=C["surface3"], fg=C["text"], activebackground=C["surface3"],
                       selectcolor=C["surface3"],
                       font=("Helvetica", 10),
                       command=self._toggle_cap).pack(anchor="w", padx=14, pady=(8, 2))

        self.frame_B = tk.Frame(lf2, bg=C["surface2"], padx=16, pady=10)
        self.frame_B.pack(fill="x", padx=32, pady=(0, 8))
        self._build_cap_fields(self.frame_B, "B",
                               cap_tip="Codice del nuovo capitolo che sostituirà quelli esistenti.\nObbligatorio.",
                               imp_lbl="Importo: nuovo importo totale (calcolato automaticamente)")

        tk.Radiobutton(lf2, text="Aggiungi nuovo capitolo (accoda ai capitoli esistenti)",
                       variable=self.var_cap, value="differenza",
                       bg=C["surface3"], fg=C["text"], activebackground=C["surface3"],
                       selectcolor=C["surface3"],
                       font=("Helvetica", 10), justify="left", anchor="w",
                       command=self._toggle_cap).pack(anchor="w", padx=14, pady=(8, 2))

        self.frame_C = tk.Frame(lf2, bg=C["surface2"], padx=16, pady=10)
        self.frame_C.pack(fill="x", padx=32, pady=(0, 10))
        self._build_cap_fields(self.frame_C, "C",
                               cap_tip="Codice del nuovo capitolo aggiunto con l'importo della differenza.\nObbligatorio.",
                               imp_lbl="Importo: differenza tra nuovo e precedente (calcolata automaticamente)")

        btns = tk.Frame(self, bg=C["surface"], pady=12)
        btns.pack(fill="x", side="bottom")
        tk.Button(btns, text="  Applica a tutte le righe", bg=C["accent"], fg="white", font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", padx=16, pady=8, command=self._apply).pack(side="right", padx=16)
        tk.Button(btns, text="  Annulla", bg=C["surface2"], font=("Helvetica", 10), relief="flat", cursor="hand2", padx=14, pady=8, command=self.destroy).pack(side="right", padx=4)
        
        self._toggle_cap()

    def _build_cap_fields(self, parent, p, cap_tip, imp_lbl):
        fields = [("Cod. Capitolo *:", f"var_{p}_cod_cap", cap_tip, True),
                  ("Cod. Ufficio:", f"var_{p}_cod_uff", "Codice ufficio (opzionale).", False),
                  ("Cod. Accertamento:", f"var_{p}_cod_acc", "Codice accertamento (opzionale).", False)]
        for r, (l, v, tip, req) in enumerate(fields):
            tk.Label(parent, text=l, bg=C["surface2"], fg=C["text"] if req else C["muted"],
                     font=("Helvetica", 9, "bold") if req else ("Helvetica", 9), width=20, anchor="w").grid(row=r, column=0, sticky="w", pady=5)
            var = tk.StringVar(); setattr(self, v, var)
            ent = make_entry(parent, var, width=24)
            ent.grid(row=r, column=1, sticky="w", padx=(12, 0), pady=5)
            Tooltip(ent, tip)
        
        note_f = tk.Frame(parent, bg=C["surface2"])
        note_f.grid(row=len(fields), column=0, columnspan=2, sticky="w", pady=(8, 0))
        tk.Label(note_f, text="ℹ", bg=C["surface2"], fg=C["accent"], font=("Helvetica", 10, "bold")).pack(side="left", padx=(0, 6))
        tk.Label(note_f, text=imp_lbl, bg=C["surface2"], fg=C["muted"], font=("Helvetica", 8, "italic"), wraplength=340, justify="left").pack(side="left")

    def _update_label(self):
        self.lbl_val.config(text="Percentuale di aumento (%):" if self.var_tipo.get() == "percentuale" else "Importo fisso da aggiungere (€):")

    def _toggle_cap(self):
        m = self.var_cap.get()
        for f, k in [(self.frame_A, "preesistente"), (self.frame_B, "sostituisci"), (self.frame_C, "differenza")]:
            active = (m == k)
            bg = C["surface"] if active else C["surface3"]
            f.configure(bg=bg)
            for ch in f.winfo_children():
                try: ch.configure(bg=bg)
                except: pass

    def _apply(self):
        raw = self.var_val.get().replace(",", ".").strip()
        try:
            delta = float(raw)
            if delta <= 0: raise ValueError
        except:
            messagebox.showerror("Valore non valido", "Inserisci un numero positivo (es. 5 oppure 1.50).", parent=self)
            return

        tipo = self.var_tipo.get(); cap_mode = self.var_cap.get()
        
        # Logica B e C
        new_cod_cap = ""
        new_cod_uff = ""
        new_cod_acc = ""
        if cap_mode in ("sostituisci", "differenza"):
            prefix = "B" if cap_mode == "sostituisci" else "C"
            new_cod_cap = getattr(self, f"var_{prefix}_cod_cap").get().strip()
            new_cod_uff = getattr(self, f"var_{prefix}_cod_uff").get().strip()
            new_cod_acc = getattr(self, f"var_{prefix}_cod_acc").get().strip()
            
            if not new_cod_cap:
                 messagebox.showerror("Campo obbligatorio", f"Inserisci il Cod. Capitolo per l'opzione {'B' if cap_mode == 'sostituisci' else 'C'}."); return

        for row in self.parent.rows:
            def _calc_v(v_str):
                v = to_float(v_str, True)
                if v is None: return None
                res = round(v * (1 + delta/100), 2) if tipo == "percentuale" else round(v + delta, 2)
                return res

            orig_v = to_float(row.get("importoDovuto"), True)
            if orig_v is not None:
                new_v = _calc_v(row["importoDovuto"])
                row["importoDovuto"] = f"{new_v:.2f}"
            
            if row.get("bilancio"):
                caps = parse_bilancio_xml(row["bilancio"])
                if cap_mode == "preesistente":
                    filtro = self.var_cap_esistente.get().strip()
                    for cap in caps:
                        if filtro and cap.get("codCapitolo") != filtro: continue
                        for acc in cap.get("accertamenti", []):
                            if acc.get("importo"):
                                res = _calc_v(acc["importo"])
                                if res is not None: acc["importo"] = f"{res:.2f}"
                elif cap_mode == "sostituisci":
                    acc = {"importo": row["importoDovuto"]}
                    if new_cod_acc: acc["codAccertamento"] = new_cod_acc
                    caps = [{"codCapitolo": new_cod_cap, "codUfficio": new_cod_uff, "accertamenti": [acc]}]
                elif cap_mode == "differenza":
                    diff = new_v - orig_v if (new_v is not None and orig_v is not None) else 0.0
                    if diff > 0.001:
                        acc = {"importo": f"{diff:.2f}"}
                        if new_cod_acc: acc["codAccertamento"] = new_cod_acc
                        caps.append({"codCapitolo": new_cod_cap, "codUfficio": new_cod_uff, "accertamenti": [acc]})
                row["bilancio"] = build_bilancio_xml(caps)
        
        messagebox.showinfo("OK", "Aumento applicato.")
        self.destroy()
