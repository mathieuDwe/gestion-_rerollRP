# ==========================================
# SYSTÈME DE CONNEXION (Recherche dans 'users')
# ==========================================
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.current_user = ""

if not st.session_state.logged_in:
  st.markdown(
      "<h1 style='text-align: center;'>🛡️ FAFNIR - CONNEXION</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #888;'>Connexion sécurisée via la"
      " base de données des utilisateurs.</p>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 1, 1])
  with col2:
    username_input = st.text_input("Nom d'utilisateur (nom)")
    password_input = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter", use_container_width=True):
      if username_input and password_input:
        # Sélection sécurisée uniquement des colonnes nécessaires
        user_data = run_query(
            "SELECT nom, password FROM users WHERE nom = %s",
            (username_input,),
            fetch=True,
        )

        if user_data:
          db_nom, db_password = user_data[0]

          # Vérification du mot de passe
          if str(db_password) == str(password_input):
            st.session_state.logged_in = True
            st.session_state.current_user = db_nom
            st.success(f"Bienvenue {db_nom} !")
            st.rerun()
          else:
            st.error("Mot de passe incorrect.")
        else:
          st.error("Nom d'utilisateur introuvable dans la base de données.")
      else:
        st.warning("Veuillez remplir tous les champs.")
  st.stop()
