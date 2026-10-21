from datetime import datetime
import pandas as pd
import streamlit as st
from database import run_query


def render():
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