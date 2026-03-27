# Manuale Utente — MyPay4 CSV Generator

## 1. Introduzione
**MyPay4 CSV Generator** è un'applicazione desktop progettata per la creazione e la gestione dei flussi di pagamento (dovuti) nel formato CSV richiesto dal portale **MyPay4** della Regione Puglia (intermediario PagoPA).

L'applicazione garantisce la conformità al **tracciato 1.4** e permette di validare i dati prima del salvataggio.

---

## 2. Installazione e Avvio
### Utenti Windows
1. Scarica l'ultima release (`MyPay4_Generator_v2.3.2.exe`).
2. Fai doppio clic sul file per avviarlo. Non è necessaria installazione.

---

## 3. Interfaccia Principale
L'applicazione è composta da:
1.  **Barra degli Strumenti**: In alto, contiene i pulsanti per le operazioni principali come **Nuova riga**, **Apri CSV**, **Salva** e **Aumento importi**.
2.  **Tabella Dati**: Al centro, elenca i record caricati con evidenziazione a righe alternate.
3.  **Barra di Stato**: In basso, indica il numero di righe totali e il file correntemente in uso.

---

## 4. Guida alle Funzionalità

### 4.1. Inserimento e Modifica
*   **Nuova riga**: Apre l'editor per un nuovo record.
*   **Modifica / Doppio clic**: Apre l'editor per la riga selezionata.
*   I campi obbligatori sono contrassegnati da un asterisco rosso (`*`).
*   Passando il mouse (hover) sui nomi dei campi, apparirà un **tooltip** con le specifiche tecniche (lunghezza, formato, codici errore).

### 4.2. Editor Bilancio (XML)
Per i record che richiedono la struttura contabile:
1.  Nell'editor di riga, individua il campo **"Bilancio (XML)"**.
2.  Fai clic sul pulsante **"Editor Bilancio"** a destra.
3.  Usa **"Aggiungi Capitolo"** e **"Aggiungi Accertamento"** per comporre la struttura.
4.  L'app calcola il totale in tempo reale e segnala se non corrisponde all'importo dovuto.
5.  Usa **"Conferma e genera XML"** per terminare.

### 4.3. Aumento importi
Questa funzione (accessibile dalla barra strumenti) permette di applicare modifiche massive:
*   **Tipo di aumento**: Percentuale (%) o valore fisso (€).
*   **Gestione bilancio XML**: Permette di decidere come aggiornare l'XML (es. aggiungere la differenza ai capitoli esistenti o sostituirli) per mantenere la coerenza con il nuovo importo calcolato.

---

## 5. Salvataggio e Caricamento
1.  Fai clic su **"Salva"** o **"Salva come..."**.
2.  L'applicazione effettua una validazione preventiva. Se vengono trovati errori, apparirà un avviso (puoi comunque decidere di procedere).
3.  Verrà generato un file con estensione **.zip**.
4.  **Importante**: Il file .zip generato è pronto per l'upload sul portale MyPay4 (es. tramite servizio `paaSILAutorizzaImportFlusso`). Non è necessario estrarre il file CSV contenuto.

---

## 6. Supporto
*   **Username GitHub**: ChiricoG
*   **Indirizzo email**: gianmarco.chirico@clebari.com
*   **Licenza**: EUPL-1.2
