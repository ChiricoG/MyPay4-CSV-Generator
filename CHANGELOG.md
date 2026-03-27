# Changelog

Tutte le modifiche rilevanti a questo progetto sono documentate in questo file.

Il formato segue [Keep a Changelog](https://keepachangelog.com/it/1.0.0/)
e il progetto adotta il [Semantic Versioning](https://semver.org/lang/it/).

---

## [2.3.2] — 2025-03-27

### Risolto
- **Stabilità Globale**: Bonifica totale di tutti i dialoghi (`RowEditor`, `BilancioEditor`, `BulkIncreaseDialog`) per prevenire il `TclError` legato allo scroll del mouse dopo la chiusura delle finestre.

## [2.3.1] — 2025-03-27

### Risolto
- **Mouse Wheel**: Fix per il crash nel `BilancioEditor` durante l'uso della rotellina del mouse.

## [2.3.0] — 2025-03-27

### Aggiunto
- **Parità Funzionale 100%**: Ripristinate tutte le logiche di business della v2.1.0 omesse nel refactoring iniziale.
- **Validazione Pre-Salvataggio**: Controllo di tutti i record con popup di riepilogo errori prima della generazione dello ZIP.
- **Supporto ZIP**: Implementata l'apertura diretta di archivi ZIP contenenti CSV.
- **Rilevamento Automatico**: Implementato il riconoscimento automatico della versione del tracciato (1.1-1.4) e dell'Ente (IPA) dal nome file.
- **Exception Hook**: Ripristinato il `sys.excepthook` per la gestione globale degli errori non gestiti.

## [2.2.1] — 2025-03-27

### Risolto
- **Bulk Increase**: Risolto `AttributeError: var_S_cod_cap` nel wizard di aumento massivo dovuto a una mappatura errata dei prefissi.

## [2.2.0] — 2025-03-27

### Modificato
- **Refactoring Modulare**: Trasformazione dello script monolitico in un pacchetto Python professionale (`src/mypay4_generator`).
- **Parità UI/UX**: Ripristino integrale di tutti i 35 campi, dei tooltip originali e del look & feel della versione 2.1.0.
- **Packaging**: Aggiunto supporto per `pyproject.toml`, `pip install` e script di build EXE centralizzato.


## [2.1.0] — 2025-03-27

### Aggiunto
- Licenza EUPL-1.2 (riuso PA italiana ed europea).
- File `publiccode.yml` conforme alle Linee Guida AGID sul riuso del software.
- File `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `AUTHORS.md`, `SECURITY.md`.
- File `requirements.txt` e `pyproject.toml` (PEP 517/518).
- Docstring complete su tutte le funzioni e classi pubbliche.
- Header SPDX (`SPDX-License-Identifier: EUPL-1.2`) in cima al sorgente.
- Suite di test in `tests/` con `pytest`.
- Asset logo separato in `assets/logo_mypay4.png` (rimosso `_LOGO_B64` inline).
- Logging strutturato: formato JSON opzionale via variabile d'ambiente `MYPAY4_LOG_JSON=1`.
- Messaggi di validazione standardizzati con codici errore alfanumerici (`MP-001` … `MP-NNN`).

### Modificato
- Header del file sorgente: copyright aggiornato, licenza proprietaria sostituita con EUPL-1.2.
- `_LOGO_B64`: la costante inline è stata rimossa; il logo viene caricato da `assets/logo_mypay4.png`.
- Logging: aggiunto formatter JSON alternativo per ambienti di produzione.

### Deprecato
- Costante `_LOGO_B64` inline (rimossa in questa versione).

---

## [2.0.0] — 2025-01-01

### Aggiunto
- Supporto completo al **tracciato 1\_4** (campi multibeneficiario e bilancio XML).
- Aumento massivo importi: percentuale, valore fisso, gestione capitoli bilancio XML (opzioni A/B/C).
- Funzione di importazione CSV / ZIP esistente.
- Logging rotante su file (RotatingFileHandler, max 5 × 1 MB).
- Handler globale eccezioni non gestite (`sys.excepthook`).

### Modificato
- Interfaccia grafica completamente ridisegnata (tema blu MyPay / PagoPA).
- Tooltip contestuali su ogni campo con riferimento al manuale di integrazione.

---

## [1.0.0] — 2022-06-27

### Aggiunto
- Prima versione pubblica.
- Supporto tracciato 1\_0 e 1\_1.
- Interfaccia grafica Tkinter base.
- Esportazione CSV e ZIP.
