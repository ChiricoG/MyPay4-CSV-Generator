# MyPay4 CSV Generator — Tracciato 1\_4 (v2.3.2)

[![Licenza: EUPL-1.2](https://img.shields.io/badge/Licenza-EUPL--1.2-blue.svg)](https://opensource.org/licenses/EUPL-1.2)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.9-yellow.svg)](https://www.python.org/)
[![Stato sviluppo](https://img.shields.io/badge/Stato-Stabile-green.svg)]()

Applicazione desktop per la creazione, modifica e validazione di file CSV nel formato **MyPay4 tracciato 1\_4**, conforme alle [specifiche di integrazione della Regione Puglia](https://pagamenti.regione.puglia.it) per il portale dei pagamenti PagoPA.

---

## Indice

- [Descrizione](#descrizione)
- [Manuale Utente](MANUALE_UTENTE.md)
- [Funzionalità](#funzionalità)
- [Prerequisiti](#prerequisiti)
- [Installazione](#installazione)
- [Utilizzo](#utilizzo)
- [Struttura del progetto](#struttura-del-progetto)
- [Tracciato CSV supportato](#tracciato-csv-supportato)
- [Test](#test)
- [Licenza](#licenza)
- [Autori](#autori)

---

## Descrizione

MyPay4 CSV Generator è uno strumento desktop (Python/Tkinter) che consente agli operatori degli **Enti Locali** di creare e gestire i flussi CSV di **dovuti** da importare nel portale dei pagamenti **MyPay4** della Regione Puglia, intermediario PagoPA.

Il software implementa integralmente il **tracciato di import versione 1\_4** descritto nel:

> *Manuale Integrazione Ente - MyPay4 v2.2* — Regione Puglia, Direzione ICT e Agenda Digitale, 21/02/2025

---

## Funzionalità

- **Creazione guidata** di righe CSV con validazione in tempo reale di tutti i campi obbligatori e facoltativi del tracciato 1\_4
- Supporto completo per **pagamenti multibeneficiario** (`flagMultiBeneficiario`, ente secondario)
- **Editor visuale bilancio XML** (capitoli, uffici, accertamenti) con parser e builder integrati
- **Aumento massivo importi** (percentuale o valore fisso) con opzioni avanzate di gestione del bilancio XML
- **Importazione e modifica** di CSV esistenti
- **Generazione automatica IUD** con prefisso configurabile
- **Esportazione ZIP** pronto per l'upload via web service `paaSILAutorizzaImportFlusso`
- **Logging rotante** su file per audit e diagnostica (max 5 file × 1 MB)
- Interfaccia grafica Tkinter — nessuna dipendenza da browser o servizi esterni

---

## Prerequisiti

| Componente | Versione minima | Note |
|---|---|---|
| Python | 3.9 ||
| Pillow | 9.0 (opzionale) | Solo per visualizzare il logo |

```powershell
python -m pip -r install requirements.txt
```

---

## Installazione

È consigliato l'uso di un virtual environment:

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -e .
```

## Utilizzo

Per avviare l'applicazione:

```powershell
python main.py
```

### Eseguibile standalone (Windows)

Per generare l'eseguibile `.exe` in modo automatico (versione 2.3.2):

```powershell
python build_exe.py
```

L'eseguibile sarà disponibile nella cartella `dist/MyPay4_Generator_v2.2.0.exe`. Lo script gestisce automaticamente l'icona e l'incorporazione degli asset.

---

## Struttura del progetto

Il progetto è ora organizzato come un pacchetto Python moderno e modularizzato:

```text
.
├── main.py                  # Entry point dell'applicazione
├── pyproject.toml           # Configurazione pacchetto e dipendenze
├── assets/
│   └── logo_mypay4.png      # Logo istituzionale
├── src/
│   └── mypay4_generator/    # Codice sorgente principale
│       ├── core/            # Logica di business, validazione e XML
│       ├── ui/              # Componenti interfaccia grafica (Tkinter)
│       └── utils/           # Utility (logging, helpers)
├── tests/                   # Suite di test unitari (pytest)
└── requirements.txt         # Dipendenze (per installazione classica)
```

---

## Tracciato CSV supportato

Il software genera file CSV conformi al **tracciato 1\_4** (versione più recente) del Manuale di Integrazione MyPay4 v2.2.

| Campo | Obbl. | Lunghezza | Tipo |
|---|---|---|---|
| IUD | ✓ | 1–35 | Alfanumerico |
| codIuv | | 1–35 | Alfanumerico |
| tipoIdentificativoUnivoco | ✓ | 1 | F / G |
| codiceIdentificativoUnivoco | ✓ | 1–35 | CF / P.IVA / ANONIMO |
| anagraficaPagatore | ✓ | 1–70 | Testo |
| dataEsecuzionePagamento | ✓* | 10 | YYYY-MM-DD |
| importoDovuto | ✓ | 3–12 | Decimale |
| tipoDovuto | ✓ | 1–64 | Alfanumerico |
| causaleVersamento | ✓ | 1–1024 | Testo |
| datiSpecificiRiscossione | ✓ | 5–140 | `[0129]/codice` |
| bilancio | | 1–4096 | XML |
| flgGeneraIuv | | — | true/false |
| flagMultiBeneficiario | | — | true/false |
| azione | ✓ | 1 | I / M / A |

---

## Test

```bash
python -m pytest tests/ -v
```

---

## Licenza

Questo software è distribuito sotto licenza **European Union Public Licence v1.2 (EUPL-1.2)**.

Vedi [LICENSE](LICENSE) per il testo completo.

---

## Autori

Gianmarco Chirico — deda.cle
