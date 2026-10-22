import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("ℹ️ Informations & Annonces")

  # --- FORMULAIRE D'AJOUT ---
  with st.form("form_add_info"):
    st.subheader("Publier une nouvelle information")
    titre = st.text_input("Titre de l'information")
    contenu = st.text_area("Contenu de l'annonce")
    submit_add = st.form_submit_button("Publier")

    if submit_add and titre and contenu:
      # Récupération automatique du membre connecté dans la session
      auteur = st.session_state.get("current_user", "Inconnu")

      run_query(
          "INSERT INTO info (titre, contenu, auteur) VALUES (%s, %s, %s)",
          (titre, contenu, auteur),
      )
      st.success("Information publiée avec succès !")
      st.rerun()

  st.markdown("---")

  # --- AFFICHAGE DES INFORMATIONS ---
  data_info = run_query(
      "SELECT id, titre, contenu, auteur FROM info ORDER BY id DESC",
      fetch=True,
  )
  if data_info:
    df_info = pd.DataFrame(
        data_info, columns=["ID", "Titre", "Contenu", "Auteur"]
    )
    df_info = df_info.astype({"ID": int})
    st.dataframe(df_info, use_container_width=True)

    col_mod, col_del = st.columns(2)

    # --- MODIFIER UNE INFO ---
    with col_mod:
      with st.form("form_update_info"):
        st.subheader("Modifier une information")
        id_mod = st.number_input(
            "ID de l'information", min_value=0, step=1, key="mod_info_id"
        )
        new_titre = st.text_input("Nouveau titre", key="mod_info_titre")
        new_contenu = st.text_area(
            "Nouveau contenu", key="mod_info_contenu"
        )
        submit_mod = st.form_submit_button("Mettre à jour")

        if submit_mod and id_mod > 0:
          run_query(
              "UPDATE info SET titre = %s, contenu = %s WHERE id = %s",
              (new_titre, new_contenu, id_mod),
          )
          st.success(f"Information ID {id_mod} mise à jour avec succès !")
          st.rerun()

    # --- SUPPRIMER UNE INFO ---
    with col_del:
      with st.form("form_delete_info"):
        st.subheader("Supprimer une information")
        id_del = st.number_input(
            "ID de l'information à supprimer",
            min_value=0,
            step=1,
            key="del_info_id",
        )
        submit_del = st.form_submit_button("Supprimer")

        if submit_del and id_del > 0:
          run_query("DELETE FROM info WHERE id = %s", (id_del,))
          st.warning("Information supprimée.")
          st.rerun()
  else:
    st.info("Aucune information publiée pour le moment.")
