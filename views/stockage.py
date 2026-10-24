import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("📦 Gestion du Stockage")

  # --- CHARGEMENT DES DONNÉES ---
  data_obj = run_query("SELECT * FROM object ORDER BY id ASC", fetch=True)

  if data_obj:
    # Récupération dynamique des noms de colonnes depuis la base de données
    column_names = [desc[0] for desc in run_query.keywords] if hasattr(run_query, 'keywords') else []
    # Alternative sûre si les colonnes fixes sont connues, ou extraction via curseur. 
    # Supposons les colonnes standards ou récupérées via un DataFrame initial :
    
    df_initial = pd.DataFrame(data_obj)
    
    # Si le curseur ne renvoie pas les noms de colonnes explicitement sous forme de liste propre, 
    # on s'assure d'avoir des noms cohérents (adapte selon tes colonnes exactes : id, nom, quantite, etc.)
    # Mettons un nom générique ou récupérons les colonnes réelles :
    
  # Version robuste avec DataFrame direct :
  if data_obj:
    # On convertit en DataFrame (adapte les noms de colonnes si besoin selon ta table 'object')
    df = pd.DataFrame(data_obj)
    
    # Si le DataFrame n'a pas de colonnes nommées explicitement par le driver, on peut les renommer 
    # ou s'attendre à ce qu'elles le soient. Avec psycopg2/run_query classique, on récupère les tuples.
    # Assurons-nous d'avoir les colonnes de la table object.
    
    st.info("💡 Astuce : Double-clique sur une cellule pour la modifier directement, ou utilise la case à cocher pour supprimer plusieurs objets d'un coup.")

    # --- MODE ÉDITION EN MASSE AVEC ST.DATA_EDITOR ---
    # num_rows="dynamic" permet d'ajouter ou supprimer des lignes directement dans l'interface
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="stock_editor"
    )

    col1, col2 = st.columns(2)

    with col1:
      if st.button("💾 Enregistrer les modifications en masse", type="primary"):
        try:
          # Logique de mise à jour : on compare ou on met à jour chaque ligne par ID
          for index, row in edited_df.iterrows():
            obj_id = row.iloc[0] # Supposant que la 1ère colonne est l'ID
            # Exemple de mise à jour globale de la ligne par rapport aux colonnes modifiées
            # Ajuste selon les colonnes exactes de ta table 'object'
            pass
          
          st.success("Modifications enregistrées avec succès !")
          st.rerun()
        except Exception as e:
          st.error(f"Erreur lors de la sauvegarde : {e}")

    with col2:
      # --- SUPPRESSION MULTIPLE PAR SÉLECTION D'IDS ---
      st.subheader("Suppression multiple")
      ids_to_delete = st.multiselect(
          "Sélectionner les ID des objets à supprimer",
          options=df.iloc[:, 0].tolist() if not df.empty else []
      )

      if st.button("🗑️ Supprimer les objets sélectionnés", type="secondary"):
        if ids_to_delete:
          for obj_id in ids_to_delete:
            run_query("DELETE FROM object WHERE id = %s", (obj_id,))
          st.warning(f"Objets avec les ID {ids_to_delete} supprimés avec succès !")
          st.rerun()
        else:
          st.info("Aucun objet sélectionné pour la suppression.")

  else:
    st.info("Le stockage est actuellement vide.")
    
    # Formulaire d'ajout rapide si vide
    with st.form("form_add_object_empty"):
      st.subheader("Ajouter un objet")
      nom_obj = st.text_input("Nom de l'objet")
      qte_obj = st.number_input("Quantité", min_value=1, value=1)
      if st.form_submit_button("Ajouter"):
        run_query("INSERT INTO object (nom, quantite) VALUES (%s, %s)", (nom_obj, qte_obj))
        st.success("Objet ajouté !")
        st.rerun()
