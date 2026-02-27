import pandas as pd

# ============================================================
# MODULE : kpis.py
# Objectif : Calculer les indicateurs clés (KPIs) du stock
# ============================================================


# ------------------------------------------------------------
# 1) Valeur totale du stock
# ------------------------------------------------------------
def stock_value(df):
    """
    Calcule la valeur totale du stock :
    somme(prix_achat_ht * stock_actuel)
    """
    if "prix_achat_ht" not in df.columns or "stock_actuel" not in df.columns:
        return 0.0

    return (df["prix_achat_ht"] * df["stock_actuel"]).sum()


# ------------------------------------------------------------
# 2) Marge brute moyenne
# ------------------------------------------------------------
def average_margin(df):
    """
    Calcule la marge brute moyenne :
    marge = prix_vente_ttc - prix_achat_ht
    """
    if "prix_achat_ht" not in df.columns or "prix_vente_ttc" not in df.columns:
        return 0.0

    df = df.copy()
    df["marge"] = df["prix_vente_ttc"] - df["prix_achat_ht"]
    return df["marge"].mean()


# ------------------------------------------------------------
# 3) Rotation du stock
# ------------------------------------------------------------
def stock_rotation(df):
    """
    Rotation = stock_actuel / stock_min
    Indique si un produit tourne vite ou lentement.
    """
    if "stock_actuel" not in df.columns or "stock_min" not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df["rotation"] = df["stock_actuel"] / df["stock_min"].replace(0, 1)
    return df[["designation", "rotation"]]


# ------------------------------------------------------------
# 4) Produits dormants (stock élevé + faible rotation)
# ------------------------------------------------------------
def dormant_products(df, rotation_threshold=0.5, stock_threshold=20):
    """
    Détecte les produits dormants :
    - stock élevé
    - rotation faible
    """
    if "stock_actuel" not in df.columns or "stock_min" not in df.columns:
        return pd.DataFrame()

    df = df.copy()
    df["rotation"] = df["stock_actuel"] / df["stock_min"].replace(0, 1)

    mask = (df["rotation"] < rotation_threshold) & (df["stock_actuel"] > stock_threshold)
    return df[mask]


# ------------------------------------------------------------
# 5) Top 10 produits les plus chers
# ------------------------------------------------------------
def top_expensive(df, n=10):
    """
    Retourne les N produits les plus chers (prix achat).
    """
    if "prix_achat_ht" not in df.columns:
        return pd.DataFrame()

    return df.sort_values("prix_achat_ht", ascending=False).head(n)


# ------------------------------------------------------------
# 6) Répartition par catégorie
# ------------------------------------------------------------
def category_distribution(df):
    """
    Compte le nombre de produits par catégorie.
    """
    if "categorie" not in df.columns:
        return pd.DataFrame()

    return df["categorie"].value_counts().reset_index().rename(columns={
        "index": "categorie",
        "categorie": "nombre"
    })


# ------------------------------------------------------------
# 7) Répartition par fournisseur
# ------------------------------------------------------------
def supplier_distribution(df):
    """
    Compte le nombre de produits par fournisseur.
    """
    if "fournisseur" not in df.columns:
        return pd.DataFrame()

    return df["fournisseur"].value_counts().reset_index().rename(columns={
        "index": "fournisseur",
        "fournisseur": "nombre"
    })


# ------------------------------------------------------------
# 8) Fonction principale : tous les KPIs
# ------------------------------------------------------------
def compute_all_kpis(df):
    """
    Retourne un dictionnaire contenant tous les KPIs.
    """
    return {
        "valeur_stock": stock_value(df),
        "marge_moyenne": average_margin(df),
        "rotation": stock_rotation(df),
        "dormants": dormant_products(df),
        "top_chers": top_expensive(df),
        "repartition_categories": category_distribution(df),
        "repartition_fournisseurs": supplier_distribution(df),
    }

