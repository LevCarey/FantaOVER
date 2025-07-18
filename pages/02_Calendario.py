# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 10:15:19 2025

@author: malci
"""

# pages/02_Calendario.py

import streamlit as st
import pandas as pd
from pathlib import Path

# === PERCORSI RELATIVI ===
# Siamo in pages/, quindi saliamo alla root del progetto (dove sta Home.py)
BASE_DIR = Path(__file__).parent.parent
CARTELLA_DATI = BASE_DIR / "dati"

# ATTENZIONE: usa il nome esatto del file in /dati
FILE_CALENDARIO = CARTELLA_DATI / "fantacalendario.xlsx"  # <-- cambia se il nome è diverso

# === TITOLO PAGINA ===
st.title("📅 Calendario")

# === STILE CSS PER LINK NON SOTTOLINEATI E NON BLU ===
st.markdown("""
    <style>
    a.link-squadra {
        text-decoration: none;
        color: inherit;
    }
    a.link-squadra:hover {
        text-decoration: none;
        color: #14d928;
    }
    </style>
""", unsafe_allow_html=True)

# === CARICA CALENDARIO ===
@st.cache_data
def carica_calendario(path: Path):
    return pd.read_excel(path)

try:
    df = carica_calendario(FILE_CALENDARIO)
except FileNotFoundError:
    st.error(f"File calendario non trovato: {FILE_CALENDARIO}")
    st.stop()

# === INIZIALIZZA session_state ===
if "serie_scelta" not in st.session_state:
    # fallback alla prima serie disponibile nel file, se esiste "Serie" come colonna
    if "Serie" in df.columns and not df["Serie"].empty:
        st.session_state["serie_scelta"] = sorted(df["Serie"].dropna().unique())[0]
    else:
        st.session_state["serie_scelta"] = "Serie A"

# === BOTTONI PER SCEGLIERE LA SERIE ===
col1, col2 = st.columns(2)
with col1:
    if st.button("Serie A"):
        st.session_state["serie_scelta"] = "Serie A"
with col2:
    if st.button("Serie B"):
        st.session_state["serie_scelta"] = "Serie B"

serie_scelta = st.session_state["serie_scelta"]
st.markdown(f"**{serie_scelta}**")

df_filtrato = df[df["Serie"] == serie_scelta]

# === FUNZIONE LINK ALLA PAGINA ROSE ===
# Nelle multipage Streamlit, il percorso relativo a una pagina dipende dal titolo.
# Se la tua pagina "Rose" è pages/01_Rose.py e titolo "Rose", l'URL tipico sarà .../Rose
# Usiamo query param ?squadra=... per passarla.
def link_squadra(nome_squadra: str) -> str:
    return f'<a href="/Rose?squadra={nome_squadra}" class="link-squadra" target="_self">{nome_squadra}</a>'

# Se preferisci un link robusto che funzioni anche con percorsi dinamici, puoi invece mostrare un pulsante con st.page_link
# (commentato qui per semplicità)

# === DIVIDI IN ANDATA E RITORNO ===
# (adatta le soglie se cambiano il numero di giornate)
andata = df_filtrato[df_filtrato["Giornata"] <= 7]
ritorno = df_filtrato[df_filtrato["Giornata"] > 7]

col1, col2 = st.columns(2)

# === COLONNA SINISTRA: ANDATA ===
with col1:
    st.subheader("Andata")
    for giornata in sorted(andata["Giornata"].unique()):
        st.markdown(f"**Giornata {giornata}**")
        partite = andata[andata["Giornata"] == giornata][["Casa", "Trasferta"]]

        for _, row in partite.iterrows():
            casa = row["Casa"]
            trasferta = row["Trasferta"]
            st.markdown(
                f"- {link_squadra(casa)} - {link_squadra(trasferta)} = ⬜⬜",
                unsafe_allow_html=True
            )

# === COLONNA DESTRA: RITORNO ===
with col2:
    st.subheader("Ritorno")
    for giornata in sorted(ritorno["Giornata"].unique()):
        st.markdown(f"**Giornata {giornata}**")
        partite = ritorno[ritorno["Giornata"] == giornata][["Casa", "Trasferta"]]

        for _, row in partite.iterrows():
            casa = row["Casa"]
            trasferta = row["Trasferta"]
            st.markdown(
                f"- {link_squadra(casa)} - {link_squadra(trasferta)} = ⬜⬜",
                unsafe_allow_html=True
            )
