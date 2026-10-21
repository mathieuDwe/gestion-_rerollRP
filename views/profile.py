import streamlit as st
from database import run_query


def render():
  st.title("⚙️ Gestion de mon profil")
  st.write(f"Connecté en tant que : **{st.session_state.current_user}**")

  # Récupération des données avec la nouvelle structure (attention aux majuscules/espaces)
  user_info = run_query(
      "SELECT nom, prenom, \"num Compte\", num, password, Role FROM users"
      " WHERE username = %s",
      (st.session_state.current_user,),
      fetch=True,
  )

  if user_info:
    cur_nom = user_info[0][0] if user_info[0][0] else ""
    cur_prenom = user_info[0][1] if user_info[0][1] else ""
    cur_num_compte = user_info[0][2] if user_info[0][2] else ""
    cur_num = int(user_info[0][3]) if user_info[0][3] else 0
    cur_pass = user_info[0][4] if user_info[0][4] else ""
    cur_role = user_info[0][5] if user_info[0][5] else "Membre"

    st.info(f"Rôle actuel : **{cur_role}**")

    with st.form("form_update_profile"):
      st.subheader("Modifier mes informations")
      new_nom = st.text_input("Nom", value=cur_nom)
      new_prenom = st.text_input("Prénom", value=cur_prenom)
      new_num_compte = st.text_input("Numéro de compte", value=cur_num_compte)
      new_num = st.number_input("Numéro de téléphone", value=cur_num, step=1)
      new_password = st.text_input(
          "Nouveau mot de passe", value=cur_pass, type="password"
      )

      submit_update = st.form_submit_button("Enregistrer les modifications")

      if submit_update:
        run_query(
            "UPDATE users SET nom = %s, prenom = %s, \"num Compte\" = %s, num ="
            " %s, password = %s WHERE username = %s",
            (
                new_nom,
                new_prenom,
                new_num_compte,
                new_num,
                new_password,
                st.session_state.current_user,
            ),
        )
        st.success("Profil mis à jour avec succès dans Supabase !")
        st.rerun()