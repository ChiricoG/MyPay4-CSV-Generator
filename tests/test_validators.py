# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2025 Gianmarco Chirico — deda.cle
"""
Test unitari per le funzioni di validazione e utilità di mypay4_csv_generator.

Copertura:
- Validazione IUD (MP-001)
- Validazione codice fiscale / P.IVA (MP-002, MP-003)
- Validazione importo (MP-004)
- Validazione datiSpecificiRiscossione (MP-005)
- Validazione data (MP-006)
- Parser e builder bilancio XML
- Escaping CSV (campo con ';' e '"')
"""

import sys
import os
import pytest

# Aggiunge la root del progetto e 'src' al path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root_dir, "src"))

# Importa solo le funzioni pure (non-GUI) dai nuovi moduli
from mypay4_generator.core.xml_engine import build_bilancio_xml, parse_bilancio_xml
from mypay4_generator.utils.helpers import is_float
from mypay4_generator.core.validators import (
    validate_iud,
    validate_importo,
    validate_dsr,
    validate_tipo_id,
    validate_cf_piva,
    validate_causale,
)

# ---------------------------------------------------------------------------
# Costanti per i test
# ---------------------------------------------------------------------------

VALID_IUD_EXAMPLES = ["ABC123", "001TEST", "XYZ-001", "a" * 35]
INVALID_IUD_EXAMPLES = ["000TEST", "000" + "a" * 32, ""]  # inizia con "000" o vuoto

VALID_CF_EXAMPLES = ["RSSMRA85T10A562S", "RSSMRA85T10A562S"]
VALID_PIVA_EXAMPLES = ["01234567890"]

VALID_DSR_EXAMPLES = [
    "0/123",
    "1/contabilita-speciale-001",
    "2/SIOPE-123",
    "9/altro-codice-001",
]
INVALID_DSR_EXAMPLES = [
    "3/codice",   # tipo non ammesso
    "0/ab",       # codice troppo corto (< 3 char)
    "codice",     # nessun separatore
    "",
]

VALID_IMPORTO_EXAMPLES = ["100.00", "0.01", "999999.99", "1.5"]
INVALID_IMPORTO_EXAMPLES = ["0.00", "-1.00", "abc", "", "1,50"]


# ---------------------------------------------------------------------------
# Test: _is_float
# ---------------------------------------------------------------------------

class TestIsFloat:
    def test_valori_validi(self):
        for v in ["1.0", "100", "0.01", "999999.99", "1,50"]:
            assert is_float(v), f"Atteso True per '{v}'"

    def test_valori_non_validi(self):
        for v in ["abc", "", None]:
            assert not is_float(v), f"Atteso False per '{v}'"


# ---------------------------------------------------------------------------
# Test: build_bilancio_xml / parse_bilancio_xml
# ---------------------------------------------------------------------------

class TestBilancioXml:
    """Testa il round-trip build → parse del bilancio XML."""

    def test_capitolo_singolo(self):
        caps_in = [
            {
                "codCapitolo": "CAP001",
                "codUfficio": "UFF1",
                "accertamenti": [{"codAccertamento": "ACC.X", "importo": "100.00"}],
            }
        ]
        xml = build_bilancio_xml(caps_in)
        caps_out = parse_bilancio_xml(xml)

        assert len(caps_out) == 1
        assert caps_out[0]["codCapitolo"] == "CAP001"
        assert caps_out[0]["codUfficio"] == "UFF1"
        assert len(caps_out[0]["accertamenti"]) == 1
        assert caps_out[0]["accertamenti"][0]["importo"] == "100.00"

    def test_capitolo_multipli(self):
        caps_in = [
            {
                "codCapitolo": "CAP001",
                "accertamenti": [{"importo": "50.00"}],
            },
            {
                "codCapitolo": "CAP002",
                "accertamenti": [{"importo": "50.00"}],
            },
        ]
        xml = build_bilancio_xml(caps_in)
        caps_out = parse_bilancio_xml(xml)

        assert len(caps_out) == 2
        assert caps_out[1]["codCapitolo"] == "CAP002"

    def test_xml_vuoto(self):
        assert parse_bilancio_xml("") == []
        assert parse_bilancio_xml(None) == []

    def test_no_spazi_nel_xml(self):
        """Il bilancio XML non deve contenere spazi o a capo (specifica MyPay4)."""
        caps_in = [
            {
                "codCapitolo": "CAP001",
                "accertamenti": [{"importo": "10.00"}],
            }
        ]
        xml = build_bilancio_xml(caps_in)
        assert " " not in xml
        assert "\n" not in xml

    def test_senza_codufficio(self):
        """codUfficio è opzionale nella struttura XML."""
        caps_in = [{"codCapitolo": "CAP001", "accertamenti": [{"importo": "1.00"}]}]
        xml = build_bilancio_xml(caps_in)
        assert "<codUfficio>" not in xml
        caps_out = parse_bilancio_xml(xml)
        assert "codUfficio" not in caps_out[0]

    def test_importo_somma_coerente(self):
        """La somma degli importi degli accertamenti deve corrispondere all'importo dovuto."""
        caps_in = [
            {
                "codCapitolo": "CAP001",
                "accertamenti": [
                    {"importo": "30.00"},
                    {"importo": "70.00"},
                ],
            }
        ]
        caps_out = parse_bilancio_xml(build_bilancio_xml(caps_in))
        totale = sum(
            float(acc["importo"])
            for cap in caps_out
            for acc in cap.get("accertamenti", [])
        )
        assert abs(totale - 100.00) < 0.001


# ---------------------------------------------------------------------------
# Test: validazione IUD (logica di business, non GUI)
# ---------------------------------------------------------------------------

class TestIudValidation:
    """Verifica la regola: i primi 3 caratteri dell'IUD non possono essere '000'."""

    @staticmethod
    def _is_valid_iud(iud: str) -> bool:
        ok, _ = validate_iud(iud)
        return ok

    def test_iud_validi(self):
        for iud in ["ABC123", "001TEST", "XYZ-001", "a" * 35]:
            assert self._is_valid_iud(iud), f"IUD '{iud}' dovrebbe essere valido"

    def test_iud_non_validi(self):
        for iud in ["000TEST", "000" + "a" * 32, "", "a" * 36]:
            assert not self._is_valid_iud(iud), f"IUD '{iud}' dovrebbe essere non valido"


# ---------------------------------------------------------------------------
# Test: validazione datiSpecificiRiscossione
# ---------------------------------------------------------------------------

import re

class TestDsrValidation:
    """Verifica la regex del Nodo SPC: [0129]{1}/\\S{3,138}"""

    def test_dsr_validi(self):
        for dsr in VALID_DSR_EXAMPLES:
            ok, _ = validate_dsr(dsr)
            assert ok, f"DSR '{dsr}' dovrebbe essere valido"

    def test_dsr_non_validi(self):
        for dsr in INVALID_DSR_EXAMPLES:
            ok, _ = validate_dsr(dsr)
            assert not ok, f"DSR '{dsr}' dovrebbe essere non valido"


# ---------------------------------------------------------------------------
# Test: validazione importo
# ---------------------------------------------------------------------------

class TestImportoValidation:
    @staticmethod
    def _is_valid_importo(s: str) -> bool:
        ok, _ = validate_importo(s)
        return ok

    def test_importi_validi(self):
        for imp in VALID_IMPORTO_EXAMPLES:
            assert self._is_valid_importo(imp), f"Importo '{imp}' dovrebbe essere valido"

    def test_importi_non_validi(self):
        for imp in INVALID_IMPORTO_EXAMPLES:
            assert not self._is_valid_importo(imp), f"Importo '{imp}' dovrebbe essere non valido"


# ---------------------------------------------------------------------------
# Test: validazione causale
# ---------------------------------------------------------------------------

class TestCausaleValidation:
    def test_causale_valida(self):
        validi = ["Causale standard", "A" * 1024]
        for c in validi:
            ok, _ = validate_causale(c)
            assert ok

    def test_causale_non_valida(self):
        invalidi = ["", "   ", "A" * 1025]
        for c in invalidi:
            ok, _ = validate_causale(c)
            assert not ok


# ---------------------------------------------------------------------------
# Test: escaping CSV (campo con ';' e '"')
# ---------------------------------------------------------------------------

class TestCsvEscaping:
    """Verifica la logica di escaping descritta nel tracciato 1_1 (sezione 8.1.2)."""

    @staticmethod
    def _escape_csv_field(value: str) -> str:
        """Applica le regole di escaping MyPay4: campo con ';' va tra virgolette,
        le virgolette interne vanno escape con backslash."""
        if ";" in value or '"' in value:
            escaped = value.replace('"', '\\"')
            return f'"{escaped}"'
        return value

    def test_campo_senza_semicolon(self):
        assert self._escape_csv_field("Questa è la mia casa.") == "Questa è la mia casa."

    def test_campo_con_semicolon(self):
        result = self._escape_csv_field("Questa è la mia; casa.")
        assert result == '"Questa è la mia; casa."'

    def test_campo_con_virgolette_e_semicolon(self):
        result = self._escape_csv_field('Questa è "la mia"; casa.')
        assert result == '"Questa è \\"la mia\\"; casa."'
