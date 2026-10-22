import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("⚖️ Gestion des Récidives")

  # --- FORMULAIRE D'AJOUT ---
  with st.form("form_recidive"):
    st.subheader("Ajouter une récidive")

    users_data = run_query("SELECT id, username FROM users", fetch=True)
    user_dict = {u[1]: u[0] for u in users_data} if users_data else {}

    if user_dict:
      selected_username = st.selectbox(
          "Membre concerné", options=list(user_dict.keys())
      )
    else:
      selected_username = None
      st.warning("Aucun utilisateur disponible.")

    motif = st.text_area("Motif / Infraction")

    submit = st.form_submit_button("Enregistrer la récidive")

    if submit and motif and selected_username:
      user_id = user_dict[selected_username]
      # Utilisation de la colonne 'membre'
      run_query(
          "INSERT INTO recidive (membre, motif) VALUES (%s, %s)",
          (user_id, motif),
      )
      st.success("Récidive enregistrée avec succès !")
      st.rerun()

  st.markdown("---")

  # --- AFFICHAGE (AVEC LA JOINTURE SUR 'membre') ---
  data_recidive = run_query(
      """
        SELECT r.id, u.username, r.motif 
        FROM recidive r 
        LEFT JOIN users u ON r.membre = u.id 
        ORDER BY r.id DESC
    """,
      fetch=True,
  )

  if data_recidive:
    df_recidive = pd.DataFrame(
        data_recidive, columns=["ID", "Membre", "Motif"]
    )
    df_recidive = df_recidive.astype({"ID": int})
    st.dataframe(df_recidive, use_container_width=True)

    # --- SUPPRIMER UNE RÉCIDIVE ---
    with st.form("form_del_recidive"):
      st.subheader("Supprimer une récidive")
      id_del = st.number_input(
          "ID de la récidive à supprimer", min_value=0, step=1, key="del_rec_id"
      )
      if st.form_submit_button("Supprimer"):
        run_query("DELETE FROM recidive WHERE id = %s", (id_del,))
        st.warning("Récidive supprimée.")
        st.rerun()
  else:
    st.info("Aucune récidive enregistrée pour le moment.")
