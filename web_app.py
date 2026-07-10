import streamlit as st
import csv
import json
from groq import Groq

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Immobiliare Premium", page_icon="🏠")
st.title("🏠 Immobiliare Premium")

# Inserisci la tua chiave API
API_KEY = ""
client = Groq(api_key=API_KEY)

# --- PROMPT DI SISTEMA CORRETTO ---
PROMPT_SISTEMA = """
Sei l'assistente telefonico di Immobiliare Premium. Il tuo compito è raccogliere i dati del cliente per un appuntamento immobiliare.
Raccogli queste informazioni una alla volta, seguendo rigorosamente questo ordine:
1. Nome e Cognome del cliente.
2. Se cerca in affitto o in acquisto.
3. Il budget massimo.
4. Il numero di telefono.
5. L'orario preferito per essere ricontattato. ACCETTA QUALSIASI NUMERO INTERO TRA 9 E 18 (es. 9, 10, 11, 12, 13, 14, 15, 16, 17, 18).
6. Il GIORNO preferito per l'appuntamento.

REGOLE RIGIDE:
- NON fare esempi di orario durante la conversazione. Chiedi l'orario e basta.
- Se l'utente scrive un numero compreso tra 9 e 18, consideralo valido e procedi alla domanda successiva.
- Se l'utente fa domande fuori pista, rispondi che non puoi fornirle e torna a chiedere il dato mancante.
- Alla fine di ogni tua risposta, aggiungi SEMPRE la riga strutturata JSON:
[DATA: {"nome": "N/D", "servizio": "N/D", "budget": "N/D", "telefono": "N/D", "orario": "N/D", "giorno": "N/D"}]
- Quando hai finito, scrivi un saluto e il tag [CHIUDI_CHAT].
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": PROMPT_SISTEMA}]
    st.session_state.scheda = {"nome": "N/D", "servizio": "N/D", "budget": "N/D", "telefono": "N/D", "orario": "N/D", "giorno": "N/D"}

def pulisci_visualizzazione(text):
    # Rimuove il JSON e il tag di chiusura dalla vista dell'utente
    text = text.split("[DATA:")[0].replace("[CHIUDI_CHAT]", "").strip()
    return text

# Funzione per il design del riepilogo
def mostra_riepilogo():
    s = st.session_state.scheda
    st.markdown("---")
    st.success("✅ Appuntamento telefonico salvato!")
    st.subheader("📋 Riepilogo Dati Cliente")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**👤 Nome:** {s['nome']}")
        st.write(f"**🏠 Servizio:** {s['servizio']}")
        st.write(f"**💰 Budget:** {s['budget']}")
    with col2:
        st.write(f"**📞 Telefono:** {s['telefono']}")
        st.write(f"**🕒 Orario:** {s['orario']}")
        st.write(f"**📅 Giorno:** {s['giorno']}")

# Visualizzazione Chat
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(pulisci_visualizzazione(msg["content"]))

# Input Utente
if user_input := st.chat_input("Scrivi qui..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        stream = client.chat.completions.create(
            model="llama-3.1-8b-instant", messages=st.session_state.messages, stream=True, temperature=0
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_res += chunk.choices[0].delta.content
                placeholder.markdown(pulisci_visualizzazione(full_res))
    
    st.session_state.messages.append({"role": "assistant", "content": full_res})

    # Parsing dati
    if "[DATA:" in full_res:
        try:
            dati_str = full_res.split("[DATA:")[1].split("]")[0]
            nuovi_dati = json.loads(dati_str)
            for k, v in nuovi_dati.items():
                if v != "N/D": st.session_state.scheda[k] = v
        except: pass

    # Salvataggio finale
    if "[CHIUDI_CHAT]" in full_res:
        with open("appuntamenti.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(st.session_state.scheda.values())
        mostra_riepilogo() # Mostra il design pulito
        st.stop()
