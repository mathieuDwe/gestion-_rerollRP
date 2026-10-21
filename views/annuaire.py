import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("📖 Contacts Externes")

  with st.form("form_annuaire"):
    col1, col2, col3 = st.columns(3)
    nom_a = col1.text_input("Nom")
    prenom_a = col2.text_input("Prénom")
    num_a = col3.number_input("Numéro", value=0, step=1)
    submit_a = st.form_submit_button("Ajouter le contact")

    if submit_a and nom_a:
      run_query(
          "INSERT INTO annuaire (nom, prenom, num) VALUES (%s, %s, %s)",
          (nom_a, prenom_a, num_a),
      )
      st.success("Contact ajouté !")
      st.rerun()

  data_annuaire = run_query(
      "SELECT id, nom, prenom, num FROM annuaire", fetch=True
  )
  if data_annuaire:
    df_annuaire = pd.DataFrame(
        data_annuaire, columns=["ID", "Nom", "Prénom", "Numéro"]
    )
    st.dataframe(df_annuaire, use_container_width=True)

    id_del_an = st.number_input(
        "ID du contact à supprimer", min_value=0, step=1, key="del_an"
    )
    if st.button("Supprimer ce contact"):
      run_query("DELETE FROM annuaire WHERE id = %s", (id_del_an,))
      st.warning("Contact supprimé.")
      st.rerun()
  else:
    st.info("Annuaire vide.")