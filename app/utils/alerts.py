import pandas as pd
from datetime import datetime, timedelta

# ============================================================
# MODULE : alerts.py
# Objectif : Générer toutes les alertes pharmaceutiques
# ============================================================


# ------------------------------------------------------------
# 1) Alerte : Produits périmés
# ------------------------------------------------------------
def alert_expired(df):
    """
    Retourne les produits dont la date de péremption est dépassée.
    """
    today = datetime.today()
    if "date_peremption" not in df.columns:
        return pd.DataFrame()

    return df[df["date_peremption"] < today]


# ------------------------------------------------------------
# 2) Alerte : Produits bientôt périmés (< 90 jours)
# ------------------------------------------------------------
def alert_soon_expired(df, days=90):
    """
    Retourne les produits qui expirent dans moins de X jours.
    """
    today = datetime.today()
    limit = today + timedelta(days=days)

    if "date_peremption" not in df.columns:
        return pd.DataFrame()

    mask = (df["date_peremption"] >= today) & (df["date_peremption"] <= limit)
    return df[mask]


# ------------------------------------------------------------
# 3) Alerte : Ruptures (stock = 0)
# ------------------------------------------------------------
def alert_out_of_stock(df):
    """
    Retourne les produits en rupture totale.
    """
    if "stock_actuel" not in df.columns:
        return pd.DataFrame()

    return df[df["stock_actuel"] == 0]


# ------------------------------------------------------------
# 4) Alerte : Stock critique (stock < stock_min)
# ------------------------------------------------------------
def alert_low_stock(df):
    """
    Retourne les produits dont le stock est inférieur au stock minimum.
    """
    if "stock_actuel" not in df.columns or "stock_min" not in df.columns:
        return pd.DataFrame()

    return df[df["stock_actuel"] < df["stock_min"]]


# ------------------------------------------------------------
# 5) Alerte : Anomalies de prix (prix_vente < prix_achat)
# ------------------------------------------------------------
def alert_price_anomaly(df):
    """
    Retourne les produits dont le prix de vente est inférieur au prix d'achat.
    """
    if "prix_achat_ht" not in df.columns or "prix_vente_ttc" not in df.columns:
        return pd.DataFrame()

    return df[df["prix_vente_ttc"] < df["prix_achat_ht"]]


# ------------------------------------------------------------
# 6) Alerte : Doublons CIP (sécurité supplémentaire)
# ------------------------------------------------------------
def alert_duplicate_cip(df):
    """
    Retourne les produits ayant un CIP dupliqué.
    """
    if "code_cip" not in df.columns:
        return pd.DataFrame()

    dup = df[df.duplicated(subset=["code_cip"], keep=False)]
    return dup.sort_values("code_cip")


# ------------------------------------------------------------
# 7) Alerte : Produits à forte valeur immobilisée
# ------------------------------------------------------------
def alert_high_value(df, threshold=40):
    """
    Retourne les produits dont le prix d'achat est supérieur à un seuil.
    Par défaut : 40€ (produits chers).
    """
    if "prix_achat_ht" not in df.columns:
        return pd.DataFrame()

    return df[df["prix_achat_ht"] >= threshold]


# ------------------------------------------------------------
# 8) Alerte : Produits sensibles (catégories critiques)
# ------------------------------------------------------------
SENSITIVE_CATEGORIES = ["antibiotique", "stupefiant", "anticoagulant"]

def alert_sensitive_products(df):
    """
    Retourne les produits appartenant à des catégories sensibles.
    """
    if "categorie" not in df.columns:
        return pd.DataFrame()

    return df[df["categorie"].isin(SENSITIVE_CATEGORIES)]


# ------------------------------------------------------------
# 9) Alerte : Produits hors FEFO
# ------------------------------------------------------------
def alert_fefo_violation(df):
    """
    Détecte les produits dont la date de péremption est courte
    mais qui ont un stock élevé (risque de perte).
    """
    if "date_peremption" not in df.columns or "stock_actuel" not in df.columns:
        return pd.DataFrame()

    soon = alert_soon_expired(df, days=120)
    return soon[soon["stock_actuel"] > 10]


# ------------------------------------------------------------
# 10) Fonction principale : toutes les alertes
# ------------------------------------------------------------
def generate_all_alerts(df):
    """
    Retourne un dictionnaire contenant toutes les alertes.
    """
    return {
        "perimes": alert_expired(df),
        "bientot_perimes": alert_soon_expired(df),
        "ruptures": alert_out_of_stock(df),
        "stock_critique": alert_low_stock(df),
        "prix_anormal": alert_price_anomaly(df),
        "cip_duplique": alert_duplicate_cip(df),
        "produits_chers": alert_high_value(df),
        "produits_sensibles": alert_sensitive_products(df),
        "fefo_violation": alert_fefo_violation(df),
    }

