# -*- coding: utf-8 -*-
"""
geocodificar_addresses.py - Geocodifica direcciones del RUES con Nominatim (GRATIS)

Estrategia:
  - Nominatim (OpenStreetMap) es gratuito y sin limite de registros
  - Rate limit: 1 peticion/segundo (respetado automaticamente)
  - Para 14,642 registros: ~4 horas (puede correr de fondo o en la noche)
  - Para 1,000 registros de prueba: ~17 minutos

Uso:
    python geocodificar_addresses.py                   # todos (14k)
    python geocodificar_addresses.py --limite 500      # primeros 500
    python geocodificar_addresses.py --limite 500 --desde 500  # reanudar

Genera:
    BD_Geocodificada.xlsx  (actualizado cada 100 registros)

Requiere:
    pip install pandas openpyxl requests
"""

import pandas as pd
import requests
import time
import os
import sys
import argparse
from datetime import date

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────
# CONFIGURACION
# ─────────────────────────────────────────────────────────────────
ARCHIVO_ENTRADA = "BD_Regiones_Prioritarias.xlsx"
ARCHIVO_SALIDA  = "BD_Geocodificada.xlsx"
USER_AGENT      = "CensoFerreteriasArgos/1.0 (daniel.agudelo@proyecto.co; educational)"

# Cache de municipios ya geocodificados (evita llamadas repetidas)
_cache_municipios = {}

# ─────────────────────────────────────────────────────────────────
# FUNCIONES
# ─────────────────────────────────────────────────────────────────

def geocodificar_direccion(direccion: str, municipio: str, departamento: str) -> tuple:
    """
    Intenta geocodificar en 3 niveles de precision:
    1. Direccion completa (mas preciso)
    2. Municipio + Departamento (si la direccion falla)
    3. Departamento (ultimo recurso)
    """
    headers = {"User-Agent": USER_AGENT}

    # Nivel 1: Direccion completa
    if len(direccion.strip()) > 5:
        query1 = f"{direccion}, {municipio}, {departamento}, Colombia"
        result = _llamar_nominatim(query1, headers)
        if result:
            return result[0], result[1], "direccion"

    # Nivel 2: Solo municipio
    cache_key = f"{municipio.upper()}_{departamento.upper()}"
    if cache_key in _cache_municipios:
        lat, lon = _cache_municipios[cache_key]
        return lat, lon, "municipio_cache"

    query2 = f"{municipio}, {departamento}, Colombia"
    result2 = _llamar_nominatim(query2, headers)
    time.sleep(1.1)  # Siempre esperar entre llamadas

    if result2:
        _cache_municipios[cache_key] = (result2[0], result2[1])
        return result2[0], result2[1], "municipio"

    return None, None, "no_encontrado"


def _llamar_nominatim(query: str, headers: dict) -> tuple | None:
    """Llama Nominatim y retorna (lat, lon) o None."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "co",
        "addressdetails": 0
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────────────────────────────

def main(limite: int = None, desde: int = 0):
    print("=" * 65)
    print("GEOCODIFICACION NOMINATIM - GRATIS, SIN API KEY")
    print(f"Fecha: {date.today()}")
    print("=" * 65)

    # Cargar (continuar si existe archivo previo)
    if os.path.exists(ARCHIVO_SALIDA) and desde > 0:
        print(f"\nContinuando desde '{ARCHIVO_SALIDA}' (fila {desde})...")
        df = pd.read_excel(ARCHIVO_SALIDA)
    else:
        print(f"\nCargando '{ARCHIVO_ENTRADA}'...")
        df = pd.read_excel(ARCHIVO_ENTRADA)

    print(f"  Total registros: {len(df):,}")

    # Rango a procesar
    fin = len(df) if limite is None else min(desde + limite, len(df))
    total = fin - desde
    tiempo_estimado = total * 1.2 / 60
    print(f"  Procesando: filas {desde} a {fin} ({total} registros)")
    print(f"  Tiempo estimado: ~{tiempo_estimado:.0f} minutos")

    if "latitud" not in df.columns:
        df["latitud"] = ""
    if "longitud" not in df.columns:
        df["longitud"] = ""
    if "precision_geocode" not in df.columns:
        df["precision_geocode"] = ""

    # Asegurar columnas como object
    for col in ["latitud", "longitud", "precision_geocode"]:
        df[col] = df[col].astype(object)

    encontrados = 0
    por_direccion = 0
    por_municipio = 0
    no_encontrados = 0

    print("\nIniciando geocodificacion...\n")

    for i in range(desde, fin):
        row = df.iloc[i]

        # Saltar si ya tiene coordenadas reales
        lat_actual = str(row.get("latitud", "")).strip()
        if lat_actual and lat_actual not in ("nan", "None", ""):
            try:
                float(lat_actual)
                print(f"[{i+1}/{fin}] SKIP (ya tiene coords): {str(row.get('nombre_rues',''))[:40]}")
                continue
            except ValueError:
                pass

        direccion    = str(row.get("direccion_comercial", "")).strip()
        municipio    = str(row.get("municipio", "")).strip().title()
        departamento = str(row.get("departamento", "")).strip().title()
        nombre       = str(row.get("nombre_rues", "")).strip()

        lat, lon, precision = geocodificar_direccion(direccion, municipio, departamento)

        if lat is not None:
            df.at[i, "latitud"]           = lat
            df.at[i, "longitud"]          = lon
            df.at[i, "precision_geocode"] = precision
            df.at[i, "fuente"]            = f"RUES + Nominatim ({precision})"
            encontrados += 1
            if precision == "direccion":
                por_direccion += 1
                print(f"[{i+1}/{fin}] GPS exact: {nombre[:35]:35} -> ({lat:.4f},{lon:.4f})")
            else:
                por_municipio += 1
                print(f"[{i+1}/{fin}] GPS muni:  {nombre[:35]:35} -> {municipio}")
        else:
            no_encontrados += 1
            print(f"[{i+1}/{fin}] NO COORD: {nombre[:35]}")

        # Guardar progreso cada 100 registros
        if (i - desde + 1) % 100 == 0:
            df.to_excel(ARCHIVO_SALIDA, index=False, engine="openpyxl")
            cobertura = encontrados / (i - desde + 1) * 100
            print(f"\n  -- Guardado (fila {i+1} | cobertura {cobertura:.0f}%) --\n")

        time.sleep(1.1)  # Respetar rate limit Nominatim

    # Guardar final
    df.to_excel(ARCHIVO_SALIDA, index=False, engine="openpyxl")

    print("\n" + "=" * 65)
    print("GEOCODIFICACION COMPLETADA")
    procesados = fin - desde
    print(f"  Registros procesados: {procesados:,}")
    print(f"  Con coordenadas:      {encontrados:,} ({encontrados/max(procesados,1)*100:.1f}%)")
    print(f"    - Por direccion:    {por_direccion:,}")
    print(f"    - Por municipio:    {por_municipio:,}")
    print(f"  Sin coordenadas:      {no_encontrados:,}")
    print(f"  Archivo: '{ARCHIVO_SALIDA}'")
    print("=" * 65)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(description="Geocodifica direcciones RUES con Nominatim (gratis)")
    parser.add_argument("--limite", type=int, default=None, help="Max registros a geocodificar")
    parser.add_argument("--desde",  type=int, default=0,    help="Fila de inicio para reanudar")
    args = parser.parse_args()

    main(limite=args.limite, desde=args.desde)
