# -*- coding: utf-8 -*-
"""
Created on Wed Jul 16 10:15:19 2025

@author: malci
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# === CONFIG ===
secrets = st.secrets
CARTELLA_DATI = Path(secrets["cartella_dati"])
FILE_CALENDARIO = CARTELLA_DATI / "FantaCalendario.xlsx"

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
        text-decoration: none;  /* niente sottolineatura */
        color: #14d928;  /* colore opzionale al passaggio del mouse */
    }
    </style>
""", unsafe_allow_html=True)


# === CARICA CALENDARIO ===
df = pd.read_excel(FILE_CALENDARIO)

# === INIZIALIZZA session_state ===
if "serie_scelta" not in st.session_state:
    st.session_state["serie_scelta"] = "Serie A"  # default

# === BOTTONI PER SCEGLIERE LA SERIE ===
col1, col2 = st.columns(2)
with col1:
    if st.button("Serie A"):
        st.session_state["serie_scelta"] = "Serie A"
with col2:
    if st.button("Serie B"):
        st.session_state["serie_scelta"] = "Serie B"

serie_scelta = st.session_state["serie_scelta"]

st.markdown(f"{serie_scelta}")

df_filtrato = df[df["Serie"] == serie_scelta]

# === FUNZIONE PER LINK ALLA PAGINA ROSE ===
def link_squadra(nome_squadra):
    return f'<a href="/Rose?squadra={nome_squadra}" class="link-squadra" target="_self">{nome_squadra}</a>'

# === DIVIDI IN ANDATA E RITORNO ===
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
            link_casa = link_squadra(casa)
            link_trasferta = link_squadra(trasferta)
            st.markdown(f"- {link_casa} - {link_trasferta} = ⬜⬜", unsafe_allow_html=True)

# === COLONNA DESTRA: RITORNO ===
with col2:
    st.subheader("Ritorno")
    for giornata in sorted(ritorno["Giornata"].unique()):
        st.markdown(f"**Giornata {giornata}**")
        partite = ritorno[ritorno["Giornata"] == giornata][["Casa", "Trasferta"]]

        for _, row in partite.iterrows():
            casa = row["Casa"]
            trasferta = row["Trasferta"]
            link_casa = link_squadra(casa)
            link_trasferta = link_squadra(trasferta)
            st.markdown(f"- {link_casa} - {link_trasferta} = ⬜⬜", unsafe_allow_html=True)
