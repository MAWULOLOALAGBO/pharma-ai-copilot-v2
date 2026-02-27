from datetime import datetime

def summarize_alerts(alerts):
    summary = []
    for key, df in alerts.items():
        summary.append(f"- {key.replace('_', ' ').capitalize()} : {len(df)} produit(s)")
    return "\n".join(summary)

def summarize_kpis(kpis):
    return (
        f"- Valeur totale du stock : {kpis['valeur_stock']:.2f} €\n"
        f"- Marge brute moyenne : {kpis['marge_moyenne']:.2f} €\n"
        f"- Produits dormants : {len(kpis['dormants'])}\n"
        f"- Top produits chers : {len(kpis['top_chers'])}"
    )

def summarize_risk(df_risk):
    avg = df_risk["risk_score"].mean()
    high = len(df_risk[df_risk["risk_score"] >= 70])
    mid = len(df_risk[(df_risk["risk_score"] >= 40) & (df_risk["risk_score"] < 70)])
    low = len(df_risk[df_risk["risk_score"] < 40])

    return (
        f"- Score moyen : {avg:.1f}/100\n"
        f"- Risque élevé : {high}\n"
        f"- Risque moyen : {mid}\n"
        f"- Risque faible : {low}"
    )

def generate_full_report(alerts, kpis, df_risk):
    date = datetime.now().strftime("%d/%m/%Y %H:%M")

    return f"""
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
- Vérifier les produits périmés
- Prioriser l'écoulement des produits chers
- Réapprovisionner les ruptures
- Surveiller les produits dormants

================================
Fin du rapport
================================
"""
