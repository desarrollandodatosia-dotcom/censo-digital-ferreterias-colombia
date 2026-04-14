# -*- coding: utf-8 -*-
"""
mapa_v1.py - Mapa interactivo de ferreterias Colombia (Cementos Argos)

Estrategia de coordenadas:
  1. Si BD_Enriquecida.xlsx existe y tiene coordenadas -> usa esas (Apify)
  2. Si no -> geocodifica por municipio con Nominatim (1 llamada por municipio, no por ferreteria)
     ~100-200 municipios en regiones prioritarias = menos de 5 minutos

Genera:
    mapa_v1.html   (abrir en navegador)

Uso:
    python mapa_v1.py                          # genera mapa completo
    python mapa_v1.py --input BD_Enriquecida.xlsx

Requiere:
    pip install pandas folium openpyxl requests
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
import requests
import time
import os
import sys
import random
import argparse
from datetime import date
from collections import defaultdict

# Forzar UTF-8 en consola Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────
# CONFIGURACION
# ─────────────────────────────────────────────────────────────────
ARCHIVO_ENTRADA = "BD_Regiones_Prioritarias.xlsx"   # fallback si no hay BD_Enriquecida
ARCHIVO_SALIDA  = "mapa_v1.html"

COLORES_DEP = {
    "BOGOTA":        "#E74C3C",  # rojo
    "ANTIOQUIA":     "#3498DB",  # azul
    "CUNDINAMARCA":  "#2ECC71",  # verde
    "RISARALDA":     "#9B59B6",  # morado
    "CALDAS":        "#E67E22",  # naranja
    "QUINDIO":       "#1ABC9C",  # teal
}

# Coordenadas precargadas para municipios principales (evita llamadas a Nominatim)
COORDS_BASE = {
    "BOGOTA":           (4.7110, -74.0721),
    "BOGOTA D.C.":      (4.7110, -74.0721),
    "MEDELLIN":         (6.2442, -75.5812),
    "BELLO":            (6.3366, -75.5568),
    "ITAGUI":           (6.1847, -75.5997),
    "ENVIGADO":         (6.1751, -75.5921),
    "RIONEGRO":         (6.1550, -75.3741),
    "BUCARAMANGA":      (7.1193, -73.1227),
    "MANIZALES":        (5.0703, -75.5138),
    "PEREIRA":          (4.8133, -75.6961),
    "ARMENIA":          (4.5339, -75.6811),
    "CALI":             (3.4516, -76.5320),
    "SOACHA":           (4.5795, -74.2176),
    "ZIPAQUIRA":        (5.0234, -73.9991),
    "FACATATIVA":       (4.8145, -74.3550),
    "CHIA":             (4.8614, -74.0591),
    "CAJICA":           (4.9184, -74.0259),
    "FUSAGASUGA":       (4.3432, -74.3638),
    "DOS QUEBRADAS":    (4.8395, -75.6728),
    "SANTA ROSA DE CABAL": (4.8686, -75.6219),
    "LA DORADA":        (5.4550, -74.6700),
    "CHINCHINA":        (4.9826, -75.6030),
    "CALARCA":          (4.5168, -75.6438),
    "VILLAVICENCIO":    (4.1420, -73.6266),
    "CARTAGENA":        (10.3910, -75.4794),
    "BARRANQUILLA":     (10.9685, -74.7813),
    "TUNJA":            (5.5353, -73.3678),
    "PASTO":            (1.2136, -77.2811),
    "CUCUTA":           (7.8939, -72.5078),
    "IBAGUE":           (4.4389, -75.2322),
}

# ─────────────────────────────────────────────────────────────────
# GEOCODIFICACION (Nominatim - gratuito)
# ─────────────────────────────────────────────────────────────────

def geocodificar_municipio(municipio: str, departamento: str) -> tuple:
    """Geocodifica un municipio colombiano. Primero revisa cache local."""
    key = municipio.upper().strip()

    # 1. Buscar en diccionario precargado
    if key in COORDS_BASE:
        return COORDS_BASE[key]

    # 2. Llamar Nominatim
    query = f"{municipio}, {departamento}, Colombia"
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "co",
        "addressdetails": 0
    }
    headers = {"User-Agent": "CensoFerreteriasArgos/1.0 (educational-project)"}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        if resp.status_code == 200 and resp.json():
            r = resp.json()[0]
            lat, lon = float(r["lat"]), float(r["lon"])
            COORDS_BASE[key] = (lat, lon)  # guardar en cache
            return lat, lon
    except Exception:
        pass

    return None, None


def geocodificar_todos_municipios(df: pd.DataFrame) -> dict:
    """
    Geocodifica todos los municipios unicos del DataFrame.
    Retorna dict: municipio -> (lat, lon)
    """
    municipios_unicos = df[["municipio", "departamento"]].drop_duplicates()
    total = len(municipios_unicos)
    print(f"  Geocodificando {total} municipios unicos...")

    coords_mun = {}
    encontrados = 0

    for i, (_, row) in enumerate(municipios_unicos.iterrows()):
        mun = str(row["municipio"]).upper().strip()
        dep = str(row["departamento"]).upper().strip()

        lat, lon = geocodificar_municipio(mun, dep)

        if lat is not None:
            coords_mun[mun] = (lat, lon)
            encontrados += 1
            print(f"  [{i+1}/{total}] {mun}: ({lat:.4f}, {lon:.4f})")
        else:
            print(f"  [{i+1}/{total}] {mun}: NO ENCONTRADO")

        # Respetar rate limit Nominatim (1 req/seg)
        # Solo esperar si se hizo llamada real (no estaba en cache)
        if mun not in COORDS_BASE:
            time.sleep(1.1)

    print(f"  Municipios con coordenadas: {encontrados}/{total}")
    return coords_mun


# ─────────────────────────────────────────────────────────────────
# CONSTRUCCION DEL MAPA
# ─────────────────────────────────────────────────────────────────

def crear_mapa(df: pd.DataFrame) -> folium.Map:
    """Crea el mapa Folium interactivo con todos los marcadores."""

    # Obtener coordenadas de municipios
    print("\nObteniendo coordenadas de municipios...")
    coords_mun = geocodificar_todos_municipios(df)

    # Mapa base centrado en Colombia
    mapa = folium.Map(
        location=[5.5, -74.5],
        zoom_start=6,
        tiles="CartoDB positron",
        prefer_canvas=True
    )

    # Titulo del mapa
    titulo_html = """
    <div style="
        position: fixed; top: 12px; left: 50%; transform: translateX(-50%);
        z-index: 1000; background: white; padding: 10px 20px;
        border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        font-family: Arial, sans-serif; text-align: center; min-width: 300px;
    ">
        <b style="font-size: 15px; color: #2C3E50;">
            Censo Digital Ferreterias Colombia
        </b>
        <br>
        <span style="font-size: 12px; color: #7F8C8D;">
            Cementos Argos &mdash; Regiones Prioritarias &mdash; {total:,} ferreterias
        </span>
    </div>
    """.format(total=len(df))
    mapa.get_root().html.add_child(folium.Element(titulo_html))

    # ── Capa 1: Marcadores individuales (cluster) ────────────────
    cluster = MarkerCluster(
        name="Ferreterias (detalle)",
        options={
            "maxClusterRadius": 50,
            "disableClusteringAtZoom": 13
        }
    )

    marcadores = 0
    sin_coords  = 0
    random.seed(42)

    for _, row in df.iterrows():
        municipio    = str(row.get("municipio", "")).upper().strip()
        departamento = str(row.get("departamento", "")).upper().strip()
        nombre_rues  = str(row.get("nombre_rues", ""))
        nombre_com   = str(row.get("nombre_comercial", "") or row.get("nombre_comercial_maps", ""))
        correo       = str(row.get("correo_rues", ""))
        direccion    = str(row.get("direccion_comercial", ""))
        tamano       = str(row.get("tamano_empresa", ""))
        org          = str(row.get("org_juridica", ""))
        telefono     = str(row.get("telefono", ""))
        match_g      = str(row.get("match_google", ""))
        fuente       = str(row.get("fuente", "RUES"))

        # Nombre a mostrar: comercial si existe, si no razon social
        nombre_display = nombre_com if nombre_com and nombre_com != "nan" else nombre_rues

        # Obtener coordenadas
        lat = row.get("latitud", "")
        lon = row.get("longitud", "")

        if lat and lon and str(lat).replace(".", "").replace("-", "").isdigit():
            # Coordenadas reales de Apify
            coords = (float(lat), float(lon))
        elif municipio in coords_mun:
            # Coordenadas de municipio + dispersión aleatoria (radio ~1.5 km)
            base_lat, base_lon = coords_mun[municipio]
            coords = (
                base_lat + random.uniform(-0.015, 0.015),
                base_lon + random.uniform(-0.015, 0.015)
            )
        else:
            sin_coords += 1
            continue

        # Color por departamento
        color = COLORES_DEP.get(departamento, "#95A5A6")

        # Popup HTML
        icon_match = "✅" if match_g == "Si" else ("⚠️" if match_g == "Parcial" else "📋")
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; min-width: 220px; font-size: 13px;">
            <b style="font-size: 14px; color: #2C3E50;">{nombre_display[:55]}</b>
            <hr style="margin: 6px 0; border-color: #ECF0F1;">
            <table style="width:100%; border-collapse: collapse;">
                <tr><td style="color:#7F8C8D; width:30%">Direccion</td>
                    <td>{direccion[:50]}</td></tr>
                <tr><td style="color:#7F8C8D;">Ciudad</td>
                    <td>{municipio.title()}, {departamento.title()}</td></tr>
                <tr><td style="color:#7F8C8D;">Correo</td>
                    <td>{correo if correo and correo != 'nan' else '—'}</td></tr>
                <tr><td style="color:#7F8C8D;">Telefono</td>
                    <td>{telefono if telefono and telefono != 'nan' else '—'}</td></tr>
                <tr><td style="color:#7F8C8D;">Tamano</td>
                    <td>{tamano}</td></tr>
            </table>
            <hr style="margin: 6px 0; border-color: #ECF0F1;">
            <small style="color:#95A5A6;">
                {icon_match} Google Maps: {match_g} &nbsp;|&nbsp; Fuente: {fuente}
            </small>
        </div>
        """

        folium.CircleMarker(
            location=coords,
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            weight=1,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=nombre_display[:45]
        ).add_to(cluster)

        marcadores += 1

    cluster.add_to(mapa)

    # ── Capa 2: Mapa de calor ────────────────────────────────────
    heat_data = []
    for _, row in df.iterrows():
        mun = str(row.get("municipio", "")).upper().strip()
        dep = str(row.get("departamento", "")).upper().strip()
        lat = row.get("latitud", "")
        lon = row.get("longitud", "")

        if lat and lon and str(lat).replace(".", "").replace("-", "").isdigit():
            heat_data.append([float(lat), float(lon)])
        elif mun in coords_mun:
            base_lat, base_lon = coords_mun[mun]
            heat_data.append([
                base_lat + random.uniform(-0.008, 0.008),
                base_lon + random.uniform(-0.008, 0.008)
            ])

    HeatMap(
        heat_data,
        name="Mapa de Calor (densidad)",
        min_opacity=0.3,
        radius=15,
        blur=10,
        show=False  # desactivado por defecto, se activa desde el control de capas
    ).add_to(mapa)

    # ── Capa 3: Circulos por municipio (con conteo) ──────────────
    capa_municipios = folium.FeatureGroup(name="Conteo por municipio", show=False)

    conteo_mun = df.groupby(["municipio", "departamento"]).size().reset_index(name="count")

    for _, row in conteo_mun.iterrows():
        mun = str(row["municipio"]).upper().strip()
        dep = str(row["departamento"]).upper().strip()
        cnt = int(row["count"])

        if mun not in coords_mun:
            continue

        lat_m, lon_m = coords_mun[mun]
        color = COLORES_DEP.get(dep, "#95A5A6")
        radio = min(5 + cnt * 0.015, 25)  # radio proporcional al conteo

        folium.CircleMarker(
            location=(lat_m, lon_m),
            radius=radio,
            color=color,
            fill=True,
            fill_opacity=0.6,
            popup=f"<b>{mun.title()}</b><br>{dep.title()}<br><b>{cnt:,} ferreterias</b>",
            tooltip=f"{mun.title()}: {cnt:,}"
        ).add_to(capa_municipios)

    capa_municipios.add_to(mapa)

    # Control de capas
    folium.LayerControl(collapsed=False).add_to(mapa)

    # ── Leyenda ──────────────────────────────────────────────────
    leyenda_items = ""
    for dep, color in COLORES_DEP.items():
        cnt = len(df[df["departamento"] == dep])
        leyenda_items += (
            f'<div><span style="display:inline-block; width:12px; height:12px; '
            f'background:{color}; border-radius:50%; margin-right:6px;"></span>'
            f'{dep.title()} ({cnt:,})</div>'
        )

    leyenda_html = f"""
    <div style="
        position: fixed; bottom: 30px; right: 12px; z-index: 1000;
        background: white; padding: 12px 16px;
        border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif; font-size: 13px; min-width: 180px;
    ">
        <b style="color: #2C3E50;">Departamento</b>
        <hr style="margin: 6px 0; border-color: #ECF0F1;">
        {leyenda_items}
        <hr style="margin: 6px 0; border-color: #ECF0F1;">
        <small style="color: #95A5A6;">Total: {len(df):,} registros</small>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(leyenda_html))

    print(f"\n  Marcadores agregados: {marcadores:,}")
    print(f"  Sin coordenadas:      {sin_coords:,}")

    return mapa


# ─────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────

def main(archivo_entrada: str):
    print("=" * 65)
    print("MAPA V1 - FERRETERIAS COLOMBIA (Cementos Argos)")
    print(f"Fecha: {date.today()}")
    print("=" * 65)

    print(f"\nCargando '{archivo_entrada}'...")
    df = pd.read_excel(archivo_entrada)
    print(f"  Registros: {len(df):,}")

    # Estadisticas rapidas
    deps = df["departamento"].value_counts()
    print("\n  Distribucion por departamento:")
    for dep, n in deps.items():
        print(f"    {dep}: {n:,}")

    con_coords = df["latitud"].notna() & (df["latitud"] != "") if "latitud" in df.columns else pd.Series([False]*len(df))
    print(f"\n  Con coordenadas reales (Apify): {con_coords.sum():,}")
    print(f"  Sin coordenadas (usara municipio): {(~con_coords).sum():,}")

    print("\nGenerando mapa interactivo...")
    mapa = crear_mapa(df)

    mapa.save(ARCHIVO_SALIDA)
    print(f"\n[OK] Mapa guardado: '{ARCHIVO_SALIDA}'")
    print("     Abrir en el navegador (doble clic en el archivo).")
    print()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(description="Genera mapa interactivo de ferreterias")
    parser.add_argument(
        "--input",
        default=None,
        help="Archivo Excel de entrada (default: BD_Enriquecida.xlsx si existe, si no BD_Regiones_Prioritarias.xlsx)"
    )
    args = parser.parse_args()

    # Seleccionar archivo de entrada
    if args.input:
        entrada = args.input
    elif os.path.exists("BD_Enriquecida.xlsx"):
        entrada = "BD_Enriquecida.xlsx"
        print("[INFO] Usando BD_Enriquecida.xlsx (datos con Google Maps)")
    else:
        entrada = ARCHIVO_ENTRADA
        print("[INFO] Usando BD_Regiones_Prioritarias.xlsx (solo datos RUES)")

    if not os.path.exists(entrada):
        print(f"ERROR: No se encontro '{entrada}'")
        print("Ejecuta primero: python limpiar_datos.py")
        sys.exit(1)

    main(entrada)
