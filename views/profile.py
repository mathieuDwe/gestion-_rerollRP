import streamlit as st
from database import run_query


def render():
  st.title("⚙️ Gestion de mon profil")
  st.write(f"Connecté en tant que : **{st.session_state.current_user}**")

  # Récupération des informations incluant le username
  user_info = run_query(
      "SELECT username, nom, prenom, \"num compte\", num, password, \"Role\""
      " FROM users WHERE username = %s",
      (st.session_state.current_user,),
      fetch=True,
  )

  if user_info:
    cur_username = user_info[0][0] if user_info[0][0] else ""
    cur_nom = user_info[0][1] if user_info[0][1] else ""
    cur_prenom = user_info[0][2] if user_info[0][2] else ""
    cur_num_compte = user_info[0][3] if user_info[0][3] else ""
    cur_num = int(user_info[0][4]) if user_info[0][4] else 0
    cur_pass = user_info[0][5] if user_info[0][5] else ""
    cur_role = user_info[0][6] if user_info[0][6] else "Membre"

    st.info(f"Rôle actuel : **{cur_role}**")

    with st.form("form_update_profile"):
      st.subheader("Modifier mes informations")

      # Champ pour modifier le username
      new_username = st.text_input(
          "Nom d'utilisateur (Username)", value=cur_username
      )
      new_nom = st.text_input("Nom", value=cur_nom)
      new_prenom = st.text_input("Prénom", value=cur_prenom)
      new_num_compte = st.text_input("Numéro de compte", value=cur_num_compte)
      new_num = st.number_input("Numéro de téléphone", value=cur_num, step=1)
      new_password = st.text_input(
          "Nouveau mot de passe", value=cur_pass, type="password"
      )

      submit_update = st.form_submit_button("Enregistrer les modifications")

      if submit_update:
        if new_username.strip() == "":
          st.error("Le nom d'utilisateur ne peut pas être vide.")
        else:
          # Mise à jour dans la base de données Supabase
          run_query(
              "UPDATE users SET username = %s, nom = %s, prenom = %s, \"num"
              " compte\" = %s, num = %s, password = %s WHERE username = %s",
              (
                  new_username,
                  new_nom,
                  new_prenom,
                  new_num_compte,
                  new_num,
                  new_password,
                  st.session_state.current_user,
              ),
          )
          # Mise à jour de la session active avec le nouveau username
          st.session_state.current_user = new_username
          st.success("Profil mis à jour avec succès dans Supabase !")
          st.rerun()
