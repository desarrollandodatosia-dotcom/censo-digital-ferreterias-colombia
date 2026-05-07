# -*- coding: utf-8 -*-
"""
importar_a_supabase.py
Importa BD_Geocodificada.xlsx + BD_Enriquecida.xlsx a la tabla ferreterias en Supabase.
Estrategia: BD_Geocodificada es la base (14,642 filas).
            BD_Enriquecida (178 filas) sobreescribe las columnas enriquecidas.
Uso: python importar_a_supabase.py
"""

import pandas as pd
import requests
import json
import math
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─── Config Supabase ─────────────────────────────────────────────
SUPABASE_URL = "https://asaknpdzozkpexfrvlzw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzYWtucGR6b3prcGV4ZnJ2bHp3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0NTg4ODYsImV4cCI6MjA4NzAzNDg4Nn0.qLaz-S0TAmuX-QtjzAi404s4D8DFvyBGuEtS-8WubfA"
TABLA        = "ferreterias"
BATCH_SIZE   = 500

_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_GEO = os.path.join(_DIR, "BD_Geocodificada.xlsx")
RUTA_ENR = os.path.join(_DIR, "BD_Enriquecida.xlsx")

HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}


def limpiar(valor):
    """Convierte NaN / inf a None para JSON."""
    if valor is None:
        return None
    if isinstance(valor, float) and (math.isnan(valor) or math.isinf(valor)):
        return None
    if isinstance(valor, str) and valor.strip() in ("", "nan", "None", "NaN", "NaT"):
        return None
    return valor


def df_a_registros(df: pd.DataFrame) -> list:
    """Convierte DataFrame a lista de dicts limpios para Supabase."""
    registros = []
    for _, row in df.iterrows():
        rec = {k: limpiar(v) for k, v in row.items()}
        registros.append(rec)
    return registros


def upsert_batch(registros: list) -> bool:
    """Inserta un batch de registros en Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/{TABLA}"
    resp = requests.post(url, headers=HEADERS, data=json.dumps(registros), timeout=60)
    if resp.status_code in (200, 201):
        return True
    print(f"  [ERROR {resp.status_code}] {resp.text[:300]}")
    return False


def main():
    print("=" * 60)
    print("IMPORTAR → SUPABASE  tabla: ferreterias")
    print("=" * 60)

    # 1. Cargar BD_Geocodificada como base
    print(f"\n[1/3] Leyendo {RUTA_GEO}...")
    df_geo = pd.read_excel(RUTA_GEO, engine="openpyxl")
    print(f"      {len(df_geo):,} filas, {len(df_geo.columns)} columnas")

    # 2. Cargar BD_Enriquecida
    print(f"\n[2/3] Leyendo {RUTA_ENR}...")
    df_enr = pd.read_excel(RUTA_ENR, engine="openpyxl")
    print(f"      {len(df_enr):,} filas, {len(df_enr.columns)} columnas")

    # 3. Merge: BD_Geo como base, BD_Enr sobreescribe filas que existen
    cols_enr_extra = [c for c in df_enr.columns if c not in df_geo.columns]
    for col in cols_enr_extra:
        df_geo[col] = None

    # Para las 178 filas que están en BD_Enriquecida, usar sus datos
    df_geo["numero_identificacion"] = pd.to_numeric(
        df_geo["numero_identificacion"], errors="coerce"
    )
    df_enr["numero_identificacion"] = pd.to_numeric(
        df_enr["numero_identificacion"], errors="coerce"
    )
    enr_ids = set(df_enr["numero_identificacion"].dropna().astype(int))

    # Filas de BD_Geo que NO están en BD_Enr → quedan como están
    df_no_enr = df_geo[~df_geo["numero_identificacion"].isin(enr_ids)].copy()
    # Filas de BD_Enr → usan todos sus datos (más columnas enriquecidas)
    df_enr_full = df_enr.copy()
    # Asegurar que df_enr_full tiene las mismas columnas que df_geo
    for col in df_geo.columns:
        if col not in df_enr_full.columns:
            df_enr_full[col] = None

    df_final = pd.concat([df_no_enr, df_enr_full[df_geo.columns]], ignore_index=True)
    print(f"\n[3/3] Dataset final: {len(df_final):,} filas")

    # Convertir tipos problemáticos a string donde necesario
    for col in ["numero_identificacion", "nit"]:
        if col in df_final.columns:
            df_final[col] = pd.to_numeric(df_final[col], errors="coerce")

    registros = df_a_registros(df_final)
    total     = len(registros)
    lotes     = math.ceil(total / BATCH_SIZE)

    print(f"\nSubiendo {total:,} registros en {lotes} lotes de {BATCH_SIZE}...")
    ok = 0
    for i in range(lotes):
        batch = registros[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        exito = upsert_batch(batch)
        if exito:
            ok += len(batch)
        pct = (i + 1) / lotes * 100
        print(f"  Lote {i+1}/{lotes} ({pct:.0f}%) — {'OK' if exito else 'ERROR'} — {ok:,} insertados")

    print(f"\n{'='*60}")
    print(f"COMPLETADO: {ok:,}/{total:,} registros en Supabase")
    print(f"{'='*60}")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
