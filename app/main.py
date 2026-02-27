import streamlit as st
import pandas as pd

from utils.cleaning import process_uploaded_file
from utils.alerts import generate_all_alerts
from utils.kpis import compute_all_kpis
from utils.risk import compute_risk_and_recos
from utils.report import generate_full_report

st.set_page_config(
    page_title="Pharma-AI Copilot",
    page_icon="💊",
    layout="wide"
)

st.title("💊 Pharma-AI Copilot")
st.write("Assistant intelligent d'analyse de stock pharmacie")

st.markdown("---")

uploaded_file = st.file_uploader(
    "Importer un fichier de stock (CSV, XLSX)",
    type=["csv", "xlsx"]
)

# 🔥 Empêche Streamlit de prévisualiser le fichier brut (cause de l’erreur)
if uploaded_file:
    uploaded_file.seek(0)

if uploaded_file is None:
    st.info("Veuillez importer un fichier pour commencer.")
    st.stop()

st.subheader("📦 Nettoyage et préparation des données")

try:
    df_clean = process_uploaded_file(uploaded_file)
    st.success("Fichier importé et nettoyé avec succès.")

    # 🔥 Affichage du DataFrame NETTOYÉ uniquement
    st.dataframe(df_clean, use_container_width=True)

except Exception as e:
    st.error(f"Erreur lors du traitement du fichier : {e}")
    st.stop()

st.markdown("---")

# Le reste de ton code (alertes, KPIs, risques, rapport) reste identique
