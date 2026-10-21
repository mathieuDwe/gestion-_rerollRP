from datetime import datetime
import sqlite3
import pandas as pd
import streamlit as st

# ==========================================
# CONFIGURATION DE LA PAGE & DESIGN CSS
# ==========================================
st.set_page_config(
    page_title="Fafnir - Gestion Interne", page_icon="🔴", layout="wide"
)

# Injection de CSS personnalisé (Thème Noir & Rouge strict)
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
# GESTION DE LA BASE DE DONNÉES (SQLite)
# ==========================================
DB_NAME = "fafnir.db"


def init_db():
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()

  # Table Stockage
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS stockage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            quantite INTEGER NOT NULL,
            categorie TEXT,
            date_maj TEXT
        )
    """)

  # Table Membres (avec ajout du champ password)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS membres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            grade TEXT,
            telephone TEXT,
            statut TEXT,
            notes TEXT,
            password TEXT NOT NULL
        )
    """)

  # Création d'un compte Admin par défaut si la table est vide
  cursor.execute("SELECT COUNT(*) FROM membres")
  if cursor.fetchone()[0] == 0:
    cursor.execute(
        "INSERT INTO membres (nom, grade, telephone, statut, notes, password)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (
            "Admin",
            "Boss",
            "555-FAFNIR",
            "Actif",
            "Compte administrateur principal",
            "fafnir2026",
        ),
    )

  # Table Annuaire
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS annuaire (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            type_contact TEXT,
            telephone TEXT,
            notes TEXT
        )
    """)

  # Table Récidive
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS recidive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            membre TEXT,
            motif TEXT,
            sanction TEXT
        )
    """)

  # Table Infos
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS infos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            contenu TEXT,
            date TEXT
        )
    """)

  conn.commit()
  conn.close()


init_db()


def run_query(query, params=(), fetch=False):
  conn = sqlite3.connect(DB_NAME)
  cursor = conn.cursor()
  cursor.execute(query, params)
  if fetch:
    result = cursor.fetchall()
    conn.close()
    return result
  conn.commit()
  conn.close()


# ==========================================
# SYSTÈME DE CONNEXION PAR LA BASE DE DONNÉES
# ==========================================
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.current_user = ""
  st.session_state.current_grade = ""

if not st.session_state.logged_in:
  st.markdown(
      "<h1 style='text-align: center;'>🛡️ FAFNIR - CONNEXION</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #888;'>Identifiez-vous avec votre"
      " compte membre.</p>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; font-size: 13px; color: #ff0033;'>Par"
      " défaut : Nom: <b>Admin</b> | Mot de passe: <b>fafnir2026</b></p>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 1, 1])
  with col2:
    username_input = st.text_input("Nom & Prénom RP (Identifiant)")
    password_input = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter", use_container_width=True):
      if username_input and password_input:
        # Vérification dans la base de données
        user_data = run_query(
            "SELECT nom, grade, password FROM membres WHERE nom = ?",
            (username_input,),
            fetch=True,
        )
        if user_data and user_data[0][2] == password_input:
          st.session_state.logged_in = True
          st.session_state.current_user = user_data[0][0]
          st.session_state.current_grade = user_data[0][1]
          st.rerun()
        else:
          st.error("Nom ou mot de passe incorrect.")
      else:
        st.warning("Veuillez remplir tous les champs.")
  st.stop()

# ==========================================
# BARRE LATÉRALE DE NAVIGATION (SIDEBAR)
# ==========================================
st.sidebar.markdown(
    "<h2 style='text-align: center;'>🔴 FAFNIR</h2>", unsafe_allow_html=True
)
st.sidebar.markdown(
    f"<p style='text-align: center; font-size: 13px; color: #ff0033;'>Connecté"
    f" : <b>{st.session_state.current_user}</b><br>({st.session_state.current_grade})</p>",
    unsafe_allow_html=True,
)
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "📦 Stockage", "👥 Membres", "📖 Annuaire", "⚖️ Récidive", "ℹ️ Info"],
)

st.sidebar.markdown("---")
if st.sidebar.button("Déconnexion", use_container_width=True):
  st.session_state.logged_in = False
  st.session_state.current_user = ""
  st.session_state.current_grade = ""
  st.rerun()

# ==========================================
# ONGLET 0 : DASHBOARD
# ==========================================
if menu == "🏠 Dashboard":
  st.title("📊 Tableau de Bord - Fafnir")
  st.write(
      f"Bienvenue, {st.session_state.current_user}. Vue d'ensemble de"
      " l'activité du groupe :"
  )

  try:
    nb_stock = len(run_query("SELECT * FROM stockage", fetch=True))
    nb_membres = len(run_query("SELECT * FROM membres", fetch=True))
    nb_contacts = len(run_query("SELECT * FROM annuaire", fetch=True))
    nb_recidives = len(run_query("SELECT * FROM recidive", fetch=True))
  except:
    nb_stock, nb_membres, nb_contacts, nb_recidives = 0, 0, 0, 0

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("📦 Items en Stock", nb_stock)
  col2.metric("👥 Membres Actifs", nb_membres)
  col3.metric("📖 Contacts Annuaire", nb_contacts)
  col4.metric("⚖️ Cas Récidive", nb_recidives)

  st.markdown("---")
  st.subheader("📢 Dernières Infos du Groupe")
  dernieres_infos = run_query(
      "SELECT titre, contenu, date FROM infos ORDER BY id DESC LIMIT 3",
      fetch=True,
  )
  if dernieres_infos:
    for titre, contenu, date in dernieres_infos:
      with st.expander(f"📌 {titre} ({date})"):
        st.write(contenu)
  else:
    st.info("Aucune information récente.")

# ==========================================
# ONGLET 1 : STOCKAGE
# ==========================================
elif menu == "📦 Stockage":
  st.title("📦 Gestion du Stockage")
  st.write("Suivi des armes, munitions, drogues, argent et matériel.")

  with st.form("form_stock"):
    col1, col2, col3 = st.columns(3)
    item = col1.text_input("Nom de l'item (ex: Heavy Pistol, Materiaux)")
    quantite = col2.number_input("Quantité", min_value=0, step=1)
    categorie = col3.selectbox(
        "Catégorie", ["Armement", "Drogue", "Argent sale", "Matériel", "Divers"]
    )
    submit = st.form_submit_button("Ajouter / Modifier l'item")

    if submit and item:
      date_maj = datetime.now().strftime("%Y-%m-%d %H:%M")
      run_query(
          "INSERT INTO stockage (item, quantite, categorie, date_maj) VALUES"
          " (?, ?, ?, ?)",
          (item, quantite, categorie, date_maj),
      )
      st.success(f"Item '{item}' enregistré avec succès !")
      st.rerun()

  st.markdown("### Inventaire actuel")
  data_stock = run_query(
      "SELECT id, item, quantite, categorie, date_maj FROM stockage", fetch=True
  )
  if data_stock:
    df_stock = pd.DataFrame(
        data_stock,
        columns=["ID", "Item", "Quantité", "Catégorie", "Dernière MàJ"],
    )
    st.dataframe(df_stock, use_container_width=True)

    item_id_del = st.number_input(
        "ID de l'item à supprimer", min_value=0, step=1, key="del_stock"
    )
    if st.button("Supprimer cet item"):
      run_query("DELETE FROM stockage WHERE id = ?", (item_id_del,))
      st.warning("Item supprimé.")
      st.rerun()
  else:
    st.info("Le stockage est vide pour le moment.")

# ==========================================
# ONGLET 2 : MEMBRES
# ==========================================
elif menu == "👥 Membres":
  st.title("👥 Annuaire Interne - Membres")
  st.write("Gestion des effectifs, grades, numéros RP et accès de connexion.")

  with st.form("form_membre"):
    col1, col2, col3 = st.columns(3)
    nom = col1.text_input("Nom & Prénom RP")
    grade = col2.text_input("Grade (ex: Boss, Bras droit, Soldat)")
    password = col3.text_input(
        "Mot de passe de connexion", type="password"
    )  # Nouveau champ mdp

    col4, col5 = st.columns(2)
    telephone = col4.text_input("Numéro de téléphone")
    statut = col5.selectbox("Statut", ["Actif", "Inactif", "En pause"])

    notes = st.text_area("Notes particulières")
    submit_m = st.form_submit_button("Ajouter le membre")

    if submit_m and nom and password:
      try:
        run_query(
            "INSERT INTO membres (nom, grade, telephone, statut, notes,"
            " password) VALUES (?, ?, ?, ?, ?, ?)",
            (nom, grade, telephone, statut, notes, password),
        )
        st.success(f"Membre {nom} ajouté avec succès !")
        st.rerun()
      except sqlite3.IntegrityError:
        st.error(
            "Un membre avec ce nom existe déjà dans la base de données."
        )
    elif submit_m:
      st.warning("Le nom et le mot de passe sont obligatoires.")

  st.markdown("### Liste des effectifs")
  # On masque le mot de passe dans l'affichage du tableau pour des raisons de sécurité
  data_membres = run_query(
      "SELECT id, nom, grade, telephone, statut, notes FROM membres",
      fetch=True,
  )
  if data_membres:
    df_membres = pd.DataFrame(
        data_membres,
        columns=["ID", "Nom", "Grade", "Téléphone", "Statut", "Notes"],
    )
    st.dataframe(df_membres, use_container_width=True)

    membre_id_del = st.number_input(
        "ID du membre à supprimer", min_value=0, step=1, key="del_membre"
    )
    if st.button("Supprimer ce membre"):
      run_query("DELETE FROM membres WHERE id = ?", (membre_id_del,))
      st.warning("Membre supprimé.")
      st.rerun()
  else:
    st.info("Aucun membre enregistré.")

# ==========================================
# ONGLET 3 : ANNUAIRE
# ==========================================
elif menu == "📖 Annuaire":
  st.title("📖 Contacts Externes & Fournisseurs")
  st.write("Carnet d'adresses utiles en ville (fournisseurs, alliés, etc.).")

  with st.form("form_annuaire"):
    col1, col2 = st.columns(2)
    nom_c = col1.text_input("Nom / Alias du contact")
    type_c = col2.text_input(
        "Type (ex: Fournisseur armes, Informateur, Garage)"
    )
    col3, col4 = st.columns(2)
    tel_c = col3.text_input("Téléphone du contact")
    notes_c = col4.text_input("Notes / Localisation")
    submit_a = st.form_submit_button("Ajouter à l'annuaire")

    if submit_a and nom_c:
      run_query(
          "INSERT INTO annuaire (nom, type_contact, telephone, notes) VALUES"
          " (?, ?, ?, ?)",
          (nom_c, type_c, tel_c, notes_c),
      )
      st.success("Contact ajouté !")
      st.rerun()

  data_annuaire = run_query(
      "SELECT id, nom, type_contact, telephone, notes FROM annuaire",
      fetch=True,
  )
  if data_annuaire:
    df_annuaire = pd.DataFrame(
        data_annuaire,
        columns=["ID", "Nom / Alias", "Type", "Téléphone", "Notes"],
    )
    st.dataframe(df_annuaire, use_container_width=True)

    id_del_a = st.number_input(
        "ID du contact à supprimer", min_value=0, step=1, key="del_annuaire"
    )
    if st.button("Supprimer ce contact"):
      run_query("DELETE FROM annuaire WHERE id = ?", (id_del_a,))
      st.warning("Contact supprimé.")
      st.rerun()
  else:
    st.info("Annuaire vide.")

# ==========================================
# ONGLET 4 : RÉCIDIVE
# ==========================================
elif menu == "⚖️ Récidive":
  st.title("⚖️ Suivi de Récidive & Incidents")
  st.write(
      "Suivi des antécédents, confrontations, amendes ou peines de prison."
  )

  with st.form("form_recidive"):
    col1, col2 = st.columns(2)
    date_r = col1.text_input(
        "Date (JJ/MM/AAAA)", value=datetime.now().strftime("%d/%m/%Y")
    )
    membre_r = col2.text_input("Membre concerné")
    motif_r = st.text_input("Motif / Infraction (ex: Braquage, Course-poursuite)")
    sanction_r = st.text_input(
        "Sanction / Amende / Peine (ex: 50 mois, 15000$)"
    )
    submit_r = st.form_submit_button("Enregistrer l'incident")

    if submit_r and motif_r:
      run_query(
          "INSERT INTO recidive (date, membre, motif, sanction) VALUES (?, ?,"
          " ?, ?)",
          (date_r, membre_r, motif_r, sanction_r),
      )
      st.success("Récidive enregistrée.")
      st.rerun()

  data_rec = run_query(
      "SELECT id, date, membre, motif, sanction FROM recidive", fetch=True
  )
  if data_rec:
    df_rec = pd.DataFrame(
        data_rec, columns=["ID", "Date", "Membre", "Motif", "Sanction"]
    )
    st.dataframe(df_rec, use_container_width=True)

    id_del_r = st.number_input(
        "ID de l'incident à supprimer", min_value=0, step=1, key="del_rec"
    )
    if st.button("Supprimer cet incident"):
      run_query("DELETE FROM recidive WHERE id = ?", (id_del_r,))
      st.warning("Incident supprimé.")
      st.rerun()
  else:
    st.info("Aucun antécédent enregistré.")

# ==========================================
# ONGLET 5 : INFO
# ==========================================
elif menu == "ℹ️ Info":
  st.title("ℹ️ Informations & Consignes Internes")
  st.write("Tableau d'affichage officiel du groupe Fafnir.")

  with st.form("form_info"):
    titre_i = st.text_input("Titre de l'annonce")
    contenu_i = st.text_area("Contenu de l'annonce / Consignes")
    submit_i = st.form_submit_button("Publier l'information")

    if submit_i and titre_i:
      date_i = datetime.now().strftime("%d/%m/%Y")
      run_query(
          "INSERT INTO infos (titre, contenu, date) VALUES (?, ?, ?)",
          (titre_i, contenu_i, date_i),
      )
      st.success("Annonce publiée !")
      st.rerun()

  st.markdown("### Historique des annonces")
  data_infos = run_query(
      "SELECT id, titre, contenu, date FROM infos ORDER BY id DESC", fetch=True
  )
  if data_infos:
    for id_info, titre, contenu, date in data_infos:
      with st.expander(f"📌 {titre} (Posté le {date}) [ID: {id_info}]"):
        st.write(contenu)

    id_del_i = st.number_input(
        "ID de l'annonce à supprimer", min_value=0, step=1, key="del_info"
    )
    if st.button("Supprimer cette annonce"):
      run_query("DELETE FROM infos WHERE id = ?", (id_del_i,))
      st.warning("Annonce supprimée.")
      st.rerun()
  else:
    st.info("Aucune information publiée.")