import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("👥 Annuaire Interne & Gestion des Comptes")

  with st.form("form_user"):
    col1, col2, col3 = st.columns(3)
    username = col1.text_input("Nom d'utilisateur (Username de connexion)")
    password = col2.text_input("Mot de passe", type="password")
    role = col3.selectbox("Rôle", ["Membre", "Responsable", "Admin"])

    col4, col5, col6 = st.columns(3)
    nom = col4.text_input("Nom")
    prenom = col5.text_input("Prénom")
    num_compte = col6.text_input("Numéro de compte")

    col7, col8 = st.columns(2)
    num = col7.number_input("Numéro de téléphone", value=0, step=1)
    statuts = col8.checkbox("Compte Actif", value=True)

    submit_u = st.form_submit_button("Créer l'utilisateur")

    if submit_u and username and password:
      # Ajout des guillemets autour de "Role" et "num Compte"
      run_query(
          "INSERT INTO users (username, password, \"Role\", nom, prenom, \"num"
          " Compte\", num, statuts) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
          (username, password, role, nom, prenom, num_compte, num, statuts),
      )
      st.success("Utilisateur ajouté avec succès à la base de données !")
      st.rerun()

  # Correction de la sélection avec "Role" entre guillemets
  data_users = run_query(
      'SELECT id, username, "Role", nom, prenom, "num Compte", num, statuts'
      " FROM users",
      fetch=True,
  )
  if data_users:
    df_users = pd.DataFrame(
        data_users,
        columns=[
            "ID",
            "Username",
            "Rôle",
            "Nom",
            "Prénom",
            "N° Compte",
            "Téléphone",
            "Actif",
        ],
    )
    df_users = df_users.astype(
        {"ID": int}
    )  # Nettoyage visuel propre pour les IDs
    st.dataframe(df_users, use_container_width=True)

    with st.form("form_del_user"):
      id_del_u = st.number_input(
          "ID du membre à supprimer", min_value=0, step=1
      )
      if st.form_submit_button("Supprimer ce membre"):
        run_query("DELETE FROM users WHERE id = %s", (id_del_u,))
        st.warning("Membre supprimé.")
        st.rerun()
  else:
    st.info("Aucun utilisateur dans la base.")
