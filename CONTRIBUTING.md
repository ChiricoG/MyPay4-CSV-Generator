# Guida alla contribuzione

Grazie per l'interesse nel contribuire a **MyPay4 CSV Generator**!

Questo documento descrive le linee guida per segnalare bug, proporre nuove funzionalità e inviare Pull Request.

---

## Codice di condotta

Tutti i partecipanti devono rispettare il [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/it/version/2/1/code_of_conduct/).

---

## Come segnalare un bug

1. Verifica che il bug non sia già stato segnalato nelle [Issue aperte](https://github.com/ChiricoG/mypay4-csv-generator/issues).
2. Apri una nuova Issue utilizzando il template **Bug report**.
3. Includi:
   - Versione del software (vedi `pyproject.toml`).
   - Sistema operativo e versione Python.
   - Passi per riprodurre il problema.
   - Comportamento atteso vs. comportamento effettivo.
   - Contenuto del file di log `mypay4_generator.log` (rimuovi eventuali dati personali).

---

## Come proporre una nuova funzionalità

1. Apri una Issue con il template **Feature request**.
2. Descrivi il caso d'uso, citando se possibile il paragrafo del *Manuale Integrazione Ente MyPay4* di riferimento.
3. Attendi il feedback dei maintainer prima di iniziare l'implementazione.

---

## Processo di Pull Request

### Prerequisiti

- Python ≥ 3.9
- `pip install -r requirements.txt`
- `pip install pytest ruff`

### Passi

1. Fai un fork del repository.
2. Crea un branch descrittivo:
   ```bash
   git checkout -b fix/validazione-iud   # per bug fix
   git checkout -b feat/tracciato-1-5    # per nuove funzionalità
   ```
3. Scrivi o aggiorna i test in `tests/`.
4. Esegui la suite di test:
   ```bash
   pytest tests/ -v
   ```
5. Verifica la formattazione:
   ```bash
   ruff check src/
   ```
6. Descrivi le modifiche apportate nella Pull Request.
7. Apri la Pull Request verso il branch `main` con una descrizione chiara.

---

## Convenzioni di codice

- **Lingua**: commenti e docstring in **italiano** (per coerenza con il dominio PA italiana).
- **Docstring**: formato Google Style, obbligatorie su tutte le funzioni e classi pubbliche.
- **Tipi**: annotazioni di tipo (`typing`) raccomandate per le funzioni nuove.
- **Header SPDX**: ogni file sorgente deve iniziare con:
  ```python
  # SPDX-License-Identifier: EUPL-1.2
  # SPDX-FileCopyrightText: 2025 Gianmarco Chirico
  ```
- **Costanti** in `UPPER_SNAKE_CASE`, funzioni private con prefisso `_`.
- **Messaggi di errore**: usare i codici standardizzati `MP-NNN` definiti in `VALIDATION_ERRORS`.

---

## Struttura dei test

```
tests/
├── __init__.py
├── test_validators.py     # Validazione campi CSV (IUD, CF, importo, DSR…)
└── test_csv_export.py     # Export CSV e ZIP
```

Ogni test deve essere indipendente, deterministico e non richiedere connessioni di rete.

---

## Licenza dei contributi

Inviando una Pull Request accetti che il tuo contributo venga distribuito sotto licenza **EUPL-1.2**, come il resto del progetto.
