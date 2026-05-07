# -*- coding: utf-8 -*-
"""
cruce_apify.py v2 - Enriquece BD RUES con Google Maps via Apify (modo BATCH)

Mejoras v2 (Apr 2026):
  - TIMEOUT_RUN corregido: 2700s (45 min, antes era 800s)
  - Rescata datos parciales si el run expira (no perder trabajo)
  - Aborta runs zombie antes del siguiente lote (libera slot FREE)
  - Filtro por categoryName de Google Maps
  - Validacion geoespacial Haversine (< 50m = match automatico)
  - Validacion por IA Gemini 1.5 Flash para casos ambiguos
  - maxCrawledPlacesPerSearch reducido de 3 a 2
  - Query mejorada para Persona Natural ("Ferreteria {direccion}, {ciudad}")
  - Carga BD_Geocodificada.xlsx para geofencing si existe

Uso:
    python cruce_apify.py --token apify_api_XXX --solo-grandes
    python cruce_apify.py --token apify_api_XXX --solo-grandes --inicio 20

Variable de entorno (opcional, para validacion IA):
    set GEMINI_API_KEY=AIza...    # Windows
    pip install google-generativeai

Genera:
    BD_Enriquecida.xlsx  (actualizado despues de cada lote)

Requiere:
    pip install pandas fuzzywuzzy python-Levenshtein openpyxl requests
"""

import pandas as pd
import requests
import time
import os
import sys
import argparse
from math import radians, sin, cos, sqrt, atan2
from datetime import date

try:
    from fuzzywuzzy import fuzz
except ImportError:
    print("ERROR: pip install fuzzywuzzy python-Levenshtein")
    sys.exit(1)

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────
# CONFIGURACION
# ─────────────────────────────────────────────────────────────────
ARCHIVO_ENTRADA  = "BD_Regiones_Prioritarias.xlsx"
ARCHIVO_GEOCOD   = "BD_Geocodificada.xlsx"    # fallback local si Supabase no está disponible
ARCHIVO_SALIDA   = "BD_Enriquecida.xlsx"      # fallback local
ACTOR_ID         = "compass~crawler-google-places"
TAMANO_LOTE      = 10
TIMEOUT_RUN      = 2700     # FIX: antes 800s. Runs de 10 queries tardan 35-45 min.

# ─────────────────────────────────────────────────────────────────
# SUPABASE — I/O en la nube (reemplaza lectura/escritura de Excel)
# ─────────────────────────────────────────────────────────────────
SUPABASE_URL = "https://asaknpdzozkpexfrvlzw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzYWtucGR6b3prcGV4ZnJ2bHp3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE0NTg4ODYsImV4cCI6MjA4NzAzNDg4Nn0.qLaz-S0TAmuX-QtjzAi404s4D8DFvyBGuEtS-8WubfA"
_SB_HEADERS = {
    "apikey":        SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type":  "application/json",
}


def _sb_leer_ferreterias(solo_grandes: bool = False) -> pd.DataFrame:
    """Lee ferreterías desde Supabase. Filtra MEDIANA+GRANDE si solo_grandes=True."""
    import math as _math
    import json as _json
    PAGE = 1000
    registros = []
    offset = 0
    while True:
        params = {"select": "*", "limit": PAGE, "offset": offset}
        if solo_grandes:
            params["tamano_empresa"] = "in.(MEDIANA,GRANDE)"
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/ferreterias",
            headers={**_SB_HEADERS, "Range-Unit": "items"},
            params=params,
            timeout=30,
        )
        if not resp.ok:
            print(f"  [SB ERROR {resp.status_code}] {resp.text[:200]}")
            break
        lote = resp.json()
        if not lote:
            break
        registros.extend(lote)
        if len(lote) < PAGE:
            break
        offset += PAGE
    df = pd.DataFrame(registros) if registros else pd.DataFrame()
    return df


def _sb_actualizar_lote(df_lote: pd.DataFrame) -> bool:
    """
    Actualiza las filas procesadas en Supabase usando el campo `id` (BIGSERIAL).
    Hace PATCH por id para cada fila — más seguro que upsert masivo.
    """
    import json as _json
    import math as _math
    cols_actualizar = [
        "nombre_comercial_maps", "telefono", "latitud", "longitud",
        "pagina_web", "calificacion_google", "score_fuzzy",
        "categoria_google", "distancia_geo_metros", "match_google",
        "validacion_metodo", "fuente", "fecha_actualizacion", "nombre_comercial",
    ]
    errores = 0
    for _, row in df_lote.iterrows():
        sid = row.get("id")
        if sid is None:
            continue
        payload = {}
        for col in cols_actualizar:
            if col in row:
                val = row[col]
                if isinstance(val, float) and (_math.isnan(val) or _math.isinf(val)):
                    val = None
                elif str(val).strip() in ("", "nan", "None", "NaN"):
                    val = None
                payload[col] = val
        resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/ferreterias?id=eq.{int(sid)}",
            headers=_SB_HEADERS,
            data=_json.dumps(payload),
            timeout=15,
        )
        if not resp.ok:
            errores += 1
    return errores == 0

# Keywords de categorias Google Maps que confirman ferreteria o negocio afin
CATEGORIAS_VALIDAS = {
    'ferretería', 'ferreteria', 'hardware store',
    'materiales de construcción', 'materiales de construccion',
    'tienda de artículos para el hogar', 'tienda de articulos para el hogar',
    'depósito de materiales', 'deposito de materiales',
    'ferretero', 'pinturas', 'herramientas',
    'cerrajería', 'cerrajeria',
    'electrical supply store', 'home improvement store',
    'building materials store', 'paint store',
}

# ─────────────────────────────────────────────────────────────────
# CONFIGURACION IA (Gemini, opcional)
# ─────────────────────────────────────────────────────────────────
_gemini_disponible = False
_gemini_client = None
_GEMINI_MODEL = "models/gemini-2.5-flash"

# Rate limiter proactivo: free tier = 5 req/min → 1 req cada 12s
# Esperar ANTES de llamar evita el 429 por completo (vs reaccionar después)
_gemini_last_call: float = 0.0
_GEMINI_MIN_INTERVAL: float = 13.0  # 12s + 1s de buffer


def _leer_api_key() -> str:
    """Lee GEMINI_API_KEY desde env o desde .streamlit/secrets.toml."""
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    secrets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, encoding="utf-8") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY"):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return ""


def _inicializar_gemini():
    global _gemini_disponible, _gemini_client
    api_key = _leer_api_key()
    if not api_key:
        return
    try:
        from google import genai
        _gemini_client = genai.Client(api_key=api_key)
        _gemini_disponible = True
    except ImportError:
        print("  [IA] Instala: pip install google-genai")
    except Exception as e:
        print(f"  [IA] Error inicializando Gemini: {e}")


# ─────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────

def es_categoria_valida(categoria: str) -> bool:
    """True si categoryName de Google indica ferreteria o negocio afin."""
    if not categoria:
        return False
    cat_lower = categoria.lower()
    return any(kw in cat_lower for kw in CATEGORIAS_VALIDAS)


def distancia_metros(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia Haversine entre dos puntos GPS en metros."""
    R = 6_371_000
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlam = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlam / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def validar_con_gemini(nombre_rues: str, nombre_maps: str,
                       categoria: str, distancia_m) -> str:
    """
    Gemini valida si dos registros son la misma ferreteria.
    Retorna: 'Si', 'Parcial' o 'No'.

    Rate limiting PROACTIVO: espera antes de llamar para no superar
    5 req/min del free tier. Evita el 429 en lugar de reaccionar a el.
    """
    global _gemini_last_call

    if not _gemini_disponible or _gemini_client is None:
        return "Parcial"

    # ── Pace proactivo ────────────────────────────────────────────
    elapsed = time.time() - _gemini_last_call
    if elapsed < _GEMINI_MIN_INTERVAL:
        wait = _GEMINI_MIN_INTERVAL - elapsed
        print(f"    [Gemini] Pacing {wait:.1f}s...", end=" ", flush=True)
        time.sleep(wait)

    dist_txt = f"{distancia_m:.0f} metros" if distancia_m is not None else "desconocida"
    prompt = (
        "Eres un asistente validando si dos registros corresponden a la misma ferretería en Colombia.\n"
        f"Registro RUES (nombre legal): '{nombre_rues}'\n"
        f"Resultado Google Maps: título='{nombre_maps}', categoría='{categoria}'\n"
        f"Distancia entre las ubicaciones: {dist_txt}\n\n"
        "Responde ÚNICAMENTE con una de estas palabras: Si | Parcial | No\n"
        "Criterio: Si=mismo negocio alta confianza, Parcial=posible match, No=diferente negocio."
    )
    import re as _re
    for intento in range(3):
        try:
            _gemini_last_call = time.time()
            resp = _gemini_client.models.generate_content(model=_GEMINI_MODEL, contents=prompt)
            texto = resp.text.strip()
            if "Si" in texto or "sí" in texto.lower():
                return "Si"
            if "Parcial" in texto or "parcial" in texto.lower():
                return "Parcial"
            return "No"
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                # Backup: si aun así llega 429, extraer retryDelay y esperar
                m = _re.search(r"retryDelay.*?(\d+)s", err_str)
                wait_s = int(m.group(1)) + 3 if m else 20
                print(f"    [Gemini 429] Backup wait {wait_s}s (intento {intento+1}/3)...")
                time.sleep(wait_s)
                _gemini_last_call = time.time()
                continue
            print(f"    [Gemini error] {e}")
            return "Parcial"
    print("    [Gemini] 3 reintentos agotados → Parcial")
    return "Parcial"


def _parse_float(valor):
    """Convierte valor a float, retorna None si no es posible o es 0.0."""
    try:
        f = float(str(valor).strip())
        return f if f != 0.0 else None
    except (ValueError, TypeError):
        return None


def _tomar_decision(nombre_rues: str, nombre_maps: str, categoria: str,
                    score_fuzzy: int, distancia_m):
    """
    Cascada de validacion. Retorna (decision, metodo).

    1. distancia < 50m           → 'Si' (certeza fisica)
    2. categoria valida + < 500m → 'Si' (categoria + ubicacion)
    3. score_fuzzy >= 85%        → 'Si' (nombre muy similar)
    4. score_fuzzy < 30% + sin cat → 'No'
    5. caso ambiguo              → Gemini AI decide
    """
    cat_ok = es_categoria_valida(categoria)

    if distancia_m is not None and distancia_m < 50:
        return "Si", "distancia_50m"

    if cat_ok and (distancia_m is None or distancia_m < 500):
        return "Si", "categoria_valida"

    if score_fuzzy >= 85:
        return "Si", "fuzzy_85"

    if score_fuzzy < 30 and not cat_ok:
        return "No", "fuzzy_bajo"

    decision_ia = validar_con_gemini(nombre_rues, nombre_maps, categoria, distancia_m)
    return decision_ia, "ia_gemini"


# ─────────────────────────────────────────────────────────────────
# CONSTRUIR QUERY DE BUSQUEDA
# ─────────────────────────────────────────────────────────────────

def construir_query(row: pd.Series) -> str:
    """
    Query optimizada por tipo de persona:
    - Natural:   'Ferreteria {direccion}, {ciudad}, Colombia'
    - Juridica:  '{nombre comercial/razon social} {ciudad}, Colombia'
    """
    org = str(row.get("org_juridica", "")).strip()
    nombre = str(row.get("nombre_rues", "")).strip()
    nombre_com = str(row.get("nombre_comercial", "")).strip()
    municipio = str(row.get("municipio", "")).strip().title()
    direccion = str(row.get("direccion_comercial", "")).strip()

    # Persona Natural: buscar por direccion, no por nombre personal
    if "Natural" in org or _es_nombre_persona(nombre):
        if len(direccion) > 5:
            return f"Ferreteria {direccion}, {municipio}, Colombia"
        return f"Ferreteria {municipio}, Colombia"

    # Persona Juridica con nombre comercial normalizado
    if nombre_com and nombre_com not in ("nan", ""):
        return f"{nombre_com} {municipio}, Colombia"

    # Persona Juridica con solo razon social
    return f"{nombre} {municipio}, Colombia"


def _es_nombre_persona(nombre: str) -> bool:
    """Heuristica: >= 3 palabras sin keywords de empresa = persona natural."""
    keywords_empresa = {"FERRETERIA", "FERRETER", "MATERIAL", "DISTRIBU",
                        "DEPOSITO", "ALMACEN", "COMERCIO", "S.A.S", "LTDA", "S.A", "CIA"}
    tiene_empresa = any(k in nombre.upper() for k in keywords_empresa)
    return len(nombre.upper().split()) >= 3 and not tiene_empresa


# ─────────────────────────────────────────────────────────────────
# APIFY ASYNC RUN
# ─────────────────────────────────────────────────────────────────

def iniciar_run_apify(queries: list, token: str):
    """Inicia un run asíncrono en Apify. Retorna run_id o None."""
    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "searchStringsArray": queries,
        "maxCrawledPlacesPerSearch": 2,   # Reducido de 3 — primer resultado es casi siempre correcto
        "language": "es",
        "countryCode": "co",
        "maxImages": 0,
        "maxReviews": 0,
        "includeHistogram": False,
        "includeOpeningHours": False,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 201:
            return resp.json().get("data", {}).get("id")
        print(f"  [ERROR iniciar run] HTTP {resp.status_code}: {resp.text[:300]}")
    except Exception as e:
        print(f"  [ERROR iniciar run] {e}")
    return None


def esperar_run(run_id: str, token: str, timeout_seg: int = TIMEOUT_RUN) -> bool:
    """
    Espera a que el run de Apify termine.
    Retorna True si SUCCEEDED, False si falló o timeout.
    """
    url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    headers = {"Authorization": f"Bearer {token}"}
    inicio = time.time()

    while time.time() - inicio < timeout_seg:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.ok:
                status = resp.json().get("data", {}).get("status", "")
                if status == "SUCCEEDED":
                    return True
                if status in ("FAILED", "TIMED-OUT", "ABORTED"):
                    print(f"\n  [Run {run_id}] Terminó con status: {status}")
                    return False
                elapsed = int(time.time() - inicio)
                print(f"  [{elapsed}s] status={status}    ", end="\r")
                time.sleep(15)
            else:
                time.sleep(5)
        except Exception as e:
            print(f"  [esperar_run error] {e}")
            time.sleep(10)

    print(f"\n  [TIMEOUT] Run {run_id} no terminó en {timeout_seg}s")
    return False


def obtener_resultados(run_id: str, token: str) -> list:
    """Obtiene items del dataset (funciona aunque el run esté activo — rescate parcial)."""
    url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(url, headers=headers, timeout=60, params={"limit": 10000})
        if resp.ok:
            return resp.json()
        print(f"  [ERROR items] HTTP {resp.status_code}")
    except Exception as e:
        print(f"  [obtener_resultados error] {e}")
    return []


def abortar_run(run_id: str, token: str) -> None:
    """Aborta un run activo para liberar el slot de concurrencia del plan FREE."""
    url = f"https://api.apify.com/v2/actor-runs/{run_id}/abort"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.post(url, headers=headers, timeout=10)
        if resp.ok:
            print(f"  [Abortado] Run {run_id} liberado (slot FREE disponible).")
        else:
            print(f"  [Abort fallido] HTTP {resp.status_code}")
    except Exception as e:
        print(f"  [Abort error] {e}")


# ─────────────────────────────────────────────────────────────────
# MATCHING CON CASCADA DE VALIDACION
# ─────────────────────────────────────────────────────────────────

def procesar_lote(df_lote: pd.DataFrame, resultados: list, queries: list) -> pd.DataFrame:
    """
    Asigna resultados Apify a registros del lote usando cascada de validacion:
    distancia GPS → categoria → fuzzy >= 85% → Gemini AI (casos ambiguos)
    """
    # Agrupar resultados por searchString (query original)
    resultados_por_query = {}
    for r in resultados:
        q = r.get("searchString", "")
        if q not in resultados_por_query:
            resultados_por_query[q] = []
        resultados_por_query[q].append(r)

    for i, (idx, row) in enumerate(df_lote.iterrows()):
        query = queries[i] if i < len(queries) else ""
        nombre_rues = str(row.get("nombre_rues", ""))
        candidatos = resultados_por_query.get(query, [])

        if not candidatos:
            df_lote.at[idx, "match_google"] = "No encontrado"
            df_lote.at[idx, "validacion_metodo"] = "sin_resultados"
            continue

        # Elegir candidato con mayor score fuzzy
        mejor = None
        mejor_score = 0
        for c in candidatos:
            nombre_c = c.get("title", "")
            if not nombre_c:
                continue
            s = fuzz.token_sort_ratio(nombre_rues.upper(), nombre_c.upper())
            if s > mejor_score:
                mejor_score = s
                mejor = c

        if not mejor:
            df_lote.at[idx, "match_google"] = "No encontrado"
            df_lote.at[idx, "validacion_metodo"] = "sin_titulo"
            continue

        # Datos del mejor candidato
        loc = mejor.get("location") or {}
        lat_apify = _parse_float(loc.get("lat"))
        lon_apify = _parse_float(loc.get("lng"))
        nombre_maps = mejor.get("title", "")
        categoria = mejor.get("categoryName", "")

        # GPS de RUES (Nominatim) para comparacion geoespacial
        lat_rues = _parse_float(row.get("latitud"))
        lon_rues = _parse_float(row.get("longitud"))

        distancia_m = None
        if lat_rues and lon_rues and lat_apify and lon_apify:
            distancia_m = distancia_metros(lat_rues, lon_rues, lat_apify, lon_apify)

        # Decisión en cascada
        decision, metodo = _tomar_decision(nombre_rues, nombre_maps, categoria,
                                           mejor_score, distancia_m)

        if metodo == "ia_gemini":
            print(f"    [IA] '{nombre_rues[:28]}' ↔ '{nombre_maps[:28]}' → {decision}")

        # Actualizar DataFrame
        df_lote.at[idx, "nombre_comercial_maps"] = nombre_maps
        df_lote.at[idx, "telefono"]              = mejor.get("phone", "")
        df_lote.at[idx, "latitud"]               = lat_apify if lat_apify else ""
        df_lote.at[idx, "longitud"]              = lon_apify if lon_apify else ""
        df_lote.at[idx, "pagina_web"]            = mejor.get("website", "")
        df_lote.at[idx, "calificacion_google"]   = mejor.get("totalScore", "")
        df_lote.at[idx, "score_fuzzy"]           = mejor_score
        df_lote.at[idx, "categoria_google"]      = categoria
        df_lote.at[idx, "distancia_geo_metros"]  = round(distancia_m, 1) if distancia_m else ""
        df_lote.at[idx, "match_google"]          = decision
        df_lote.at[idx, "validacion_metodo"]     = metodo
        df_lote.at[idx, "fuente"]                = "RUES + Google Maps"
        df_lote.at[idx, "fecha_actualizacion"]   = str(date.today())

        if decision == "Si":
            df_lote.at[idx, "nombre_comercial"] = nombre_maps

    return df_lote


# ─────────────────────────────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────────────────────────────

def main(token: str, tamano_lote: int = 10, inicio: int = 0,
         limite: int = None, solo_grandes: bool = False):

    _inicializar_gemini()

    print("=" * 65)
    print("CRUCE RUES + GOOGLE MAPS v2 — IA + Geofencing + Categoria")
    print(f"Fecha: {date.today()}")
    print(f"Gemini IA: {'ACTIVA' if _gemini_disponible else 'NO disponible (solo FuzzyWuzzy)'}")
    print("=" * 65)

    # Carga desde Supabase (fuente de verdad) con fallback a Excel local
    try:
        print("\nCargando datos desde Supabase...")
        df = _sb_leer_ferreterias()
        if df.empty:
            raise ValueError("Supabase devolvió 0 registros")
        print(f"  {len(df):,} filas cargadas desde Supabase")
    except Exception as _sb_err:
        print(f"  [Supabase no disponible: {_sb_err}] — usando Excel local")
        if os.path.exists(ARCHIVO_SALIDA):
            print(f"  Continuando desde '{ARCHIVO_SALIDA}'...")
            df = pd.read_excel(ARCHIVO_SALIDA)
        elif os.path.exists(ARCHIVO_GEOCOD):
            print(f"  Cargando '{ARCHIVO_GEOCOD}'...")
            df = pd.read_excel(ARCHIVO_GEOCOD)
        else:
            print(f"  Cargando '{ARCHIVO_ENTRADA}'...")
            df = pd.read_excel(ARCHIVO_ENTRADA)

    print(f"  Total registros: {len(df):,}")

    # Filtrar solo MEDIANA y GRANDE si se solicita
    if solo_grandes:
        mask = df["tamano_empresa"].isin(["MEDIANA", "GRANDE"])
        df = df[mask].reset_index(drop=True)
        print(f"  Filtro --solo-grandes: {len(df):,} registros")
        print(f"  Distribucion: {df['tamano_empresa'].value_counts().to_dict()}")

    # Inicializar columnas nuevas si no existen
    nuevas_cols = ["nombre_comercial_maps", "telefono", "pagina_web",
                   "calificacion_google", "match_google", "score_fuzzy",
                   "categoria_google", "distancia_geo_metros", "validacion_metodo"]
    for col in nuevas_cols:
        if col not in df.columns:
            df[col] = ""
    for col in nuevas_cols + ["fuente", "fecha_actualizacion", "nombre_comercial"]:
        if col in df.columns:
            df[col] = df[col].astype(object)

    # Determinar rango
    fin = len(df) if limite is None else min(inicio + limite, len(df))
    total_a_procesar = fin - inicio
    lotes = (total_a_procesar + tamano_lote - 1) // tamano_lote
    print(f"  Procesando filas {inicio}-{fin} ({total_a_procesar} registros, {lotes} lotes)")
    print(f"  Costo estimado: ~${total_a_procesar * 0.021:.2f} USD\n")

    total_si = 0
    total_parcial = 0
    total_no = 0
    total_ia = 0

    for n_lote in range(lotes):
        fila_inicio = inicio + n_lote * tamano_lote
        fila_fin    = min(fila_inicio + tamano_lote, fin)
        df_lote     = df.iloc[fila_inicio:fila_fin]

        # Saltar si ya procesado
        ya_ok = df_lote["match_google"].apply(
            lambda x: str(x).strip() not in ("", "nan", "None")
        ).all()
        if ya_ok and len(df_lote) > 0:
            print(f"[Lote {n_lote+1}/{lotes}] Ya procesado — saltando")
            continue

        print(f"\n{'─'*65}")
        print(f"[Lote {n_lote+1}/{lotes}] Filas {fila_inicio}-{fila_fin-1} ({len(df_lote)} registros)")

        queries = [construir_query(row) for _, row in df_lote.iterrows()]
        print(f"  Query[0]: {queries[0][:70]}")
        if len(queries) > 1:
            print(f"  Query[-1]: {queries[-1][:70]}")

        # Iniciar run Apify
        print(f"  Iniciando run Apify...", end=" ", flush=True)
        run_id = iniciar_run_apify(queries, token)
        if not run_id:
            print("[ERROR] No se pudo iniciar. Saltando lote.")
            continue
        print(f"OK → {run_id}")

        # Esperar resultado
        print(f"  Esperando resultado (max {TIMEOUT_RUN//60} min)...", flush=True)
        exito = esperar_run(run_id, token, timeout_seg=TIMEOUT_RUN)

        # Obtener resultados (siempre, incluso en timeout — rescate parcial)
        resultados = obtener_resultados(run_id, token)
        print(f"\n  Resultados {'completos' if exito else 'PARCIALES (timeout)'}: {len(resultados)}")

        # En timeout/fallo: abortar run para liberar slot concurrencia FREE
        if not exito:
            abortar_run(run_id, token)
            if not resultados:
                print(f"  Sin datos recuperables. Saltando lote.")
                continue
            print(f"  Procesando {len(resultados)} items rescatados...")

        # Match y actualizar df
        df_lote_act = procesar_lote(df_lote.copy(), resultados, queries)

        lote_si      = (df_lote_act["match_google"] == "Si").sum()
        lote_parcial = (df_lote_act["match_google"] == "Parcial").sum()
        lote_no      = (df_lote_act["match_google"].isin(["No", "No encontrado"])).sum()
        lote_ia      = (df_lote_act["validacion_metodo"] == "ia_gemini").sum()

        total_si      += lote_si
        total_parcial += lote_parcial
        total_no      += lote_no
        total_ia      += lote_ia

        print(f"  Si: {lote_si} | Parcial: {lote_parcial} | No: {lote_no} | IA: {lote_ia}")

        # Actualizar df en memoria (para tracking de lotes ya procesados)
        df.iloc[fila_inicio:fila_fin] = df_lote_act.values

        # Guardar en Supabase (fuente principal)
        sb_ok = _sb_actualizar_lote(df_lote_act)
        if sb_ok:
            print(f"  Guardado → Supabase ({len(df_lote_act)} filas actualizadas)")
        else:
            print(f"  [WARN] Errores en Supabase — guardando Excel de respaldo...")
            try:
                df.to_excel(ARCHIVO_SALIDA, index=False, engine="openpyxl")
                print(f"  Respaldo → '{ARCHIVO_SALIDA}'")
            except Exception as e:
                print(f"  [ERROR respaldo] {e}")

        time.sleep(3)

    # Resumen final
    procesados = fin - inicio
    print("\n" + "=" * 65)
    print("CRUCE COMPLETADO")
    print(f"  Registros procesados:    {procesados:,}")
    print(f"  Match confirmado (Si):   {total_si:,} ({total_si/max(procesados,1)*100:.1f}%)")
    print(f"  Match parcial:           {total_parcial:,} ({total_parcial/max(procesados,1)*100:.1f}%)")
    print(f"  No encontrado/No:        {total_no:,} ({total_no/max(procesados,1)*100:.1f}%)")
    print(f"  Validados por IA Gemini: {total_ia:,}")
    print(f"\n  Datos persistidos en: Supabase → tabla ferreterias")
    print("=" * 65)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(
        description="Cruce RUES + Google Maps v2 (batch + IA Gemini + geofencing + categoria)"
    )
    parser.add_argument("--token",        required=True,       help="Token Apify (apify_api_XXX)")
    parser.add_argument("--lote",         type=int, default=10, help="Queries por run (default: 10)")
    parser.add_argument("--inicio",       type=int, default=0,  help="Fila de inicio para reanudar")
    parser.add_argument("--limite",       type=int, default=None, help="Max registros a procesar")
    parser.add_argument("--solo-grandes", action="store_true",  help="Solo MEDIANA+GRANDE")
    args = parser.parse_args()

    main(
        token=args.token,
        tamano_lote=args.lote,
        inicio=args.inicio,
        limite=args.limite,
        solo_grandes=args.solo_grandes,
    )
