import pandas as pd
from datetime import datetime, timedelta

# ============================================================
# MODULE : risk.py
# Objectif : Calculer un score de risque + recommandations IA
# ============================================================


# ------------------------------------------------------------
# 1) Score de risque par produit
# ------------------------------------------------------------
def compute_risk_score(df):
    """
    Calcule un score de risque (0 à 100) pour chaque produit.
    Le score est basé sur :
    - péremption
    - rupture / stock critique
    - prix élevé
    - marge faible
    - rotation lente
    - dépendance fournisseur
    """

    df = df.copy()

    # Initialisation du score
    df["risk_score"] = 0

    today = datetime.today()

    # -----------------------------
    # A) Risque de péremption
    # -----------------------------
    if "date_peremption" in df.columns:
        soon = today + timedelta(days=90)
        df.loc[df["date_peremption"] < today, "risk_score"] += 40  # périmé
        df.loc[(df["date_peremption"] >= today) & (df["date_peremption"] <= soon), "risk_score"] += 20  # bientôt périmé

    # -----------------------------
    # B) Risque de rupture
    # -----------------------------
    if "stock_actuel" in df.columns and "stock_min" in df.columns:
        df.loc[df["stock_actuel"] == 0, "risk_score"] += 30
        df.loc[df["stock_actuel"] < df["stock_min"], "risk_score"] += 15

    # -----------------------------
    # C) Risque financier (produits chers)
    # -----------------------------
    if "prix_achat_ht" in df.columns:
        df.loc[df["prix_achat_ht"] >= 40, "risk_score"] += 15

    # -----------------------------
    # D) Marge faible
    # -----------------------------
    if "prix_achat_ht" in df.columns and "prix_vente_ttc" in df.columns:
        df["marge"] = df["prix_vente_ttc"] - df["prix_achat_ht"]
        df.loc[df["marge"] < 2, "risk_score"] += 10

    # -----------------------------
    # E) Rotation lente
    # -----------------------------
    if "stock_actuel" in df.columns and "stock_min" in df.columns:
        df["rotation"] = df["stock_actuel"] / df["stock_min"].replace(0, 1)
        df.loc[df["rotation"] < 0.5, "risk_score"] += 10

    # -----------------------------
    # F) Dépendance fournisseur
    # -----------------------------
    if "fournisseur" in df.columns:
        supplier_counts = df["fournisseur"].value_counts(normalize=True)
        df["supplier_risk"] = df["fournisseur"].map(supplier_counts)
        df.loc[df["supplier_risk"] > 0.4, "risk_score"] += 5

    # Score max = 100
    df["risk_score"] = df["risk_score"].clip(0, 100)

    return df


# ------------------------------------------------------------
# 2) Recommandations IA par produit
# ------------------------------------------------------------
def generate_recommendations(df):
    """
    Génère des recommandations intelligentes pour chaque produit.
    """
    df = df.copy()
    df["recommendation"] = ""

    today = datetime.today()

    for idx, row in df.iterrows():
        recos = []

        # Péremption
        if "date_peremption" in df.columns:
            if row["date_peremption"] < today:
                recos.append("Retirer immédiatement (périmé).")
            elif row["date_peremption"] < today + timedelta(days=90):
                recos.append("Écouler rapidement (bientôt périmé).")

        # Rupture / stock critique
        if row.get("stock_actuel", 999) == 0:
            recos.append("Commander en urgence (rupture).")
        elif row.get("stock_actuel", 999) < row.get("stock_min", 0):
            qty = row["stock_min"] - row["stock_actuel"]
            recos.append(f"Commander {qty} unités (stock critique).")

        # Rotation lente
        if "rotation" in row and row["rotation"] < 0.5:
            recos.append("Produit dormant : revoir l'assortiment.")

        # Produit cher
        if row.get("prix_achat_ht", 0) >= 40:
            recos.append("Produit coûteux : surveiller l'immobilisation.")

        # Marge faible
        if "marge" in row and row["marge"] < 2:
            recos.append("Marge faible : vérifier le prix de vente.")

        # Fournisseur dominant
        if row.get("supplier_risk", 0) > 0.4:
            recos.append("Dépendance fournisseur élevée.")

        df.at[idx, "recommendation"] = " ".join(recos) if recos else "Aucune action urgente."

    return df


# ------------------------------------------------------------
# 3) Fonction principale : score + recommandations
# ------------------------------------------------------------
def compute_risk_and_recos(df):
    """
    Retourne un DataFrame enrichi :
    - risk_score
    - rotation
    - marge
    - supplier_risk
    - recommendation
    """
    df_scored = compute_risk_score(df)
    df_final = generate_recommendations(df_scored)
    return df_final

