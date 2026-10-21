from datetime import datetime
import pandas as pd
import psycopg2
import streamlit as st

# ==========================================
# CONFIGURATION DE LA PAGE & DESIGN CSS
# ==========================================
st.set_page_config(
    page_title="Fafnir - Gestion Interne", page_icon="🔴", layout="wide"
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0b0b;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #121212;
        border-right: 1px solid #ff0033;
    }
    h1, h2, h3 {
        color: #ff0033 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stButton>button {
        background-color: #ff0033;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #cc0029;
        color: white;
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div {
        background-color: #1a1a1a;
        color: white;
        border: 1px solid #333333;
        border-radius: 5px;
    }
    div.stMarkdown {
        color: #e0e0e0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# CONNEXION SUPABASE
# ==========================================


def get_db_connection():
  db_url = st.secrets["postgres"]["url"]
  return psycopg2.connect(db_url)


def run_query(query, params=(), fetch=False):
  conn = get_db_connection()
  cursor = conn.cursor()
  cursor.execute(query, params)
  if fetch:
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result
  conn.commit()
  cursor.close()
  conn.close()


# ==========================================
# SYSTÈME DE CONNEXION 
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
    username_input = st.text_input("Nom d'utilisateur (username)")
    password_input = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter", use_container_width=True):
      if username_input and password_input:
        # Sélection sécurisée uniquement des colonnes nécessaires
        user_data = run_query(
            "SELECT username, password FROM users WHERE nom = %s",
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
  st.session_state.current_user = ""
  st.rerun()

# ==========================================
# ONGLET 0 : DASHBOARD
# ==========================================
if menu == "🏠 Dashboard":
  st.title("📊 Tableau de Bord - Fafnir")
  st.write(f"Bienvenue sur l'espace d'administration, {st.session_state.current_user}.")

  try:
    nb_stock = len(run_query("SELECT * FROM object", fetch=True))
    nb_membres = len(run_query("SELECT * FROM users", fetch=True))
    nb_contacts = len(run_query("SELECT * FROM annuaire", fetch=True))
    nb_amendes = len(run_query("SELECT * FROM amende", fetch=True))
  except:
    nb_stock, nb_membres, nb_contacts, nb_amendes = 0, 0, 0, 0

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("📦 Objets en Stock", nb_stock)
  col2.metric("👥 Membres Inscrits", nb_membres)
  col3.metric("📖 Contacts Annuaire", nb_contacts)
  col4.metric("⚖️ Amendes / Récidives", nb_amendes)

# ==========================================
# ONGLET 1 : STOCKAGE
# ==========================================
elif menu == "📦 Stockage":
  st.title("📦 Gestion du Stockage")

  with st.form("form_object"):
    col1, col2, col3, col4 = st.columns(4)
    obj_nom = col1.text_input("Nom de l'objet")
    quantite = col2.number_input("Quantité", min_value=0, step=1)
    poid = col3.number_input("Poids", min_value=0, step=1)
    revente = col4.number_input("Prix Revente", min_value=0.0, step=1.0)
    submit = st.form_submit_button("Ajouter l'objet")

    if submit and obj_nom:
      run_query(
          "INSERT INTO object (object, quantite, poid, revente) VALUES (%s,"
          " %s, %s, %s)",
          (obj_nom, quantite, poid, revente),
      )
      st.success("Objet ajouté avec succès !")
      st.rerun()

  data_stock = run_query(
      "SELECT id, object, quantite, poid, revente FROM object", fetch=True
  )
  if data_stock:
    df_stock = pd.DataFrame(
        data_stock, columns=["ID", "Objet", "Quantité", "Poids", "Revente"]
    )
    st.dataframe(df_stock, use_container_width=True)

    id_del = st.number_input(
        "ID de l'objet à supprimer", min_value=0, step=1, key="del_obj"
    )
    if st.button("Supprimer cet objet"):
      run_query("DELETE FROM object WHERE id = %s", (id_del,))
      st.warning("Objet supprimé.")
      st.rerun()
  else:
    st.info("Stock vide.")

# ==========================================
# ONGLET 2 : MEMBRES
# ==========================================
elif menu == "👥 Membres":
  st.title("👥 Annuaire Interne & Gestion des Comptes")

  with st.form("form_user"):
    col1, col2, col3 = st.columns(3)
    nom = col1.text_input("Nom (Identifiant de connexion)")
    prenom = col2.text_input("Prénom")
    num_compte = col3.text_input("Numéro de compte")

    col4, col5, col6 = st.columns(3)
    num = col4.number_input("Numéro de téléphone", value=0, step=1)
    password = col5.text_input("Mot de passe de connexion", type="password")
    statuts = col6.checkbox("Compte Actif", value=True)

    submit_u = st.form_submit_button("Créer l'utilisateur")

    if submit_u and nom and password:
      run_query(
          "INSERT INTO users (nom, prenom, \"num compte\", num, password,"
          " statuts) VALUES (%s, %s, %s, %s, %s, %s)",
          (nom, prenom, num_compte, num, password, statuts),
      )
      st.success("Utilisateur ajouté avec succès à la base de données !")
      st.rerun()

  data_users = run_query(
      "SELECT id, nom, prenom, \"num compte\", num, statuts FROM users",
      fetch=True,
  )
  if data_users:
    df_users = pd.DataFrame(
        data_users,
        columns=["ID", "Nom", "Prénom", "N° Compte", "Téléphone", "Actif"],
    )
    st.dataframe(df_users, use_container_width=True)

    id_del_u = st.number_input(
        "ID du membre à supprimer", min_value=0, step=1, key="del_user"
    )
    if st.button("Supprimer ce membre"):
      run_query("DELETE FROM users WHERE id = %s", (id_del_u,))
      st.warning("Membre supprimé.")
      st.rerun()
  else:
    st.info("Aucun utilisateur dans la base.")

# ==========================================
# ONGLET 3 : ANNUAIRE
# ==========================================
elif menu == "📖 Annuaire":
  st.title("📖 Contacts Externes")

  with st.form("form_annuaire"):
    col1, col2, col3 = st.columns(3)
    nom_a = col1.text_input("Nom")
    prenom_a = col2.text_input("Prénom")
    num_a = col3.number_input("Numéro", value=0, step=1)
    submit_a = st.form_submit_button("Ajouter le contact")

    if submit_a and nom_a:
      run_query(
          "INSERT INTO annuaire (nom, prenom, num) VALUES (%s, %s, %s)",
          (nom_a, prenom_a, num_a),
      )
      st.success("Contact ajouté !")
      st.rerun()

  data_annuaire = run_query(
      "SELECT id, nom, prenom, num FROM annuaire", fetch=True
  )
  if data_annuaire:
    df_annuaire = pd.DataFrame(
        data_annuaire, columns=["ID", "Nom", "Prénom", "Numéro"]
    )
    st.dataframe(df_annuaire, use_container_width=True)

    id_del_an = st.number_input(
        "ID du contact à supprimer", min_value=0, step=1, key="del_an"
    )
    if st.button("Supprimer ce contact"):
      run_query("DELETE FROM annuaire WHERE id = %s", (id_del_an,))
      st.warning("Contact supprimé.")
      st.rerun()
  else:
    st.info("Annuaire vide.")

# ==========================================
# ONGLET 4 : RÉCIDIVE
# ==========================================
elif menu == "⚖️ Récidive":
  st.title("⚖️ Suivi des Amendes & Récidives")

  with st.form("form_amende"):
    col1, col2 = st.columns(2)
    membre_r = col1.text_input("Membre concerné")
    recidive_time = col2.text_input(
        "Date (AAAA-MM-JJ)", value=datetime.now().strftime("%Y-%m-%d")
    )
    motif_r = st.text_input("Motif")
    submit_r = st.form_submit_button("Enregistrer")

    if submit_r and motif_r:
      run_query(
          "INSERT INTO amende (recidive_time, membre, motif) VALUES (%s, %s,"
          " %s)",
          (recidive_time, membre_r, motif_r),
      )
      st.success("Incident enregistré.")
      st.rerun()

  data_amende = run_query(
      "SELECT id, created_at, recidive_time, membre, motif FROM amende",
      fetch=True,
  )
  if data_amende:
    df_amende = pd.DataFrame(
        data_amende,
        columns=[
            "ID",
            "Créé le",
            "Date Récidive",
            "Membre",
            "Motif",
        ],
    )
    st.dataframe(df_amende, use_container_width=True)

    id_del_am = st.number_input(
        "ID à supprimer", min_value=0, step=1, key="del_am"
    )
    if st.button("Supprimer cette entrée"):
      run_query("DELETE FROM amende WHERE id = %s", (id_del_am,))
      st.warning("Supprimé.")
      st.rerun()
  else:
    st.info("Aucun incident enregistré.")

# ==========================================
# ONGLET 5 : INFO
# ==========================================
elif menu == "ℹ️ Info":
  st.title("ℹ️ Informations Internes")
  st.info("Consignes générales pour le groupe Fafnir.")

# ==========================================
# ONGLET 6 : MON COMPTE (Espace utilisateur)
# ==========================================
elif menu == "⚙️ Mon Compte":
  st.title("⚙️ Gestion de mon profil")
  st.write(
      f"Connecté en tant que : **{st.session_state.current_user}** (Nom non"
      " modifiable)"
  )

  # Récupérer les données actuelles de l'utilisateur connecté
  user_info = run_query(
      "SELECT prenom, \"num compte\", num, password FROM users WHERE nom = %s",
      (st.session_state.current_user,),
      fetch=True,
  )

  if user_info:
    cur_prenom = user_info[0][0] if user_info[0][0] else ""
    cur_num_compte = user_info[0][1] if user_info[0][1] else ""
    cur_num = int(user_info[0][2]) if user_info[0][2] else 0
    cur_pass = user_info[0][3] if user_info[0][3] else ""

    with st.form("form_update_profile"):
      st.subheader("Modifier mes métadonnées")
      new_prenom = st.text_input("Prénom", value=cur_prenom)
      new_num_compte = st.text_input("Numéro de compte", value=cur_num_compte)
      new_num = st.number_input("Numéro de téléphone", value=cur_num, step=1)
      new_password = st.text_input(
          "Nouveau mot de passe", value=cur_pass, type="password"
      )

      submit_update = st.form_submit_button("Enregistrer les modifications")

      if submit_update:
        run_query(
            "UPDATE users SET prenom = %s, \"num compte\" = %s, num = %s,"
            " password = %s WHERE nom = %s",
            (
                new_prenom,
                new_num_compte,
                new_num,
                new_password,
                st.session_state.current_user,
            ),
        )
        st.success("Profil mis à jour avec succès dans Supabase !")
        st.rerun()
