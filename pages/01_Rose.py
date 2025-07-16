# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 18:20:20 2025

@author: malci
"""

# pages/01_Rose.py

import streamlit as st
import pandas as pd
from pathlib import Path

# === COSTANTI ===
CARTELLA_DATI = Path(st.secrets["cartella_dati"])
FILE_ROSE = CARTELLA_DATI / "Rose Fantasquadre.xlsx"

@st.cache_data
def carica_rose():
    return pd.read_excel(FILE_ROSE)

# === TITOLO PAGINA ===
st.title("Rose")

df = carica_rose()


# === CREA LISTA FANTASQUADRE UNICHE con SERIE ===
# Supponiamo che ogni squadra sia associata a una sola Serie (A o B)
info_fantasquadre = df.groupby("Fantasquadra").agg({
    "Serie": "first",
    "Presidente": "first"
}).reset_index()

# Ordina dataset
info_fantasquadre = info_fantasquadre.sort_values(by=["Serie", "Fantasquadra"])


# Collegamento dalla pagina 02_Calendario
# === RILEVA PARAMETRO DALL'URL (es. ?squadra=SquadraX) ===
query_params = st.query_params
param_squadra = query_params.get("squadra")

# Se presente, forza la selezione iniziale
if param_squadra and param_squadra in df["Fantasquadra"].unique():
    serie_default = df[df["Fantasquadra"] == param_squadra]["Serie"].iloc[0]
    squadra_default = param_squadra
else:
    serie_default = sorted(info_fantasquadre["Serie"].unique())[0]
    squadra_default = None


# === MENU SERIE ===
serie_scelta = st.selectbox("Seleziona la Serie", sorted(info_fantasquadre["Serie"].unique()), index=sorted(info_fantasquadre["Serie"].unique()).index(serie_default))

# Filtra squadre della serie scelta
squadre_filtrate = info_fantasquadre[info_fantasquadre["Serie"] == serie_scelta]

# Crea etichetta: "Nome Fantasquadra – Nome Presidente"
squadre_filtrate = info_fantasquadre[info_fantasquadre["Serie"] == serie_scelta].copy()
squadre_filtrate.loc[:, "etichetta"] = squadre_filtrate["Fantasquadra"] + " – " + squadre_filtrate["Presidente"]

# Mappa etichetta → fantasquadra
mappa_fantasquadre = dict(zip(squadre_filtrate["etichetta"], squadre_filtrate["Fantasquadra"]))

# === MENU FANTASQUADRA ===
scelta_etichetta = st.selectbox("Seleziona una fantasquadra", squadre_filtrate["etichetta"],
                                index=squadre_filtrate["Fantasquadra"].tolist().index(squadra_default)
                                if squadra_default in squadre_filtrate["Fantasquadra"].tolist() else 0)

# Fantasquadra selezionata
scelta_squadra = mappa_fantasquadre[scelta_etichetta]

# === FILTRA ROSA DELLA SQUADRA ===
rosa = df[df["Fantasquadra"] == scelta_squadra].copy()
presidente = rosa["Presidente"].iloc[0]

if rosa.empty:
    st.warning("Questa fantasquadra non ha ancora giocatori.")
else:
    # === FILTRO PER RUOLO ===
    ruoli_base = ["P", "D", "C", "A"]
    ruoli_scelti = st.multiselect("Filtra per ruolo", ruoli_base, default=ruoli_base)

    def contiene_ruolo(ruoli_giocatore, ruoli_selezionati):
        ruoli_individuali = [r.strip() for r in ruoli_giocatore.split(",")]
        return any(r in ruoli_individuali for r in ruoli_selezionati)

    rosa_filtrata = rosa[rosa["Ruolo"].apply(lambda x: contiene_ruolo(x, ruoli_scelti))]

    # === RICREA INDICE ===
    rosa_filtrata.index = range(1, len(rosa_filtrata) + 1)

    # === MOSTRA TABELLA ===
    st.dataframe(rosa_filtrata[["Nome", "Squadra", "Ruolo", "Costo"]], use_container_width=True, height=1087)
