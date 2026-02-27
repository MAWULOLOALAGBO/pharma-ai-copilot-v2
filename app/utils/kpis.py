import pandas as pd

def compute_all_kpis(df):
    kpis = {}

    kpis["valeur_stock"] = (df["stock_actuel"] * df["prix_vente_ttc"]).sum()
    kpis["marge_moyenne"] = (df["prix_vente_ttc"] - df["prix_achat_ht"]).mean()

    kpis["dormants"] = df[df["stock_actuel"] > 0].sort_values("stock_actuel", ascending=False).head(20)
    kpis["top_chers"] = df.sort_values("prix_vente_ttc", ascending=False).head(20)

    kpis["repartition_categories"] = df["categorie"].value_counts().reset_index()
    kpis["repartition_fournisseurs"] = df["fournisseur"].value_counts().reset_index()

    return kpis
