import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("📦 Gestion du Stockage")

  # --- AJOUT D'UN OBJET ---
  with st.form("form_object"):
    st.subheader("Ajouter un nouvel objet")
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

  st.markdown("---")

  # Affichage du stock actuel
  data_stock = run_query(
      "SELECT id, object, quantite, poid, revente FROM object", fetch=True
  )
  if data_stock:
    df_stock = pd.DataFrame(
        data_stock, columns=["ID", "Objet", "Quantité", "Poids", "Revente"]
    )
    st.dataframe(df_stock, use_container_width=True)

    col_mod, col_del = st.columns(2)

    # --- MODIFIER LA QUANTITÉ ---
    with col_mod:
      with st.form("form_update_stock"):
        st.subheader("Modifier une quantité")
        id_mod = st.number_input(
            "ID de l'objet à modifier", min_value=0, step=1, key="mod_id"
        )
        new_quantite = st.number_input(
            "Nouvelle quantité", min_value=0, step=1, key="mod_qty"
        )
        submit_mod = st.form_submit_button("Mettre à jour la quantité")

        if submit_mod:
          run_query(
              "UPDATE object SET quantite = %s WHERE id = %s",
              (new_quantite, id_mod),
          )
          st.success(
              f"Quantité de l'objet ID {id_mod} mise à jour avec succès !"
          )
          st.rerun()

    # --- SUPPRIMER UN OBJET ---
    with col_del:
      with st.form("form_delete_stock"):
        st.subheader("Supprimer un objet")
        id_del = st.number_input(
            "ID de l'objet à supprimer", min_value=0, step=1, key="del_obj"
        )
        submit_del = st.form_submit_button("Supprimer cet objet")

        if submit_del:
          run_query("DELETE FROM object WHERE id = %s", (id_del,))
          st.warning("Objet supprimé de la base.")
          st.rerun()
  else:
    st.info("Le stock est actuellement vide.")
