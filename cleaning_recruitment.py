import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================================
# 1. CHARGEMENT DES DONNEES
# ==========================================================

fichier = r"Data\Recruitment Data.xlsx"

df = pd.read_excel(fichier, sheet_name="Raw Data")

print("=" * 70)
print("CHARGEMENT DES DONNEES")
print("=" * 70)

print("Données originales :", df.shape)


# ==========================================================
# 2. NETTOYAGE DES NOMS DE COLONNES
# ==========================================================

df.columns = df.columns.str.replace("\xa0", " ", regex=False).str.strip()

print("\nColonnes après nettoyage :")

for col in df.columns:
    print("-", col)


# ==========================================================
# 3. NETTOYAGE DES COLONNES TEXTE
# ==========================================================

colonnes_textuelles = df.select_dtypes(include=["object"]).columns

for col in colonnes_textuelles:

    # Conversion en type string
    df[col] = df[col].astype("string")

    # Suppression des espaces avant et après
    df[col] = df[col].str.strip()

    # Remplacement des espaces multiples par un seul
    df[col] = df[col].str.replace(r"\s+", " ", regex=True)

    # Les chaînes vides deviennent NULL
    df[col] = df[col].replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})


# ==========================================================
# 4. ANALYSE DES COLONNES COMPLETEMENT VIDES
# ==========================================================
# IMPORTANT :
# On ne supprime PAS ces colonnes.
# On les signale simplement.

colonnes_vides = [col for col in df.columns if df[col].isna().all()]

print("\n" + "=" * 70)
print("COLONNES COMPLETEMENT VIDES")
print("=" * 70)

if colonnes_vides:

    for col in colonnes_vides:
        print("-", col)

else:

    print("Aucune colonne complètement vide.")


# ==========================================================
# 5. ANALYSE DES DOUBLONS
# ==========================================================
# IMPORTANT :
# On ne supprime PAS les doublons automatiquement.
# On les compte et on les signale.

nb_doublons = df.duplicated().sum()

print("\n" + "=" * 70)
print("DOUBLONS")
print("=" * 70)

print("Nombre de lignes dupliquées :", nb_doublons)


# ==========================================================
# 6. NORMALISATION DES VALEURS CATEGORIELLES
# ==========================================================

colonnes_a_normaliser = [
    "Department",
    "Shortlisted Status",
    "Hire Status",
    "Offer Status",
    "Level/Band",
    "Rejected By",
]

for col in colonnes_a_normaliser:

    if col in df.columns:

        # Nettoyage des espaces
        df[col] = df[col].str.strip()


# ----------------------------------------------------------
# Normalisation de certaines colonnes de statut
# ----------------------------------------------------------

if "Shortlisted Status" in df.columns:

    df["Shortlisted Status"] = df["Shortlisted Status"].str.title()


if "Hire Status" in df.columns:

    df["Hire Status"] = df["Hire Status"].str.title()


if "Offer Status" in df.columns:

    df["Offer Status"] = df["Offer Status"].str.title()


if "Rejected By" in df.columns:

    df["Rejected By"] = df["Rejected By"].str.title()


# ==========================================================
# 7. CONVERSION DES DATES
# ==========================================================

colonnes_dates = [
    "Position Requisition Date",
    "Vacancy approval date",
    "Job advert open date",
    "Job advert closing date",
    "Interview date",
    "Date job offer",
    "Date contract prepared",
    "Date contract issued",
    "Reporting date",
    "Date of induction/onboarding",
    "Date e-file opened",
    "Date physical file open",
    "Date of inclusion to benefits",
    "Date of File Closure",
]


print("\n" + "=" * 70)
print("CONVERSION DES DATES")
print("=" * 70)


for col in colonnes_dates:

    if col in df.columns:

        df[col] = pd.to_datetime(df[col], errors="coerce")

        print(f"{col} → {df[col].dtype}")


# ==========================================================
# 8. NORMALISATION DE LA COLONNE HIRED
# ==========================================================

if "Hired" in df.columns:

    df["Hired"] = pd.to_numeric(df["Hired"], errors="coerce")

    df["Hired"] = df["Hired"].astype("Int64")


# ==========================================================
# 9. CONTROLE DES VALEURS MANQUANTES
# ==========================================================

print("\n" + "=" * 70)
print("VALEURS MANQUANTES")
print("=" * 70)

missing_report = pd.DataFrame(
    {
        "Colonne": df.columns,
        "Valeurs_manquantes": [df[col].isna().sum() for col in df.columns],
        "Pourcentage_manquant": [
            round(df[col].isna().mean() * 100, 2) for col in df.columns
        ],
    }
)

print(
    missing_report.sort_values("Pourcentage_manquant", ascending=False).to_string(
        index=False
    )
)


# ==========================================================
# 10. CONTROLE CHRONOLOGIQUE DES DATES
# ==========================================================
# IMPORTANT :
# Les anomalies sont signalées mais les lignes
# NE SONT PAS SUPPRIMEES.

print("\n" + "=" * 70)
print("CONTROLE CHRONOLOGIQUE")
print("=" * 70)


ordre_dates = [
    "Position Requisition Date",
    "Vacancy approval date",
    "Job advert open date",
    "Job advert closing date",
    "Interview date",
    "Date job offer",
    "Date contract prepared",
    "Date contract issued",
    "Reporting date",
    "Date of induction/onboarding",
    "Date e-file opened",
    "Date physical file open",
    "Date of inclusion to benefits",
    "Date of File Closure",
]


quality_issues = []


for i in range(len(ordre_dates) - 1):

    date1 = ordre_dates[i]

    date2 = ordre_dates[i + 1]

    if date1 in df.columns and date2 in df.columns:

        erreurs = df[date1].notna() & df[date2].notna() & (df[date2] < df[date1])

        nombre = erreurs.sum()

        print(f"{date1} → {date2} : {nombre} incohérences")

        # Enregistrer les anomalies
        for index in df.index[erreurs]:

            quality_issues.append(
                {
                    "Row": index + 2,
                    "Issue_Type": "Date inconsistency",
                    "Column_1": date1,
                    "Column_2": date2,
                    "Description": f"{date2} est antérieure à {date1}",
                }
            )


# ==========================================================
# 11. CREATION D'UN RAPPORT DE QUALITE
# ==========================================================

print("\n" + "=" * 70)
print("RAPPORT DE QUALITE")
print("=" * 70)


quality_df = pd.DataFrame(quality_issues)


if len(quality_df) > 0:

    print("Nombre d'incohérences détectées :", len(quality_df))

else:

    print("Aucune incohérence détectée.")


# ==========================================================
# 12. CONTROLE FINAL
# ==========================================================

print("\n" + "=" * 70)
print("CONTROLE FINAL")
print("=" * 70)

print("Nombre de lignes :", len(df))

print("Nombre de colonnes :", len(df.columns))

print("Nombre de doublons :", df.duplicated().sum())

print("Nombre total de valeurs NULL :", df.isna().sum().sum())


# ==========================================================
# 13. EXPORT DES DONNEES NETTOYEES
# ==========================================================

output_file = r"Data\Recruitment_Data_Clean.xlsx"

df.to_excel(output_file, index=False)

print("\nFichier nettoyé créé :")
print(output_file)


# ==========================================================
# 14. EXPORT DU RAPPORT DE QUALITE
# ==========================================================

quality_report = r"Data\Recruitment_Data_Quality_Report.xlsx"


with pd.ExcelWriter(quality_report, engine="openpyxl") as writer:

    # Rapport valeurs manquantes
    missing_report.to_excel(writer, sheet_name="Missing Values", index=False)

    # Colonnes complètement vides
    pd.DataFrame({"Empty Columns": colonnes_vides}).to_excel(
        writer, sheet_name="Empty Columns", index=False
    )

    # Doublons
    duplicate_rows = df[df.duplicated(keep=False)]

    duplicate_rows.to_excel(writer, sheet_name="Duplicates", index=False)

    # Incohérences de dates
    quality_df.to_excel(writer, sheet_name="Date Issues", index=False)


print("\nRapport qualité créé :")
print(quality_report)


print("\n" + "=" * 70)
print("NETTOYAGE TERMINE")
print("=" * 70)
