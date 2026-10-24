import pandas as pd
import streamlit as st
from database import run_query


def render():
  st.title("📦 Gestion du Stockage")

  # --- RÉCUPÉRATION DYNAMIQUE DES COLONNES ---
  cols_data = run_query(
      "SELECT column_name FROM information_schema.columns WHERE table_name ="
      " 'object' ORDER BY ordinal_position",
      fetch=True,
  )
  column_names = [c[0] for c in cols_data] if cols_data else []

  if not column_names or "id" not in column_names:
    st.error("Impossible de récupérer la structure de la table 'object'.")
    return

  # --- CHARGEMENT DES DONNÉES ---
  data_obj = run_query("SELECT * FROM object ORDER BY id ASC", fetch=True)

  if data_obj:
    df = pd.DataFrame(data_obj, columns=column_names)

    st.info(
        "💡 Modifie directement les cellules dans le tableau ci-dessous, puis"
        " clique sur **'Enregistrer les modifications'** pour valider."
    )

    # --- MODE ÉDITION EN MASSE ---
    edited_df = st.data_editor(
        df, num_rows="dynamic", use_container_width=True, key="stock_editor"
    )

    # --- BOUTON DE SAUVEGARDE DES MODIFICATIONS ---
    if st.button("💾 Enregistrer les modifications", type="primary"):
      try:
        updatable_cols = [col for col in column_names if col != "id"]

        for _, row in edited_df.iterrows():
          row_id = row["id"]

          # Si l'ID est vide/NaN, c'est une nouvelle ligne ajoutée par l'utilisateur
          if pd.isna(row_id):
            cols_to_insert = [
                c
                for c in column_names
                if c != "id" and not pd.isna(row[c])
            ]
            if cols_to_insert:
              placeholders = ", ".join(["%s"] * len(cols_to_insert))
              cols_str = ", ".join([f'"{c}"' for c in cols_to_insert])
              values = tuple(row[c] for c in cols_to_insert)
              run_query(
                  f"INSERT INTO object ({cols_str}) VALUES ({placeholders})",
                  values,
              )
          else:
            # Mise à jour de la ligne existante
            set_clause = ", ".join([f'"{col}" = %s' for col in updatable_cols])
            values = [row[col] for col in updatable_cols] + [row_id]
            run_query(
                f"UPDATE object SET {set_clause} WHERE id = %s", tuple(values)
            )

        st.success("Modifications enregistrées avec succès dans la base !")
        st.rerun()
      except Exception as e:
        st.error(f"Erreur lors de l'enregistrement : {e}")

    st.markdown("---")
    st.subheader("Suppression multiple")

    ids_disponibles = df["id"].tolist()
    ids_to_delete = st.multiselect(
        "Sélectionner les ID des objets à supprimer",
        options=ids_disponibles,
        key="multiselect_del_stock",
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

    # --- FORMULAIRE D'AJOUT RAPIDE SI VIDE ---
    with st.form("form_add_object_empty"):
      st.subheader("Ajouter un objet")
      non_id_cols = [c for c in column_names if c != "id"]
      form_values = {}

      for col in non_id_cols:
        form_values[col] = st.text_input(f"Champ : {col}")

      if st.form_submit_button("Ajouter"):
        cols_str = ", ".join([f'"{c}"' for c in non_id_cols])
        placeholders = ", ".join(["%s"] * len(non_id_cols))
        values = tuple(form_values[col] for col in non_id_cols)
        run_query(
            f"INSERT INTO object ({cols_str}) VALUES ({placeholders})", values
        )
        st.success("Objet ajouté avec succès !")
        st.rerun()
