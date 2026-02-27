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

if uploaded_file is None:
    st.info("Veuillez importer un fichier pour commencer.")
    st.stop()

st.subheader("📦 Nettoyage et préparation des données")

try:
    # 🔥 Nettoyage complet
    df_clean = process_uploaded_file(uploaded_file)

    st.success("Fichier importé et nettoyé avec succès.")

    # 🔥 AFFICHAGE DU DATAFRAME NETTOYÉ UNIQUEMENT
    st.dataframe(df_clean)

except Exception as e:
    st.error(f"Erreur lors du traitement du fichier : {e}")
    st.stop()

st.markdown("---")

# 🚨 ALERTES
st.subheader("🚨 Alertes pharmaceutiques")
alerts = generate_all_alerts(df_clean)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Produits périmés", len(alerts["perimes"]))
    st.metric("Bientôt périmés (<90j)", len(alerts["bientot_perimes"]))

with col2:
    st.metric("Ruptures", len(alerts["ruptures"]))
    st.metric("Stock critique", len(alerts["stock_critique"]))

with col3:
    st.metric("Prix anormal", len(alerts["prix_anormal"]))
    st.metric("CIP dupliqué", len(alerts["cip_duplique"]))

for key, df_alert in alerts.items():
    if len(df_alert) > 0:
        st.write(f"### 🔎 {key.replace('_', ' ').capitalize()}")
        st.dataframe(df_alert)

st.markdown("---")

# 📊 KPIs
st.subheader("📊 Indicateurs clés (KPIs)")
kpis = compute_all_kpis(df_clean)

colA, colB = st.columns(2)

with colA:
    st.metric("Valeur totale du stock (€)", f"{kpis['valeur_stock']:.2f}")
    st.metric("Marge brute moyenne (€)", f"{kpis['marge_moyenne']:.2f}")

with colB:
    st.metric("Produits dormants", len(kpis["dormants"]))
    st.metric("Top produits chers", len(kpis["top_chers"]))

st.write("### Répartition par catégories")
st.dataframe(kpis["repartition_categories"])

st.write("### Répartition par fournisseurs")
st.dataframe(kpis["repartition_fournisseurs"])

st.markdown("---")

# 🔥 RISQUE
st.subheader("🔥 Score de risque & recommandations IA")
df_risk = compute_risk_and_recos(df_clean)

st.write("### Tableau complet avec score de risque")
st.dataframe(df_risk[[
    "designation", "categorie", "stock_actuel", "stock_min",
    "prix_achat_ht", "prix_vente_ttc", "risk_score", "recommendation"
]])

st.markdown("---")

# 📄 RAPPORT
st.subheader("📄 Rapport complet (Audit ARS)")
report_text = generate_full_report(alerts, kpis, df_risk)

st.text_area("Rapport généré", report_text, height=400)

st.download_button(
    label="📥 Télécharger le rapport (TXT)",
    data=report_text,
    file_name="rapport_pharmacie.txt"
)
