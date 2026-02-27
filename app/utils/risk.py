import pandas as pd

def compute_risk_and_recos(df):
    df = df.copy()

    df["risk_score"] = (
        (df["stock_actuel"] == 0).astype(int) * 40 +
        (df["stock_actuel"] <= df["stock_min"]).astype(int) * 20 +
        (df["prix_vente_ttc"] > 50).astype(int) * 20 +
        (df["date_peremption"] < pd.Timestamp.today()).astype(int) * 20
    )

    df["recommendation"] = df["risk_score"].apply(lambda x:
        "Action urgente" if x >= 70 else
        "Surveillance" if x >= 40 else
        "Risque faible"
    )

    return df
