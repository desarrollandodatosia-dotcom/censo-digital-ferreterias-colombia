# -*- coding: utf-8 -*-
"""
limpiar_datos.py - Pipeline ETL Censo Digital Ferreterias Colombia
Fuente principal: RUES CSV (34,135 registros)

Uso:
    python limpiar_datos.py

Genera:
    BD_RUES_Limpia.xlsx            — 34k registros completos
    BD_Regiones_Prioritarias.xlsx  — 14,642 registros (Bogotá, Antioquia,
                                     Cundinamarca, Eje Cafetero)

Requiere:
    pip install pandas fuzzywuzzy python-Levenshtein openpyxl
"""

import pandas as pd
import re
import os
import sys
from datetime import date

# Forzar UTF-8 en consola Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────
ARCHIVO_RUES        = "RUES_Ferreterias_7-4-2026 16_5_4(in).csv"
SALIDA_COMPLETA     = "BD_RUES_Limpia.xlsx"
SALIDA_PRIORITARIA  = "BD_Regiones_Prioritarias.xlsx"

REGIONES_PRIORITARIAS = [
    "BOGOTA", "ANTIOQUIA", "CUNDINAMARCA",
    "RISARALDA", "CALDAS", "QUINDIO"
]

# Dominios de correo personal (no corporativo)
DOMINIOS_PERSONALES = {
    "gmail.com", "hotmail.com", "yahoo.com", "outlook.com",
    "live.com", "icloud.com", "hotmail.es", "yahoo.es",
    "yahoo.co", "yahoo.com.co", "aol.com", "msn.com",
    "me.com", "mac.com", "googlemail.com"
}

# Sufijos legales colombianos a eliminar del nombre
SUFIJOS_LEGALES = [
    r"\bS\.?\s*A\.?\s*S\.?\b",
    r"\bLTDA\.?\b",
    r"\bS\.?\s*A\.?\b",
    r"\bE\.?\s*U\.?\b",
    r"\b&\s*CIA\.?\b",
    r"\bY\s+CIA\.?\b",
    r"\bCOMERCIALIZADORA\b",
    r"\bINVERSIONES\b",
]

# ─────────────────────────────────────────────────────────────────
# FUNCIONES
# ─────────────────────────────────────────────────────────────────

def primer_correo(valor: str) -> str:
    """Extrae el primer correo si hay múltiples en el campo."""
    if not isinstance(valor, str) or not valor.strip():
        return ""
    correos = re.split(r"[\s,;]+", valor.strip())
    for c in correos:
        if "@" in c:
            return c.strip().lower()
    return valor.strip().lower()


def clasificar_correo(valor: str) -> str:
    """Clasifica correo como Personal, Corporativo o Sin correo."""
    correo = primer_correo(valor)
    if not correo or "@" not in correo:
        return "Sin correo"
    dominio = correo.split("@")[-1].lower().strip()
    return "Personal" if dominio in DOMINIOS_PERSONALES else "Corporativo"


def normalizar_nombre_empresa(nombre: str) -> str:
    """
    Limpia sufijos legales (SAS, LTDA…) y aplica Title Case.
    Solo para Personas Jurídicas — no toca nombres de persona natural.
    """
    if not isinstance(nombre, str) or not nombre.strip():
        return ""

    n = nombre.strip()
    for patron in SUFIJOS_LEGALES:
        n = re.sub(patron, "", n, flags=re.IGNORECASE).strip()

    # Limpiar puntuación colgante al final
    n = re.sub(r"[.,\-\s]+$", "", n).strip()

    # Title case
    n = n.title()

    # Restaurar artículos en minúscula
    for art in [" De ", " Del ", " La ", " El ", " Los ", " Las ",
                " Y ", " En ", " Al ", " Con ", " Por ", " Para "]:
        n = n.replace(art.title(), art)

    return n.strip()


def es_nombre_empresa(razon_social: str) -> bool:
    """
    Devuelve True si parece un nombre de empresa (no persona natural).
    Heurística: contiene palabras clave de ferretería/empresa.
    """
    if not isinstance(razon_social, str):
        return False
    kw = ["FERRETERI", "FERRETER", "MATERIAL", "DISTRIBU", "DEPOSITO",
          "ALMACEN", "COMERCIO", "INDUSTRIA", "INVERSIONES", "S.A.S",
          "LTDA", "E.U", "S.A", "CIA"]
    razon_upper = razon_social.upper()
    return any(k in razon_upper for k in kw)


# ─────────────────────────────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print("PIPELINE ETL - RUES -> BD FERRETERIAS ARGOS")
    print(f"Fecha: {date.today()}")
    print("=" * 65)

    # ── 1. VERIFICAR ARCHIVO ────────────────────────────────────
    if not os.path.exists(ARCHIVO_RUES):
        print(f"\nERROR: No se encontró '{ARCHIVO_RUES}'")
        print("Asegúrate de estar en la carpeta correcta (Etapa3/).")
        return

    # ── 2. CARGAR RUES ──────────────────────────────────────────
    print(f"\n[1/6] Cargando '{ARCHIVO_RUES}'...")
    df_raw = pd.read_csv(
        ARCHIVO_RUES,
        encoding="latin-1",
        sep=";",
        dtype={"numero_identificacion": str},
        low_memory=False
    )
    print(f"  Registros cargados: {len(df_raw):,}")

    # ── 3. MAPEAR AL ESQUEMA DE BD ──────────────────────────────
    print("\n[2/6] Construyendo esquema de base de datos...")

    # Solo hay dos valores: "Persona Natural" y "Persona Jurídica"
    # Invertir la búsqueda de Natural (sin acento) para evitar problemas de encoding
    mask_natural  = df_raw["org_juridica"].fillna("").str.contains("Natural", case=True, na=False)
    mask_juridica = ~mask_natural

    df = pd.DataFrame()

    # Identificación
    df["tipo_identificacion"]   = df_raw["tipo_identificacion"].fillna("").str.strip()
    df["numero_identificacion"] = df_raw["numero_identificacion"].fillna("").str.strip()
    df["nit"] = df_raw.apply(
        lambda r: r["numero_identificacion"]
        if "NIT" in str(r.get("tipo_identificacion", "")).upper()
        else "",
        axis=1
    )

    # Razón social original (RUES)
    df["nombre_rues"] = df_raw["razon_social"].fillna("").str.strip()

    # Nombre comercial normalizado (solo para personas jurídicas con nombre de empresa)
    df["nombre_comercial"] = ""
    df.loc[mask_juridica, "nombre_comercial"] = (
        df.loc[mask_juridica, "nombre_rues"].apply(normalizar_nombre_empresa)
    )
    # Personas naturales con nombre tipo empresa también se normalizan
    mask_empresa_natural = mask_natural & df["nombre_rues"].apply(es_nombre_empresa)
    df.loc[mask_empresa_natural, "nombre_comercial"] = (
        df.loc[mask_empresa_natural, "nombre_rues"].apply(normalizar_nombre_empresa)
    )

    # Organización y tamaño
    df["org_juridica"]    = df_raw["org_juridica"].fillna("").str.strip()
    df["tamano_empresa"]  = df_raw["desc_tamano_empresa"].fillna("").str.strip()

    # Ubicación
    df["departamento"]        = df_raw["departamento"].fillna("").str.strip().str.upper()
    df["municipio"]           = df_raw["municipio"].fillna("").str.strip().str.upper()
    df["direccion_comercial"] = df_raw["direccion_comercial"].fillna("").str.strip()

    # Coordenadas (vacías hasta cruce con Apify)
    df["latitud"]   = ""
    df["longitud"]  = ""

    # Contacto
    df["telefono"]  = ""   # no disponible en RUES
    df["whatsapp"]  = ""

    df["correo_rues"]       = df_raw["correo_comercial"].apply(primer_correo)
    df["tipo_correo"]       = df_raw["correo_comercial"].apply(clasificar_correo)
    df["correo_verificado"] = ""
    df["pagina_web"]        = ""

    # Verificación de cemento
    df["vende_cemento"] = "No verificado"

    # Fechas y metadatos
    df["fecha_matricula_rues"] = df_raw["fecha_matricula"].fillna("").str.strip()
    df["fecha_actualizacion"]  = str(date.today())
    df["fuente"]               = "RUES"
    df["match_google"]         = ""     # se llenará en cruce_apify.py
    df["calificacion_google"]  = ""
    df["notas"] = df_raw["org_juridica"].apply(
        lambda x: "Nombre de persona - requiere verificacion en Google Maps"
        if "NATURAL" in str(x).upper() else ""
    )

    print(f"  Personas Juridicas: {mask_juridica.sum():,} ({mask_juridica.mean()*100:.1f}%)")
    print(f"  Personas Naturales: {mask_natural.sum():,} ({mask_natural.mean()*100:.1f}%)")
    print(f"  Campos construidos: {len(df.columns)}")

    # ── 4. ESTADÍSTICAS DE CORREO ───────────────────────────────
    print("\n[3/6] Análisis de correos...")
    tipos = df["tipo_correo"].value_counts()
    for tipo, n in tipos.items():
        print(f"  {tipo}: {n:,} ({n/len(df)*100:.1f}%)")

    # ── 5. ELIMINAR DUPLICADOS ──────────────────────────────────
    print("\n[4/6] Eliminando duplicados...")
    antes = len(df)
    df = df.drop_duplicates(
        subset=["numero_identificacion", "tipo_identificacion"],
        keep="first"
    ).reset_index(drop=True)
    print(f"  Duplicados eliminados: {antes - len(df):,}")
    print(f"  Registros únicos: {len(df):,}")

    # ── 6. FILTRAR REGIONES PRIORITARIAS ────────────────────────
    print("\n[5/6] Filtrando regiones prioritarias...")
    mask_prior = df["departamento"].isin(REGIONES_PRIORITARIAS)
    df_prior = df[mask_prior].reset_index(drop=True)
    print(f"  Total regiones prioritarias: {len(df_prior):,}")
    for dep in REGIONES_PRIORITARIAS:
        n = len(df_prior[df_prior["departamento"] == dep])
        print(f"    {dep}: {n:,}")

    # ── 7. EXPORTAR ─────────────────────────────────────────────
    print("\n[6/6] Exportando archivos...")

    df.to_excel(SALIDA_COMPLETA, index=False, engine="openpyxl")
    print(f"  [OK] BD completa:           '{SALIDA_COMPLETA}' ({len(df):,} registros)")

    df_prior.to_excel(SALIDA_PRIORITARIA, index=False, engine="openpyxl")
    print(f"  [OK] Regiones prioritarias: '{SALIDA_PRIORITARIA}' ({len(df_prior):,} registros)")

    # Resumen final
    print("\n" + "=" * 65)
    print("COMPLETADO")
    print(f"  BD nacional limpia:     {len(df):,} registros -> {SALIDA_COMPLETA}")
    print(f"  BD regiones prio:       {len(df_prior):,} registros -> {SALIDA_PRIORITARIA}")
    print(f"  Correos disponibles:    {(df['correo_rues'] != '').sum():,}")
    print(f"  Correos corporativos:   {(df['tipo_correo'] == 'Corporativo').sum():,}")
    print(f"  Con nombre comercial:   {(df['nombre_comercial'] != '').sum():,}")
    print("=" * 65)

    print("\nMuestra (5 registros - regiones prioritarias):")
    cols = ["nombre_rues", "nombre_comercial", "municipio", "correo_rues", "tipo_correo"]
    print(df_prior[cols].head().to_string(index=False))

    return df, df_prior


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
