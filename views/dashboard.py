import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("📊 Tableau de Bord - Fafnir")
  st.write(f"Bienvenue sur l'espace d'administration, {st.session_state.current_user}.")

  try:
    nb_stock = len(run_query("SELECT * FROM object", fetch=True))
    nb_membres = len(run_query("SELECT * FROM users", fetch=True))
    nb_contacts = len(run_query("SELECT * FROM annuaire", fetch=True))
    nb_amendes = len(run_query("SELECT * FROM amende", fetch=True))
  except:
    nb_stock, nb_membres, nb_contacts, nb_amendes = 0, 0, 0, 0

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("📦 Objets en Stock", nb_stock)
  col2.metric("👥 Membres Inscrits", nb_membres)
  col3.metric("📖 Contacts Annuaire", nb_contacts)
  col4.metric("⚖️ Amendes / Récidives", nb_amendes)