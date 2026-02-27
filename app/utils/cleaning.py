import os
os.environ["PYARROW_IGNORE_TIMEZONE"] = "1"

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import unicodedata

def fix_duplicate_columns(df):
    new_cols = []
    seen = {}
    for col in df.columns:
        base = col.strip()
        if base not in seen:
            seen[base] = 0
            new_cols.append(base)
        else:
            seen[base] += 1
            new_cols.append(f"{base}_{seen[base]}")
    df.columns = new_cols
    return df

COLUMN_ALIASES = {
    "stock": "stock_actuel",
    "qte": "stock_actuel",
    "quantite": "stock_actuel",
    "quantité": "stock_actuel",
    "stock_physique": "stock_actuel",
    "min": "stock_min",
    "seuil": "stock_min",
    "stock_minimum": "stock_min",
    "prix_achat": "prix_achat_ht",
    "pa_ht": "prix_achat_ht",
    "pa": "prix_achat_ht",
    "prix_vente": "prix_vente_ttc",
    "pv_ttc": "prix_vente_ttc",
    "pv": "prix_vente_ttc",
    "peremption": "date_peremption",
    "date_exp": "date_peremption",
    "exp": "date_peremption",
    "dlc": "date_peremption",
    "rayon": "emplacement_rayon",
    "emplacement": "emplacement_rayon",
    "localisation": "emplacement_rayon",
}

def excel_date_to_datetime(value):
    try:
        if isinstance(value, (int, float)):
            return datetime(1899, 12, 30) + timedelta(days=int(value))
        return pd.to_datetime(value, errors="coerce")
    except:
        return pd.NaT

def normalize_text(value):
    if pd.isna(value):
        return value
    value = str(value).strip().lower()
    value = ''.join(c for c in unicodedata.normalize('NFD', value)
                    if unicodedata.category(c) != 'Mn')
    return value

def detect_column(col, sample_values):
    col_norm = normalize_text(col)
    if sample_values.str.match(r"^\d{7,13}$", na=False).sum() > 5:
        return "code_cip"
    if sample_values.apply(lambda x: isinstance(excel_date_to_datetime(x), datetime)).sum() > 5:
        return "date_peremption"
    if sample_values.apply(lambda x: str(x).replace('.', '').isdigit()).sum() > 5:
        if "vente" in col_norm:
            return "prix_vente_ttc"
        if "achat" in col_norm:
            return "prix_achat_ht"
    if sample_values.apply(lambda x: str(x).isdigit()).sum() > 5:
        if "min" in col_norm:
            return "stock_min"
        return "stock_actuel"
    if sample_values.str.contains("anti", na=False).sum() > 3:
        return "categorie"
    if sample_values.str.contains("laboratoire", na=False).sum() > 3:
        return "fournisseur"
    return None

def clean_dataframe(df):
    df = df.copy()
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    df = df[~df.apply(lambda row: row.astype(str).str.contains("total", case=False).any(), axis=1)]
    new_cols = {}
    for col in df.columns:
        col_norm = normalize_text(col)
        if col_norm in COLUMN_ALIASES:
            new_cols[col] = COLUMN_ALIASES[col_norm]
    df = df.rename(columns=new_cols)
    for col in df.columns:
        if col not in COLUMN_ALIASES.values():
            detected = detect_column(col, df[col].astype(str))
            if detected:
                df = df.rename(columns={col: detected})
    if "date_peremption" in df.columns:
        df["date_peremption"] = df["date_peremption"].apply(excel_date_to_datetime)
    text_cols = ["designation", "categorie", "fournisseur", "nom_pharmacie", "emplacement_rayon"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(normalize_text)
    int_cols = ["stock_actuel", "stock_min", "code_cip"]
    float_cols = ["prix_achat_ht", "prix_vente_ttc"]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    if "code_cip" in df.columns:
        df = df.drop_duplicates(subset=["code_cip"], keep="first")
    df = df.fillna({
        "categorie": "inconnue",
        "fournisseur": "inconnu",
        "designation": "non_specifie",
        "emplacement_rayon": "non_renseigne"
    })
    return df

def process_uploaded_file(uploaded_file):
    # 🔥 CSV : forcer pandas engine pour éviter pyarrow
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, engine="python")

    # 🔥 XLSX : lecture normale
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    # 🔥 Correction des colonnes dupliquées
    df = fix_duplicate_columns(df)

    # 🔥 Nettoyage complet
    df_clean = clean_dataframe(df)

    return df_clean
