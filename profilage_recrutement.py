import pandas as pd
import os

print("Répertoire de travail actuel :")
print(os.getcwd())

print("\nFichiers présents dans ce répertoire :")
print(os.listdir())

fichier = r"Data\Recruitment Data.xlsx"

print("\nJe cherche le fichier :")
print(os.path.abspath(fichier))

df = pd.read_excel(fichier, sheet_name="Raw Data")

print("\nFICHIER CHARGÉ AVEC SUCCÈS !")
print(df.shape)

# ==========================================================
# 2. TYPES DE DONNEES
# ==========================================================

print("\n" + "=" * 70)
print("TYPES DE DONNEES")
print("=" * 70)

print(df.dtypes)


# ==========================================================
# 3. VALEURS MANQUANTES
# ==========================================================

print("\n" + "=" * 70)
print("VALEURS MANQUANTES")
print("=" * 70)

missing = pd.DataFrame(
    {
        "Colonne": df.columns,
        "Valeurs_manquantes": df.isna().sum(),
        "Pourcentage": (df.isna().mean() * 100).round(2),
    }
)

print(missing.sort_values("Pourcentage", ascending=False).to_string(index=False))


# ==========================================================
# 4. VALEURS UNIQUES
# ==========================================================

print("\n" + "=" * 70)
print("NOMBRE DE VALEURS UNIQUES")
print("=" * 70)

unique = pd.DataFrame(
    {"Colonne": df.columns, "Valeurs_uniques": df.nunique(dropna=True)}
)

print(unique.to_string(index=False))


# ==========================================================
# 5. DOUBLONS
# ==========================================================

print("\n" + "=" * 70)
print("DOUBLONS")
print("=" * 70)

print("Nombre de lignes dupliquées :", df.duplicated().sum())


# ==========================================================
# 6. VALEURS DES COLONNES CATEGORIELLES
# ==========================================================

print("\n" + "=" * 70)
print("VALEURS CATEGORIELLES")
print("=" * 70)

colonnes_textuelles = df.select_dtypes(include=["object"]).columns

for col in colonnes_textuelles:

    print("\n------------------------------------------")
    print("COLONNE :", repr(col))
    print("------------------------------------------")

    print(df[col].value_counts(dropna=False).to_string())


# ==========================================================
# 7. STATISTIQUES NUMERIQUES
# ==========================================================

print("\n" + "=" * 70)
print("STATISTIQUES NUMERIQUES")
print("=" * 70)

print(df.describe(include="all").transpose())


# ==========================================================
# 8. PROFIL DES DATES
# ==========================================================

print("\n" + "=" * 70)
print("COLONNES DE TYPE DATE")
print("=" * 70)

colonnes_dates = df.select_dtypes(include=["datetime64[ns]"]).columns

for col in colonnes_dates:

    print("\n", col)

    print("Date min :", df[col].min())
    print("Date max :", df[col].max())
    print("Valeurs manquantes :", df[col].isna().sum())


# ==========================================================
# 9. EXPORT DU RAPPORT
# ==========================================================

with pd.ExcelWriter("rapport_profilage.xlsx", engine="openpyxl") as writer:

    missing.to_excel(writer, sheet_name="Valeurs_manquantes", index=False)

    unique.to_excel(writer, sheet_name="Valeurs_uniques", index=False)

    df.describe(include="all").transpose().to_excel(writer, sheet_name="Statistiques")

print("\nRapport créé : rapport_profilage.xlsx")
