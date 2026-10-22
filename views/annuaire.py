import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("📖 Annuaire")

  # --- FORMULAIRE D'AJOUT ---
  with st.form("form_annuaire"):
    st.subheader("Ajouter un contact à l'annuaire")
    col1, col2 = st.columns(2)
    nom = col1.text_input("Nom")
    prenom = col2.text_input("Prénom")

    col3, col4 = st.columns(2)
    num = col3.number_input("Numéro", value=0, step=1)
    groupe_service = col4.text_input("Groupe / Service")

    submit = st.form_submit_button("Ajouter le contact")

    if submit and nom:
      # Utilisation des guillemets doubles pour la colonne "groupe/service"
      run_query(
          'INSERT INTO annuaire (nom, prenom, num, "groupe/service") VALUES'
          " (%s, %s, %s, %s)",
          (nom, prenom, num, groupe_service),
      )
      st.success("Contact ajouté avec succès à l'annuaire !")
      st.rerun()

  st.markdown("---")

  # --- AFFICHAGE DE L'ANNUAIRE ---
  data_annuaire = run_query(
      'SELECT id, nom, prenom, num, "groupe/service" FROM annuaire', fetch=True
  )

  if data_annuaire:
    df_annuaire = pd.DataFrame(
        data_annuaire, columns=["ID", "Nom", "Prénom", "Numéro", "Groupe/Service"]
    )
    df_annuaire = df_annuaire.astype({"ID": int})
    st.dataframe(df_annuaire, use_container_width=True)

    col_mod, col_del = st.columns(2)

    # --- MODIFIER LE GROUPE/SERVICE ---
    with col_mod:
      with st.form("form_update_annuaire"):
        st.subheader("Modifier le Groupe/Service")
        id_mod = st.number_input(
            "ID du contact", min_value=0, step=1, key="mod_ann_id"
        )
        new_groupe = st.text_input("Nouveau Groupe/Service", key="mod_ann_grp")
        submit_mod = st.form_submit_button("Mettre à jour")

        if submit_mod and id_mod > 0:
          run_query(
              'UPDATE annuaire SET "groupe/service" = %s WHERE id = %s',
              (new_groupe, id_mod),
          )
          st.success(
              f"Groupe/Service du contact ID {id_mod} mis à jour avec"
              " succès !"
          )
          st.rerun()

    # --- SUPPRIMER UN CONTACT ---
    with col_del:
      with st.form("form_delete_annuaire"):
        st.subheader("Supprimer un contact")
        id_del = st.number_input(
            "ID du contact à supprimer", min_value=0, step=1, key="del_ann_id"
        )
        submit_del = st.form_submit_button("Supprimer")

        if submit_del and id_del > 0:
          run_query("DELETE FROM annuaire WHERE id = %s", (id_del,))
          st.warning("Contact supprimé de l'annuaire.")
          st.rerun()
  else:
    st.info("L'annuaire est actuellement vide.")
