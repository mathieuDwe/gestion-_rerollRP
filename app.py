# ==========================================
# SYSTÈME DE CONNEXION AVEC DEBUG
# ==========================================
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.current_user = None
  st.session_state.user_id = None

if not st.session_state.logged_in:
  st.markdown(
      "<h1 style='text-align: center;'>🛡️ FAFNIR - CONNEXION</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #888;'>Portail sécurisé de"
      " gestion interne.</p>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 1, 1])
  with col2:
    with st.form("login_form"):
      username_input = st.text_input("Nom d'utilisateur")
      password_input = st.text_input("Mot de passe", type="password")
      submit_login = st.form_submit_button(
          "Se connecter", use_container_width=True
      )

      if submit_login:
        if username_input and password_input:
          query = """
                        SELECT id, username, password, statuts 
                        FROM users 
                        WHERE LOWER(TRIM(nom)) = LOWER(TRIM(%s))
                    """
          user_data = run_query(query, (username_input,), fetch=True)

          if user_data:
            user_id, db_nom, db_password, db_statut = user_data[0]

            if str(db_password) == str(password_input):
              if db_statut is False:
                st.error(
                    "Ce compte est désactivé. Contactez un administrateur."
                )
              else:
                st.session_state.logged_in = True
                st.session_state.current_user = db_nom
                st.session_state.user_id = user_id
                st.success(f"Bienvenue {db_nom} !")
                st.rerun()
            else:
              st.error("Mot de passe incorrect.")
          else:
            st.error("Nom d'utilisateur introuvable dans la base de données.")
        else:
          st.warning("Veuillez remplir tous les champs.")

    # --- PANNEAU DE DEBUG TEMPORAIRE ---
    with st.expander("🛠️ Voir ce que contient la table 'users'"):
      try:
        debug_data = run_query(
            "SELECT id, nom, password FROM users", fetch=True
        )
        if debug_data:
          st.write("Utilisateurs enregistrés dans Supabase :")
          for u in debug_data:
            st.code(f"ID: {u[0]} | Nom: '{u[1]}' | MDP: '{u[2]}'")
        else:
          st.warning(
              "La table 'users' est actuellement **totalement vide** !"
          )
      except Exception as e:
        st.error(f"Erreur de lecture de la table : {e}")
  st.stop()
