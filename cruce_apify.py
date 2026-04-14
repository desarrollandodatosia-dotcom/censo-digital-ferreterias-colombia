# -*- coding: utf-8 -*-
"""
cruce_apify.py - Enriquece BD RUES con Google Maps via Apify (modo BATCH)

Estrategia eficiente:
  - En vez de 1 llamada por registro (14,642 llamadas = $150+),
    enviamos LOTES de 50 queries en UNA sola llamada (async run)
  - Reduce el costo ~50x

Uso:
    # Solo MEDIANA+GRANDE (recomendado - 178 registros, ~$3.78 USD)
    python cruce_apify.py --token apify_api_XXXXXXX --solo-grandes

    # Todos (costoso - $150+ para 14k registros)
    python cruce_apify.py --token apify_api_XXXXXXX

    # Reanudar desde fila 50
    python cruce_apify.py --token apify_api_XXXXXXX --solo-grandes --inicio 50

NOTA IMPORTANTE:
    - Cada lote de 10 queries tarda ~10 minutos en Apify
    - Costo aprox: $0.021 por registro
    - Con $4.50 restantes -> maximo ~210 registros
    - Usar --solo-grandes para maximizar el valor: 178 ferr. MEDIANA+GRANDE

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
import json
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
ARCHIVO_SALIDA   = "BD_Enriquecida.xlsx"
ACTOR_ID         = "compass~crawler-google-places"
UMBRAL_FUZZY     = 70   # umbral mas permisivo para capturar mas matches
TAMANO_LOTE      = 10   # queries por run — cada query tarda ~30-60s en Apify
# IMPORTANTE: con 10 queries por lote, cada run tarda ~8-12 minutos
# No usar lotes mayores a 10-15 para no exceder el timeout

# ─────────────────────────────────────────────────────────────────
# CONSTRUIR QUERY DE BUSQUEDA
# ─────────────────────────────────────────────────────────────────

def construir_query(row: pd.Series) -> str:
    """
    Construye la query de busqueda optima para cada ferreteria.
    - Persona Juridica con nombre de empresa: usar nombre + ciudad
    - Persona Natural: usar 'ferreteria' + direccion + ciudad (no el nombre personal)
    """
    org = str(row.get("org_juridica", "")).strip()
    nombre = str(row.get("nombre_rues", "")).strip()
    nombre_com = str(row.get("nombre_comercial", "")).strip()
    municipio = str(row.get("municipio", "")).strip().title()
    direccion = str(row.get("direccion_comercial", "")).strip()

    # Si tiene nombre comercial normalizado, usarlo
    if nombre_com and nombre_com not in ("nan", ""):
        return f"{nombre_com} {municipio} Colombia"

    # Persona Natural: no usar nombre de persona, usar direccion
    if "Natural" in org or _es_nombre_persona(nombre):
        if len(direccion) > 5:
            return f"ferreteria {direccion} {municipio} Colombia"
        return f"ferreteria materiales {municipio} Colombia"

    # Persona Juridica: usar razon social limpia
    return f"{nombre} {municipio} Colombia"


def _es_nombre_persona(nombre: str) -> bool:
    """Heuristica: si tiene dos apellidos en mayuscula, es persona natural."""
    partes = nombre.upper().split()
    # Si mas de 3 palabras y ninguna es keyword de empresa, probablemente persona
    keywords_empresa = {"FERRETERIA", "FERRETER", "MATERIAL", "DISTRIBU",
                        "DEPOSITO", "ALMACEN", "COMERCIO", "S.A.S", "LTDA", "S.A", "CIA"}
    tiene_empresa = any(k in nombre.upper() for k in keywords_empresa)
    return len(partes) >= 3 and not tiene_empresa


# ─────────────────────────────────────────────────────────────────
# APIFY ASYNC RUN
# ─────────────────────────────────────────────────────────────────

def iniciar_run_apify(queries: list, token: str) -> str | None:
    """
    Inicia un run ASINCRONO en Apify con multiples queries.
    Retorna el run_id.
    """
    url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "searchStringsArray": queries,
        "maxCrawledPlacesPerSearch": 3,  # max 3 resultados por query
        "language": "es",
        "countryCode": "co",
        "maxImages": 0,
        "maxReviews": 0,
        "includeHistogram": False,
        "includeOpeningHours": False,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code == 201:
        run_data = resp.json().get("data", {})
        return run_data.get("id")
    print(f"  [ERROR iniciar run] HTTP {resp.status_code}: {resp.text[:200]}")
    return None


def esperar_run(run_id: str, token: str, timeout_seg: int = 300) -> bool:
    """
    Espera a que el run de Apify termine.
    Retorna True si SUCCEEDED, False si fallo.
    """
    url = f"https://api.apify.com/v2/actor-runs/{run_id}"
    headers = {"Authorization": f"Bearer {token}"}
    inicio = time.time()

    while time.time() - inicio < timeout_seg:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.ok:
            status = resp.json().get("data", {}).get("status", "")
            if status == "SUCCEEDED":
                return True
            if status in ("FAILED", "TIMED-OUT", "ABORTED"):
                print(f"  [Run {run_id}] Status: {status}")
                return False
            # RUNNING o READY -> seguir esperando
            print(f"  [Run {run_id}] Esperando... status={status}", end="\r")
            time.sleep(10)
        else:
            time.sleep(5)

    print(f"\n  [TIMEOUT] Run {run_id} no terminó en {timeout_seg}s")
    return False


def obtener_resultados(run_id: str, token: str) -> list:
    """Obtiene los items del dataset del run."""
    url = f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=60, params={"limit": 10000})
    if resp.ok:
        return resp.json()
    print(f"  [ERROR items] HTTP {resp.status_code}")
    return []


# ─────────────────────────────────────────────────────────────────
# MATCHING RESULTADO -> REGISTRO RUES
# ─────────────────────────────────────────────────────────────────

def hacer_match(nombre_rues: str, resultado: dict) -> int:
    """Calcula similitud entre nombre RUES y resultado de Google Maps."""
    nombre_maps = resultado.get("title", "")
    if not nombre_maps:
        return 0
    return fuzz.token_sort_ratio(nombre_rues.upper(), nombre_maps.upper())


def procesar_lote(df_lote: pd.DataFrame, resultados: list, queries: list) -> pd.DataFrame:
    """
    Asigna los resultados de Apify a los registros del lote usando:
    1. searchString (query original) para saber a qué ferretería corresponde
    2. fuzzy match del nombre para validar
    """
    # Agrupar resultados por searchString
    resultados_por_query = {}
    for r in resultados:
        q = r.get("searchString", "")
        if q not in resultados_por_query:
            resultados_por_query[q] = []
        resultados_por_query[q].append(r)

    for i, (idx, row) in enumerate(df_lote.iterrows()):
        query = queries[i]
        nombre_rues = str(row.get("nombre_rues", ""))

        candidatos = resultados_por_query.get(query, [])

        if not candidatos:
            df_lote.at[idx, "match_google"] = "No encontrado"
            continue

        # Elegir el candidato con mayor score
        mejor = None
        mejor_score = 0
        for c in candidatos:
            s = hacer_match(nombre_rues, c)
            if s > mejor_score:
                mejor_score = s
                mejor = c

        if mejor:
            loc = mejor.get("location") or {}
            lat = loc.get("lat", "")
            lon = loc.get("lng", "")
            nombre_maps = mejor.get("title", "")

            df_lote.at[idx, "nombre_comercial_maps"] = nombre_maps
            df_lote.at[idx, "telefono"]              = mejor.get("phone", "")
            df_lote.at[idx, "latitud"]               = lat if lat else ""
            df_lote.at[idx, "longitud"]              = lon if lon else ""
            df_lote.at[idx, "pagina_web"]            = mejor.get("website", "")
            df_lote.at[idx, "calificacion_google"]   = mejor.get("totalScore", "")
            df_lote.at[idx, "score_fuzzy"]           = mejor_score
            df_lote.at[idx, "fuente"]                = "RUES + Google Maps"
            df_lote.at[idx, "fecha_actualizacion"]   = str(date.today())

            if mejor_score >= UMBRAL_FUZZY:
                df_lote.at[idx, "match_google"]    = "Si"
                df_lote.at[idx, "nombre_comercial"] = nombre_maps
            else:
                df_lote.at[idx, "match_google"] = "Parcial"

    return df_lote


# ─────────────────────────────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────────────────────────────

def main(token: str, tamano_lote: int = 10, inicio: int = 0, limite: int = None, solo_grandes: bool = False):
    print("=" * 65)
    print("CRUCE RUES + GOOGLE MAPS - MODO BATCH (Apify async)")
    print(f"Fecha: {date.today()}")
    print("=" * 65)

    # Cargar BD base o continuar desde archivo previo si existe
    if os.path.exists(ARCHIVO_SALIDA) and inicio > 0:
        print(f"\nContinuando desde '{ARCHIVO_SALIDA}' (fila {inicio})...")
        df = pd.read_excel(ARCHIVO_SALIDA)
    else:
        print(f"\nCargando '{ARCHIVO_ENTRADA}'...")
        df = pd.read_excel(ARCHIVO_ENTRADA)

    print(f"  Total registros: {len(df):,}")

    # Filtrar solo MEDIANA y GRANDE si se solicita
    if solo_grandes:
        mask = df["tamano_empresa"].isin(["MEDIANA", "GRANDE"])
        df = df[mask].reset_index(drop=True)
        print(f"  Filtro --solo-grandes: {len(df):,} registros (MEDIANA + GRANDE)")
        print(f"  Distribucion: {df['tamano_empresa'].value_counts().to_dict()}")
        print(f"  Costo estimado: ~${len(df) * 0.021:.2f} USD")

    # Inicializar columnas nuevas si no existen
    for col in ["nombre_comercial_maps", "telefono", "latitud", "longitud",
                "pagina_web", "calificacion_google", "match_google", "score_fuzzy"]:
        if col not in df.columns:
            df[col] = ""
    # Asegurar que columnas numericas sean object para poder escribir strings
    for col in ["telefono", "pagina_web", "calificacion_google", "match_google",
                "score_fuzzy", "nombre_comercial_maps"]:
        df[col] = df[col].astype(object)

    # Determinar rango a procesar
    fin = len(df) if limite is None else min(inicio + limite, len(df))
    total_a_procesar = fin - inicio
    print(f"  Procesando filas {inicio} a {fin} ({total_a_procesar} registros)")
    print(f"  Tamano de lote: {tamano_lote} queries por run Apify")
    lotes = (total_a_procesar + tamano_lote - 1) // tamano_lote
    print(f"  Total de lotes: {lotes}")
    print(f"  Costo estimado: ~${lotes * 0.015:.2f} USD\n")

    # Estadisticas acumuladas
    total_match = 0
    total_parcial = 0
    total_no_encontrado = 0

    for n_lote in range(lotes):
        fila_inicio = inicio + n_lote * tamano_lote
        fila_fin    = min(fila_inicio + tamano_lote, fin)
        df_lote     = df.iloc[fila_inicio:fila_fin]

        print(f"\n[Lote {n_lote+1}/{lotes}] Filas {fila_inicio}-{fila_fin} ({len(df_lote)} registros)")

        # 1. Construir queries
        queries = [construir_query(row) for _, row in df_lote.iterrows()]
        queries_unicas = len(set(queries))
        print(f"  Queries: {len(queries)} ({queries_unicas} unicas)")
        print(f"  Ejemplos: {queries[0][:60]}")
        if len(queries) > 1:
            print(f"            {queries[-1][:60]}")

        # 2. Iniciar run async
        print(f"  Iniciando run Apify...", end=" ")
        run_id = iniciar_run_apify(queries, token)
        if not run_id:
            print("[ERROR] No se pudo iniciar el run. Saltando lote.")
            continue
        print(f"OK (run_id={run_id})")

        # 3. Esperar resultado
        print(f"  Esperando resultado (max 5 min)...")
        exito = esperar_run(run_id, token, timeout_seg=800)  # 10 queries * 60s = 600s min
        if not exito:
            print(f"  [FALLO] Lote {n_lote+1} no completó correctamente")
            continue

        # 4. Obtener resultados
        resultados = obtener_resultados(run_id, token)
        print(f"  Resultados obtenidos: {len(resultados)}")

        # 5. Hacer match y actualizar df
        df_lote_actualizado = procesar_lote(df_lote.copy(), resultados, queries)

        # Contar resultados del lote
        lote_match  = (df_lote_actualizado["match_google"] == "Si").sum()
        lote_parcial = (df_lote_actualizado["match_google"] == "Parcial").sum()
        lote_no     = (df_lote_actualizado["match_google"] == "No encontrado").sum()
        lote_coords  = (df_lote_actualizado["latitud"] != "").sum()

        total_match += lote_match
        total_parcial += lote_parcial
        total_no_encontrado += lote_no

        print(f"  Match OK:       {lote_match} | Parcial: {lote_parcial} | No encontrado: {lote_no}")
        print(f"  Con coordenadas: {lote_coords}")

        # 6. Actualizar df principal con el lote procesado
        df.iloc[fila_inicio:fila_fin] = df_lote_actualizado.values

        # 7. Guardar progreso
        df.to_excel(ARCHIVO_SALIDA, index=False, engine="openpyxl")
        print(f"  Guardado -> '{ARCHIVO_SALIDA}'")

        time.sleep(2)  # Pausa entre lotes

    # Resumen final
    procesados = fin - inicio
    print("\n" + "=" * 65)
    print("CRUCE COMPLETADO")
    print(f"  Registros procesados:   {procesados:,}")
    print(f"  Match alto (>={UMBRAL_FUZZY}%):   {total_match:,} ({total_match/max(procesados,1)*100:.1f}%)")
    print(f"  Match parcial:          {total_parcial:,} ({total_parcial/max(procesados,1)*100:.1f}%)")
    print(f"  No encontrados:         {total_no_encontrado:,} ({total_no_encontrado/max(procesados,1)*100:.1f}%)")

    con_coords = df.iloc[inicio:fin]["latitud"].apply(
        lambda x: x != "" and str(x) not in ("nan", "None", "")
    ).sum()
    print(f"  Con coordenadas GPS:    {con_coords:,}")
    print(f"\n  Archivo: '{ARCHIVO_SALIDA}'")
    print("=" * 65)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(description="Cruce RUES + Google Maps via Apify (batch)")
    parser.add_argument("--token",  required=True,  help="Token Apify (apify_api_XXX)")
    parser.add_argument("--lote",        type=int,  default=10,   help="Queries por run Apify (default: 10, cada una ~60s)")
    parser.add_argument("--inicio",      type=int,  default=0,    help="Fila de inicio para reanudar")
    parser.add_argument("--limite",      type=int,  default=None, help="Max registros a procesar")
    parser.add_argument("--solo-grandes", action="store_true",    help="Procesar solo MEDIANA+GRANDE (178 registros, ~$3.78)")
    args = parser.parse_args()

    main(
        token=args.token,
        tamano_lote=args.lote,
        inicio=args.inicio,
        limite=args.limite,
        solo_grandes=args.solo_grandes
    )
