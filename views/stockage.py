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

    # Ajout de la colonne de suppression au début
    df.insert(0, "🗑️ Supprimer", False)

    st.info(
        "💡 **Astuce** : Ajoute une ligne en bas du tableau (l'ID se créera"
        " tout seul), modifie les cellules, ou coche **🗑️ Supprimer** pour"
        " effacer des lignes."
    )

    # Configuration des colonnes pour bloquer l'ID (géré par la BDD)
    column_config = {
        "🗑️ Supprimer": st.column_config.CheckboxColumn(
            "Supprimer ?", default=False
        ),
        "id": st.column_config.NumberColumn(
            "ID (Auto)", disabled=True, help="Généré automatiquement par la base"
        ),
    }

    # --- TABLEAU INTERACTIF ---
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="stock_editor",
        column_config=column_config,
    )

    # Récupération des lignes cochées pour suppression
    rows_to_delete = (
        edited_df[edited_df["🗑️ Supprimer"] == True]
        if "🗑️ Supprimer" in edited_df.columns
        else pd.DataFrame()
    )

    col1, col2 = st.columns(2)

    # --- BOUTON : ENREGISTRER (MODIFICATIONS & NOUVEAUX ITEMS) ---
    with col1:
      if st.button("💾 Enregistrer les modifications", type="primary"):
        try:
          updatable_cols = [col for col in column_names if col != "id"]

          for _, row in edited_df.iterrows():
            row_id = row["id"]

            # Si la ligne est cochée pour suppression, on passe
            if (
                "🗑️ Supprimer" in row
                and row["🗑️ Supprimer"] == True
                and not pd.isna(row_id)
            ):
              continue

            if pd.isna(row_id):
              # --- NOUVELLE LIGNE : L'ID EST IGNORÉ POUR LAISSER LA BDD LE GÉNÉRER ---
              cols_to_insert = [
                  c for c in column_names if c != "id" and not pd.isna(row[c])
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
              # --- MISE À JOUR D'UNE LIGNE EXISTANTE ---
              set_clause = ", ".join(
                  [f'"{col}" = %s' for col in updatable_cols]
              )
              values = [row[col] for col in updatable_cols] + [row_id]
              run_query(
                  f"UPDATE object SET {set_clause} WHERE id = %s",
                  tuple(values),
              )

          st.success(
              "Modifications et nouveaux objets enregistrés avec succès !"
          )
          st.rerun()
        except Exception as e:
          st.error(f"Erreur lors de l'enregistrement : {e}")

    # --- BOUTON : SUPPRESSION MULTIPLE (APPARAÎT SI COCHÉ) ---
    with col2:
      if not rows_to_delete.empty:
        count_del = len(rows_to_delete)
        if st.button(
            f"🗑️ Confirmer la suppression ({count_del} sélectionné(s))",
            type="secondary",
        ):
          try:
            for _, row in rows_to_delete.iterrows():
              row_id = row["id"]
              if not pd.isna(row_id):
                run_query("DELETE FROM object WHERE id = %s", (int(row_id),))
            st.warning(f"{count_del} objet(s) supprimé(s) avec succès !")
            st.rerun()
          except Exception as e:
            st.error(f"Erreur lors de la suppression : {e}")
      else:
        st.info("Cochez 'Supprimer' sur une ligne pour afficher l'option.")

  else:
    st.info("Le stockage est actuellement vide.")

    # --- FORMULAIRE D'AJOUT SI LA TABLE EST VIDE ---
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
        st.success("Objet ajouté avec succès (ID auto-généré) !")
        st.rerun()
