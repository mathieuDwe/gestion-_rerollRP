import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("👥 Annuaire Interne & Gestion des Comptes")

  # --- FORMULAIRE DE CRÉATION ---
  with st.form("form_user"):
    st.subheader("Créer un nouvel utilisateur")
    col1, col2, col3 = st.columns(3)
    username = col1.text_input("Nom d'utilisateur (Username de connexion)")
    password = col2.text_input("Mot de passe", type="password")
    role = col3.text_input(
        "Rôle", value="Membre"
    )  # Saisie libre du rôle avec valeur par défaut

    col4, col5, col6 = st.columns(3)
    nom = col4.text_input("Nom")
    prenom = col5.text_input("Prénom")
    num_compte = col6.text_input("Numéro de compte")

    col7, col8 = st.columns(2)
    num = col7.number_input("Numéro de téléphone", value=0, step=1)

    submit_u = st.form_submit_button("Créer l'utilisateur")

    if submit_u and username and password:
      run_query(
          "INSERT INTO users (username, password, \"Role\", nom, prenom, \"num"
          " compte\", num) VALUES (%s, %s, %s, %s, %s, %s, %s)",
          (username, password, role, nom, prenom, num_compte, num, statuts),
      )
      st.success("Utilisateur ajouté avec succès à la base de données !")
      st.rerun()

  st.markdown("---")

  # --- AFFICHAGE DES MEMBRES ---
  data_users = run_query(
      'SELECT id, username, "Role", nom, prenom, "num compte", num'
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
           
        ],
    )
    df_users = df_users.astype({"ID": int})
    st.dataframe(df_users, use_container_width=True)

    col_mod_role, col_del = st.columns(2)

    # --- MODIFIER LE RÔLE D'UN MEMBRE ---
    with col_mod_role:
      with st.form("form_update_role"):
        st.subheader("Modifier le rôle d'un membre")
        id_role = st.number_input(
            "ID du membre", min_value=0, step=1, key="role_id"
        )
        new_role = st.text_input(
            "Nouveau rôle", key="role_select"
        )  # Saisie libre pour la modification
        submit_role = st.form_submit_button("Mettre à jour le rôle")

        if submit_role and new_role:
          run_query(
              'UPDATE users SET "Role" = %s WHERE id = %s',
              (new_role, id_role),
          )
          st.success(
              f"Rôle du membre ID {id_role} mis à jour avec succès en"
              f" '{new_role}' !"
          )
          st.rerun()

    # --- SUPPRIMER UN MEMBRE ---
    with col_del:
      with st.form("form_del_user"):
        st.subheader("Supprimer un membre")
        id_del_u = st.number_input(
            "ID du membre à supprimer", min_value=0, step=1, key="del_user_id"
        )
        if st.form_submit_button("Supprimer ce membre"):
          run_query("DELETE FROM users WHERE id = %s", (id_del_u,))
          st.warning("Membre supprimé.")
          st.rerun()
  else:
    st.info("Aucun utilisateur dans la base.")
