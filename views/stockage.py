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

  non_id_cols = [c for c in column_names if c != "id"]

  # --- ESPACE DÉDIÉ POUR AJOUTER UN OBJET ---
  with st.expander("➕ Ajouter un nouvel objet", expanded=True):
    with st.form("form_add_object_clean"):
      st.subheader("Informations du nouvel objet")
      form_values = {}

      # Génère un champ de saisie pour chaque colonne de la table (sauf l'ID)
      for col in non_id_cols:
        form_values[col] = st.text_input(f"Champ : {col}")

      submit_add = st.form_submit_button("Ajouter l'objet")

      if submit_add:
        if any(form_values.values()):
          cols_str = ", ".join([f'"{c}"' for c in non_id_cols])
          placeholders = ", ".join(["%s"] * len(non_id_cols))
          values = tuple(form_values[col] for col in non_id_cols)
          run_query(
              f"INSERT INTO object ({cols_str}) VALUES ({placeholders})", values
          )
          st.success("Objet ajouté avec succès (ID auto-généré) !")
          st.rerun()
        else:
          st.warning("Veuillez remplir au moins un champ.")

  st.markdown("---")

  # --- CHARGEMENT DES DONNÉES EXISTANTES ---
  data_obj = run_query("SELECT * FROM object ORDER BY id ASC", fetch=True)

  if data_obj:
    df = pd.DataFrame(data_obj, columns=column_names)
    df.insert(0, "🗑️ Supprimer", False)

    st.info(
        "💡 Modifie les cellules directement dans le tableau ci-dessous, puis"
        " clique sur **'Enregistrer les modifications'**."
    )

    column_config = {
        "🗑️ Supprimer": st.column_config.CheckboxColumn(
            "Supprimer ?", default=False
        ),
        "id": st.column_config.NumberColumn(
            "ID (Auto)", disabled=True, help="Généré automatiquement par la BDD"
        ),
    }

    # --- TABLEAU INTERACTIF (MODIFICATION & SUPPRESSION) ---
    edited_df = st.data_editor(
        df,
        num_rows="fixed",
        use_container_width=True,
        key="stock_editor",
        column_config=column_config,
    )

    rows_to_delete = (
        edited_df[edited_df["🗑️ Supprimer"] == True]
        if "🗑️ Supprimer" in edited_df.columns
        else pd.DataFrame()
    )

    col1, col2 = st.columns(2)

    # --- BOUTON : ENREGISTRER LES MODIFICATIONS ---
    with col1:
      if st.button("💾 Enregistrer les modifications", type="primary"):
        try:
          updatable_cols = [col for col in column_names if col != "id"]

          for _, row in edited_df.iterrows():
            row_id = row["id"]

            # Si la ligne est cochée pour suppression, on ignore la modification
            if (
                "🗑️ Supprimer" in row
                and row["🗑️ Supprimer"] == True
                and not pd.isna(row_id)
            ):
              continue

            if not pd.isna(row_id):
              set_clause = ", ".join(
                  [f'"{col}" = %s' for col in updatable_cols]
              )
              values = [row[col] for col in updatable_cols] + [row_id]
              run_query(
                  f"UPDATE object SET {set_clause} WHERE id = %s",
                  tuple(values),
              )

          st.success("Modifications enregistrées avec succès !")
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
    st.info(
        "Le stockage est actuellement vide. Utilise le formulaire ci-dessus"
        " pour ajouter ton premier objet !"
    )
