import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import unicodedata

# ============================================================
# MODULE : cleaning.py
# Objectif : Nettoyer, corriger et normaliser n'importe quel
# fichier de stock pharmacie (CSV, XLSX, fichiers tests).
# Version : Robuste + IA légère + anti-duplication
# ============================================================


# ------------------------------------------------------------
# 0) Correction automatique des colonnes dupliquées
# ------------------------------------------------------------
def fix_duplicate_columns(df):
    """
    Renomme automatiquement les colonnes dupliquées.
    Exemple :
    date_peremption, date_peremption → date_peremption_1, date_peremption_2
    """
    cols = df.columns
    new_cols = []
    seen = {}

    for col in cols:
        col_norm = col.strip()
        if col_norm not in seen:
            seen[col_norm] = 0
            new_cols.append(col_norm)
        else:
            seen[col_norm] += 1
            new_cols.append(f"{col_norm}_{seen[col_norm]}")

    df.columns = new_cols
    return df


# ------------------------------------------------------------
# 1) Mapping intelligent des colonnes
# ------------------------------------------------------------
COLUMN_ALIASES = {
    # Stock actuel
    "stock": "stock_actuel",
    "qte": "stock_actuel",
    "quantite": "stock_actuel",
    "quantité": "stock_actuel",
    "stock_physique": "stock_actuel",

    # Stock minimum
    "min": "stock_min",
    "seuil": "stock_min",
    "stock_minimum": "stock_min",

    # Prix achat
    "prix_achat": "prix_achat_ht",
    "pa_ht": "prix_achat_ht",
    "pa": "prix_achat_ht",

    # Prix vente
    "prix_vente": "prix_vente_ttc",
    "pv_ttc": "prix_vente_ttc",
    "pv": "prix_vente_ttc",

    # Dates
    "peremption": "date_peremption",
    "date_exp": "date_peremption",
    "exp": "date_peremption",
    "dlc": "date_peremption",

    # Emplacement
    "rayon": "emplacement_rayon",
    "emplacement": "emplacement_rayon",
    "localisation": "emplacement_rayon",
}


# ------------------------------------------------------------
# 2) Conversion automatique des dates Excel
# ------------------------------------------------------------
def excel_date_to_datetime(value):
    try:
        if isinstance(value, (int, float)):
            return datetime(1899, 12, 30) + timedelta(days=int(value))
        return pd.to_datetime(value, errors="coerce")
    except:
        return pd.NaT


# ------------------------------------------------------------
# 3) Normalisation du texte
# ------------------------------------------------------------
def normalize_text(value):
    if pd.isna(value):
        return value
    value = str(value).strip().lower()
    value = ''.join(c for c in unicodedata.normalize('NFD', value)
                    if unicodedata.category(c) != 'Mn')
    return value


# ------------------------------------------------------------
# 4) Détection IA légère des colonnes inconnues
# ------------------------------------------------------------
def detect_column(col, sample_values):
    col_norm = normalize_text(col)

    # CIP (7 à 13 chiffres)
    if sample_values.str.match(r"^\d{7,13}$", na=False).sum() > 5:
        return "code_cip"

    # Dates
    if sample_values.apply(lambda x: isinstance(excel_date_to_datetime(x), datetime)).sum() > 5:
        return "date_peremption"

    # Prix
    if sample_values.apply(lambda x: str(x).replace('.', '').isdigit()).sum() > 5:
        if "vente" in col_norm:
            return "prix_vente_ttc"
        if "achat" in col_norm:
            return "prix_achat_ht"

    # Stock
    if sample_values.apply(lambda x: str(x).isdigit()).sum() > 5:
        if "min" in col_norm:
            return "stock_min"
        return "stock_actuel"

    # Catégories
    if sample_values.str.contains("anti", na=False).sum() > 3:
        return "categorie"

    # Fournisseurs
    if sample_values.str.contains("laboratoire", na=False).sum() > 3:
        return "fournisseur"

    return None


# ------------------------------------------------------------
# 5) Nettoyage principal
# ------------------------------------------------------------
def clean_dataframe(df):
    df = df.copy()

    # A) Nettoyage agressif
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")
    df = df[~df.apply(lambda row: row.astype(str).str.contains("total", case=False).any(), axis=1)]

    # B) Normalisation des noms de colonnes
    new_cols = {}
    for col in df.columns:
        col_norm = normalize_text(col)
        if col_norm in COLUMN_ALIASES:
            new_cols[col] = COLUMN_ALIASES[col_norm]
    df = df.rename(columns=new_cols)

    # C) Détection IA légère
    for col in df.columns:
        if col not in COLUMN_ALIASES.values():
            detected = detect_column(col, df[col].astype(str))
            if detected:
                df = df.rename(columns={col: detected})

    # D) Correction des dates
    if "date_peremption" in df.columns:
        df["date_peremption"] = df["date_peremption"].apply(excel_date_to_datetime)

    # E) Normalisation du texte
    text_cols = ["designation", "categorie", "fournisseur", "nom_pharmacie", "emplacement_rayon"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).apply(normalize_text)

    # F) Conversion des types
    int_cols = ["stock_actuel", "stock_min", "code_cip"]
    float_cols = ["prix_achat_ht", "prix_vente_ttc"]

    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # G) Suppression des doublons CIP
    if "code_cip" in df.columns:
        df = df.drop_duplicates(subset=["code_cip"], keep="first")

    # H) Valeurs manquantes
    df = df.fillna({
        "categorie": "inconnue",
        "fournisseur": "inconnu",
        "designation": "non_specifie",
        "emplacement_rayon": "non_renseigne"
    })

    return df


# ------------------------------------------------------------
# 6) Fonction principale appelée par Streamlit
# ------------------------------------------------------------
def process_uploaded_file(uploaded_file):
    """
    Charge un fichier CSV/XLSX, corrige les colonnes dupliquées,
    nettoie les données et retourne un DataFrame propre.
    """
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file, engine="openpyxl")

    # 🔥 Correction immédiate AVANT tout traitement
    df = fix_duplicate_columns(df)

    df_clean = clean_dataframe(df)
    return df_clean
