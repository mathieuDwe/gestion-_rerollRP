import streamlit as st
from database import run_query

# Configuration de la page
st.set_page_config(
    page_title="Fafnir - Test", page_icon="🔴", layout="wide"
)

# Initialisation de la session
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.current_user = None

# --- ÉTAPE 1 : CONNEXION ---
if not st.session_state.logged_in:
  st.title("🛡️ FAFNIR - CONNEXION (TEST)")
  
  with st.form("login_form"):
    username_input = st.text_input("Nom d'utilisateur (username)")
    password_input = st.text_input("Mot de passe", type="password")
    submit = st.form_submit_button("Se connecter")

    if submit:
      if username_input and password_input:
        query = 'SELECT id, username, password, "Role" FROM users WHERE LOWER(TRIM(username)) = LOWER(TRIM(%s))'
        user_data = run_query(query, (username_input,), fetch=True)

        if user_data:
          user = user_data[0]
          # Récupération sécurisée par index
          db_id, db_user, db_pass, db_role = user[0], user[1], user[2], user[3]

          if str(db_pass) == str(password_input):
            st.session_state.logged_in = True
            st.session_state.current_user = db_user
            st.success("Connexion réussie ! Redémarrage...")
            st.rerun()
          else:
            st.error("Mot de passe incorrect.")
        else:
          st.error("Utilisateur introuvable.")
      else:
        st.warning("Remplis tous les champs.")
  st.stop()

# --- ÉTAPE 2 : UNE FOIS CONNECTÉ ---
st.sidebar.title("Menu de Test")
choix = st.sidebar.radio("Aller à", ["Accueil", "Vérification Fichiers"])

if choix == "Accueil":
  st.title(f"Bienvenue {st.session_state.current_user} !")
  st.success("🎉 Si tu vois ce message, la connexion et le rendu de base fonctionnent parfaitement !")
  
  if st.button("Se déconnecter"):
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.rerun()

elif choix == "Vérification Fichiers":
  st.title("Test des modules views/")
  try:
    from views import dashboard
    st.write("Le module `dashboard` a été importé avec succès.")
    dashboard.render()
  except Exception as e:
    st.error(f"Erreur lors du chargement du dashboard : {e}")
