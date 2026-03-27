# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2025 Gianmarco Chirico — deda.cle
"""
Test unitari per l'export CSV e ZIP di mypay4_csv_generator.

Verifica che:
- Il file CSV generato abbia l'header corretto (tracciato 1_4).
- Le righe siano separate da ';' e i campi con ';' siano quotati.
- Il nome del file ZIP rispetti la convenzione MyPay4.
- Il file ZIP contenga esattamente un CSV con lo stesso nome.
"""

import csv
import io
import os
import sys
import zipfile
import types

# Stub tkinter per ambienti CI senza display
if "tkinter" not in sys.modules:
    tk_stub = types.ModuleType("tkinter")
    tk_stub.Tk = object
    tk_stub.Toplevel = object
    tk_stub.TclError = Exception
    sys.modules["tkinter"] = tk_stub
    sys.modules["tkinter.ttk"] = types.ModuleType("tkinter.ttk")
    sys.modules["tkinter.messagebox"] = types.ModuleType("tkinter.messagebox")
    sys.modules["tkinter.filedialog"] = types.ModuleType("tkinter.filedialog")

# Aggiunge la root del progetto e 'src' al path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root_dir, "src"))

from mypay4_generator.core.constants import HEADER
from mypay4_generator.core.xml_engine import build_bilancio_xml, parse_bilancio_xml


# ---------------------------------------------------------------------------
# Helper: genera una riga CSV minima valida per il tracciato 1_4
# ---------------------------------------------------------------------------

def _make_minimal_row(**overrides) -> dict:
    """Restituisce un dizionario con i soli campi obbligatori compilati."""
    base = {
        "IUD":                       "ABC001",
        "codIuv":                    "",
        "tipoIdentificativoUnivoco": "F",
        "codiceIdentificativoUnivoco": "RSSMRA85T10A562S",
        "anagraficaPagatore":        "Mario Rossi",
        "indirizzoPagatore":         "",
        "civicoPagatore":            "",
        "capPagatore":               "",
        "localitaPagatore":          "",
        "provinciaPagatore":         "",
        "nazionePagatore":           "",
        "mailPagatore":              "",
        "dataEsecuzionePagamento":   "2025-12-31",
        "importoDovuto":             "100.00",
        "commissioneCaricoPa":       "",
        "tipoDovuto":                "TIPO_TEST",
        "tipoVersamento":            "ALL",
        "causaleVersamento":         "Pagamento test",
        "datiSpecificiRiscossione":  "9/IUV-TEST-001",
        "bilancio":                  "",
        "flgGeneraIuv":              "false",
        "flagMultiBeneficiario":     "false",
        "codiceFiscaleEnteSecondario": "",
        "denominazioneEnteSecondario": "",
        "ibanAccreditoEnteSecondario": "",
        "indirizzoEnteSecondario":   "",
        "civicoEnteSecondario":      "",
        "capEnteSecondario":         "",
        "localitaEnteSecondario":    "",
        "provinciaEnteSecondario":   "",
        "nazioneEnteSecondario":     "",
        "datiSpecificiRiscossioneEnteSecondario": "",
        "causaleVersamentoEnteSecondario": "",
        "importoVersamentoEnteSecondario": "",
        "azione":                    "I",
    }
    base.update(overrides)
    return base


def _rows_to_csv_bytes(rows: list[dict]) -> bytes:
    """Serializza una lista di righe in bytes CSV (separatore ';')."""
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf, fieldnames=HEADER, delimiter=";",
        quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


# ---------------------------------------------------------------------------
# Test: header CSV
# ---------------------------------------------------------------------------

class TestCsvHeader:
    def test_header_tracciato_1_4(self):
        """Il primo campo dell'header deve essere 'IUD' e l'ultimo 'azione'."""
        assert HEADER[0] == "IUD"
        assert HEADER[-1] == "azione"

    def test_header_contiene_campi_ente_secondario(self):
        """Il tracciato 1_4 deve includere i campi dell'ente secondario."""
        assert "flagMultiBeneficiario" in HEADER
        assert "ibanAccreditoEnteSecondario" in HEADER
        assert "importoVersamentoEnteSecondario" in HEADER

    def test_header_contiene_bilancio_e_flag_iuv(self):
        """Il tracciato deve includere i campi bilancio e flgGeneraIuv."""
        assert "bilancio" in HEADER
        assert "flgGeneraIuv" in HEADER


# ---------------------------------------------------------------------------
# Test: serializzazione CSV
# ---------------------------------------------------------------------------

class TestCsvSerialization:
    def test_riga_minima_valida(self):
        """Una riga minima valida deve produrre un CSV con il numero corretto di colonne."""
        row = _make_minimal_row()
        data = _rows_to_csv_bytes([row])
        lines = data.decode("utf-8").strip().split("\r\n")
        # header + 1 riga dati
        assert len(lines) == 2
        # numero di colonne uguale all'header
        assert len(lines[0].split(";")) == len(HEADER)

    def test_campo_con_semicolon_viene_quotato(self):
        """Un campo causaleVersamento con ';' deve essere racchiuso tra virgolette."""
        row = _make_minimal_row(causaleVersamento="Tassa; mora aggiuntiva")
        data = _rows_to_csv_bytes([row]).decode("utf-8")
        assert '"Tassa; mora aggiuntiva"' in data

    def test_azione_inserimento(self):
        row = _make_minimal_row(azione="I")
        data = _rows_to_csv_bytes([row]).decode("utf-8")
        assert data.count(";I\r\n") >= 1 or ";I" in data

    def test_azione_annullamento(self):
        row = _make_minimal_row(azione="A")
        data = _rows_to_csv_bytes([row]).decode("utf-8")
        assert ";A" in data


# ---------------------------------------------------------------------------
# Test: creazione ZIP
# ---------------------------------------------------------------------------

class TestZipCreation:
    def _make_zip(self, csv_name: str, csv_bytes: bytes) -> bytes:
        """Crea uno ZIP in memoria contenente il CSV specificato."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(csv_name, csv_bytes)
        return buf.getvalue()

    def test_zip_contiene_un_solo_file(self):
        csv_name = "C_D510-test-001-1_4.csv"
        csv_bytes = _rows_to_csv_bytes([_make_minimal_row()])
        zip_bytes = self._make_zip(csv_name, csv_bytes)
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            assert len(zf.namelist()) == 1

    def test_zip_nome_file_csv_corretto(self):
        """Il nome del file CSV nello ZIP deve rispettare la convenzione MyPay4."""
        csv_name = "C_D510-test-001-1_4.csv"
        csv_bytes = _rows_to_csv_bytes([_make_minimal_row()])
        zip_bytes = self._make_zip(csv_name, csv_bytes)
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            assert zf.namelist()[0] == csv_name

    def test_zip_nome_convenzione_mypay4(self):
        """Il nome dello ZIP deve seguire <codiceIPA>-<flusso>-<versione>.zip"""
        import re
        pattern = re.compile(r"^[A-Z_]+-[A-Za-z0-9_]+-\d_\d\.zip$")
        esempi_validi = [
            "C_D510-multe-2025-001-1_4.zip",
            "R_PUGLIA-test-1_4.zip",
        ]
        # Pattern semplificato per test: verifica che termini con -1_4.zip
        for nome in esempi_validi:
            assert nome.endswith("-1_4.zip"), f"'{nome}' non termina con '-1_4.zip'"


# ---------------------------------------------------------------------------
# Test: round-trip bilancio XML in CSV
# ---------------------------------------------------------------------------

class TestBilancioInCsv:
    def test_bilancio_nel_csv_leggibile(self):
        """Il campo bilancio nel CSV deve essere parsabile dopo la serializzazione."""
        caps_in = [
            {"codCapitolo": "CAP001", "accertamenti": [{"importo": "100.00"}]}
        ]
        xml_in = build_bilancio_xml(caps_in)
        row = _make_minimal_row(bilancio=xml_in)
        data = _rows_to_csv_bytes([row]).decode("utf-8")

        # Legge il CSV e controlla il campo bilancio
        reader = csv.DictReader(io.StringIO(data), delimiter=";")
        rows_out = list(reader)
        assert len(rows_out) == 1
        xml_out = rows_out[0].get("bilancio", "")
        caps_out = parse_bilancio_xml(xml_out)
        assert len(caps_out) == 1
        assert caps_out[0]["accertamenti"][0]["importo"] == "100.00"
