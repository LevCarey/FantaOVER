# -*- coding: utf-8 -*-
"""
Created on Sat Jul 12 16:25:39 2025

@author: malci
"""

import streamlit as st
import pandas as pd
from pathlib import Path

# Prende il percorso della cartella FantaDati dal file secrets.toml
CARTELLA_DATI = Path(st.secrets["cartella_dati"])
FILE_ROSE = CARTELLA_DATI / "Rose Fantasquadre.xlsx"
FILE_GIOCATORI = CARTELLA_DATI / "Database giocatori.xlsx"


@st.cache_data
def carica_rose():
    return pd.read_excel(FILE_ROSE)

@st.cache_data
def carica_giocatori():
    return pd.read_excel(FILE_GIOCATORI)

moduli_validi = {
    "5-4-1": (5, 4, 1),
    "5-3-2": (5, 3, 2),
    "4-5-1": (4, 5, 1),
    "4-4-2": (4, 4, 2),
    "4-3-3": (4, 3, 3),
    "3-5-2": (3, 5, 2),
    "3-4-3": (3, 4, 3),
}

def salva_formazione(df, username):
    """
    Salva il DataFrame formazione nella cartella specificata nei secrets,
    con nome file Formazione_<username>.xlsx
    """
    cartella_formazioni = Path(st.secrets["cartella_formazioni"])
    cartella_formazioni.mkdir(parents=True, exist_ok=True)
    nome_file = cartella_formazioni / f"Formazione_{username.replace(' ', '_')}.xlsx"
    df.to_excel(nome_file, index=False)
    return nome_file


# === LOGIN / LOGOUT ===

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.nome_squadra = None
    st.session_state.username = None

utenti = st.secrets["utenti"]
squadre = st.secrets["nome_fantasquadra"]

if not st.session_state.logged_in:
    username = st.text_input("Nome utente", key="username_input")
    password_inserita = st.text_input("Inserisci la password", type="password", key="password_input")

    if st.button("Login"):
        if password_inserita == utenti.get(username):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.nome_squadra = squadre[username]
            st.rerun()
        else:
            st.error("Nome utente o password errati")
    st.stop()

# Se qui, sei loggato
nome_squadra = st.session_state.nome_squadra
username = st.session_state.username

st.markdown(f"### Benvenuto, **{username}**")

# Sidebar con info utente e logout
st.sidebar.markdown("## 👤 Accesso")
st.sidebar.markdown(f"**Utente:** {username}")
st.sidebar.markdown(f"**Fantasquadra:** {nome_squadra}")
if st.sidebar.button("🔒 Logout"):
    st.session_state.logged_in = False
    st.session_state.nome_squadra = None
    st.session_state.username = None
    st.rerun()


# --- CARICAMENTO DATI DOPO LOGIN ---

rose_df = carica_rose()
giocatori_df = carica_giocatori()
rosa = rose_df[rose_df["Presidente"] == username]

st.title("Inserisci la formazione")

modulo = st.selectbox("Scegli il modulo", list(moduli_validi.keys()))
n_dif, n_cent, n_att = moduli_validi[modulo]

def etichetta_giocatore(row):
    return f"{row['Nome']} ({row['Squadra']} - {row['Ruolo']})"

def estrai_nome(etichetta):
    return etichetta.split(" (")[0] if etichetta else None

giocatori_scelti = set()

# Portiere
st.subheader("Portiere")
portieri_df = rosa[rosa["Ruolo"].str.contains("P")]
portieri_options = [""] + portieri_df.apply(etichetta_giocatore, axis=1).tolist()
sel_portiere_label = st.selectbox(" ", [g for g in portieri_options if estrai_nome(g) not in giocatori_scelti], key="portiere", label_visibility="collapsed")
sel_portiere = estrai_nome(sel_portiere_label)
if sel_portiere:
    giocatori_scelti.add(sel_portiere)

# Difensori
st.subheader("Difensori")
difensori_df = rosa[rosa["Ruolo"].str.contains("D")]
difensori_options = [""] + difensori_df.apply(etichetta_giocatore, axis=1).tolist()
sel_dif = []
for i in range(n_dif):
    opzioni_disponibili = [g for g in difensori_options if estrai_nome(g) not in giocatori_scelti]
    label = st.selectbox(" ", opzioni_disponibili, key=f"dif_{i}", label_visibility="collapsed")
    nome = estrai_nome(label)
    if nome:
        sel_dif.append(nome)
        giocatori_scelti.add(nome)

# Centrocampisti
st.subheader("Centrocampisti")
centrocampisti_df = rosa[rosa["Ruolo"].str.contains("C")]
centrocampisti_options = [""] + centrocampisti_df.apply(etichetta_giocatore, axis=1).tolist()
sel_cent = []
for i in range(n_cent):
    opzioni_disponibili = [g for g in centrocampisti_options if estrai_nome(g) not in giocatori_scelti]
    label = st.selectbox(" ", opzioni_disponibili, key=f"cent_{i}", label_visibility="collapsed")
    nome = estrai_nome(label)
    if nome:
        sel_cent.append(nome)
        giocatori_scelti.add(nome)

# Attaccanti
st.subheader("Attaccanti")
attaccanti_df = rosa[rosa["Ruolo"].str.contains("A")]
attaccanti_options = [""] + attaccanti_df.apply(etichetta_giocatore, axis=1).tolist()
sel_att = []
for i in range(n_att):
    opzioni_disponibili = [g for g in attaccanti_options if estrai_nome(g) not in giocatori_scelti]
    label = st.selectbox(" ", opzioni_disponibili, key=f"att_{i}", label_visibility="collapsed")
    nome = estrai_nome(label)
    if nome:
        sel_att.append(nome)
        giocatori_scelti.add(nome)

# Panchina
st.subheader("Panchina")
panchina_df = rosa[~rosa["Nome"].isin(giocatori_scelti)]
panchina_options = panchina_df.apply(etichetta_giocatore, axis=1).tolist()
panchina_selezionata = st.multiselect(
    "Seleziona giocatori per la panchina (max 11)",
    options=panchina_options,
    max_selections=11
)
panchina = [estrai_nome(label) for label in panchina_selezionata if label]


# Prima definisci la cartella Formazioni
CARTELLA_FORMAZIONI = Path(st.secrets["cartella_formazioni"])

# === SALVA FORMAZIONE ===

if st.button("Salva Formazione"):
    errori = []
    if not sel_portiere:
        errori.append("Devi scegliere un portiere")
    if len(sel_dif) != n_dif:
        errori.append(f"Scegli esattamente {n_dif} difensori")
    if len(sel_cent) != n_cent:
        errori.append(f"Scegli esattamente {n_cent} centrocampisti")
    if len(sel_att) != n_att:
        errori.append(f"Scegli esattamente {n_att} attaccanti")
    if errori:
        for e in errori:
            st.error(e)
        st.stop()

    titolari = []
    titolari.append((sel_portiere, "P"))
    titolari.extend([(g, "D") for g in sel_dif])

    # Logica centrocampisti
    mod_difensivo = modulo in ["5-4-1", "5-3-2", "4-3-3"]
    for i, g in enumerate(sel_cent):
        if (mod_difensivo and i == 0) or (not mod_difensivo and i < 2):
            ruolo_modulo = "C dif"
        else:
            ruolo_modulo = "C off"
        titolari.append((g, ruolo_modulo))

    titolari.extend([(g, "A") for g in sel_att])

    dati_salva = []
    for nome_giocatore, ruolo_modulo_gioc in titolari:
        r_rosa = rosa[rosa["Nome"] == nome_giocatore].iloc[0]
        r_gioc = giocatori_df[giocatori_df["Nome"] == nome_giocatore].iloc[0]
        dati_salva.append({
            "Codice WS": r_gioc["Codice WS"],
            "Nome": nome_giocatore,
            "Squadra": r_gioc["Squadra"],
            "Ruolo": r_gioc["Ruolo"],
            "Fantasquadra": r_rosa["Fantasquadra"],
            "Modulo": modulo,
            "Ruolo Modulo": ruolo_modulo_gioc,
            "Presidente": username,
        })

    for nome_giocatore in panchina:
        r_rosa = rosa[rosa["Nome"] == nome_giocatore].iloc[0]
        r_gioc = giocatori_df[giocatori_df["Nome"] == nome_giocatore].iloc[0]
        dati_salva.append({
            "Codice WS": r_gioc["Codice WS"],
            "Nome": nome_giocatore,
            "Squadra": r_gioc["Squadra"],
            "Ruolo": r_gioc["Ruolo"],
            "Fantasquadra": r_rosa["Fantasquadra"],
            "Modulo": modulo,
            "Ruolo Modulo": "",
            "Presidente": username,
        })

    df_salva = pd.DataFrame(dati_salva)

    nome_file = salva_formazione(df_salva, username)
    st.success(f"Formazione salvata in '{nome_file}'")


# Mostra la formazione completa (Titolari, Panchina, Non convocati)

    # Titolari: quelli con "Ruolo Modulo" non vuoto
    titolari_df = df_salva[df_salva["Ruolo Modulo"] != ""]
    titolari_df.index = range(1, len(titolari_df) + 1)
    st.subheader("Titolari")
    # Altezza fissa per 11 righe circa (50 px per riga * 11 = 550)
    st.dataframe(titolari_df[["Nome", "Squadra", "Ruolo", "Ruolo Modulo"]], use_container_width=True, height=423)

    # Panchina: quelli con "Ruolo Modulo" vuoto
    panchina_df = df_salva[df_salva["Ruolo Modulo"] == ""]
    panchina_df.index = range(12, 12 + len(panchina_df))
    st.subheader("Panchina")
    # Altezza fissa per 11 righe
    st.dataframe(panchina_df[["Nome", "Squadra", "Ruolo"]], use_container_width=True, height=423)

    # Giocatori convocati (titolari + panchina)
    convocati = df_salva["Nome"].tolist()

    # Filtra rosa per la fantasquadra corrente
    rosa_mia = rose_df[rose_df["Presidente"] == username]

    # Giocatori non convocati: quelli in rosa_mia ma non in convocati
    non_convocati_df = rosa_mia[~rosa_mia["Nome"].isin(convocati)]
    non_convocati_df.index = range(1, len(non_convocati_df) + 1)

    st.subheader("Non convocati")
    if len(non_convocati_df) == 0:
        st.write("Tutti i giocatori della rosa sono convocati.")
    else:
        # Altezza fissa per 8 righe (dato che la rosa massima sono 30 giocatori)
        st.dataframe(non_convocati_df[["Nome", "Squadra", "Ruolo"]], use_container_width=True, height=317)
