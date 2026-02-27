import pandas as pd
from datetime import datetime

# ============================================================
# MODULE : report.py
# Objectif : Générer un rapport synthétique (Audit ARS + résumé)
# ============================================================


# ------------------------------------------------------------
# 1) Résumé des alertes
# ------------------------------------------------------------
def summarize_alerts(alerts_dict):
    """
    Prend le dictionnaire d'alertes généré par alerts.py
    et retourne un résumé lisible.
    """
    summary = []

    for key, df in alerts_dict.items():
        count = len(df)
        label = key.replace("_", " ").capitalize()
        summary.append(f"- {label} : {count} produit(s)")

    return "\n".join(summary)


# ------------------------------------------------------------
# 2) Résumé des KPIs
# ------------------------------------------------------------
def summarize_kpis(kpis_dict):
    """
    Prend le dictionnaire de KPIs généré par kpis.py
    et retourne un résumé lisible.
    """
    valeur = kpis_dict.get("valeur_stock", 0)
    marge = kpis_dict.get("marge_moyenne", 0)

    summary = [
        f"- Valeur totale du stock : {valeur:.2f} €",
        f"- Marge brute moyenne : {marge:.2f} €",
        f"- Produits dormants : {len(kpis_dict.get('dormants', []))}",
        f"- Top produits chers : {len(kpis_dict.get('top_chers', []))}",
    ]

    return "\n".join(summary)


# ------------------------------------------------------------
# 3) Résumé du risque global
# ------------------------------------------------------------
def summarize_risk(df_risk):
    """
    Analyse les scores de risque et génère un résumé global.
    """
    if "risk_score" not in df_risk.columns:
        return "Aucun score de risque disponible."

    avg_risk = df_risk["risk_score"].mean()
    high_risk = df_risk[df_risk["risk_score"] >= 70]
    medium_risk = df_risk[(df_risk["risk_score"] >= 40) & (df_risk["risk_score"] < 70)]
    low_risk = df_risk[df_risk["risk_score"] < 40]

    summary = [
        f"- Score de risque moyen : {avg_risk:.1f}/100",
        f"- Produits à risque élevé : {len(high_risk)}",
        f"- Produits à risque moyen : {len(medium_risk)}",
        f"- Produits à faible risque : {len(low_risk)}",
    ]

    return "\n".join(summary)


# ------------------------------------------------------------
# 4) Rapport complet
# ------------------------------------------------------------
def generate_full_report(alerts, kpis, df_risk):
    """
    Génère un rapport complet sous forme de texte structuré.
    """
    date = datetime.now().strftime("%d/%m/%Y %H:%M")

    report = f"""
===============================
   RAPPORT D'ANALYSE PHARMACIE
===============================
Généré le : {date}

--------------------------------
1) Synthèse des alertes
--------------------------------
{summarize_alerts(alerts)}

--------------------------------
2) Indicateurs clés (KPIs)
--------------------------------
{summarize_kpis(kpis)}

--------------------------------
3) Analyse du risque global
--------------------------------
{summarize_risk(df_risk)}

--------------------------------
4) Recommandations générales
--------------------------------
- Vérifier les produits périmés et bientôt périmés.
- Prioriser l'écoulement des produits à forte valeur.
- Réapprovisionner les produits en rupture ou en stock critique.
- Surveiller les produits dormants pour réduire l'immobilisation financière.
- Contrôler les marges faibles et ajuster les prix si nécessaire.

--------------------------------
5) Données détaillées disponibles
--------------------------------
- Liste des alertes par catégorie
- Liste des produits dormants
- Liste des produits à forte valeur
- Liste des produits à risque élevé
- Recommandations individuelles par produit

================================
Fin du rapport
================================
"""

    return report

