# -*- coding: utf-8 -*-
"""MonitorPilot - gestione monitor, finestre e profili per Windows."""
import sys
import os
import json
import time
import ctypes
import traceback
import argparse
from pathlib import Path

# DPI per-monitor: va impostato prima della creazione di QApplication.
def imposta_dpi_awareness():
    if os.name != 'nt':
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

imposta_dpi_awareness()

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor, QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog, QDialogButtonBox,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QFormLayout, QMessageBox,
    QSystemTrayIcon, QMenu, QFileDialog, QInputDialog, QGroupBox,
    QStatusBar)

try:
    import psutil
except Exception as exc:
    psutil = None
    _PSUTIL_ERROR = str(exc)
else:
    _PSUTIL_ERROR = ''

try:
    import win32api
    import win32con
    import win32gui
    import win32process
except Exception as exc:
    win32api = win32con = win32gui = win32process = None
    _WIN32_ERROR = str(exc)
else:
    _WIN32_ERROR = ''

APP_NAME = 'MonitorPilot'
# Centralized UI translations.
STRINGS = {
    'it': {
        'Regola finestra': 'Regola finestra',
        'es. chrome.exe': 'es. chrome.exe',
        'Sfoglia...': 'Sfoglia...',
        'Programmi aperti': 'Programmi aperti',
        'Facoltativo: testo contenuto nel titolo': 'Facoltativo: testo contenuto nel titolo',
        'Regola abilitata': 'Regola abilitata',
        'Processo (.exe)': 'Processo (.exe)',
        'Filtro titolo': 'Filtro titolo',
        'Monitor': 'Monitor',
        'Modalità': 'Modalità',
        'Larghezza': 'Larghezza',
        'Altezza': 'Altezza',
        'Coordinate/dimensioni': 'Coordinate/dimensioni',
        'Nessun programma visibile rilevato': 'Nessun programma visibile rilevato',
        'Seleziona eseguibile': 'Seleziona eseguibile',
        'Eseguibili (*.exe)': 'Eseguibili (*.exe)',
        'Sposta finestra': 'Sposta finestra',
        'MonitorPilot · Desktop Control': 'MonitorPilot · Desktop Control',
        '●  MONITORAGGIO ATTIVO': '●  MONITORAGGIO ATTIVO',
        'Pronto · regole applicate una sola volta per finestra': 'Pronto · regole applicate una sola volta per finestra',
        'Windows richiesto': 'Windows richiesto',
        'MonitorPilot usa API Win32 e può funzionare soltanto su Windows. La UI è stata avviata in modalità dimostrativa.': 'MonitorPilot usa API Win32 e può funzionare soltanto su Windows. La UI è stata avviata in modalità dimostrativa.',
        'Dipendenze mancanti': 'Dipendenze mancanti',
        'Impossibile caricare pywin32 o psutil. Avvia avvia_monitorpilot.bat per installare i componenti richiesti.': 'Impossibile caricare pywin32 o psutil. Avvia avvia_monitorpilot.bat per installare i componenti richiesti.',
        'Processo': 'Processo',
        'Stato': 'Stato',
        'ID': 'ID',
        '＋  Aggiungi': '＋  Aggiungi',
        '✎  Modifica': '✎  Modifica',
        '－  Elimina': '－  Elimina',
        'Aggiorna': 'Aggiorna',
        'Una regola viene applicata una sola volta a ogni nuova finestra corrispondente. In seguito puoi spostarla liberamente.': 'Una regola viene applicata una sola volta a ogni nuova finestra corrispondente. In seguito puoi spostarla liberamente.',
        'Regole': 'Regole',
        'Attiva': 'Attiva',
        'Disattiva': 'Disattiva',
        'Dato mancante': 'Dato mancante',
        'Inserisci il nome del processo.': 'Inserisci il nome del processo.',
        'Elimina regola': 'Elimina regola',
        'Eliminare la regola selezionata?': 'Eliminare la regola selezionata?',
        '#': '#',
        'Device name': 'Device name',
        'Nome': 'Nome',
        'Risoluzione': 'Risoluzione',
        'Posizione': 'Posizione',
        'Hz': 'Hz',
        'DPI': 'DPI',
        'Primario/Attivo': 'Primario/Attivo',
        '↻  Aggiorna': '↻  Aggiorna',
        'Identifica': 'Identifica',
        'Imposta primario': 'Imposta primario',
        'Attiva/Disattiva': 'Attiva/Disattiva',
        'Risoluzione / frequenza': 'Risoluzione / frequenza',
        'Rinomina': 'Rinomina',
        'Ripristina nome originale': 'Ripristina nome originale',
        'Spegni monitor': 'Spegni monitor',
        'Accendi monitor': 'Accendi monitor',
        'Esporta JSON': 'Esporta JSON',
        '●  NESSUN MONITOR RILEVATO': '●  NESSUN MONITOR RILEVATO',
        '●  {n} MONITOR ATTIVI': '●  {n} MONITOR ATTIVI',
        'Rinomina monitor': 'Rinomina monitor',
        'Windows non ha fornito un identificativo hardware stabile per questo monitor.': 'Windows non ha fornito un identificativo hardware stabile per questo monitor.',
        'Nome personalizzato:': 'Nome personalizzato:',
        'Impossibile': 'Impossibile',
        'Windows non ha accettato la modifica (codice %s).': 'Windows non ha accettato la modifica (codice %s).',
        'Errore': 'Errore',
        'Operazione non consentita': 'Operazione non consentita',
        'Non puoi disattivare l’ultimo monitor attivo.': 'Non puoi disattivare l’ultimo monitor attivo.',
        'Conferma': 'Conferma',
        'La modifica può spostare le finestre o richiedere un ripristino. Continuare?': 'La modifica può spostare le finestre o richiedere un ripristino. Continuare?',
        'Non riuscito': 'Non riuscito',
        'Windows ha rifiutato il cambio (codice {rc}).': 'Windows ha rifiutato il cambio (codice {rc}).',
        'Modalità disponibile': 'Modalità disponibile',
        'Risoluzione e frequenza': 'Risoluzione e frequenza',
        'Modalità rifiutata (codice ': 'Modalità rifiutata (codice ',
        'Modalità rifiutata (codice {rc}).': 'Modalità rifiutata (codice {rc}).',
        'Esporta stato': 'Esporta stato',
        'monitorpilot-export.json': 'monitorpilot-export.json',
        'JSON (*.json)': 'JSON (*.json)',
        'Esportazione completata': 'Esportazione completata',
        'Errore esportazione': 'Errore esportazione',
        'Titolo': 'Titolo',
        'Dimensione': 'Dimensione',
        'X, Y': 'X, Y',
        'Finestre': 'Finestre',
        'Sposta…': 'Sposta…',
        'Massimizza': 'Massimizza',
        'Minimizza': 'Minimizza',
        'Ripristina': 'Ripristina',
        'Chiudi': 'Chiudi',
        'Sempre in primo piano': 'Sempre in primo piano',
        'Crea regola da finestra': 'Crea regola da finestra',
        'Spostamento in blocco': 'Spostamento in blocco',
        'Da': 'Da',
        'A': 'A',
        'Sposta tutte': 'Sposta tutte',
        'Spostamento non riuscito': 'Spostamento non riuscito',
        'Windows non ha consentito di spostare questa finestra.': 'Windows non ha consentito di spostare questa finestra.',
        'Chiudi finestra': 'Chiudi finestra',
        'Inviare un messaggio di chiusura alla finestra?': 'Inviare un messaggio di chiusura alla finestra?',
        'Operazione non riuscita': 'Operazione non riuscita',
        'Spostare {n} finestre sul monitor selezionato?': 'Spostare {n} finestre sul monitor selezionato?',
        'Nome profilo': 'Nome profilo',
        'Finestre salvate': 'Finestre salvate',
        'Salva layout corrente': 'Salva layout corrente',
        'Ripristina profilo': 'Ripristina profilo',
        'Elimina profilo': 'Elimina profilo',
        'Il ripristino abbina prima processo + titolo (parziale, senza distinzione maiuscole/minuscole), poi soltanto il processo. Le impostazioni video sono memorizzate quando leggibili; l’applicazione automatica della topologia non è garantita da Windows.': 'Il ripristino abbina prima processo + titolo (parziale, senza distinzione maiuscole/minuscole), poi soltanto il processo. Le impostazioni video sono memorizzate quando leggibili; l’applicazione automatica della topologia non è garantita da Windows.',
        'Salva profilo': 'Salva profilo',
        'Nome del nuovo layout:': 'Nome del nuovo layout:',
        "Ripristinare '{name}'? Le finestre corrispondenti verranno spostate.": "Ripristinare '{name}'? Le finestre corrispondenti verranno spostate.",
        'Nuovo nome:': 'Nuovo nome:',
        'Eliminare il profilo selezionato?': 'Eliminare il profilo selezionato?',
        'Comportamento': 'Comportamento',
        'Avvia MonitorPilot all’accesso a Windows': 'Avvia MonitorPilot all’accesso a Windows',
        'Avvia minimizzato nella tray': 'Avvia minimizzato nella tray',
        'Abilita motore regole globale': 'Abilita motore regole globale',
        'Controllo regole ogni': 'Controllo regole ogni',
        ' ms': ' ms',
        'Salva impostazioni': 'Salva impostazioni',
        'Configurazione: ': 'Configurazione: ',
        '\nLa tray resta attiva quando chiudi la finestra. Per uscire usa il menu MonitorPilot sull’icona nell’area di notifica.': '\nLa tray resta attiva quando chiudi la finestra. Per uscire usa il menu MonitorPilot sull’icona nell’area di notifica.',
        'Impostazioni': 'Impostazioni',
        'Avvio Windows non aggiornato': 'Avvio Windows non aggiornato',
        'Impostazione locale salvata, ma non è stato possibile aggiornare il Registro:\n{e}': 'Impostazione locale salvata, ma non è stato possibile aggiornare il Registro:\n{e}',
        'Impostazioni salvate': 'Impostazioni salvate',
        'Errore configurazione': 'Errore configurazione',
        'Apri MonitorPilot': 'Apri MonitorPilot',
        'Esci': 'Esci',
        'L’applicazione continua nell’area di notifica.': 'L’applicazione continua nell’area di notifica.',
        'È già in esecuzione.': 'È già in esecuzione.',
        'MonitorPilot': 'MonitorPilot',
        'Avvio MonitorPilot non riuscito:\n': 'Avvio MonitorPilot non riuscito:\n',
    },
    'en': {
        'Regola finestra': 'Window rule',
        'es. chrome.exe': 'e.g. chrome.exe',
        'Sfoglia...': 'Browse...',
        'Programmi aperti': 'Open programs',
        'Facoltativo: testo contenuto nel titolo': 'Optional text contained in the title',
        'Regola abilitata': 'Rule enabled',
        'Processo (.exe)': 'Process (.exe)',
        'Filtro titolo': 'Title filter',
        'Monitor': 'Monitor',
        'Modalità': 'Mode',
        'Larghezza': 'Width',
        'Altezza': 'Height',
        'Coordinate/dimensioni': 'Coordinates/size',
        'Nessun programma visibile rilevato': 'No visible programs detected',
        'Seleziona eseguibile': 'Select executable',
        'Eseguibili (*.exe)': 'Executables (*.exe)',
        'Sposta finestra': 'Move window',
        'MonitorPilot · Desktop Control': 'MonitorPilot · Desktop Control',
        '●  MONITORAGGIO ATTIVO': '●  MONITORING ACTIVE',
        'Pronto · regole applicate una sola volta per finestra': 'Ready · rules applied once per window',
        'Windows richiesto': 'Windows required',
        'MonitorPilot usa API Win32 e può funzionare soltanto su Windows. La UI è stata avviata in modalità dimostrativa.': 'MonitorPilot uses Win32 APIs and only works on Windows. The UI started in demo mode.',
        'Dipendenze mancanti': 'Missing dependencies',
        'Impossibile caricare pywin32 o psutil. Avvia avvia_monitorpilot.bat per installare i componenti richiesti.': 'Could not load pywin32 or psutil. Run avvia_monitorpilot.bat to install the required components.',
        'Processo': 'Process',
        'Stato': 'Status',
        'ID': 'ID',
        '＋  Aggiungi': '＋  Add',
        '✎  Modifica': '✎  Edit',
        '－  Elimina': '－  Delete',
        'Aggiorna': 'Refresh',
        'Una regola viene applicata una sola volta a ogni nuova finestra corrispondente. In seguito puoi spostarla liberamente.': 'Each matching new window receives a rule only once. You can move it freely afterward.',
        'Regole': 'Rules',
        'Attiva': 'Enabled',
        'Disattiva': 'Disabled',
        'Dato mancante': 'Missing information',
        'Inserisci il nome del processo.': 'Enter the process name.',
        'Elimina regola': 'Delete rule',
        'Eliminare la regola selezionata?': 'Delete the selected rule?',
        '#': '#',
        'Device name': 'Device name',
        'Nome': 'Name',
        'Risoluzione': 'Resolution',
        'Posizione': 'Position',
        'Hz': 'Hz',
        'DPI': 'DPI',
        'Primario/Attivo': 'Primary/Active',
        '↻  Aggiorna': '↻  Refresh',
        'Identifica': 'Identify',
        'Imposta primario': 'Set primary',
        'Attiva/Disattiva': 'Enable/Disable',
        'Risoluzione / frequenza': 'Resolution / refresh rate',
        'Rinomina': 'Rename',
        'Ripristina nome originale': 'Restore original name',
        'Spegni monitor': 'Turn monitor off',
        'Accendi monitor': 'Turn monitor on',
        'Esporta JSON': 'Export JSON',
        '●  NESSUN MONITOR RILEVATO': '●  NO MONITORS DETECTED',
        '●  {n} MONITOR ATTIVI': '●  {n} ACTIVE MONITORS',
        'Rinomina monitor': 'Rename monitor',
        'Windows non ha fornito un identificativo hardware stabile per questo monitor.': 'Windows did not provide a stable hardware identifier for this monitor.',
        'Nome personalizzato:': 'Custom name:',
        'Impossibile': 'Unable',
        'Windows non ha accettato la modifica (codice %s).': 'Windows did not accept the change (code %s).',
        'Errore': 'Error',
        'Operazione non consentita': 'Operation not allowed',
        'Non puoi disattivare l’ultimo monitor attivo.': 'You cannot disable the last active monitor.',
        'Conferma': 'Confirm',
        'La modifica può spostare le finestre o richiedere un ripristino. Continuare?': 'This change may move windows or require a restore. Continue?',
        'Non riuscito': 'Failed',
        'Windows ha rifiutato il cambio (codice {rc}).': 'Windows rejected the change (code {rc}).',
        'Modalità disponibile': 'Available mode',
        'Risoluzione e frequenza': 'Resolution and refresh rate',
        'Modalità rifiutata (codice ': 'Mode rejected (code ',
        'Modalità rifiutata (codice {rc}).': 'Mode rejected (code {rc}).',
        'Esporta stato': 'Export state',
        'monitorpilot-export.json': 'monitorpilot-export.json',
        'JSON (*.json)': 'JSON (*.json)',
        'Esportazione completata': 'Export complete',
        'Errore esportazione': 'Export error',
        'Titolo': 'Title',
        'Dimensione': 'Size',
        'X, Y': 'X, Y',
        'Finestre': 'Windows',
        'Sposta…': 'Move…',
        'Massimizza': 'Maximize',
        'Minimizza': 'Minimize',
        'Ripristina': 'Restore',
        'Chiudi': 'Close',
        'Sempre in primo piano': 'Always on top',
        'Crea regola da finestra': 'Create rule from window',
        'Spostamento in blocco': 'Bulk move',
        'Da': 'From',
        'A': 'To',
        'Sposta tutte': 'Move all',
        'Spostamento non riuscito': 'Move failed',
        'Windows non ha consentito di spostare questa finestra.': 'Windows could not move this window.',
        'Chiudi finestra': 'Close window',
        'Inviare un messaggio di chiusura alla finestra?': 'Send a close message to the window?',
        'Operazione non riuscita': 'Operation failed',
        'Spostare {n} finestre sul monitor selezionato?': 'Move {n} windows to the selected monitor?',
        'Nome profilo': 'Profile name',
        'Finestre salvate': 'Saved windows',
        'Salva layout corrente': 'Save current layout',
        'Ripristina profilo': 'Restore profile',
        'Elimina profilo': 'Delete profile',
        'Il ripristino abbina prima processo + titolo (parziale, senza distinzione maiuscole/minuscole), poi soltanto il processo. Le impostazioni video sono memorizzate quando leggibili; l’applicazione automatica della topologia non è garantita da Windows.': 'Restore matches process + title first (partial, case-insensitive), then process only. Video settings are stored when readable; Windows does not guarantee automatic topology changes.',
        'Salva profilo': 'Save profile',
        'Nome del nuovo layout:': 'Name for the new layout:',
        "Ripristinare '{name}'? Le finestre corrispondenti verranno spostate.": "Restore '{name}'? Matching windows will be moved.",
        'Nuovo nome:': 'New name:',
        'Eliminare il profilo selezionato?': 'Delete the selected profile?',
        'Comportamento': 'Behavior',
        'Avvia MonitorPilot all’accesso a Windows': 'Start MonitorPilot when you sign in to Windows',
        'Avvia minimizzato nella tray': 'Start minimized to the notification area',
        'Abilita motore regole globale': 'Enable global rules engine',
        'Controllo regole ogni': 'Check rules every',
        ' ms': ' ms',
        'Salva impostazioni': 'Save settings',
        'Configurazione: ': 'Configuration: ',
        '\nLa tray resta attiva quando chiudi la finestra. Per uscire usa il menu MonitorPilot sull’icona nell’area di notifica.': '\nThe notification area icon remains active when you close the window. To exit, use the MonitorPilot icon menu.',
        'Impostazioni': 'Settings',
        'Avvio Windows non aggiornato': 'Windows startup setting not updated',
        'Impostazione locale salvata, ma non è stato possibile aggiornare il Registro:\n{e}': 'Local setting saved, but the Registry could not be updated:\n{e}',
        'Impostazioni salvate': 'Settings saved',
        'Errore configurazione': 'Configuration error',
        'Apri MonitorPilot': 'Open MonitorPilot',
        'Esci': 'Exit',
        'L’applicazione continua nell’area di notifica.': 'The application continues running in the notification area.',
        'È già in esecuzione.': 'It is already running.',
        'MonitorPilot': 'MonitorPilot',
        'Avvio MonitorPilot non riuscito:\n': 'Could not start MonitorPilot:\n',
    },
}

_EXTRA_STRINGS = {
    'it': {
        'Massimizzata': 'Massimizzata',
        'Schermo intero': 'Schermo intero',
        'Centrata': 'Centrata',
        'Dimensione personalizzata': 'Dimensione personalizzata',
        'Mantieni dimensione': 'Mantieni dimensione',
        'CONTROL ROOM  /  WINDOWS DESKTOP': 'CONTROL ROOM  /  WINDOWS DESKTOP',
        'MONITORPILOT': 'MONITORPILOT',
        '#': '#',
        'Primario · ': 'Primario · ',
        'Attivo': 'Attivo',
        'Non attivo': 'Non attivo',
        'Profili': 'Profili',
        'Rinomina profilo': 'Rinomina profilo',
        'Aggiorna': 'Aggiorna',
        'Sposta': 'Sposta',
        'Spostare {count} finestre sul monitor selezionato?': 'Spostare {count} finestre sul monitor selezionato?',
        'Lingua / Language': 'Lingua / Language',
        'Aggiungi': 'Aggiungi',
        'Finestre salvate': 'Finestre salvate',
        'fine': 'fine',
        'Salva': 'Salva',
        'Annulla': 'Annulla',
        'OK': 'OK',
        'Nome del nuovo layout:': 'Nome del nuovo layout:',
        'Avvia nascosto nell’area di notifica': 'Avvia nascosto nell’area di notifica',
        'Impostazione locale salvata, ma non è stato possibile aggiornare il Registro:\n{e}': 'Impostazione locale salvata, ma non è stato possibile aggiornare il Registro:\n{e}',
        'Avvio MonitorPilot non riuscito:\n{error}\n\n{trace}': 'Avvio MonitorPilot non riuscito:\n{error}\n\n{trace}',
        'Errore configurazione': 'Errore configurazione',
        'Esportazione completata': 'Esportazione completata',
        '●  {count} MONITOR ATTIVI': '●  {count} MONITOR ATTIVI',
        '{count} finestre · {index}': '{count} finestre · {index}',
    },
    'en': {
        'Massimizzata': 'Maximized',
        'Schermo intero': 'Fullscreen',
        'Centrata': 'Centered',
        'Dimensione personalizzata': 'Custom size',
        'Mantieni dimensione': 'Keep size',
        'CONTROL ROOM  /  WINDOWS DESKTOP': 'CONTROL ROOM  /  WINDOWS DESKTOP',
        'MONITORPILOT': 'MONITORPILOT',
        '#': '#',
        'Primario · ': 'Primary · ',
        'Attivo': 'Active',
        'Non attivo': 'Inactive',
        'Profili': 'Profiles',
        'Rinomina profilo': 'Rename profile',
        'Aggiorna': 'Refresh',
        'Sposta': 'Move',
        'Spostare {count} finestre sul monitor selezionato?': 'Move {count} windows to the selected monitor?',
        'Lingua / Language': 'Language / Lingua',
        'Aggiungi': 'Add',
        'Finestre salvate': 'Saved windows',
        'fine': 'fine',
        'Salva': 'Save',
        'Annulla': 'Cancel',
        'OK': 'OK',
        'Nome del nuovo layout:': 'Name for the new layout:',
        'Avvia nascosto nell’area di notifica': 'Start hidden in the notification area',
        'Impostazione locale salvata, ma non è stato possibile aggiornare il Registro:\n{e}': 'Local setting saved, but the Registry could not be updated:\n{e}',
        'Avvio MonitorPilot non riuscito:\n{error}\n\n{trace}': 'Could not start MonitorPilot:\n{error}\n\n{trace}',
        'Errore configurazione': 'Configuration error',
        'Esportazione completata': 'Export completed',
        '●  {count} MONITOR ATTIVI': '●  {count} ACTIVE MONITORS',
        '{count} finestre · {index}': '{count} windows · {index}',
    },
}
for _lang in ('it', 'en'):
    STRINGS[_lang].update(_EXTRA_STRINGS[_lang])


_EXTRA_REPAIRS = {
    'it': {
        'Non attivo': 'Non attivo',
        'Massimizzata': 'Massimizzata',
        'Schermo intero': 'Schermo intero',
        'Centrata': 'Centrata',
        'Dimensione personalizzata': 'Dimensione personalizzata',
        'Mantieni dimensione': 'Mantieni dimensione',
        'CONTROL ROOM  /  WINDOWS DESKTOP': 'CONTROL ROOM  /  WINDOWS DESKTOP',
        'MONITORPILOT': 'MONITORPILOT',
        'Profili': 'Profili',
        'Rinomina profilo': 'Rinomina profilo',
        'Attivo': 'Attivo',
        'Primario · ': 'Primario · ',
        'Elimina': 'Elimina',
        'Lingua / Language': 'Lingua / Language',
        'Italiano': 'Italiano',
        'English': 'English',
        'Avvia nascosto nell’area di notifica': 'Avvia nascosto nell’area di notifica',
        'Esportazione completata': 'Esportazione completata',
        'Avvio MonitorPilot non riuscito:': 'Avvio MonitorPilot non riuscito:',
        'È già in esecuzione.': 'È già in esecuzione.',
        'Configurazione: ': 'Configurazione: ',
        '\nLa tray resta attiva quando chiudi la finestra. Per uscire usa il menu MonitorPilot sull’icona nell’area di notifica.': '\nLa tray resta attiva quando chiudi la finestra. Per uscire usa il menu MonitorPilot sull’icona nell’area di notifica.',
        'Impostazione locale salvata, ma non è stato possibile aggiornare il Registro:\n{e}': 'Impostazione locale salvata, ma non è stato possibile aggiornare il Registro:\n{e}',
        'Attiva': 'Attiva',
        'Disattiva': 'Disattiva',
        '{count} finestre · {index}': '{count} finestre · {index}',
        '●  {n} MONITOR ATTIVI': '●  {n} MONITOR ATTIVI',
        '●  NESSUN MONITOR RILEVATO': '●  NESSUN MONITOR RILEVATO',
        'MONITORAGGIO': 'MONITORAGGIO',
    },
    'en': {
        'Non attivo': 'Inactive',
        'Massimizzata': 'Maximized',
        'Schermo intero': 'Fullscreen',
        'Centrata': 'Centered',
        'Dimensione personalizzata': 'Custom size',
        'Mantieni dimensione': 'Keep size',
        'CONTROL ROOM  /  WINDOWS DESKTOP': 'CONTROL ROOM  /  WINDOWS DESKTOP',
        'MONITORPILOT': 'MONITORPILOT',
        'Profili': 'Profiles',
        'Rinomina profilo': 'Rename profile',
        'Attivo': 'Active',
        'Primario · ': 'Primary · ',
        'Elimina': 'Delete',
        'Lingua / Language': 'Language / Lingua',
        'Italiano': 'Italian',
        'English': 'English',
        'Avvia nascosto nell’area di notifica': 'Start hidden in the notification area',
        'Esportazione completata': 'Export complete',
        'Avvio MonitorPilot non riuscito:': 'Could not start MonitorPilot:',
        'È già in esecuzione.': 'Already running.',
        'Configurazione: ': 'Configuration: ',
        '\nLa tray resta attiva quando chiudi la finestra. Per uscire usa il menu MonitorPilot sull’icona nell’area di notifica.': '\nThe tray remains active when the window is closed. To exit, use the MonitorPilot menu on its notification-area icon.',
        'Impostazione locale salvata, ma non è stato possibile aggiornare il Registro:\n{e}': 'Local setting saved, but the Registry could not be updated:\n{e}',
        'Attiva': 'Enabled',
        'Disattiva': 'Disabled',
        '{count} finestre · {index}': '{count} windows · {index}',
        '●  {n} MONITOR ATTIVI': '●  {n} ACTIVE MONITORS',
        '●  NESSUN MONITOR RILEVATO': '●  NO MONITORS DETECTED',
        'MONITORAGGIO': 'MONITORING',
    },
}
for _language in ('it', 'en'):
    STRINGS[_language].update(_EXTRA_REPAIRS[_language])

CURRENT_LANGUAGE = 'it'
def t(key, **fmt):
    value = STRINGS.get(CURRENT_LANGUAGE, STRINGS['en']).get(key, key)
    try: return value.format(**fmt) if fmt else value
    except Exception: return value

def mode_value(label):
    return next((m for m in MODES if t(m) == label), label)

def windows_default_language():
    try:
        import locale
        return 'it' if (locale.getlocale()[0] or '').lower().startswith('it') else 'en'
    except Exception:
        return 'en'

APP_DIR = Path(os.environ.get('APPDATA', str(Path.home()))) / APP_NAME
CONFIG_PATH = APP_DIR / 'config.json'
RUN_KEY = r'Software\Microsoft\Windows\CurrentVersion\Run'
MODES = ['Massimizzata', 'Schermo intero', 'Centrata', 'Dimensione personalizzata', 'Mantieni dimensione']

_MONITOR_ALIASES = {}

DEFAULT_CONFIG = {
    'rules': [], 'profiles': [], 'monitor_aliases': {}, 'settings': {
        'start_minimized': False, 'rule_interval': 1000, 'rules_enabled': True
    }
}

# -------------------------- Configurazione e logica pura ---------------------
def carica_config():
    """Legge config salvando una copia di sicurezza dei dati incompatibili."""
    APP_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with CONFIG_PATH.open('r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError('La configurazione non è un oggetto JSON.')
    except FileNotFoundError:
        data = {}
    except Exception as exc:
        try:
            CONFIG_PATH.rename(CONFIG_PATH.with_suffix('.json.corrotto'))
        except Exception:
            pass
        data = {}
        print('Configurazione non leggibile; ripristinati i valori predefiniti:', exc)
    out = dict(DEFAULT_CONFIG)
    out.update(data)
    out['language'] = out.get('language') if out.get('language') in ('it', 'en') else windows_default_language()
    out['rules'] = out.get('rules') if isinstance(out.get('rules'), list) else []
    out['monitor_aliases'] = out.get('monitor_aliases') if isinstance(out.get('monitor_aliases'), dict) else {}
    global _MONITOR_ALIASES
    _MONITOR_ALIASES = out['monitor_aliases']
    out['profiles'] = out.get('profiles') if isinstance(out.get('profiles'), list) else []
    settings = dict(DEFAULT_CONFIG['settings'])
    if isinstance(out.get('settings'), dict):
        settings.update(out['settings'])
    out['settings'] = settings
    return out


def salva_config(config):
    global _MONITOR_ALIASES
    if not isinstance(config.get('monitor_aliases'), dict):
        config['monitor_aliases'] = {}
    _MONITOR_ALIASES = config['monitor_aliases']
    APP_DIR.mkdir(parents=True, exist_ok=True)
    tmp = CONFIG_PATH.with_suffix('.json.tmp')
    with tmp.open('w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    tmp.replace(CONFIG_PATH)


def parse_edid_name(edid):
    """Restituisce il nome EDID (descriptor 0xFC), oppure produttore + product code.

    La funzione è pura e tollera dati incompleti: restituisce None se l'EDID
    non contiene almeno i byte base necessari.
    """
    try:
        data = bytes(edid)
        if len(data) < 128:
            return None
        for offset in range(54, 126, 18):
            block = data[offset:offset + 18]
            if len(block) == 18 and block[:5] == b'\x00\x00\x00\xfc\x00':
                text = block[5:18].decode('ascii', errors='ignore')
                text = ''.join(ch for ch in text if ch.isprintable()).strip(' \x00\r\n\t')
                if text:
                    return text
        manufacturer_code = (data[8] << 8) | data[9]
        manufacturer = ''.join(chr(64 + ((manufacturer_code >> shift) & 0x1f))
                               for shift in (10, 5, 0))
        if not all('A' <= c <= 'Z' for c in manufacturer):
            manufacturer = ''
        product_code = data[10] | (data[11] << 8)
        if manufacturer:
            return f'{manufacturer} {product_code:04X}'
        return None
    except Exception:
        return None


def monitor_device_identity(device_id):
    """Estrae (hardware ID, instance, chiave stabile) dal DeviceID del monitor."""
    try:
        parts = [part.strip() for part in str(device_id or '').split('\\') if part.strip()]
        if len(parts) < 3:
            return None, None, None
        # La sottochiave Enum\DISPLAY è il primo segmento dopo l'HWID;
        # il DeviceID può avere componenti finali aggiuntive (es. \\0001).
        hardware_id, instance = parts[1], parts[2]
        stable_instance = '\\'.join(parts[2:])
        return hardware_id, instance, f'{hardware_id}\\{stable_instance}'
    except Exception:
        return None, None, None


def monitor_edid_name(device_id):
    """Legge EDID dal registro, provando i percorsi corrispondenti all'HWID."""
    hardware_id, instance, stable_key = monitor_device_identity(device_id)
    if not hardware_id or os.name != 'nt':
        return None
    try:
        import winreg
        root = r'SYSTEM\CurrentControlSet\Enum\DISPLAY'
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, root) as displays:
            for i in range(winreg.QueryInfoKey(displays)[0]):
                try:
                    hw_subkey = winreg.EnumKey(displays, i)
                    if hw_subkey.casefold() != hardware_id.casefold():
                        continue
                    hw_path = root + '\\' + hw_subkey
                    # Il DeviceID può rappresentare l'instance come uno o più segmenti.
                    candidates = []
                    if stable_key:
                        tail = stable_key.split('\\', 1)[1]
                        candidates.append(tail)
                    if instance and instance not in candidates:
                        candidates.append(instance)
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, hw_path) as hw_key:
                        registered = [winreg.EnumKey(hw_key, j) for j in range(winreg.QueryInfoKey(hw_key)[0])]
                    candidates.extend(name for name in registered if name not in candidates)
                    for instance_path in candidates:
                        try:
                            path = hw_path + '\\' + instance_path + r'\Device Parameters'
                            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as params:
                                edid, _kind = winreg.QueryValueEx(params, 'EDID')
                            name = parse_edid_name(edid)
                            if name:
                                return name
                        except Exception:
                            continue
                except Exception:
                    continue
    except Exception:
        pass
    return None


def regola_corrisponde(regola, processo, titolo):
    """Confronto case-insensitive per exe e sottostringa titolo opzionale."""
    if not regola.get('enabled', True):
        return False
    wanted = str(regola.get('process', '')).strip().casefold()
    actual = os.path.basename(str(processo or '')).casefold()
    if not wanted or wanted != actual:
        return False
    filtro = str(regola.get('title', '')).strip().casefold()
    return not filtro or filtro in str(titolo or '').casefold()

# -------------------------- Supporto Win32 ----------------------------------
user32 = ctypes.windll.user32 if os.name == 'nt' else None
kernel32 = ctypes.windll.kernel32 if os.name == 'nt' else None
shcore = ctypes.windll.shcore if os.name == 'nt' else None

class RECT(ctypes.Structure):
    _fields_ = [('left', ctypes.c_long), ('top', ctypes.c_long), ('right', ctypes.c_long), ('bottom', ctypes.c_long)]

class MONITORINFOEXW(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_ulong), ('rcMonitor', RECT), ('rcWork', RECT),
                ('dwFlags', ctypes.c_ulong), ('szDevice', ctypes.c_wchar * 32)]

class DEVMODEW(ctypes.Structure):
    _fields_ = [('_dmDeviceName', ctypes.c_wchar * 32), ('dmSpecVersion', ctypes.c_ushort),
        ('dmDriverVersion', ctypes.c_ushort), ('dmSize', ctypes.c_ushort), ('dmDriverExtra', ctypes.c_ushort),
        ('dmFields', ctypes.c_ulong), ('dmPositionX', ctypes.c_long), ('dmPositionY', ctypes.c_long),
        ('dmDisplayOrientation', ctypes.c_ulong), ('dmDisplayFixedOutput', ctypes.c_ulong),
        ('dmColor', ctypes.c_short), ('dmDuplex', ctypes.c_short), ('dmYResolution', ctypes.c_short),
        ('dmTTOption', ctypes.c_short), ('dmCollate', ctypes.c_short), ('dmFormName', ctypes.c_wchar * 32),
        ('dmLogPixels', ctypes.c_ushort), ('dmBitsPerPel', ctypes.c_ulong), ('dmPelsWidth', ctypes.c_ulong),
        ('dmPelsHeight', ctypes.c_ulong), ('dmDisplayFlags', ctypes.c_ulong), ('dmDisplayFrequency', ctypes.c_ulong),
        ('dmICம்ம', ctypes.c_ulong)]

# Firma API esplicite: evitano conversioni a int a 32 bit degli handle su Windows 64 bit.
if user32:
    _MONCB = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(RECT), ctypes.c_long)
    user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFOEXW)]
    user32.GetMonitorInfoW.restype = ctypes.c_int
    user32.EnumDisplayMonitors.argtypes = [ctypes.c_void_p, ctypes.c_void_p, _MONCB, ctypes.c_long]
    user32.EnumDisplayMonitors.restype = ctypes.c_int
    user32.EnumDisplaySettingsW.argtypes = [ctypes.c_wchar_p, ctypes.c_ulong, ctypes.POINTER(DEVMODEW)]
    user32.EnumDisplaySettingsW.restype = ctypes.c_int
    user32.ChangeDisplaySettingsExW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(DEVMODEW), ctypes.c_void_p, ctypes.c_ulong, ctypes.c_void_p]
    user32.ChangeDisplaySettingsExW.restype = ctypes.c_long
    user32.SendMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]
    user32.SendMessageW.restype = ctypes.c_ssize_t

# Struttura DEVMODEW completa (campi video e campi terminali inclusi).


def assegna_devmode(devmode, larghezza=None, altezza=None, frequenza=None, x=None, y=None):
    """Imposta campi DEVMODE e bit dmFields compatibili con l'API Win32."""
    if larghezza is not None:
        devmode.dmPelsWidth = int(larghezza); devmode.dmFields |= 0x80000
    if altezza is not None:
        devmode.dmPelsHeight = int(altezza); devmode.dmFields |= 0x100000
    if frequenza is not None:
        devmode.dmDisplayFrequency = int(frequenza); devmode.dmFields |= 0x400000
    if x is not None:
        devmode.dmPositionX = int(x); devmode.dmFields |= 0x20
    if y is not None:
        devmode.dmPositionY = int(y); devmode.dmFields |= 0x40


def monitors_info():
    """Enumera monitor attivi; restituisce lista di dizionari indipendente dalla UI."""
    if os.name != 'nt' or not user32:
        return []
    result = []
    callback_type = _MONCB
    def callback(hmon, _hdc, _rect, _data):
        try:
            mi = MONITORINFOEXW(); mi.cbSize = ctypes.sizeof(mi)
            if not user32.GetMonitorInfoW(hmon, ctypes.byref(mi)):
                return 1
            l, t, r, b = mi.rcMonitor.left, mi.rcMonitor.top, mi.rcMonitor.right, mi.rcMonitor.bottom
            dev = mi.szDevice
            dm = DEVMODEW(); dm.dmSize = ctypes.sizeof(dm)
            freq = 0; nome = dev
            if user32.EnumDisplaySettingsW(dev, -1, ctypes.byref(dm)):
                freq = int(dm.dmDisplayFrequency)
            windows_name = dev
            device_id = ''
            try:
                dd = win32api.EnumDisplayDevices(dev, 0)
                windows_name = getattr(dd, 'DeviceString', '') or dev
                device_id = getattr(dd, 'DeviceID', '') or ''
            except Exception:
                pass
            _hwid, _instance, stable_key = monitor_device_identity(device_id)
            edid_name = monitor_edid_name(device_id)
            alias = str(_MONITOR_ALIASES.get(stable_key, '')).strip() if stable_key else ''
            nome = alias or edid_name or windows_name
            dpi = '—'
            try:
                dx = ctypes.c_uint(); dy = ctypes.c_uint()
                if shcore and shcore.GetDpiForMonitor(hmon, 0, ctypes.byref(dx), ctypes.byref(dy)) == 0:
                    dpi = f'{dx.value} × {dy.value}'
            except Exception:
                pass
            result.append({'device': dev, 'device_id': device_id, 'stable_key': stable_key,
                'windows_name': windows_name, 'edid_name': edid_name, 'alias': alias, 'name': nome, 'x': l, 'y': t, 'width': r-l, 'height': b-t,
                'frequency': freq, 'dpi': dpi, 'primary': bool(mi.dwFlags & 1), 'active': True})
        except Exception:
            pass
        return 1
    try:
        user32.EnumDisplayMonitors(0, 0, callback_type(callback), 0)
    except Exception:
        return []
    return sorted(result, key=lambda m: (not m['primary'], m['x'], m['y']))


def process_name(hwnd):
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name()
    except Exception:
        return ''


def finestra_valida(hwnd):
    """Esclude finestre invisibili, senza titolo, tool window e cloaked."""
    try:
        if not win32gui.IsWindowVisible(hwnd): return False
        titolo = win32gui.GetWindowText(hwnd).strip()
        if not titolo: return False
        ex = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if ex & win32con.WS_EX_TOOLWINDOW: return False
        try:
            cloaked = ctypes.c_int()
            if ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd, 14, ctypes.byref(cloaked), ctypes.sizeof(cloaked)) == 0 and cloaked.value:
                return False
        except Exception:
            pass
        return True
    except Exception:
        return False


def rect_finestra(hwnd):
    try:
        l, t, r, b = win32gui.GetWindowRect(hwnd)
        return [int(l), int(t), int(r-l), int(b-t)]
    except Exception:
        return [0, 0, 0, 0]


def monitor_per_rect(rect, monitors):
    x, y, w, h = rect
    cx, cy = x + max(w, 1)//2, y + max(h, 1)//2
    for i, m in enumerate(monitors):
        if m['x'] <= cx < m['x']+m['width'] and m['y'] <= cy < m['y']+m['height']:
            return i
    if not monitors: return 0
    return min(range(len(monitors)), key=lambda i: (max(monitors[i]['x']-cx, 0, cx-(monitors[i]['x']+monitors[i]['width']))**2 + max(monitors[i]['y']-cy, 0, cy-(monitors[i]['y']+monitors[i]['height']))**2))


def enum_finestre():
    if not win32gui or not psutil: return []
    found = []
    own_pid = os.getpid()
    def cb(hwnd, _):
        if not finestra_valida(hwnd): return True
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid == own_pid: return True
            proc = psutil.Process(pid).name()
            rect = rect_finestra(hwnd)
            mons = monitors_info()
            idx = monitor_per_rect(rect, mons)
            placement = win32gui.GetWindowPlacement(hwnd)
            maximized = placement[1] == win32con.SW_MAXIMIZE
            found.append({'hwnd': int(hwnd), 'title': win32gui.GetWindowText(hwnd), 'process': proc,
                'pid': pid, 'rect': rect, 'monitor': idx, 'maximized': maximized})
        except Exception:
            pass
        return True
    try: win32gui.EnumWindows(cb, None)
    except Exception: pass
    return found


def programmi_aperti():
    """Nomi exe unici e ordinati per le finestre visibili attualmente aperte."""
    if not win32gui or not psutil:
        return []
    names = set()
    try:
        def cb(hwnd, _):
            try:
                if finestra_valida(hwnd):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid == os.getpid():
                        return True
                    name = psutil.Process(pid).name().strip()
                    if name:
                        names.add(os.path.basename(name))
            except Exception:
                pass
            return True
        win32gui.EnumWindows(cb, None)
    except Exception:
        pass
    return sorted(names, key=str.casefold)


def sposta_hwnd(hwnd, monitor, mode='Mantieni dimensione', custom=None):
    mons = monitors_info()
    if not mons: return False
    monitor = max(0, min(int(monitor), len(mons)-1)); m = mons[monitor]
    try:
        try: win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        except Exception: pass
        if mode == 'Massimizzata':
            win32gui.SetWindowPos(hwnd, 0, m['x'], m['y'], m['width'], m['height'], win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            return True
        if mode == 'Schermo intero':
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, m['x'], m['y'], m['width'], m['height'], win32con.SWP_NOACTIVATE)
            return True
        if mode == 'Centrata':
            _, _, w, h = rect_finestra(hwnd); w = min(w, m['width']); h = min(h, m['height'])
            x, y = m['x']+(m['width']-w)//2, m['y']+(m['height']-h)//2
        elif mode == 'Dimensione personalizzata' and custom:
            rx, ry, w, h = [int(v) for v in custom]
            x, y = m['x']+rx, m['y']+ry
        else:
            _, _, w, h = rect_finestra(hwnd)
            x, y = m['x'], m['y']
        win32gui.SetWindowPos(hwnd, 0, int(x), int(y), max(100, int(w)), max(80, int(h)), win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE)
        return True
    except Exception:
        return False

# -------------------------- Componenti UI ----------------------------------
STYLE = """
QWidget { background:#111820; color:#e7edf2; font-family:'Segoe UI'; font-size:10pt; }
QMainWindow { background:#0c1218; }
QTabWidget::pane { border:1px solid #263541; background:#111820; border-radius:8px; top:-1px; }
QTabBar::tab { background:#17222c; color:#91a5b4; padding:11px 18px; margin-right:4px; border-top-left-radius:7px; border-top-right-radius:7px; }
QTabBar::tab:selected { color:#eafff8; background:#20322f; border-bottom:2px solid #51d6ad; }
QPushButton { background:#20313d; border:1px solid #324857; padding:8px 12px; border-radius:6px; }
QPushButton:hover { background:#29404c; border-color:#51d6ad; }
QPushButton:pressed { background:#315b55; }
QPushButton#primary { background:#157f69; border-color:#33b99a; color:white; font-weight:600; }
QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox { background:#0d151c; border:1px solid #30414d; border-radius:5px; padding:6px; }
QComboBox QAbstractItemView { background:#17222c; selection-background-color:#157f69; }
QTableWidget { background:#0d151c; alternate-background-color:#121d26; gridline-color:#263541; border:1px solid #263541; border-radius:6px; selection-background-color:#1d574e; }
QHeaderView::section { background:#1a2832; color:#a9bbc7; padding:8px; border:0; border-right:1px solid #263541; }
QGroupBox { border:1px solid #263541; border-radius:7px; margin-top:12px; padding:12px; font-weight:600; color:#a9bbc7; }
QGroupBox::title { subcontrol-origin:margin; left:12px; padding:0 5px; }
QStatusBar { color:#8295a3; border-top:1px solid #263541; }
QCheckBox { spacing:8px; }
"""


def item(value):
    cell = QTableWidgetItem(str(value)); cell.setFlags(cell.flags() & ~Qt.ItemIsEditable); return cell


def setup_table(table):
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    table.horizontalHeader().setStretchLastSection(True)

class Overlay(QLabel):
    """Numero identificativo temporaneo disegnato sopra ciascun monitor."""
    def __init__(self, numero, monitor):
        super().__init__(str(numero))
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('background:rgba(16,27,35,220);color:#54e3b5;border:5px solid #54e3b5;border-radius:30px;font-size:100px;font-weight:800;')
        self.setGeometry(monitor['x']+monitor['width']//2-100, monitor['y']+monitor['height']//2-100, 200, 200)
        self.show(); self.raise_()

class RuleDialog(QDialog):
    def __init__(self, monitors, rule=None, parent=None):
        super().__init__(parent); self.setWindowTitle(t('Regola finestra')); self.setMinimumWidth(650)
        form = QFormLayout(self)
        self.process = QLineEdit(); self.process.setPlaceholderText(t('es. chrome.exe'))
        process_row = QWidget(); process_lay = QHBoxLayout(process_row); process_lay.setContentsMargins(0, 0, 0, 0)
        process_lay.addWidget(self.process, 1)
        browse = QPushButton(t('Sfoglia...')); browse.clicked.connect(self.browse_exe); process_lay.addWidget(browse)
        self.open_programs_button = QPushButton(t('Programmi aperti'))
        self.open_programs_button.clicked.connect(self.show_open_programs); process_lay.addWidget(self.open_programs_button)
        self.open_programs_menu = QMenu(self)
        self.title = QLineEdit(); self.title.setPlaceholderText(t('Facoltativo: testo contenuto nel titolo'))
        self.monitor = QComboBox()
        for i,m in enumerate(monitors): self.monitor.addItem(f'{i+1} · {m["name"]} ({m["width"]}×{m["height"]})', i)
        self.mode = QComboBox(); self.mode.addItems([t(m) for m in MODES])
        self.x=QSpinBox(); self.x.setRange(-10000,10000); self.y=QSpinBox(); self.y.setRange(-10000,10000)
        self.w=QSpinBox(); self.w.setRange(100,10000); self.w.setValue(900)
        self.h=QSpinBox(); self.h.setRange(80,10000); self.h.setValue(650)
        self.enabled=QCheckBox(t('Regola abilitata')); self.enabled.setChecked(True)
        form.addRow(t('Processo (.exe)'),process_row); form.addRow(t('Filtro titolo'),self.title)
        form.addRow(t('Monitor'),self.monitor); form.addRow(t('Modalità'),self.mode)
        row=QWidget(); lay=QHBoxLayout(row); lay.setContentsMargins(0,0,0,0)
        for label,widget in [('X',self.x),('Y',self.y),(t('Larghezza'),self.w),(t('Altezza'),self.h)]:
            lay.addWidget(QLabel(label)); lay.addWidget(widget)
        form.addRow(t('Coordinate/dimensioni'),row); form.addRow('',self.enabled)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel); buttons.button(QDialogButtonBox.Save).setText(t('Salva')); buttons.button(QDialogButtonBox.Cancel).setText(t('Annulla')); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); form.addRow(buttons)
        if rule:
            self.process.setText(rule.get('process','')); self.title.setText(rule.get('title',''))
            self.monitor.setCurrentIndex(max(0,self.monitor.findData(rule.get('monitor',0))))
            self.mode.setCurrentText(t(rule.get('mode',MODES[0]))); c=rule.get('custom',[0,0,900,650])
            for box,val in zip((self.x,self.y,self.w,self.h),c): box.setValue(int(val))
            self.enabled.setChecked(rule.get('enabled',True))
    def browse_exe(self):
        path, _ = QFileDialog.getOpenFileName(self, t('Seleziona eseguibile'), '', t('Eseguibili (*.exe)'))
        if path:
            self.process.setText(os.path.basename(path))

    def show_open_programs(self):
        self.open_programs_menu.clear()
        names = programmi_aperti()
        if not names:
            empty = self.open_programs_menu.addAction(t('Nessun programma visibile rilevato'))
            empty.setEnabled(False)
        else:
            for name in names:
                action = self.open_programs_menu.addAction(name)
                action.triggered.connect(lambda checked=False, value=name: self.process.setText(value))
        self.open_programs_menu.popup(self.open_programs_button.mapToGlobal(
            self.open_programs_button.rect().bottomLeft()))

    def values(self):
        return {'process':self.process.text().strip(),'title':self.title.text().strip(),
            'monitor':self.monitor.currentData() or 0,'mode':mode_value(self.mode.currentText()),
            'custom':[self.x.value(),self.y.value(),self.w.value(),self.h.value()], 'enabled':self.enabled.isChecked()}

class ModeDialog(QDialog):
    def __init__(self, monitors, parent=None):
        super().__init__(parent); self.setWindowTitle(t('Sposta finestra')); form=QFormLayout(self)
        self.monitor=QComboBox()
        for i,m in enumerate(monitors): self.monitor.addItem(f'{i+1} · {m["name"]}',i)
        self.mode=QComboBox(); self.mode.addItems([t(m) for m in MODES])
        self.x=QSpinBox(); self.x.setRange(-10000,10000); self.y=QSpinBox(); self.y.setRange(-10000,10000)
        self.w=QSpinBox(); self.w.setRange(100,10000); self.w.setValue(900); self.h=QSpinBox(); self.h.setRange(80,10000); self.h.setValue(650)
        form.addRow(t('Monitor'),self.monitor); form.addRow(t('Modalità'),self.mode)
        for label,box in [('X',self.x),('Y',self.y),(t('Larghezza'),self.w),(t('Altezza'),self.h)]: form.addRow(label,box)
        bb=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); bb.button(QDialogButtonBox.Ok).setText(t('OK')); bb.button(QDialogButtonBox.Cancel).setText(t('Annulla')); bb.accepted.connect(self.accept); bb.rejected.connect(self.reject); form.addRow(bb)
    def values(self): return self.monitor.currentData() or 0, mode_value(self.mode.currentText()), [self.x.value(),self.y.value(),self.w.value(),self.h.value()]

class MainWindow(QMainWindow):
    def __init__(self, config, start_hidden=False):
        super().__init__(); self.config=config; self.managed=set(); self.overlays=[]; self.closing_to_tray=False
        self.setWindowTitle(t('MonitorPilot · Desktop Control')); self.resize(1120,720); self.setMinimumSize(850,560)
        self.setStyleSheet(STYLE)
        root=QWidget(); v=QVBoxLayout(root); v.setContentsMargins(20,16,20,12); v.setSpacing(12)
        header=QHBoxLayout(); brand=QVBoxLayout(); title=QLabel(t('MONITORPILOT')); title.setStyleSheet('color:#54e3b5;font-size:21pt;font-weight:800;letter-spacing:2px;')
        subtitle=QLabel(t('CONTROL ROOM  /  WINDOWS DESKTOP')); subtitle.setStyleSheet('color:#79909f;font-size:9pt;letter-spacing:1px;')
        brand.addWidget(title); brand.addWidget(subtitle); header.addLayout(brand); header.addStretch()
        self.monitor_badge=QLabel(t('●  MONITORAGGIO ATTIVO')); self.monitor_badge.setStyleSheet('color:#54e3b5;background:#18332f;padding:8px 12px;border-radius:12px;')
        header.addWidget(self.monitor_badge); v.addLayout(header)
        self.tabs=QTabWidget(); v.addWidget(self.tabs,1)
        self.build_rules(); self.build_monitors(); self.build_windows(); self.build_profiles(); self.build_settings()
        self.setCentralWidget(root); self.setStatusBar(QStatusBar()); self.statusBar().showMessage(t('Pronto · regole applicate una sola volta per finestra'))
        self.make_tray()
        self.timer=QTimer(self); self.timer.timeout.connect(self.applica_regole)
        self.timer.start(max(250,int(self.config['settings'].get('rule_interval',1000))))
        self.refresh_rules(); self.refresh_monitors(); self.refresh_windows(); self.refresh_profiles(); self.load_settings_ui()
        self.set_rules_ui_state()
        if start_hidden: self.hide()
        if os.name!='nt': QTimer.singleShot(300,self.avviso_non_windows)
        elif not win32gui or not psutil: QTimer.singleShot(300,self.avviso_dipendenze)

    def avviso_non_windows(self): QMessageBox.warning(self,t('Windows richiesto'),t('MonitorPilot usa API Win32 e può funzionare soltanto su Windows. La UI è stata avviata in modalità dimostrativa.'))
    def avviso_dipendenze(self): QMessageBox.critical(self,t('Dipendenze mancanti'),t('Impossibile caricare pywin32 o psutil. Avvia avvia_monitorpilot.bat per installare i componenti richiesti.'))
    def panel(self):
        w=QWidget(); lay=QVBoxLayout(w); lay.setContentsMargins(12,14,12,12); lay.setSpacing(10); return w,lay
    def button_row(self, layout, buttons):
        row=QHBoxLayout()
        for text,slot,primary in buttons:
            b=QPushButton(text); b.clicked.connect(slot)
            if primary: b.setObjectName('primary')
            row.addWidget(b)
        row.addStretch(); layout.addLayout(row)

    def build_rules(self):
        w,l=self.panel(); self.rules_table=QTableWidget(0,6); self.rules_table.setHorizontalHeaderLabels([t('Processo'),t('Filtro titolo'),t('Monitor'),t('Modalità'),t('Stato'),t('ID')]); setup_table(self.rules_table); self.rules_table.setColumnHidden(5,True); l.addWidget(self.rules_table)
        self.button_row(l,[(t('＋  Aggiungi'),self.add_rule,True),(t('✎  Modifica'),self.edit_rule,False),(t('－  Elimina'),self.delete_rule,False),(t('Aggiorna'),self.refresh_rules,False)])
        note=QLabel(t('Una regola viene applicata una sola volta a ogni nuova finestra corrispondente. In seguito puoi spostarla liberamente.')); note.setStyleSheet('color:#8295a3;'); l.addWidget(note); self.tabs.addTab(w,t('Regole'))
    def refresh_rules(self):
        self.rules_table.setRowCount(0)
        for i,r in enumerate(self.config.get('rules',[])):
            row=self.rules_table.rowCount(); self.rules_table.insertRow(row)
            vals=[r.get('process',''),r.get('title','') or '—',str(int(r.get('monitor',0))+1),t(r.get('mode','')), t('Attiva') if r.get('enabled',True) else t('Disattiva'),str(i)]
            for c,v in enumerate(vals): self.rules_table.setItem(row,c,item(v))
    def selected_rule(self):
        r=self.rules_table.currentRow()
        if r<0:return None
        return int(self.rules_table.item(r,5).text())
    def add_rule(self, initial=None):
        d=RuleDialog(monitors_info(),initial,self)
        if d.exec()==QDialog.Accepted:
            val=d.values()
            if not val['process']: QMessageBox.warning(self,t('Dato mancante'),t('Inserisci il nome del processo.')); return
            self.config['rules'].append(val); self.save(); self.refresh_rules()
    def edit_rule(self):
        i=self.selected_rule()
        if i is None:return
        d=RuleDialog(monitors_info(),self.config['rules'][i],self)
        if d.exec()==QDialog.Accepted:
            val=d.values()
            if val['process']: self.config['rules'][i]=val; self.save(); self.refresh_rules()
    def delete_rule(self):
        i=self.selected_rule()
        if i is not None and QMessageBox.question(self,t('Elimina regola'),t('Eliminare la regola selezionata?'))==QMessageBox.Yes:
            del self.config['rules'][i]; self.save(); self.refresh_rules()

    def build_monitors(self):
        w,l=self.panel(); self.monitor_table=QTableWidget(0,8); self.monitor_table.setHorizontalHeaderLabels([t('#'),t('Device name'),t('Nome'),t('Risoluzione'),t('Posizione'),t('Hz'),t('DPI'),t('Primario/Attivo')]); setup_table(self.monitor_table); self.monitor_table.cellDoubleClicked.connect(lambda _r, _c: self.rename_monitor()); l.addWidget(self.monitor_table)
        self.button_row(l,[(t('↻  Aggiorna'),self.refresh_monitors,True),(t('Identifica'),self.identify_monitors,False),(t('Imposta primario'),self.set_primary,False),(t('Attiva/Disattiva'),self.toggle_monitor,False),(t('Risoluzione / frequenza'),self.change_resolution,False)])
        self.button_row(l,[(t('Rinomina'),self.rename_monitor,False),(t('Ripristina nome originale'),self.restore_monitor_name,False),(t('Spegni monitor'),lambda:self.monitor_power(2),False),(t('Accendi monitor'),lambda:self.monitor_power(-1),False),(t('Esporta JSON'),self.export_json,False)])
        self.tabs.addTab(w,t('Monitor'))
    def refresh_monitors(self):
        mons=monitors_info(); self.monitor_table.setRowCount(0)
        for i,m in enumerate(mons):
            row=self.monitor_table.rowCount(); self.monitor_table.insertRow(row)
            vals=[i+1,m['device'],m['name'],f"{m['width']} × {m['height']}",f"{m['x']}, {m['y']}",m['frequency'] or '—',m['dpi'],(t('Primario · ') if m['primary'] else '')+(t('Attivo') if m['active'] else t('Non attivo'))]
            for c,v in enumerate(vals):self.monitor_table.setItem(row,c,item(v))
        self.monitor_badge.setText(t('●  {n} MONITOR ATTIVI', n=len(mons)) if mons else t('●  NESSUN MONITOR RILEVATO'))
    def selected_monitor_data(self):
        i = self.selected_monitor()
        mons = monitors_info()
        return mons[i] if 0 <= i < len(mons) else None
    def rename_monitor(self):
        monitor = self.selected_monitor_data()
        if not monitor:
            return
        key = monitor.get('stable_key')
        if not key:
            QMessageBox.warning(self, t('Rinomina monitor'), t('Windows non ha fornito un identificativo hardware stabile per questo monitor.'))
            return
        current = self.config.setdefault('monitor_aliases', {}).get(key, '')
        alias, ok = QInputDialog.getText(self, t('Rinomina monitor'), t('Nome personalizzato:'), text=current or monitor['name'])
        if ok:
            alias = alias.strip()
            if alias:
                self.config['monitor_aliases'][key] = alias
            else:
                self.config['monitor_aliases'].pop(key, None)
            self.save(); self.refresh_monitors(); self.refresh_windows()
    def restore_monitor_name(self):
        monitor = self.selected_monitor_data()
        if not monitor:
            return
        key = monitor.get('stable_key')
        aliases = self.config.setdefault('monitor_aliases', {})
        if key and key in aliases:
            aliases.pop(key, None)
            self.save(); self.refresh_monitors(); self.refresh_windows()

    def selected_monitor(self): return self.monitor_table.currentRow()
    def identify_monitors(self):
        self.refresh_monitors(); self.overlays=[]
        for i,m in enumerate(monitors_info()): self.overlays.append(Overlay(i+1,m))
        QTimer.singleShot(2000,self.clear_overlays)
    def clear_overlays(self):
        for o in self.overlays:o.close()
        self.overlays=[]
    def set_primary(self):
        i=self.selected_monitor(); mons=monitors_info()
        if i<0 or i>=len(mons):return
        if os.name!='nt':return
        try:
            dev=mons[i]['device']; dm=DEVMODEW(); dm.dmSize=ctypes.sizeof(dm)
            if user32.EnumDisplaySettingsW(dev,-1,ctypes.byref(dm)):
                # CDS_SET_PRIMARY = 0x10; modalità corrente mantenuta.
                res=user32.ChangeDisplaySettingsExW(dev,ctypes.byref(dm),None,0x10,None)
                if res==0: self.refresh_monitors()
                else: QMessageBox.warning(self,t('Impossibile'),t('Windows non ha accettato la modifica (codice %s).')%res)
        except Exception as e: QMessageBox.warning(self,t('Errore'),str(e))
    def toggle_monitor(self):
        i=self.selected_monitor(); mons=monitors_info()
        if i<0 or i>=len(mons):return
        if len(mons)<=1:
            QMessageBox.warning(self,t('Operazione non consentita'),t('Non puoi disattivare l’ultimo monitor attivo.'));return
        if QMessageBox.question(self,t('Conferma'),t('La modifica può spostare le finestre o richiedere un ripristino. Continuare?'))!=QMessageBox.Yes:return
        try:
            dev=mons[i]['device']; dm=DEVMODEW(); dm.dmSize=ctypes.sizeof(dm)
            if user32.EnumDisplaySettingsW(dev,-1,ctypes.byref(dm)):
                # CDS_DISABLED rimuove il device dalla topologia; il driver può rifiutare il cambio.
                # Non impostiamo una posizione artificiale: disabilitare un display non equivale a spostarlo.
                # CDS_UPDATEREGISTRY | CDS_NORESET | CDS_DISABLED.
                rc=user32.ChangeDisplaySettingsExW(dev,ctypes.byref(dm),None,0x12000001,None)
                if rc==0: user32.ChangeDisplaySettingsExW(None,None,None,0,None)
                if rc!=0: QMessageBox.warning(self,t('Non riuscito'),t('Windows ha rifiutato il cambio (codice {rc}).', rc=rc))
                self.refresh_monitors()
        except Exception as e: QMessageBox.warning(self,t('Errore'),str(e))
    def change_resolution(self):
        i=self.selected_monitor(); mons=monitors_info()
        if i<0 or i>=len(mons):return
        dev=mons[i]['device']; modes=[]; dm=DEVMODEW(); dm.dmSize=ctypes.sizeof(dm); n=0
        try:
            while user32.EnumDisplaySettingsW(dev,n,ctypes.byref(dm)):
                modes.append((int(dm.dmPelsWidth),int(dm.dmPelsHeight),int(dm.dmDisplayFrequency))); n+=1
                dm=DEVMODEW(); dm.dmSize=ctypes.sizeof(dm)
        except Exception as e: QMessageBox.warning(self,t('Errore'),str(e));return
        choices=list(dict.fromkeys(f'{w} × {h} @ {hz} Hz' for w,h,hz in modes))
        if not choices:return
        choice,ok=QInputDialog.getItem(self,t('Risoluzione e frequenza'),t('Modalità disponibile'),choices,0,False)
        if not ok:return
        try:
            w,h,hz=[int(x.strip().split()[0]) for x in choice.replace('@','').replace(t('Hz'),'').split('×')[:2]] if False else (None,None,None)
            # parsing esplicito dell'etichetta scelta
            left,right=choice.split('@'); w,h=[int(x.strip()) for x in left.split('×')]; hz=int(right.strip().split()[0])
            dm=DEVMODEW(); dm.dmSize=ctypes.sizeof(dm)
            if user32.EnumDisplaySettingsW(dev,-1,ctypes.byref(dm)):
                assegna_devmode(dm,w,h,hz)
                rc=user32.ChangeDisplaySettingsExW(dev,ctypes.byref(dm),None,0,None)
                if rc!=0: QMessageBox.warning(self,t('Non riuscito'),t('Modalità rifiutata (codice {rc}).', rc=rc))
                self.refresh_monitors()
        except Exception as e: QMessageBox.warning(self,t('Errore'),str(e))
    def monitor_power(self,action):
        try:
            # WM_SYSCOMMAND/SC_MONITORPOWER broadcast; -1 accende, 2 spegne.
            user32.SendMessageW(0xffff,0x0112,0xF170,action)
        except Exception as e: QMessageBox.warning(self,t('Errore'),str(e))
    def export_json(self):
        path,_=QFileDialog.getSaveFileName(self,t('Esporta stato'),t('monitorpilot-export.json'),t('JSON (*.json)'))
        if not path:return
        try:
            payload={'exported_at':time.strftime('%Y-%m-%dT%H:%M:%S'),'monitors':monitors_info(),'windows':enum_finestre()}
            Path(path).write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
            self.statusBar().showMessage(t('Esportazione completata'),5000)
        except Exception as e: QMessageBox.critical(self,t('Errore esportazione'),str(e))

    def build_windows(self):
        w,l=self.panel(); self.window_table=QTableWidget(0,6); self.window_table.setHorizontalHeaderLabels([t('Titolo'),t('Processo'),t('Monitor'),t('X, Y'),t('Dimensione'),'HWND']); setup_table(self.window_table); self.window_table.setColumnHidden(5,True); l.addWidget(self.window_table)
        self.button_row(l,[(t('↻  Aggiorna'),self.refresh_windows,True),(t('Sposta…'),self.move_selected,False),(t('Massimizza'),lambda:self.window_action('max'),False),(t('Minimizza'),lambda:self.window_action('min'),False),(t('Ripristina'),lambda:self.window_action('restore'),False),(t('Chiudi'),lambda:self.window_action('close'),False)])
        self.button_row(l,[(t('Sempre in primo piano'),self.toggle_topmost,False),(t('Crea regola da finestra'),self.rule_from_window,False)])
        group=QGroupBox(t('Spostamento in blocco')); row=QHBoxLayout(group); self.from_monitor=QComboBox(); self.to_monitor=QComboBox(); self.bulk_mode=QComboBox(); self.bulk_mode.addItems([t(m) for m in MODES])
        row.addWidget(QLabel(t('Da')));row.addWidget(self.from_monitor);row.addWidget(QLabel(t('A')));row.addWidget(self.to_monitor);row.addWidget(self.bulk_mode)
        b=QPushButton(t('Sposta tutte'));b.clicked.connect(self.move_all);row.addWidget(b);l.addWidget(group);self.tabs.addTab(w,t('Finestre'))
    def refresh_windows(self):
        windows=enum_finestre(); mons=monitors_info(); self.window_table.setRowCount(0)
        for f in windows:
            row=self.window_table.rowCount();self.window_table.insertRow(row);x,y,w,h=f['rect']
            monitor_label = f['monitor'] + 1
            if 0 <= f['monitor'] < len(mons): monitor_label = f'{monitor_label} · {mons[f["monitor"]]["name"]}'
            vals=[f['title'],f['process'],monitor_label,f'{x}, {y}',f'{w} × {h}',str(f['hwnd'])]
            for c,v in enumerate(vals):self.window_table.setItem(row,c,item(v))
        for combo in (getattr(self,'from_monitor',None),getattr(self,'to_monitor',None)):
            if combo:
                old=combo.currentData(); combo.clear()
                for i,m in enumerate(mons):combo.addItem(f'{i+1} · {m["name"]}',i)
                j=combo.findData(old);combo.setCurrentIndex(max(0,j))
    def selected_hwnd(self):
        r=self.window_table.currentRow()
        try:return int(self.window_table.item(r,5).text()) if r>=0 else None
        except Exception:return None
    def move_selected(self):
        hwnd=self.selected_hwnd(); mons=monitors_info()
        if hwnd is None:return
        d=ModeDialog(mons,self)
        if d.exec()==QDialog.Accepted:
            i,mode,custom=d.values()
            if not sposta_hwnd(hwnd,i,mode,custom):QMessageBox.warning(self,t('Spostamento non riuscito'),t('Windows non ha consentito di spostare questa finestra.'))
            self.refresh_windows()
    def window_action(self,action):
        hwnd=self.selected_hwnd()
        if hwnd is None:return
        try:
            if action=='max':win32gui.ShowWindow(hwnd,win32con.SW_MAXIMIZE)
            elif action=='min':win32gui.ShowWindow(hwnd,win32con.SW_MINIMIZE)
            elif action=='restore':win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)
            elif action=='close' and QMessageBox.question(self,t('Chiudi finestra'),t('Inviare un messaggio di chiusura alla finestra?'))==QMessageBox.Yes:win32gui.PostMessage(hwnd,win32con.WM_CLOSE,0,0)
            self.refresh_windows()
        except Exception as e:QMessageBox.warning(self,t('Operazione non riuscita'),str(e))
    def toggle_topmost(self):
        hwnd=self.selected_hwnd()
        if hwnd is None:return
        try:
            ex=win32gui.GetWindowLong(hwnd,win32con.GWL_EXSTYLE); flag=win32con.WS_EX_TOPMOST
            insert=win32con.HWND_NOTOPMOST if ex&flag else win32con.HWND_TOPMOST
            win32gui.SetWindowPos(hwnd,insert,0,0,0,0,win32con.SWP_NOMOVE|win32con.SWP_NOSIZE|win32con.SWP_NOACTIVATE)
        except Exception as e:QMessageBox.warning(self,t('Operazione non riuscita'),str(e))
    def move_all(self):
        src=self.from_monitor.currentData(); dst=self.to_monitor.currentData()
        if src is None or dst is None or src==dst:return
        wins=[f for f in enum_finestre() if f['monitor']==src]
        if QMessageBox.question(self,t('Spostamento in blocco'),t('Spostare {count} finestre sul monitor selezionato?', count=len(wins)))!=QMessageBox.Yes:return
        for f in wins:sposta_hwnd(f['hwnd'],dst,mode_value(self.bulk_mode.currentText()))
        self.refresh_windows()
    def rule_from_window(self):
        hwnd=self.selected_hwnd()
        if hwnd is None:return
        d=RuleDialog(monitors_info(),{'process':process_name(hwnd),'title':win32gui.GetWindowText(hwnd),'monitor':0,'mode':'Mantieni dimensione'},self)
        if d.exec()==QDialog.Accepted:
            val=d.values()
            if val['process']:self.config['rules'].append(val);self.save();self.refresh_rules();self.tabs.setCurrentIndex(0)

    def build_profiles(self):
        w,l=self.panel(); self.profile_table=QTableWidget(0,2);self.profile_table.setHorizontalHeaderLabels([t('Nome profilo'),t('Finestre salvate')]);setup_table(self.profile_table);l.addWidget(self.profile_table)
        self.button_row(l,[(t('Salva layout corrente'),self.save_profile,True),(t('Ripristina profilo'),self.restore_profile,False),(t('Rinomina'),self.rename_profile,False),(t('Elimina'),self.delete_profile,False),(t('Aggiorna'),self.refresh_profiles,False)])
        note=QLabel(t('Il ripristino abbina prima processo + titolo (parziale, senza distinzione maiuscole/minuscole), poi soltanto il processo. Le impostazioni video sono memorizzate quando leggibili; l’applicazione automatica della topologia non è garantita da Windows.'));note.setWordWrap(True);note.setStyleSheet('color:#8295a3;');l.addWidget(note);self.tabs.addTab(w,t('Profili'))
    def refresh_profiles(self):
        if not hasattr(self,'profile_table'):return
        self.profile_table.setRowCount(0)
        for i,p in enumerate(self.config.get('profiles',[])):
            row=self.profile_table.rowCount();self.profile_table.insertRow(row);self.profile_table.setItem(row,0,item(p.get('name','')));self.profile_table.setItem(row,1,item(t('{count} finestre · {index}', count=len(p.get('windows',[])), index=i)))
    def selected_profile(self):return self.profile_table.currentRow()
    def save_profile(self):
        name,ok=QInputDialog.getText(self,t('Salva profilo'),t('Nome del nuovo layout:'))
        if not ok or not name.strip():return
        windows=[]
        for f in enum_finestre(): windows.append({'process':f['process'],'title':f['title'],'rect':f['rect'],'maximized':f['maximized']})
        prof={'name':name.strip(),'created':time.strftime('%Y-%m-%d %H:%M:%S'),'windows':windows,'monitors':monitors_info()}
        self.config['profiles'].append(prof);self.save();self.refresh_profiles()
    def restore_profile(self):
        i=self.selected_profile()
        if i<0:return
        p=self.config['profiles'][i]
        if QMessageBox.question(self,t('Ripristina profilo'),t("Ripristinare '{name}'? Le finestre corrispondenti verranno spostate.", name=p.get('name'))) !=QMessageBox.Yes:return
        current=enum_finestre(); used=set()
        for saved in p.get('windows',[]):
            candidates=[f for f in current if f['hwnd'] not in used and f['process'].casefold()==saved.get('process','').casefold()]
            exact=[f for f in candidates if saved.get('title','').casefold() in f['title'].casefold() or f['title'].casefold() in saved.get('title','').casefold()]
            target=(exact or candidates)
            if not target:continue
            f=target[0];used.add(f['hwnd']); rect=saved.get('rect',[0,0,800,600])
            try:
                win32gui.ShowWindow(f['hwnd'],win32con.SW_RESTORE)
                win32gui.SetWindowPos(f['hwnd'],0,*[int(v) for v in rect],win32con.SWP_NOZORDER|win32con.SWP_NOACTIVATE)
                if saved.get('maximized'):win32gui.ShowWindow(f['hwnd'],win32con.SW_MAXIMIZE)
            except Exception:pass
        self.refresh_windows()
    def rename_profile(self):
        i=self.selected_profile()
        if i<0:return
        old=self.config['profiles'][i].get('name','');name,ok=QInputDialog.getText(self,t('Rinomina profilo'),t('Nuovo nome:'),text=old)
        if ok and name.strip():self.config['profiles'][i]['name']=name.strip();self.save();self.refresh_profiles()
    def delete_profile(self):
        i=self.selected_profile()
        if i>=0 and QMessageBox.question(self,t('Elimina profilo'),t('Eliminare il profilo selezionato?'))==QMessageBox.Yes:
            del self.config['profiles'][i];self.save();self.refresh_profiles()

    def build_settings(self):
        w,l=self.panel(); group=QGroupBox(t('Comportamento')); form=QFormLayout(group)
        self.language=QComboBox(); self.language.addItem(t('Italiano'), 'it'); self.language.addItem(t('English'), 'en')
        self.language.setCurrentIndex(max(0, self.language.findData(self.config.get('language', 'en'))))
        self.language.currentIndexChanged.connect(self.change_language)
        form.addRow(t('Lingua / Language'), self.language)
        self.run_start=QCheckBox(t('Avvia MonitorPilot all’accesso a Windows'));self.start_tray=QCheckBox(t('Avvia minimizzato nella tray'));self.rules_global=QCheckBox(t('Abilita motore regole globale'))
        self.interval=QSpinBox();self.interval.setRange(250,60000);self.interval.setSuffix(t(' ms'))
        form.addRow(self.run_start);form.addRow(self.start_tray);form.addRow(t('Controllo regole ogni'),self.interval);form.addRow(self.rules_global);l.addWidget(group)
        self.button_row(l,[(t('Salva impostazioni'),self.save_settings,True)])
        info=QLabel(t('Configurazione: ') + str(CONFIG_PATH) + t('\nLa tray resta attiva quando chiudi la finestra. Per uscire usa il menu MonitorPilot sull’icona nell’area di notifica.'));info.setWordWrap(True);info.setStyleSheet('color:#8295a3;');l.addWidget(info);l.addStretch();self.tabs.addTab(w,t('Impostazioni'))
    def change_language(self, _index):
        global CURRENT_LANGUAGE
        lang = self.language.currentData()
        if not lang or lang == CURRENT_LANGUAGE: return
        CURRENT_LANGUAGE = lang
        self.config['language'] = lang
        try: salva_config(self.config)
        except Exception: pass
        old = self
        tab = self.tabs.currentIndex()
        hidden = not self.isVisible()
        managed = set(self.managed)
        selected = {name: table.currentRow() for name, table in (('rules', self.rules_table), ('monitors', self.monitor_table), ('windows', self.window_table), ('profiles', self.profile_table))}
        old.closing_to_tray = True
        try: old.tray.hide()
        except Exception: pass
        new = MainWindow(self.config, hidden)
        new.tabs.setCurrentIndex(min(tab, new.tabs.count() - 1))
        new.managed = managed
        for name, row in selected.items():
            table = getattr(new, {'rules':'rules_table','monitors':'monitor_table','windows':'window_table','profiles':'profile_table'}[name], None)
            if table is not None and 0 <= row < table.rowCount(): table.selectRow(row)
        QApplication.instance()._monitorpilot_window = new
        if not hidden: new.show()
        old.timer.stop()
        old.deleteLater()

    def load_settings_ui(self):
        s=self.config['settings'];self.start_tray.setChecked(bool(s.get('start_minimized')));self.interval.setValue(int(s.get('rule_interval',1000)));self.rules_global.setChecked(bool(s.get('rules_enabled',True)))
        self.run_start.setChecked(self.autostart_enabled())
    def autostart_enabled(self):
        if os.name!='nt':return False
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,RUN_KEY) as k:winreg.QueryValueEx(k,APP_NAME)
            return True
        except Exception:return False
    def save_settings(self):
        self.config['settings'].update({'start_minimized':self.start_tray.isChecked(),'rule_interval':self.interval.value(),'rules_enabled':self.rules_global.isChecked()})
        self.timer.setInterval(self.interval.value());self.set_rules_ui_state()
        try:
            import winreg
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER,RUN_KEY) as k:
                if self.run_start.isChecked():
                    pyw=Path(sys.executable).with_name('pythonw.exe')
                    if not pyw.exists():pyw=Path(sys.executable)
                    cmd=f'"{pyw}" "{Path(__file__).resolve()}" --minimized'
                    winreg.SetValueEx(k,APP_NAME,0,winreg.REG_SZ,cmd)
                else:
                    try:winreg.DeleteValue(k,APP_NAME)
                    except FileNotFoundError:pass
        except Exception as e:QMessageBox.warning(self,t('Avvio Windows non aggiornato'),t('Impostazione locale salvata, ma non è stato possibile aggiornare il Registro:\n{e}', e=e))
        self.save();self.statusBar().showMessage(t('Impostazioni salvate'),4000)
    def set_rules_ui_state(self):
        enabled=bool(self.config['settings'].get('rules_enabled',True));self.monitor_badge.setStyleSheet('color:#54e3b5;background:#18332f;padding:8px 12px;border-radius:12px;' if enabled else 'color:#e4ba71;background:#382d1c;padding:8px 12px;border-radius:12px;')
    def save(self):
        try:salva_config(self.config)
        except Exception as e:QMessageBox.critical(self,t('Errore configurazione'),str(e))

    def applica_regole(self):
        if not self.config['settings'].get('rules_enabled',True) or not win32gui:return
        try:
            # Elimina gli HWND scomparsi e applica la prima regola corrispondente una volta.
            live=set(); candidates=[]
            def cb(hwnd,_):
                if finestra_valida(hwnd):
                    live.add(int(hwnd))
                    if int(hwnd) not in self.managed and int(win32process.GetWindowThreadProcessId(hwnd)[1])!=os.getpid():candidates.append(hwnd)
                return True
            win32gui.EnumWindows(cb,None); self.managed.intersection_update(live)
            for hwnd in candidates:
                proc=process_name(hwnd);title=win32gui.GetWindowText(hwnd)
                for rule in self.config['rules']:
                    if regola_corrisponde(rule,proc,title):
                        self.managed.add(int(hwnd))
                        sposta_hwnd(hwnd,int(rule.get('monitor',0)),rule.get('mode','Mantieni dimensione'),rule.get('custom'))
                        break
        except Exception:
            # Le finestre elevate o protette possono rifiutare le operazioni senza interrompere il timer.
            pass

    def make_tray(self):
        icon = QIcon()
        try:
            ico_path = Path(__file__).resolve().with_name('monitorpilot.ico')
            if not ico_path.exists():
                try:
                    from PIL import Image, ImageDraw
                    im = Image.new('RGBA', (64, 64), (12, 23, 26, 255))
                    draw = ImageDraw.Draw(im)
                    draw.rounded_rectangle((5, 5, 59, 48), radius=6, fill=(84, 227, 181, 255))
                    draw.rectangle((29, 48, 35, 56), fill=(84, 227, 181, 255))
                    draw.rounded_rectangle((19, 56, 45, 60), radius=2, fill=(84, 227, 181, 255))
                    im.save(ico_path, format='ICO', sizes=[(16,16),(32,32),(48,48),(64,64)])
                except Exception:
                    pass
            if ico_path.exists(): icon = QIcon(str(ico_path))
        except Exception:
            pass
        if icon.isNull():
            pix = QPixmap(64, 64); pix.fill(Qt.transparent)
            painter = QPainter(pix); painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor('#54e3b5')); painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(5, 5, 54, 44, 7, 7)
            painter.setBrush(QColor('#54e3b5')); painter.drawRect(29, 49, 6, 8)
            painter.drawRoundedRect(19, 57, 26, 4, 2, 2); painter.end()
            icon = QIcon(pix)
        try: self.setWindowIcon(icon)
        except Exception: pass
        try:
            self.tray = QSystemTrayIcon(icon, self)
            menu = QMenu(); show = QAction(t('Apri MonitorPilot'), self)
            show.triggered.connect(self.show_normal)
            quit_action = QAction(t('Esci'), self); quit_action.triggered.connect(self.quit_app)
            menu.addAction(show); menu.addSeparator(); menu.addAction(quit_action)
            self.tray.setContextMenu(menu)
            self.tray.activated.connect(lambda reason: self.show_normal() if reason == QSystemTrayIcon.DoubleClick else None)
            self.tray.show()
        except Exception:
            self.tray = QSystemTrayIcon(icon, self)
    def show_normal(self):self.show();self.setWindowState((self.windowState() & ~Qt.WindowMinimized)|Qt.WindowActive);self.raise_();self.activateWindow()
    def closeEvent(self,event):
        if not self.closing_to_tray and self.tray.isVisible():event.ignore();self.hide();self.tray.showMessage(t('MonitorPilot'),t('L’applicazione continua nell’area di notifica.'),QSystemTrayIcon.Information,2500)
        else:event.accept()
    def quit_app(self):self.closing_to_tray=True;self.tray.hide();QApplication.quit()

# -------------------------- Avvio / istanza singola -------------------------
def acquisisci_mutex():
    """Mutex Windows globale per impedire istanze parallele."""
    if os.name!='nt':return None
    try:
        handle=kernel32.CreateMutexW(None,False,'Local\\MonitorPilot_Instance_v1')
        ERROR_ALREADY_EXISTS=183
        if kernel32.GetLastError()==ERROR_ALREADY_EXISTS:return False
        return handle
    except Exception:return None


def main():
    parser=argparse.ArgumentParser(description='MonitorPilot - gestione desktop Windows')
    parser.add_argument('--minimized',action='store_true',help='Avvia nascosto nell’area di notifica')
    args,_=parser.parse_known_args()
    mutex=acquisisci_mutex()
    if mutex is False:
        try:
            app=QApplication(sys.argv);QSystemTrayIcon.showMessage(QSystemTrayIcon(),'MonitorPilot',t('È già in esecuzione.'))
        except Exception:pass
        return 0
    config=carica_config()
    global CURRENT_LANGUAGE
    CURRENT_LANGUAGE=config['language']
    try:
        if os.name == 'nt':
            try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('MonitorPilot.App')
            except Exception: pass
        app=QApplication(sys.argv);app.setApplicationName(APP_NAME);app.setQuitOnLastWindowClosed(False)
        try:
            _app_icon_path = Path(__file__).resolve().with_name('monitorpilot.ico')
            if _app_icon_path.exists(): app.setWindowIcon(QIcon(str(_app_icon_path)))
        except Exception: pass
        app.setStyle('Fusion')
        hidden=args.minimized or bool(config['settings'].get('start_minimized',False))
        window=MainWindow(config,hidden);window.show() if not hidden else None
        app._monitorpilot_window=window
        # Mantiene vivo l'handle mutex per tutto il ciclo di vita.
        app._monitorpilot_mutex=mutex
        return app.exec()
    except Exception as exc:
        errore=t('Avvio MonitorPilot non riuscito:')+'\n'+str(exc)+'\n\n'+traceback.format_exc()
        if os.name=='nt':
            try:user32.MessageBoxW(0,errore,'MonitorPilot - errore',0x10)
            except Exception:pass
        else:print(errore,file=sys.stderr)
        return 1

if __name__ == '__main__':
    main()
