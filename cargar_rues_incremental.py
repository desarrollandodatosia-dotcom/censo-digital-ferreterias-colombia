# -*- coding: utf-8 -*-
"""
cargar_rues_incremental.py
Carga incremental de una nueva base RUES a Supabase.

Flujo (5 fases):
  [1/5] Cargar archivo de entrada (xlsx o csv latin-1 sep=';')
  [2/5] Diff vs Supabase por numero_identificacion -> identifica NUEVAS
  [3/5] Geocodificar SOLO las nuevas con Nominatim
  [4/5] INSERT masivo en lotes de 500 (match_google=NULL para que cruce_apify.py las recoja)
  [5/5] Resumen JSON final a stdout

Uso desde CLI:
  python cargar_rues_incremental.py --input ruta.xlsx --dry-run
  python cargar_rues_incremental.py --input ruta.xlsx --token <JWT_admin>

Uso desde app.py Tab 7: se invoca como subprocess con el JWT del usuario logueado
para que el INSERT respete la policy admin_full_access de Supabase RLS.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from datetime import date, datetime
from typing import Optional

import pandas as pd
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Reusar utilidades existentes en el repo
from importar_a_supabase import limpiar  # noqa: E402
from geocodificar_addresses import geocodificar_direccion  # noqa: E402

# ─── Config ──────────────────────────────────────────────────────
SUPABASE_URL = "https://asaknpdzozkpexfrvlzw.supabase.co"
SUPABASE_KEY_PUBLISHABLE = "sb_publishable_qCZF-vGhFd6wFpm9qAMhFA_dFAeK4im"
TABLA       = "ferreterias"
BATCH_SIZE  = 500
PAGE_SIZE   = 1000
CHECKPOINT  = "rues_incremental_checkpoint.xlsx"

COLS_MIN = ["numero_identificacion", "direccion_comercial",
            "municipio", "departamento", "nombre_rues"]

# Exit codes
EXIT_OK      = 0
EXIT_ARGS    = 1
EXIT_SCHEMA  = 2
EXIT_NETWORK = 3
EXIT_FILE    = 4
EXIT_AUTH    = 5


# ─── Helpers Supabase ────────────────────────────────────────────

def _headers(jwt_token: Optional[str]) -> dict:
    """Headers para Supabase REST. Si hay JWT, usa Authorization=Bearer JWT (rol authenticated)."""
    if jwt_token:
        return {
            "apikey":        SUPABASE_KEY_PUBLISHABLE,
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type":  "application/json",
        }
    return {
        "apikey":        SUPABASE_KEY_PUBLISHABLE,
        "Authorization": f"Bearer {SUPABASE_KEY_PUBLISHABLE}",
        "Content-Type":  "application/json",
    }


def leer_ids_existentes(headers: dict) -> set:
    """Lee numero_identificacion de toda la tabla Supabase paginando 1000 por request."""
    ids = set()
    offset = 0
    while True:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/{TABLA}",
            headers={**headers, "Range-Unit": "items"},
            params={"select": "numero_identificacion", "limit": PAGE_SIZE, "offset": offset},
            timeout=30,
        )
        if not r.ok:
            raise RuntimeError(f"Supabase GET error {r.status_code}: {r.text[:200]}")
        lote = r.json()
        if not lote:
            break
        for fila in lote:
            v = fila.get("numero_identificacion")
            if v is not None:
                try:
                    ids.add(int(v))
                except (TypeError, ValueError):
                    pass
        if len(lote) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return ids


def insertar_lote(registros: list, headers: dict) -> tuple[int, str]:
    """POST batch a Supabase. Devuelve (insertados, error_msg)."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/{TABLA}",
        headers={**headers, "Prefer": "return=minimal"},
        data=json.dumps(registros),
        timeout=60,
    )
    if r.status_code in (200, 201, 204):
        return len(registros), ""
    return 0, f"{r.status_code}: {r.text[:200]}"


# ─── Pipeline principal ─────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Ruta al xlsx/csv del RUES")
    parser.add_argument("--dry-run", action="store_true", help="Solo detecta y reporta, no inserta")
    parser.add_argument("--skip-geocode", action="store_true", help="Inserta sin geocodificar (lat/lon NULL)")
    parser.add_argument("--token", default="", help="JWT de usuario admin para INSERT con RLS")
    parser.add_argument("--log", default="", help="Ruta opcional a archivo de log adicional")
    args = parser.parse_args()

    resumen = {
        "total_input": 0,
        "nuevas_detectadas": 0,
        "geocodificadas": 0,
        "insertadas": 0,
        "errores": [],
        "dry_run": args.dry_run,
        "ts_inicio": datetime.now().isoformat(timespec="seconds"),
    }

    headers = _headers(args.token or None)
    if not args.dry_run and not args.token:
        print("[WARN] Sin --token: INSERT puede fallar por RLS (policy admin_full_access requiere JWT admin).")

    # ── [1/5] Cargar archivo ────────────────────────────────────
    print(f"[1/5] Cargando archivo: {args.input}", flush=True)
    if not os.path.exists(args.input):
        resumen["errores"].append(f"archivo no existe: {args.input}")
        print(json.dumps(resumen)); return EXIT_FILE

    ext = os.path.splitext(args.input)[1].lower()
    try:
        if ext in (".xlsx", ".xls"):
            df_in = pd.read_excel(args.input, engine="openpyxl")
        elif ext == ".csv":
            df_in = pd.read_csv(args.input, encoding="latin-1", sep=";")
        else:
            resumen["errores"].append(f"extension no soportada: {ext}")
            print(json.dumps(resumen)); return EXIT_FILE
    except Exception as e:
        resumen["errores"].append(f"error leyendo archivo: {e}")
        print(json.dumps(resumen)); return EXIT_FILE

    resumen["total_input"] = len(df_in)
    print(f"      {len(df_in):,} filas, {len(df_in.columns)} columnas", flush=True)

    # Validar schema mínimo
    faltantes = [c for c in COLS_MIN if c not in df_in.columns]
    if faltantes:
        resumen["errores"].append(f"columnas faltantes: {faltantes}")
        print(f"      ERROR columnas faltantes: {faltantes}", flush=True)
        print(json.dumps(resumen)); return EXIT_SCHEMA

    # ── [2/5] Diff vs Supabase ──────────────────────────────────
    print(f"[2/5] Leyendo numero_identificacion de Supabase (esto toma ~30s)...", flush=True)
    try:
        ids_existentes = leer_ids_existentes(headers)
    except Exception as e:
        resumen["errores"].append(f"error red Supabase: {e}")
        print(json.dumps(resumen)); return EXIT_NETWORK
    print(f"      {len(ids_existentes):,} ids ya en BD", flush=True)

    df_in["numero_identificacion"] = pd.to_numeric(df_in["numero_identificacion"], errors="coerce")
    df_in = df_in.dropna(subset=["numero_identificacion"])
    df_in["numero_identificacion"] = df_in["numero_identificacion"].astype(int)

    df_nuevas = df_in[~df_in["numero_identificacion"].isin(ids_existentes)].copy()
    resumen["nuevas_detectadas"] = len(df_nuevas)
    print(f"      NUEVAS detectadas: {len(df_nuevas):,}", flush=True)

    if args.dry_run:
        resumen["ts_fin"] = datetime.now().isoformat(timespec="seconds")
        print("[DRY-RUN] Sin geocode ni insert. Fin.")
        print("=== RESUMEN_JSON ===")
        print(json.dumps(resumen, ensure_ascii=False))
        return EXIT_OK

    if len(df_nuevas) == 0:
        resumen["ts_fin"] = datetime.now().isoformat(timespec="seconds")
        print("[INFO] No hay ferreterias nuevas, nada que hacer.")
        print("=== RESUMEN_JSON ===")
        print(json.dumps(resumen, ensure_ascii=False))
        return EXIT_OK

    # ── [3/5] Geocodificar solo nuevas ──────────────────────────
    if args.skip_geocode:
        print(f"[3/5] skip-geocode activo. lat/lon quedan NULL.", flush=True)
        for col in ("latitud", "longitud", "precision_geocode", "fuente"):
            if col not in df_nuevas.columns:
                df_nuevas[col] = None
    else:
        print(f"[3/5] Geocodificando {len(df_nuevas)} nuevas con Nominatim (~{len(df_nuevas)*1.2/60:.0f} min)...", flush=True)
        for col in ("latitud", "longitud", "precision_geocode", "fuente"):
            if col not in df_nuevas.columns:
                df_nuevas[col] = None
        ok_geo = 0
        for idx, row in df_nuevas.iterrows():
            direccion = str(row.get("direccion_comercial", "") or "").strip()
            municipio = str(row.get("municipio", "") or "").strip().title()
            depto     = str(row.get("departamento", "") or "").strip().title()
            try:
                lat, lon, precision = geocodificar_direccion(direccion, municipio, depto)
            except Exception as e:
                resumen["errores"].append(f"geocode fila {idx}: {e}"); lat=lon=None; precision="error"
            if lat is not None:
                df_nuevas.at[idx, "latitud"]           = lat
                df_nuevas.at[idx, "longitud"]          = lon
                df_nuevas.at[idx, "precision_geocode"] = precision
                df_nuevas.at[idx, "fuente"]            = f"RUES {date.today()} + Nominatim ({precision})"
                ok_geo += 1
            if (idx + 1) % 50 == 0:
                try:
                    df_nuevas.to_excel(CHECKPOINT, index=False, engine="openpyxl")
                    print(f"      checkpoint guardado en fila {idx+1}", flush=True)
                except Exception:
                    pass
            time.sleep(1.1)
        resumen["geocodificadas"] = ok_geo
        print(f"      geocodificadas {ok_geo}/{len(df_nuevas)}", flush=True)

    # Asegurar columnas para INSERT
    df_nuevas["match_google"] = None
    if "fuente" not in df_nuevas.columns or df_nuevas["fuente"].isna().all():
        df_nuevas["fuente"] = f"RUES {date.today()} (incremental)"

    # ── [4/5] INSERT masivo ─────────────────────────────────────
    print(f"[4/5] Insertando en Supabase en lotes de {BATCH_SIZE}...", flush=True)
    registros = []
    for _, row in df_nuevas.iterrows():
        rec = {k: limpiar(v) for k, v in row.items()}
        rec.pop("id", None)  # dejar que BIGSERIAL asigne
        registros.append(rec)

    total = len(registros)
    lotes = math.ceil(total / BATCH_SIZE)
    insertadas = 0
    for i in range(lotes):
        batch = registros[i * BATCH_SIZE : (i + 1) * BATCH_SIZE]
        n, err = insertar_lote(batch, headers)
        if err:
            resumen["errores"].append(f"lote {i+1}/{lotes}: {err}")
            print(f"      lote {i+1}/{lotes} ERROR: {err}", flush=True)
            # 401/403 = RLS, no tiene sentido seguir
            if err.startswith(("401", "403")):
                resumen["ts_fin"] = datetime.now().isoformat(timespec="seconds")
                resumen["insertadas"] = insertadas
                print("=== RESUMEN_JSON ===")
                print(json.dumps(resumen, ensure_ascii=False))
                return EXIT_AUTH
        else:
            insertadas += n
            print(f"      lote {i+1}/{lotes} OK ({insertadas:,}/{total:,})", flush=True)
    resumen["insertadas"] = insertadas

    # ── [5/5] Resumen ───────────────────────────────────────────
    resumen["ts_fin"] = datetime.now().isoformat(timespec="seconds")
    print(f"[5/5] Listo. Insertadas {insertadas:,}/{total:,}", flush=True)
    print("=== RESUMEN_JSON ===")
    print(json.dumps(resumen, ensure_ascii=False))
    return EXIT_OK


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())
