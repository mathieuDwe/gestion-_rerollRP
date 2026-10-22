import streamlit as st
from database import run_query

# Import des vues (onglets)
from views import (
    annuaire,
    dashboard,
    info,
    membres,
    profile,
    recidive,
    stockage,
)

# ==========================================
# CONFIGURATION DE LA PAGE & DESIGN CSS
# ==========================================
st.set_page_config(
    page_title="Fafnir - Gestion Interne", page_icon="🔴", layout="wide"
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0b0b0b; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #121212; border-right: 1px solid #ff0033; }
    h1, h2, h3 { color: #ff0033 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button { background-color: #ff0033; color: white; border-radius: 6px; border: none; font-weight: bold; transition: 0.3s; }
    .stButton>button:hover { background-color: #cc0029; color: white; }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #1a1a1a; color: white; border: 1px solid #333333; border-radius: 5px;
    }
    div.stMarkdown { color: #e0e0e0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# SYSTÈME D'AUTHENTIFICATION
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
      username_input = st.text_input("Nom d'utilisateur (username)")
      password_input = st.text_input("Mot de passe", type="password")
      submit_login = st.form_submit_button(
          "Se connecter", use_container_width=True
      )

      if submit_login:
        if username_input and password_input:
          # On sélectionne explicitement et dans l'ordre exact ces 4 colonnes
          query = """
                        SELECT id, username, password, "Role" 
                        FROM users 
                        WHERE LOWER(TRIM(username)) = LOWER(TRIM(%s))
                    """
          user_data = run_query(query, (username_input,), fetch=True)

          if user_data:
            # Récupération sécurisée par index (0: id, 1: username, 2: password, 3: Role)
            user = user_data[0]
            user_id = user[0]
            db_username = user[1]
            db_password = user[2]
            db_role = user[3]

            if str(db_password) == str(password_input):
              st.session_state.logged_in = True
              st.session_state.current_user = db_username
              st.session_state.user_id = user_id
              st.session_state.user_role = db_role
              st.success(f"Bienvenue {db_username} !")
              st.rerun()
            else:
              st.error("Mot de passe incorrect.")
          else:
            st.error("Nom d'utilisateur introuvable dans la base de données.")
        else:
          st.warning("Veuillez remplir tous les champs.")
st.stop()

# ==========================================
# BARRE LATÉRALE DE NAVIGATION
# ==========================================
st.sidebar.markdown(
    "<h2 style='text-align: center;'>🔴 FAFNIR</h2>", unsafe_allow_html=True
)
st.sidebar.markdown(
    f"<p style='text-align: center; font-size: 13px; color:"
    f" #ff0033;'>Connecté : <b>{st.session_state.current_user}</b></p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "📦 Stockage",
        "👥 Membres",
        "📖 Annuaire",
        "⚖️ Récidive",
        "ℹ️ Info",
        "⚙️ Mon Compte",
    ],
)

st.sidebar.markdown("---")
if st.sidebar.button("Déconnexion", use_container_width=True):
  st.session_state.logged_in = False
  st.session_state.current_user = None
  st.session_state.user_id = None
  st.rerun()

# ==========================================
# ROUTAGE DES VUES
# ==========================================
# ==========================================
# ROUTAGE DES VUES (AVEC SÉCURITÉ)
# ==========================================
try:
  if menu == "🏠 Dashboard":
    dashboard.render()
  elif menu == "📦 Stockage":
    stockage.render()
  elif menu == "👥 Membres":
    membres.render()
  elif menu == "📖 Annuaire":
    annuaire.render()
  elif menu == "⚖️ Récidive":
    recidive.render()
  elif menu == "ℹ️ Info":
    info.render()
  elif menu == "⚙️ Mon Compte":
    profile.render()
except Exception as e:
  st.error(
      f"Une erreur est survenue lors du chargement de l'onglet '{menu}' : {e}"
  )
