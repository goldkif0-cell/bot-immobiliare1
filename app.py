import re
import ollama
import json
import os

# --- 1. CARICAMENTO CONFIGURAZIONE ---
# Assicurati che il file config.json sia nella stessa cartella di questo script
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

NOME_MODELLO = "llama3:8b-instruct-fp16"

# Prompt aziendale dinamico
PROMPT_SISTEMA_AZIENDALE = (
    f"Tu sei l'assistente virtuale ufficiale di '{config['nome_azienda']}' con sede in {config['sede']}.\n"
    f"Il tuo obiettivo è assistere i clienti per {config['descrizione']}.\n\n"
    "LINEE GUIDA PER IL TONO DI VOCE:\n"
    "- Mantieni un tono altamente professionale, serio, educato e formale (usa sempre il 'Lei').\n"
    "- Evita lodi sperticate, servilismi o l'uso di formule eccessivamente cerimonie.\n"
    "- Sii sintetico, chiaro e sicuro di te (massimo 2-3 frasi per risposta).\n\n"
    "REGOLE DI CONTROLLO DEL PERIMETRO (GUARDRAILS):\n"
    "- Se il cliente fa domande fuori contesto, rispondi con fermezza e cortesia che il tuo supporto è limitato esclusivamente ai servizi di "
    f"'{config['nome_azienda']}'.\n"
    "- Se il cliente chiede cataloghi, listini o foto, confermagli in modo professionale che il consulente che lo contatterà avrà cura di fornirgli tutto il materiale aggiornato.\n\n"
    "ISTRUZIONE PER IL FLUSSO:\n"
    "Rispondi alla domanda o affermazione attuale del cliente rispettando il tono sopra indicato. "
    "Subito dopo, se non siamo in una fase di congedo, chiedi cortesemente se ha altre richieste o se desidera concludere la conversazione."
)

# --- 2. FUNZIONI DI SUPPORTO ---

def comunica_con_ia(prompt_sistema, istruzione_utente):
    try:
        risposta = ollama.chat(
            model=NOME_MODELLO,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": istruzione_utente},
            ],
        )
        return risposta["message"]["content"].strip()
    except Exception:
        return "Mi scuso, ma si è verificato un errore tecnico temporaneo."

def valida_con_ia(tipo_controllo, testo_utente):
    # Logica invariata, mantiene la validazione rigorosa
    if tipo_controllo == "servizio":
        prompt = (f"Analizza l'intento: '{testo_utente}'. Rispondi solo 'AFFITTO', 'VENDITA' o 'NON_VALIDO'.")
    elif tipo_controllo == "chiusura":
        prompt = (f"Analizza l'ultimo messaggio: '{testo_utente}'. Rispondi solo 'CHIUDI' o 'CONTINUA'.")
    
    risultato = comunica_con_ia("Agisci come un classificatore logico di testo rigido. Rispondi con una sola parola.", prompt)
    return "".join(re.findall(r'[A-Za-z_]', risultato)).upper()

# --- 3. LOGICA DI ESECUZIONE ---

scheda_cliente = {"servizio": "", "budget": "", "telefono": "", "appuntamento_orario": ""}

print(f"--- [SISTEMA DI ASSISTENZA {config['nome_azienda'].upper()}] ---\n")
print(f"Bot Aziendale: Buongiorno. Benvenuto in {config['nome_azienda']}. Desidera informazioni per vendere o per prendere in affitto un immobile?")
print("-" * 60)

# ... [IL RESTO DEL TUO CICLO WHILE RIMANE UGUALE A PRIMA] ...
# (Assicurati di lasciare invariata la logica di raccolta dati che avevi già scritto)

# Esempio per il salvataggio finale, ora puoi usare anche il nome azienda dinamico
print(f"\n[REGISTRO LEAD ARCHIVIATO CON SUCCESSO PER {config['nome_azienda']}]")
print(f" -> Servizio:    {scheda_cliente['servizio']}")
# ... ecc ...