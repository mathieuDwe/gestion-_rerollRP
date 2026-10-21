import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("📦 Gestion du Stockage")

  with st.form("form_object"):
    col1, col2, col3, col4 = st.columns(4)
    obj_nom = col1.text_input("Nom de l'objet")
    quantite = col2.number_input("Quantité", min_value=0, step=1)
    poid = col3.number_input("Poids", min_value=0, step=1)
    revente = col4.number_input("Prix Revente", min_value=0.0, step=1.0)
    submit = st.form_submit_button("Ajouter l'objet")

    if submit and obj_nom:
      run_query(
          "INSERT INTO object (object, quantite, poid, revente) VALUES (%s,"
          " %s, %s, %s)",
          (obj_nom, quantite, poid, revente),
      )
      st.success("Objet ajouté avec succès !")
      st.rerun()

  data_stock = run_query(
      "SELECT id, object, quantite, poid, revente FROM object", fetch=True
  )
  if data_stock:
    df_stock = pd.DataFrame(
        data_stock, columns=["ID", "Objet", "Quantité", "Poids", "Revente"]
    )
    st.dataframe(df_stock, use_container_width=True)

    id_del = st.number_input(
        "ID de l'objet à supprimer", min_value=0, step=1, key="del_obj"
    )
    if st.button("Supprimer cet objet"):
      run_query("DELETE FROM object WHERE id = %s", (id_del,))
      st.warning("Objet supprimé.")
      st.rerun()
  else:
    st.info("Stock vide.")