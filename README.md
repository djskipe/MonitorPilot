# 🖥️ MonitorPilot

**Decidi tu su quale monitor si apre ogni app.**
**You decide which monitor each app opens on.**

MonitorPilot è un software per Windows con interfaccia grafica che gestisce i tuoi monitor e posiziona automaticamente app e finestre dove vuoi tu. Include anche le funzioni principali di MultiMonitorTool.

MonitorPilot is a Windows desktop app with a graphical interface that manages your monitors and automatically places apps and windows where you want them. It also includes the main features of MultiMonitorTool.

---

## 🇮🇹 Italiano

### Funzioni principali
- **Regole automatiche**: scegli un programma (per nome del processo o titolo della finestra) e il monitor su cui deve aprirsi.
- **Gestione monitor**: elenco dei monitor collegati con risoluzione, posizione e monitor principale.
- **Rinomina i monitor**: dai un nome personalizzato ai monitor invece di "Generic PnP Monitor", oppure ripristina il nome originale.
- **Avvio con Windows**: opzione per far partire il programma all'accensione del PC.
- **Icona nella tray**: resta attivo in background e si controlla dall'area di notifica.
- **Doppia lingua**: Italiano e English, con cambio immediato dalle Impostazioni e scelta salvata.
- **Icona dedicata** nella barra delle applicazioni, personalizzabile con un file `monitorpilot.ico`.

### Installazione rapida
1. Scarica o clona il repository.
2. Fai doppio clic su `avvia_monitorpilot.bat`.
   Al primo avvio controlla se Python è installato (versione consigliata **3.12**), lo installa se manca, poi installa le librerie necessarie e apre il programma.
   Dalle volte successive verifica che sia tutto a posto e avvia direttamente MonitorPilot.

### Avvio manuale
```bash
pip install -r requirements.txt
python monitorpilot.py
```

### Requisiti
- Windows 10 / 11
- Python 3.12 (consigliato)

### Come creare una regola
1. Apri l'app che vuoi gestire e lasciala aperta.
2. In **Regole** scegli la finestra dall'elenco oppure scrivi il nome del processo (es. `XboxPcApp.exe`) o il titolo della finestra.
3. Scegli il monitor di destinazione e salva.

> **Suggerimento:** per trovare il nome del processo apri Gestione attività (`Ctrl+Maiusc+Esc`), tasto destro sull'app → *Vai ai dettagli*.

---

## 🇬🇧 English

### Main features
- **Automatic rules**: pick a program (by process name or window title) and the monitor it should open on.
- **Monitor management**: list of connected monitors with resolution, position and primary display.
- **Rename monitors**: give custom names instead of "Generic PnP Monitor", or restore the original name.
- **Start with Windows**: option to launch the app at PC startup.
- **Tray icon**: runs in the background and is controlled from the notification area.
- **Two languages**: Italian and English, switchable instantly from Settings, choice is saved.
- **Dedicated taskbar icon**, customizable with a `monitorpilot.ico` file.

### Quick install
1. Download or clone the repository.
2. Double-click `avvia_monitorpilot.bat`.
   On first run it checks whether Python is installed (recommended version **3.12**), installs it if missing, installs the required libraries and launches the app.
   On later runs it checks everything is in place and starts MonitorPilot directly.

### Manual start
```bash
pip install -r requirements.txt
python monitorpilot.py
```

### Requirements
- Windows 10 / 11
- Python 3.12 (recommended)

### How to create a rule
1. Open the app you want to manage and keep it running.
2. In **Rules**, pick the window from the list or type the process name (e.g. `XboxPcApp.exe`) or the window title.
3. Choose the target monitor and save.

> **Tip:** to find the process name, open Task Manager (`Ctrl+Shift+Esc`), right-click the app → *Go to details*.

---

## 📁 Struttura / Structure
```
MonitorPilot/
├── monitorpilot.py          # programma principale / main program
├── avvia_monitorpilot.bat   # installazione e avvio / setup and launcher
├── LEGGIMI.txt              # guida / guide
└── monitorpilot.ico         # (opzionale / optional) icona personalizzata
```
