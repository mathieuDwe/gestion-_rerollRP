import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("📦 Gestion du Stockage")

  # --- RÉCUPÉRATION DYNAMIQUE DES NOMS DE COLONNES ---
  cols_data = run_query(
      "SELECT column_name FROM information_schema.columns WHERE table_name ="
      " 'object' ORDER BY ordinal_position",
      fetch=True,
  )
  column_names = [c[0] for c in cols_data] if cols_data else []

  # --- CHARGEMENT DES DONNÉES ---
  data_obj = run_query("SELECT * FROM object ORDER BY id ASC", fetch=True)

  if data_obj and column_names:
    # Création du DataFrame avec les vrais en-têtes de la base de données
    df = pd.DataFrame(data_obj, columns=column_names)

    st.info(
        "💡 Astuce : Modifie les cellules directement dans le tableau ci-dessous"
        " ou utilise la suppression multiple par ID."
    )

    # --- MODE ÉDITION EN MASSE AVEC ST.DATA_EDITOR ---
    edited_df = st.data_editor(
        df, num_rows="dynamic", use_container_width=True, key="stock_editor"
    )

    st.markdown("---")
    st.subheader("Suppression multiple")

    # Récupération sécurisée de la colonne des ID si elle existe
    ids_disponibles = df["id"].tolist() if "id" in df.columns else []
    ids_to_delete = st.multiselect(
        "Sélectionner les ID des objets à supprimer", options=ids_disponibles
    )

    col1, col2 = st.columns(2)

    with col1:
      if st.button(
          "🗑️ Supprimer les objets sélectionnés", type="primary"
      ):
        if ids_to_delete:
          for obj_id in ids_to_delete:
            run_query("DELETE FROM object WHERE id = %s", (obj_id,))
          st.warning(
              f"Objets avec les ID {ids_to_delete} supprimés avec succès !"
          )
          st.rerun()
        else:
          st.info("Aucun objet sélectionné pour la suppression.")

  else:
    st.info("Le stockage est actuellement vide.")

    # --- FORMULAIRE D'AJOUT RAPIDE ---
    with st.form("form_add_object_empty"):
      st.subheader("Ajouter un objet")
      nom_obj = st.text_input("Nom de l'objet")
      qte_obj = st.number_input("Quantité", min_value=1, value=1)
      if st.form_submit_button("Ajouter"):
        run_query(
            "INSERT INTO object (nom, quantite) VALUES (%s, %s)",
            (nom_obj, qte_obj),
        )
        st.success("Objet ajouté avec succès !")
        st.rerun()
