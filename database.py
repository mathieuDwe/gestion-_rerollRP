import psycopg2
import streamlit as st


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