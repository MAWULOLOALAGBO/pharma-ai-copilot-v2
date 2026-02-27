import pandas as pd

def generate_all_alerts(df):
    alerts = {}

    alerts["perimes"] = df[df["date_peremption"] < pd.Timestamp.today()]
    alerts["bientot_perimes"] = df[
        (df["date_peremption"] >= pd.Timestamp.today()) &
        (df["date_peremption"] <= pd.Timestamp.today() + pd.Timedelta(days=90))
    ]
    alerts["ruptures"] = df[df["stock_actuel"] == 0]
    alerts["stock_critique"] = df[df["stock_actuel"] <= df["stock_min"]]
    alerts["prix_anormal"] = df[df["prix_vente_ttc"] < df["prix_achat_ht"]]
    alerts["cip_duplique"] = df[df["code_cip"].duplicated(keep=False)]

    return alerts
