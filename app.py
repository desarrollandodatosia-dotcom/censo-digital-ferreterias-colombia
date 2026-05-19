# -*- coding: utf-8 -*-
"""
app.py - Censo Digital Ferreterias Colombia | Cementos Argos
Streamlit app con Dashboard, Mapa, Tabla y Agente IA (Gemini)

Ejecutar:
    streamlit run app.py
"""

import os
import io
import re
import subprocess
import sys
import functools
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# ─────────────────────────────────────────────────────────────────
# LOGO ARGOS — descarga, colorea a #c4d600 y embebe como base64
# ─────────────────────────────────────────────────────────────────
_ARGOS_LOGO_URL = "https://argos.co/wp-content/uploads/2021/01/logo-argos.png"
_ARGOS_GREEN = (196, 214, 0)  # #c4d600

@functools.lru_cache(maxsize=1)
def _logo_argos_pil():
    """Descarga y colorea el logo a #c4d600 para el favicon (pestaña)."""
    try:
        import requests
        from PIL import Image
        from io import BytesIO
        import numpy as np
        _h = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        ir = requests.get(_ARGOS_LOGO_URL, timeout=2, headers=_h)
        if ir.status_code == 200 and len(ir.content) > 100:
            img = Image.open(BytesIO(ir.content)).convert("RGBA")
            arr = np.array(img)
            # Reemplaza RGB de píxeles visibles (alpha > 50) por #c4d600
            mask = arr[:, :, 3] > 50
            arr[mask, 0] = _ARGOS_GREEN[0]
            arr[mask, 1] = _ARGOS_GREEN[1]
            arr[mask, 2] = _ARGOS_GREEN[2]
            return Image.fromarray(arr)
    except Exception:
        pass
    return None


@functools.lru_cache(maxsize=1)
def _logo_argos_b64():
    """Devuelve el logo coloreado en #c4d600 como data URL base64 para el header."""
    try:
        import base64
        from io import BytesIO
        img = _logo_argos_pil()
        if img:
            buf = BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            return f"data:image/png;base64,{b64}"
    except Exception:
        pass
    return None


# ─────────────────────────────────────────────────────────────────
# CONFIGURACION DE PAGINA
# ─────────────────────────────────────────────────────────────────
_page_icon = _logo_argos_pil() or "🏗️"
st.set_page_config(
    page_title="CEMANTIX",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────
# CSS — DISEÑO VISUAL COMPLETO
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base & Font ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"], * {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased !important;
}
.stApp {
    background: #f5f5f7 !important;
}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 48px !important;
    max-width: 1280px !important;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── Header (dark nav tile) ──────────────────────────────── */
.argos-header {
    background: #1d1d1f;
    padding: 20px 36px;
    border-radius: 18px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.header-title {
    color: #ffffff;
    font-size: 21px;
    font-weight: 600;
    letter-spacing: 0.2px;
    margin: 0 0 4px 0;
    line-height: 1.19;
}
.header-sub {
    color: rgba(255,255,255,0.50);
    font-size: 12px;
    font-weight: 400;
    letter-spacing: -0.12px;
    margin: 0;
}
.header-right { text-align: right; }
.header-badge {
    display: inline-block;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    color: rgba(255,255,255,0.75);
    font-size: 11px;
    font-weight: 400;
    padding: 4px 12px;
    border-radius: 9999px;
    letter-spacing: -0.08px;
    margin-bottom: 5px;
}
.header-date {
    color: rgba(255,255,255,0.28);
    font-size: 11px;
    letter-spacing: -0.08px;
}

/* ── Tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #ffffff !important;
    border-radius: 12px !important;
    padding: 5px 6px !important;
    gap: 2px !important;
    border: 1px solid #e0e0e0 !important;
    margin-top: 8px !important;
    margin-bottom: 24px !important;
    box-shadow: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 9px 20px !important;
    font-weight: 400 !important;
    font-size: 14px !important;
    letter-spacing: -0.224px !important;
    color: #6e6e73 !important;
    border: none !important;
    background: transparent !important;
    transition: color 0.15s !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #1d1d1f !important;
    background: #f5f5f7 !important;
}
.stTabs [aria-selected="true"] {
    background: #1d1d1f !important;
    color: #ffffff !important;
}
/* Fuerza texto blanco dentro del tab activo (supera la regla stMarkdownContainer p) */
.stTabs [aria-selected="true"] p,
.stTabs [aria-selected="true"] span,
.stTabs [aria-selected="true"] div,
.stTabs [aria-selected="true"] [data-testid="stMarkdownContainer"] p {
    color: #ffffff !important;
}
/* Hover sobre el tab activo no cambia el color de texto */
.stTabs [aria-selected="true"]:hover {
    background: #2c2c2e !important;
    color: #ffffff !important;
}
.stTabs [aria-selected="true"]:hover p,
.stTabs [aria-selected="true"]:hover span {
    color: #ffffff !important;
}
.stTabs [aria-selected="true"] {
    font-weight: 600 !important;
    box-shadow: none !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"]    { display: none !important; }

/* ── Section Titles ──────────────────────────────────────── */
.sec-title {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #1d1d1f;
    font-size: 17px;
    font-weight: 600;
    letter-spacing: -0.374px;
    line-height: 1.24;
    padding: 28px 0 14px 0;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 20px;
}

/* ── KPI Cards (store-utility-card) ──────────────────────── */
.kpi-wrap {
    background: #ffffff;
    border-radius: 18px;
    padding: 24px;
    height: 100%;
    min-height: 140px;
    position: relative;
    border: 1px solid #e0e0e0;
    transition: transform 0.15s;
}
.kpi-wrap:hover { transform: translateY(-1px); }
.kpi-wrap.blue, .kpi-wrap.yellow, .kpi-wrap.green,
.kpi-wrap.purple, .kpi-wrap.orange, .kpi-wrap.teal {
    border-top: none;
}
.kpi-icon  { font-size: 1.3rem; display:block; margin-bottom: 12px; }
.kpi-num   {
    font-size: 34px;
    font-weight: 600;
    color: #1d1d1f;
    letter-spacing: -0.374px;
    line-height: 1.0;
    display:block;
}
.kpi-lbl   {
    font-size: 14px;
    font-weight: 400;
    color: #6e6e73;
    letter-spacing: -0.224px;
    line-height: 1.43;
    display:block;
    margin: 6px 0 10px;
}
.kpi-badge {
    display: inline-block;
    font-size: 12px;
    font-weight: 400;
    letter-spacing: -0.12px;
    padding: 3px 10px;
    border-radius: 9999px;
    border: 1px solid #e0e0e0;
    background: #fafafc;
    color: #3a3a3c;
}
.kpi-badge.b-blue, .kpi-badge.b-green, .kpi-badge.b-yellow,
.kpi-badge.b-purple, .kpi-badge.b-orange, .kpi-badge.b-teal,
.kpi-badge.b-gray {
    background: #fafafc !important;
    color: #3a3a3c !important;
    border: 1px solid #e0e0e0 !important;
}
.kpi-cap   {
    font-size: 12px;
    color: #98989d;
    display:block;
    margin-top: 8px;
    letter-spacing: -0.12px;
    line-height: 1.3;
}

/* ── Stat Row ────────────────────────────────────────────── */
.stat-row {
    background: #ffffff;
    border-radius: 18px;
    padding: 16px 24px;
    display: flex;
    gap: 32px;
    align-items: center;
    margin-bottom: 20px;
    border: 1px solid #e0e0e0;
    flex-wrap: wrap;
}
.stat-item { text-align: center; }
.stat-num  {
    font-size: 21px;
    font-weight: 600;
    color: #1d1d1f;
    display:block;
    letter-spacing: 0.2px;
    line-height: 1.19;
}
.stat-lbl  {
    font-size: 12px;
    color: #98989d;
    letter-spacing: -0.12px;
    line-height: 1.0;
}

/* ── Filter Bar ──────────────────────────────────────────── */
.filter-bar {
    background: #ffffff;
    border-radius: 18px;
    padding: 20px 24px 10px;
    margin-bottom: 16px;
    border: 1px solid #e0e0e0;
}
.filter-label {
    font-size: 14px;
    font-weight: 600;
    color: #1d1d1f;
    letter-spacing: -0.224px;
    margin-bottom: 12px;
    display: block;
}

/* ── Download Button ─────────────────────────────────────── */
.stDownloadButton > button,
.stDownloadButton > button p,
.stDownloadButton > button span,
.stDownloadButton > button div {
    color: #ffffff !important;
}
.stDownloadButton > button {
    background: #1d1d1f !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9999px !important;
    padding: 11px 22px !important;
    font-weight: 400 !important;
    font-size: 17px !important;
    letter-spacing: -0.374px !important;
    box-shadow: none !important;
    transition: transform 0.15s !important;
}
.stDownloadButton > button:hover,
.stDownloadButton > button:hover p,
.stDownloadButton > button:hover span { background: #3a3a3c !important; color: #ffffff !important; }
.stDownloadButton > button:active { transform: scale(0.95) !important; }

/* ── Chat ────────────────────────────────────────────────── */
.chat-header-box {
    background: #1d1d1f;
    border-radius: 18px;
    padding: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 24px;
}
.chat-header-icon { font-size: 2rem; }
.chat-header-title {
    color: #ffffff;
    font-size: 21px;
    font-weight: 600;
    letter-spacing: 0.2px;
    margin: 0 0 4px;
    line-height: 1.19;
}
.chat-header-sub {
    color: rgba(255,255,255,0.50);
    font-size: 12px;
    margin: 0;
    letter-spacing: -0.12px;
}
.chat-welcome-wrap {
    text-align: center;
    padding: 48px 20px;
    background: #ffffff;
    border-radius: 18px;
    border: 1px solid #e0e0e0;
    margin-bottom: 16px;
}
.chat-welcome-icon { font-size: 2.4rem; margin-bottom: 12px; display:block; }
.chat-welcome-text {
    color: #6e6e73;
    font-size: 17px;
    line-height: 1.47;
    letter-spacing: -0.374px;
    margin-bottom: 24px;
}
.chat-examples-title {
    font-size: 12px;
    font-weight: 600;
    color: #98989d;
    letter-spacing: -0.12px;
    margin-bottom: 14px;
}

/* ── Buttons ─────────────────────────────────────────────── */
.stButton > button {
    border-radius: 9999px !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    letter-spacing: -0.224px !important;
    transition: transform 0.15s !important;
    border: 1px solid #e0e0e0 !important;
    background: #fafafc !important;
    color: #1d1d1f !important;
    padding: 8px 16px !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: #f5f5f7 !important;
    border-color: #d2d2d7 !important;
}
.stButton > button:active { transform: scale(0.95) !important; }

/* ── Metrics ─────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #ffffff;
    border-radius: 18px;
    padding: 24px !important;
    border: 1px solid #e0e0e0;
    box-shadow: none;
}

/* ── Dataframe ───────────────────────────────────────────── */
[data-testid="stDataFrame"] > div {
    border-radius: 18px !important;
    overflow: hidden !important;
    border: 1px solid #e0e0e0 !important;
    box-shadow: none !important;
}

/* ── Alerts ──────────────────────────────────────────────── */
.stAlert { border-radius: 12px !important; }

/* ── Spinner ─────────────────────────────────────────────── */
.stSpinner > div { border-color: #1d1d1f transparent transparent !important; }

/* ── Text visibility (fix Streamlit dark theme) ──────────── */
/* Forzar light color scheme a nivel de documento */
html { color-scheme: light !important; }

/* Texto nativo de Streamlit: markdown, labels, captions */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] em,
[data-testid="stMarkdownContainer"] a {
    color: #1d1d1f !important;
}
/* Nuestros tiles oscuros inyectados — inline !important gana sobre stylesheet !important */
/* (aplicado directamente en los atributos style de esos elementos) */

/* Widget labels */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
.stSelectbox label, .stMultiSelect label,
.stCheckbox label, .stNumberInput label,
.stTextInput label {
    color: #1d1d1f !important;
}
/* Chat messages */
[data-testid="stChatMessage"] {
    background: #ffffff !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 12px !important;
}
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessageContent"] li,
[data-testid="stChatMessageContent"] strong,
[data-testid="stChatMessageContent"] em,
[data-testid="stChatMessageContent"] * {
    color: #1d1d1f !important;
}
/* Expander */
[data-testid="stExpander"] summary span { color: #1d1d1f !important; }
/* Captions */
.stCaption, [data-testid="stCaption"] { color: #6e6e73 !important; }
/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    color: #1d1d1f !important;
    background: #ffffff !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 8px !important;
}
/* Dark tiles CSS classes — mayor especificidad que stMarkdownContainer */
.argos-header .header-title { color: #ffffff !important; }
.argos-header .header-sub   { color: rgba(255,255,255,0.50) !important; }
.argos-header .header-badge { color: rgba(255,255,255,0.75) !important; }
.argos-header .header-date  { color: rgba(255,255,255,0.28) !important; }
.chat-header-box .chat-header-title { color: #ffffff !important; }
.chat-header-box .chat-header-sub   { color: rgba(255,255,255,0.50) !important; }
.pipe-header .pipe-title    { color: #ffffff !important; }
.pipe-header .pipe-sub      { color: rgba(255,255,255,0.55) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# AUTENTICACION SUPABASE
# ─────────────────────────────────────────────────────────────────
def _supabase_login(email: str, password: str):
    """
    Autentica contra Supabase Auth usando requests (sin SDK).
    Retorna (user_email, access_token) o lanza Exception.
    """
    url = st.secrets.get("SUPABASE_URL", "") or os.environ.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "") or os.environ.get("SUPABASE_KEY", "")
    import requests as _req
    resp = _req.post(
        f"{url}/auth/v1/token?grant_type=password",
        headers={"apikey": key, "Content-Type": "application/json"},
        json={"email": email, "password": password},
        timeout=10,
    )
    if resp.status_code == 200:
        data = resp.json()
        return data.get("user", {}).get("email", email), data.get("access_token", "")
    # 400 = credenciales incorrectas
    raise Exception(resp.json().get("error_description", "Credenciales incorrectas"))


def _pantalla_login():
    _lb64 = _logo_argos_b64()
    logo_html = (
        f'<img src="{_lb64}" height="48" '
        f'style="object-fit:contain;margin-bottom:24px;display:block;margin-left:auto;margin-right:auto;" alt="Argos">'
        if _lb64 else '<div style="font-size:3rem;text-align:center;margin-bottom:20px;">🏗️</div>'
    )
    st.markdown(f"""
    <div style="max-width:400px;margin:64px auto 0;text-align:center;">
      {logo_html}
      <h1 style="font-size:28px;font-weight:700;color:#1d1d1f;
                 letter-spacing:-0.5px;margin:0 0 6px;line-height:1.2;">CEMANTIX</h1>
      <p style="color:#6e6e73;font-size:14px;margin:0 0 32px;letter-spacing:-0.2px;">
        Cementos Argos · Inteligencia de Mercado · EAFIT 2026
      </p>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        with st.form("login_form", clear_on_submit=False):
            st.markdown(
                '<p style="font-size:17px;font-weight:600;color:#1d1d1f;'
                'letter-spacing:-0.3px;margin-bottom:20px;text-align:center;">Iniciar sesión</p>',
                unsafe_allow_html=True,
            )
            email    = st.text_input("Correo electrónico", placeholder="usuario@argos.co")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Ingresar →", use_container_width=True, type="primary")

        if submitted:
            if not email or not password:
                st.error("Ingresa tu correo y contraseña.")
                return
            with st.spinner("Verificando credenciales..."):
                try:
                    user_email, token = _supabase_login(email, password)
                    st.session_state["auth_user"]  = user_email
                    st.session_state["auth_token"] = token
                    st.rerun()
                except Exception as e:
                    st.error(f"Acceso denegado: {e}")

    st.markdown(
        '<p style="text-align:center;color:#98989d;font-size:11px;margin-top:40px;">'
        'Acceso restringido — Solo personal autorizado Argos / EAFIT</p>',
        unsafe_allow_html=True,
    )


# Inicializar estado de autenticación
if "auth_user" not in st.session_state:
    st.session_state["auth_user"] = None

_supabase_activo = bool(
    (st.secrets.get("SUPABASE_KEY", "") or os.environ.get("SUPABASE_KEY", ""))
    and (st.secrets.get("SUPABASE_KEY", "PEGAR_ANON_KEY_AQUI") != "PEGAR_ANON_KEY_AQUI")
)

if _supabase_activo and not st.session_state["auth_user"]:
    _pantalla_login()
    st.stop()


# ─────────────────────────────────────────────────────────────────
# CARGA DE DATOS (con cache)
# ─────────────────────────────────────────────────────────────────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_GEO  = os.path.join(_SCRIPT_DIR, "BD_Geocodificada.xlsx")
RUTA_ENR  = os.path.join(_SCRIPT_DIR, "BD_Enriquecida.xlsx")
RUTA_MAPA = os.path.join(_SCRIPT_DIR, "mapa_v1.html")


def _sb_get_ferreterias_paginado(page_size: int = 1000, timeout: int = 30) -> pd.DataFrame:
    """
    Lee la tabla `ferreterias` desde Supabase con paginación por offset.
    Patrón equivalente a cruce_apify.py:_sb_leer_ferreterias (sin filtro tamano).
    Devuelve DataFrame vacío si Supabase no responde u ocurre algún error.
    """
    import requests as _req
    url = st.secrets.get("SUPABASE_URL", "") or os.environ.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "") or os.environ.get("SUPABASE_KEY", "")
    if not url or not key:
        return pd.DataFrame()
    headers = {
        "apikey":        key,
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "Range-Unit":    "items",
    }
    registros = []
    offset = 0
    while True:
        try:
            resp = _req.get(
                f"{url}/rest/v1/ferreterias",
                headers=headers,
                params={"select": "*", "limit": page_size, "offset": offset},
                timeout=timeout,
            )
        except Exception:
            return pd.DataFrame()
        if not resp.ok:
            return pd.DataFrame()
        lote = resp.json()
        if not lote:
            break
        registros.extend(lote)
        if len(lote) < page_size:
            break
        offset += page_size
    return pd.DataFrame(registros) if registros else pd.DataFrame()


@st.cache_data(ttl=300)
def cargar_datos():
    """
    Fuente preferida: Supabase tabla `ferreterias`. Fallback automático a Excel local.
    df_geo: todas las filas con lat/lon (universo geocodificado).
    df_enr: subset donde match_google IS NOT NULL (enriquecidas con Google Maps).
    """
    df_geo = pd.DataFrame()
    df_enr = pd.DataFrame()
    fuente = "excel"

    if _supabase_activo:
        df_sb = _sb_get_ferreterias_paginado()
        if len(df_sb) > 0:
            df_geo = df_sb
            if "match_google" in df_sb.columns:
                df_enr = df_sb[df_sb["match_google"].notna() & (df_sb["match_google"].astype(str).str.strip() != "")].copy()
            else:
                df_enr = pd.DataFrame()
            fuente = "supabase"

    if fuente == "excel":
        if os.path.exists(RUTA_GEO):
            df_geo = pd.read_excel(RUTA_GEO, engine="openpyxl")
        elif os.path.exists(RUTA_ENR):
            df_geo = pd.read_excel(RUTA_ENR, engine="openpyxl")
        if os.path.exists(RUTA_ENR):
            df_enr = pd.read_excel(RUTA_ENR, engine="openpyxl")

    return df_geo, df_enr


with st.spinner("Cargando datos del censo..."):
    df_geo, df_enr = cargar_datos()
TIENE_GEO = len(df_geo) > 0
TIENE_ENR = len(df_enr) > 0


# ─────────────────────────────────────────────────────────────────
# HELPER: tarjeta KPI en HTML
# ─────────────────────────────────────────────────────────────────
def kpi(icon, number, label, badge="", badge_style="b-blue", caption="", color="blue"):
    badge_html = (
        f'<span class="kpi-badge {badge_style}">{badge}</span>'
    ) if badge else ""
    cap_html = (
        f'<span class="kpi-cap">{caption}</span>'
    ) if caption else ""
    return f"""
<div class="kpi-wrap {color}">
  <span class="kpi-icon">{icon}</span>
  <span class="kpi-num">{number}</span>
  <span class="kpi-lbl">{label}</span>
  {badge_html}
  {cap_html}
</div>
"""


# ─────────────────────────────────────────────────────────────────
# RESPUESTA SIN IA (fallback)
# ─────────────────────────────────────────────────────────────────
def _respuesta_sin_ia(pregunta: str, df_geo: pd.DataFrame, df_enr: pd.DataFrame) -> str:
    preg = pregunta.lower()
    if "cuántas" in preg or "cuantas" in preg or "total" in preg:
        if "antioquia" in preg and len(df_geo) > 0 and "departamento" in df_geo.columns:
            n = (df_geo["departamento"] == "ANTIOQUIA").sum()
            return f"Hay **{n:,}** ferreterías en Antioquia. Configura Gemini API para análisis detallados."
        if ("bogotá" in preg or "bogota" in preg) and len(df_geo) > 0 and "departamento" in df_geo.columns:
            n = (df_geo["departamento"] == "BOGOTA").sum()
            return f"Hay **{n:,}** ferreterías en Bogotá."
        if len(df_geo) > 0:
            return f"El censo contiene **{len(df_geo):,}** ferreterías en las regiones prioritarias de Argos."
    if "rating" in preg or "calificaci" in preg:
        if len(df_enr) > 0 and "calificacion_google" in df_enr.columns:
            rating = pd.to_numeric(df_enr["calificacion_google"], errors="coerce").mean()
            if not pd.isna(rating):
                return f"Rating promedio de ferreterías validadas: **{rating:.2f}/5.0** según Google Maps."
    if "teléfono" in preg or "telefono" in preg:
        if len(df_enr) > 0 and "telefono" in df_enr.columns:
            n = df_enr["telefono"].apply(lambda x: str(x).strip() not in ("", "nan", "None")).sum()
            return f"**{n}** ferreterías tienen teléfono recuperado automáticamente vía Google Maps."
    return (
        "Para responder con el Agente IA, configura tu API key gratuita de Gemini:  \n"
        "`set GEMINI_API_KEY=AIza...` y reinicia la app.  \n\n"
        f"Datos disponibles: **{len(df_geo):,}** ferreterías geocodificadas | "
        f"**{len(df_enr):,}** enriquecidas con Google Maps."
    )


# ─────────────────────────────────────────────────────────────────
# HEADER PRINCIPAL
# ─────────────────────────────────────────────────────────────────
hoy = date.today().strftime("%d %b %Y")
_logo_b64 = _logo_argos_b64()
_logo_html = (
    f'<img src="{_logo_b64}" height="40" '
    f'style="object-fit:contain;display:block;max-width:130px;" alt="Argos">'
    if _logo_b64 else
    '<span style="font-size:1.8rem;">🏗️</span>'
)

# Usuario activo (si Supabase está activo)
_user_email = st.session_state.get("auth_user", "")
_user_badge = (
    f'<span class="header-badge" style="margin-right:8px;">👤 {_user_email}</span>'
    if _user_email else ""
)

st.markdown(f"""
<div class="argos-header">
  <div style="display:flex;align-items:center;gap:18px;">
    {_logo_html}
    <div>
      <p class="header-title">CEMANTIX</p>
      <p class="header-sub">Cementos Argos · Inteligencia de Mercado · EAFIT 2026</p>
    </div>
  </div>
  <div class="header-right">
    {_user_badge}
    <span class="header-date">Actualizado {hoy}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Botón de cerrar sesión (solo si Supabase activo y usuario logueado)
if _supabase_activo and _user_email:
    _c_logout = st.columns([8, 1])[1]
    with _c_logout:
        if st.button("Salir", key="logout_btn"):
            st.session_state["auth_user"]  = None
            st.session_state["auth_token"] = None
            st.rerun()

# ─────────────────────────────────────────────────────────────────
# TABS PRINCIPALES
# ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    ["📊  Dashboard", "🗺️  Mapa Interactivo", "📋  Ferreterías", "🤖  Agente IA", "⚙️  Pipeline Apify", "📧  Correos Cemento", "📥  Carga RUES"]
)

# ══════════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD
# ══════════════════════════════════════════════════════════════════
with tab1:

    # ── Cálculos ──────────────────────────────────────────────────
    total_nacional = 34_133
    total_prio     = len(df_geo) if TIENE_GEO else 14_642
    tasa_depuracion = round(total_prio / total_nacional * 100, 1)

    if TIENE_GEO and "precision_geocode" in df_geo.columns:
        gps_exacto = (df_geo["precision_geocode"] == "direccion").sum()
        pct_gps    = round(gps_exacto / max(total_prio, 1) * 100, 1)
    else:
        gps_exacto = 0; pct_gps = 0.0

    if TIENE_GEO and "precision_geocode" in df_geo.columns:
        sin_gps   = df_geo["latitud"].apply(lambda x: str(x).strip() in ("", "nan", "None")).sum()
        indice_geo = round((total_prio - sin_gps) / max(total_prio, 1) * 100, 1)
    else:
        indice_geo = 0.0

    if TIENE_ENR:
        total_enr = len(df_enr)
        def _no_vacio(col):
            if col not in df_enr.columns: return 0
            return df_enr[col].apply(lambda x: str(x).strip() not in ("", "nan", "None")).sum()
        n_telefonos = _no_vacio("telefono")
        n_webs      = _no_vacio("pagina_web")
        n_match_si  = (df_enr.get("match_google", pd.Series()) == "Si").sum()
    else:
        total_enr = n_telefonos = n_webs = n_match_si = 0

    if TIENE_ENR and "validacion_metodo" in df_enr.columns:
        n_gemini = (df_enr["validacion_metodo"] == "ia_gemini").sum()
    else:
        n_gemini = 0

    if TIENE_GEO and "tamano_empresa" in df_geo.columns:
        n_grandes  = (df_geo["tamano_empresa"] == "GRANDE").sum()
        n_medianas = (df_geo["tamano_empresa"] == "MEDIANA").sum()
        n_total_seg = len(df_geo)
    else:
        n_grandes = n_medianas = n_total_seg = 0

    if TIENE_ENR and "categoria_google" in df_enr.columns:
        n_cemento_cat = df_enr["categoria_google"].apply(
            lambda x: "material" in str(x).lower() or "construcci" in str(x).lower()
        ).sum()
    else:
        n_cemento_cat = 0
    n_cemento_est = n_grandes + n_cemento_cat

    if TIENE_ENR and "calificacion_google" in df_enr.columns:
        rating_num  = pd.to_numeric(df_enr["calificacion_google"], errors="coerce")
        rating_prom = round(rating_num.mean(), 2) if not rating_num.isna().all() else 0.0
    else:
        rating_prom = 0.0

    # ── Fila 1: Data Health ────────────────────────────────────────
    st.markdown('<div class="sec-title">📌 &nbsp; Data Health — Calidad del Dato</div>',
                unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi("🇨🇴", f"{total_nacional:,}", "Registros RUES Nacionales",
                        badge="Fuente oficial", badge_style="b-gray",
                        caption="Total nacional procesado del RUES"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi("🎯", f"{total_prio:,}", "Ferreterías Regiones Argos",
                        badge=f"{tasa_depuracion}% del total", badge_style="b-blue",
                        caption="Bogotá · Antioquia · Cundinamarca · Eje Cafetero",
                        color="blue"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi("📍", f"{gps_exacto:,}", "Con GPS Exacto (Dirección)",
                        badge=f"{pct_gps}% cobertura", badge_style="b-green",
                        caption="Geocodificados a nivel de dirección",
                        color="green"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi("🌐", f"{indice_geo}%", "Índice Veracidad Geográfica",
                        badge="Cobertura GPS", badge_style="b-blue",
                        caption="% con coordenadas verificadas"), unsafe_allow_html=True)

    # ── Fila 2: Enriquecimiento ────────────────────────────────────
    st.markdown('<div class="sec-title">🔍 &nbsp; Enriquecimiento IA — Datos Recuperados Automáticamente</div>',
                unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.markdown(kpi("🗂️", f"{total_enr:,}", "Ferreterías Enriquecidas",
                        badge="Google Maps + RUES", badge_style="b-blue",
                        caption="Procesadas con IA (MEDIANA + GRANDE)"), unsafe_allow_html=True)
    with c6:
        pct_tel = round(n_telefonos / max(total_enr, 1) * 100)
        st.markdown(kpi("📞", f"{n_telefonos:,}", "Teléfonos Recuperados por IA",
                        badge=f"{pct_tel}% cobertura", badge_style="b-green",
                        caption="No estaban en el RUES — hallados en Google Maps",
                        color="green"), unsafe_allow_html=True)
    with c7:
        pct_web = round(n_webs / max(total_enr, 1) * 100)
        st.markdown(kpi("🌍", f"{n_webs:,}", "Sitios Web Identificados",
                        badge=f"{pct_web}% cobertura", badge_style="b-purple",
                        caption="URLs verificadas automáticamente",
                        color="purple"), unsafe_allow_html=True)
    with c8:
        pct_match = round(n_match_si / max(total_enr, 1) * 100)
        st.markdown(kpi("✅", f"{n_match_si:,}", "Match Confirmado IA + GPS",
                        badge=f"{pct_match}% precisión", badge_style="b-green",
                        caption="Cascada: distancia → categoría → Gemini",
                        color="green"), unsafe_allow_html=True)

    # ── Fila 3: Inferencia IA ──────────────────────────────────────
    st.markdown('<div class="sec-title">🧠 &nbsp; Inferencia IA — Clasificación Automática</div>',
                unsafe_allow_html=True)
    c9, c10, c11, c12 = st.columns(4)
    with c9:
        st.markdown(kpi("🤖", f"{n_gemini:,}", "Validados por IA Gemini",
                        badge="Casos ambiguos resueltos", badge_style="b-purple",
                        caption="FuzzyWuzzy 30-85% → Gemini decide automáticamente",
                        color="purple"), unsafe_allow_html=True)
    with c10:
        st.markdown(kpi("📊", f"{n_total_seg:,}", "Segmentados Automáticamente",
                        badge="100% del universo", badge_style="b-blue",
                        caption=f"Grande: {n_grandes:,}  ·  Mediana: {n_medianas:,}"), unsafe_allow_html=True)
    with c11:
        st.markdown(kpi("🏭", f"~{n_cemento_est:,}", "Potenciales Vendedoras Cemento",
                        badge="Inferencia IA por cat + tamaño", badge_style="b-orange",
                        caption="Alta probabilidad de comercializar cemento Argos",
                        color="orange"), unsafe_allow_html=True)
    with c12:
        st.markdown(kpi("⭐", f"{rating_prom}/5.0", "Rating Promedio Sector",
                        badge="Google Maps", badge_style="b-yellow",
                        caption="Calificación promedio de ferreterías validadas",
                        color="yellow"), unsafe_allow_html=True)

    # ── Gráficas ───────────────────────────────────────────────────
    st.markdown('<div class="sec-title">📈 &nbsp; Distribución del Universo</div>',
                unsafe_allow_html=True)
    gc1, gc2 = st.columns(2)

    with gc1:
        if TIENE_GEO and "departamento" in df_geo.columns:
            dep_count = df_geo["departamento"].value_counts().reset_index()
            dep_count.columns = ["Departamento", "Ferreterías"]
            fig_dep = px.bar(
                dep_count, x="Ferreterías", y="Departamento", orientation="h",
                title="Ferreterías por Departamento",
                color="Ferreterías",
                color_continuous_scale=["#a7e8e7", "#071d49"],
            )
            fig_dep.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                yaxis={"categoryorder": "total ascending"},
                showlegend=False, coloraxis_showscale=False,
                margin=dict(l=0, r=10, t=44, b=10), height=320,
                font=dict(family="Inter", size=12),
                title_font=dict(size=14, color="#071d49", family="Inter"),
            )
            fig_dep.update_traces(marker_line_width=0)
            st.plotly_chart(fig_dep, use_container_width=True)
        else:
            st.info("Carga BD_Geocodificada.xlsx para ver este gráfico")

    with gc2:
        if TIENE_GEO and "tamano_empresa" in df_geo.columns:
            tam_count = df_geo["tamano_empresa"].value_counts().reset_index()
            tam_count.columns = ["Segmento", "Cantidad"]
            fig_tam = px.pie(
                tam_count, names="Segmento", values="Cantidad",
                title="Segmentación por Tamaño de Empresa",
                color_discrete_sequence=["#071d49", "#c4d600", "#0db6b4", "#6b7280"],
                hole=0.42,
            )
            fig_tam.update_layout(
                paper_bgcolor="white",
                margin=dict(l=10, r=10, t=44, b=10), height=320,
                font=dict(family="Inter", size=12),
                title_font=dict(size=14, color="#071d49", family="Inter"),
                legend=dict(orientation="v", x=1.0, y=0.5),
            )
            fig_tam.update_traces(textinfo="label+percent", textfont_size=12)
            st.plotly_chart(fig_tam, use_container_width=True)
        else:
            st.info("Carga BD_Geocodificada.xlsx para ver este gráfico")

    if TIENE_GEO and "municipio" in df_geo.columns:
        st.markdown('<div class="sec-title">🏙️ &nbsp; Top 10 Ciudades por Densidad</div>',
                    unsafe_allow_html=True)
        top_mun = df_geo["municipio"].value_counts().head(10).reset_index()
        top_mun.columns = ["Municipio", "Ferreterías"]
        fig_top = px.bar(
            top_mun, x="Municipio", y="Ferreterías",
            title="Top 10 Municipios por Número de Ferreterías",
            color="Ferreterías",
            color_continuous_scale=["#a7e8e7", "#071d49"],
            text="Ferreterías",
        )
        fig_top.update_traces(textposition="outside", marker_line_width=0)
        fig_top.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            showlegend=False, coloraxis_showscale=False,
            margin=dict(l=10, r=10, t=44, b=10), height=340,
            font=dict(family="Inter", size=12),
            title_font=dict(size=14, color="#071d49", family="Inter"),
            xaxis_title="", yaxis_title="Ferreterías",
        )
        st.plotly_chart(fig_top, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
# TAB 2: MAPA INTERACTIVO
# ══════════════════════════════════════════════════════════════════
with tab2:

    # Stat row resumen
    total_pts   = len(df_geo) if TIENE_GEO else 14_642
    pts_con_gps = 0
    if TIENE_GEO and "latitud" in df_geo.columns:
        pts_con_gps = pd.to_numeric(df_geo["latitud"], errors="coerce").notna().sum()

    st.markdown(f"""
<div class="stat-row">
  <div class="stat-item">
    <span class="stat-num">🗺️</span>
    <span class="stat-lbl">Mapa Interactivo</span>
  </div>
  <div style="width:1px;background:#e0e0e0;height:40px;"></div>
  <div class="stat-item">
    <span class="stat-num">{total_pts:,}</span>
    <span class="stat-lbl">Ferreterías mapeadas</span>
  </div>
  <div class="stat-item">
    <span class="stat-num">{pts_con_gps:,}</span>
    <span class="stat-lbl">Con GPS verificado</span>
  </div>
  <div class="stat-item">
    <span class="stat-num">3</span>
    <span class="stat-lbl">Capas de visualización</span>
  </div>
  <div style="margin-left:auto;font-size:0.78rem;color:#9ca3af;">
    Marcadores · Mapa de Calor · Conteo Municipal &nbsp;→&nbsp; usa el ícono de capas (arriba derecha del mapa)
  </div>
</div>
""", unsafe_allow_html=True)

    if not TIENE_GEO:
        st.warning("No hay datos geocodificados. Verifica BD_Geocodificada.xlsx")
        st.code("python mapa_v1.py", language="bash")
    else:
        import folium
        from folium.plugins import MarkerCluster, HeatMap, FastMarkerCluster
        from streamlit_folium import st_folium

        _COLORES_DEP = {
            "BOGOTA": "#071d49", "BOGOTA D.C.": "#071d49",
            "ANTIOQUIA": "#0db6b4", "CUNDINAMARCA": "#c4d600",
            "RISARALDA": "#E67E22", "CALDAS": "#9B59B6", "QUINDIO": "#3498DB",
        }

        # Prepara coords una sola vez
        @st.cache_data(ttl=600, show_spinner=False)
        def _prep_coords(path):
            _d = pd.read_excel(path, engine="openpyxl",
                               usecols=lambda c: c in [
                                   "nombre_rues", "municipio", "departamento",
                                   "tamano_empresa", "precision_geocode", "latitud", "longitud"
                               ])
            _d["_lat"] = pd.to_numeric(_d["latitud"], errors="coerce")
            _d["_lon"] = pd.to_numeric(_d["longitud"], errors="coerce")
            return _d.dropna(subset=["_lat", "_lon"]).reset_index(drop=True)

        df_coords = _prep_coords(RUTA_GEO)

        # ── Filtros ────────────────────────────────────────────────
        fcm1, fcm2, fcm3 = st.columns([3, 3, 2])
        with fcm1:
            deps_all = sorted(df_coords["departamento"].dropna().unique().tolist()) \
                if "departamento" in df_coords.columns else []
            sel_deps_m = st.multiselect("Departamento", deps_all,
                                        placeholder="Todos los departamentos", key="mapa_dep_sel")
        with fcm2:
            tams_all = sorted(df_coords["tamano_empresa"].dropna().unique().tolist()) \
                if "tamano_empresa" in df_coords.columns else []
            sel_tams_m = st.multiselect("Tamaño empresa", tams_all,
                                        placeholder="Todos", key="mapa_tam_sel")
        with fcm3:
            modo_calor = st.toggle("🌡️ Mapa de calor", value=False, key="mapa_calor")

        # Aplica filtros
        df_vis = df_coords.copy()
        if sel_deps_m:
            df_vis = df_vis[df_vis["departamento"].isin(sel_deps_m)]
        if sel_tams_m:
            df_vis = df_vis[df_vis["tamano_empresa"].isin(sel_tams_m)]

        n_vis = len(df_vis)
        st.caption(f"Mostrando **{n_vis:,}** ferreterías con GPS verificado")

        # ── Construir mapa Folium ──────────────────────────────────
        m = folium.Map(
            location=[5.5, -74.5], zoom_start=6,
            tiles="CartoDB positron", prefer_canvas=True
        )

        if modo_calor:
            HeatMap(
                df_vis[["_lat", "_lon"]].values.tolist(),
                radius=14, blur=12, min_opacity=0.3
            ).add_to(m)

        elif n_vis > 2500:
            # FastMarkerCluster: solo pasa coords, sin objetos Python por marcador
            FastMarkerCluster(
                df_vis[["_lat", "_lon"]].values.tolist(),
                name="Ferreterías"
            ).add_to(m)
            st.caption(
                f"Vista rápida ({n_vis:,} puntos). "
                "Filtra por departamento para ver marcadores con color y popup."
            )

        else:
            # CircleMarker con color por departamento y popup completo
            cluster = MarkerCluster(
                name="Ferreterías",
                options={"maxClusterRadius": 50, "disableClusteringAtZoom": 14}
            )
            for _, row in df_vis.iterrows():
                dep   = str(row.get("departamento", "")).upper().strip()
                color = _COLORES_DEP.get(dep, "#95A5A6")
                nombre = str(row.get("nombre_rues", ""))[:55]
                ciudad = str(row.get("municipio", "")).title()
                tamano = str(row.get("tamano_empresa", ""))
                prec   = str(row.get("precision_geocode", ""))
                folium.CircleMarker(
                    location=(row["_lat"], row["_lon"]),
                    radius=5, color=color, fill=True,
                    fill_color=color, fill_opacity=0.75, weight=1,
                    tooltip=nombre,
                    popup=folium.Popup(
                        f"<b>{nombre}</b><br>"
                        f"{ciudad} · {dep.title()}<br>"
                        f"{tamano} · GPS: {prec}",
                        max_width=260
                    )
                ).add_to(cluster)
            cluster.add_to(m)

        folium.LayerControl(collapsed=True).add_to(m)
        st_folium(m, height=580, use_container_width=True, returned_objects=[])


# ══════════════════════════════════════════════════════════════════
# TAB 3: TABLA DE FERRETERIAS
# ══════════════════════════════════════════════════════════════════
with tab3:

    df_tabla = df_enr.copy() if TIENE_ENR else (df_geo.copy() if TIENE_GEO else pd.DataFrame())

    if len(df_tabla) == 0:
        st.warning("No hay datos disponibles. Verifica que existan BD_Geocodificada.xlsx o BD_Enriquecida.xlsx")
    else:
        # Filtros en panel estilizado
        st.markdown('<div class="filter-bar"><span class="filter-label">🔍 Filtros de búsqueda</span>',
                    unsafe_allow_html=True)
        fcol1, fcol2, fcol3, fcol4 = st.columns([2, 2, 2, 2])

        with fcol1:
            if "departamento" in df_tabla.columns:
                deps    = sorted(df_tabla["departamento"].dropna().unique())
                sel_dep = st.multiselect("Departamento", deps, placeholder="Todos los departamentos")
            else:
                sel_dep = []
        with fcol2:
            if "tamano_empresa" in df_tabla.columns:
                tam_opts = sorted(df_tabla["tamano_empresa"].dropna().unique())
                sel_tam  = st.multiselect("Tamaño empresa", tam_opts, placeholder="Todos los tamaños")
            else:
                sel_tam = []
        with fcol3:
            if "match_google" in df_tabla.columns:
                match_opts = sorted(df_tabla["match_google"].dropna().unique())
                sel_match  = st.multiselect("Validación Google", match_opts, placeholder="Todos")
            else:
                sel_match = []
        with fcol4:
            st.markdown("<br>", unsafe_allow_html=True)
            solo_con_tel = st.checkbox("Solo con teléfono registrado")

        st.markdown('</div>', unsafe_allow_html=True)

        # Aplicar filtros
        df_filt = df_tabla.copy()
        if sel_dep:
            df_filt = df_filt[df_filt["departamento"].isin(sel_dep)]
        if sel_tam:
            df_filt = df_filt[df_filt["tamano_empresa"].isin(sel_tam)]
        if sel_match and "match_google" in df_filt.columns:
            df_filt = df_filt[df_filt["match_google"].isin(sel_match)]
        if solo_con_tel and "telefono" in df_filt.columns:
            df_filt = df_filt[
                df_filt["telefono"].apply(lambda x: str(x).strip() not in ("", "nan", "None"))
            ]

        # Conteo resultado
        rcol1, rcol2 = st.columns([3, 1])
        with rcol1:
            st.markdown(
                f"<span style='font-size:0.83rem;color:#6b7280;font-weight:600;'>"
                f"Mostrando <span style='color:#071d49;'>{len(df_filt):,}</span>"
                f" de {len(df_tabla):,} registros</span>",
                unsafe_allow_html=True,
            )

        # Columnas visibles
        cols_mostrar = [c for c in [
            "nombre_rues", "nombre_comercial", "nombre_comercial_maps",
            "municipio", "departamento", "tamano_empresa",
            "telefono", "pagina_web", "calificacion_google",
            "match_google", "validacion_metodo", "score_fuzzy",
            "latitud", "longitud", "fuente",
        ] if c in df_filt.columns]

        st.dataframe(
            df_filt[cols_mostrar].reset_index(drop=True),
            use_container_width=True,
            height=420,
        )

        # Descarga
        buf = io.BytesIO()
        df_filt[cols_mostrar].to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        st.download_button(
            label=f"⬇️  Descargar Excel — {len(df_filt):,} registros",
            data=buf,
            file_name=f"ferreterias_filtradas_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


# ══════════════════════════════════════════════════════════════════
# TAB 4: AGENTE IA (RAG)
# ══════════════════════════════════════════════════════════════════
with tab4:

    # Header del agente
    st.markdown("""
<div class="chat-header-box">
  <div class="chat-header-icon">🤖</div>
  <div>
    <p class="chat-header-title">Agente de Inteligencia de Mercado</p>
    <p class="chat-header-sub">Consulta el censo en lenguaje natural · Powered by Gemini 2.5 Flash</p>
  </div>
</div>
""", unsafe_allow_html=True)

    # API key y cliente Gemini
    api_key = st.secrets.get("GEMINI_API_KEY", "") or os.environ.get("GEMINI_API_KEY", "")
    gemini_ok     = False
    gemini_client = None
    _GEMINI_MODEL = "models/gemini-2.5-flash"

    if api_key:
        try:
            from google import genai as _genai
            gemini_client = _genai.Client(api_key=api_key)
            gemini_ok = True
            st.success("✅ Agente IA activo — Gemini 2.5 Flash conectado")
        except ImportError:
            st.warning("Instala el SDK: `pip install google-genai` y reinicia la app.")
        except Exception as e:
            err = str(e)
            if "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
                st.warning(
                    "⚠️ **API key sin cuota free tier.** "
                    "Obtén una key válida en [aistudio.google.com/apikey](https://aistudio.google.com/apikey) "
                    "(gratis, sin tarjeta). Actualiza `.streamlit/secrets.toml` y reinicia.  \n\n"
                    "_Mientras tanto el agente responde con análisis básico de los datos._"
                )
            elif "expired" in err.lower() or "INVALID" in err:
                st.warning(
                    "⚠️ **API key expirada.** Genera una nueva en "
                    "[aistudio.google.com/apikey](https://aistudio.google.com/apikey)"
                )
            else:
                st.warning(f"Error Gemini: {err[:120]}")
    else:
        st.info(
            "💡 Para activar el Agente IA: obtén tu key gratuita en "
            "[aistudio.google.com/apikey](https://aistudio.google.com/apikey) "
            "y agrégala en `.streamlit/secrets.toml`"
        )

    # Contexto del DataFrame para el agente
    def generar_contexto_agente():
        lineas = [
            f"CENSO DIGITAL FERRETERÍAS COLOMBIA — Cementos Argos ({date.today()})",
            "=" * 60,
        ]
        if TIENE_GEO:
            lineas += [
                f"Total ferreterías regiones prioritarias: {len(df_geo):,}",
                "Regiones: Bogotá, Antioquia, Cundinamarca, Risaralda, Caldas, Quindío",
                "",
                "DISTRIBUCIÓN POR DEPARTAMENTO:",
                df_geo["departamento"].value_counts().to_string() if "departamento" in df_geo.columns else "N/A",
                "",
                "DISTRIBUCIÓN POR TAMAÑO:",
                df_geo["tamano_empresa"].value_counts().to_string() if "tamano_empresa" in df_geo.columns else "N/A",
            ]
        if TIENE_ENR:
            def _nv(col):
                if col not in df_enr.columns: return 0
                return df_enr[col].apply(lambda x: str(x).strip() not in ("", "nan", "None")).sum()
            rating_n = pd.to_numeric(df_enr.get("calificacion_google", pd.Series()), errors="coerce")
            lineas += [
                "",
                f"ENRIQUECIMIENTO GOOGLE MAPS ({len(df_enr)} ferreterías procesadas):",
                f"  Match Si: {(df_enr.get('match_google', pd.Series()) == 'Si').sum()}",
                f"  Con teléfono: {_nv('telefono')}",
                f"  Con sitio web: {_nv('pagina_web')}",
                f"  Rating promedio: {rating_n.mean():.2f}/5.0" if not rating_n.isna().all() else "  Rating: N/D",
            ]
            if "municipio" in df_enr.columns:
                lineas += ["", "TOP 10 MUNICIPIOS (enriquecidos):",
                           df_enr["municipio"].value_counts().head(10).to_string()]

            # Registros individuales completos para respuestas específicas
            cols_show = [c for c in [
                "nombre_rues", "nombre_comercial", "municipio", "departamento",
                "tamano_empresa", "telefono", "pagina_web", "calificacion_google",
                "match_google", "vende_cemento", "correo_rues", "direccion_comercial",
                "categoria_google", "score_fuzzy"
            ] if c in df_enr.columns]
            lineas += ["", "REGISTROS INDIVIDUALES DE LAS 178 FERRETERÍAS ENRIQUECIDAS:"]
            for _, r in df_enr.iterrows():
                fila = " | ".join(
                    f"{c}={str(r[c]).strip()}"
                    for c in cols_show
                    if str(r.get(c, "")).strip() not in ("", "nan", "None", "NaN")
                )
                if fila:
                    lineas.append(f"  - {fila}")
        return "\n".join(lineas)

    contexto_bd = generar_contexto_agente()

    # Historial de chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Mostrar historial
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="🏗️" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Estado vacío — bienvenida y ejemplos
    if not st.session_state.chat_history:
        st.markdown("""
<div class="chat-welcome-wrap">
  <span class="chat-welcome-icon">💬</span>
  <p class="chat-welcome-text">
    Haz una pregunta de negocio sobre las <strong>14,642 ferreterías</strong> del censo.<br>
    El agente analiza los datos y responde con insights relevantes para Argos.
  </p>
  <p class="chat-examples-title">Preguntas de ejemplo</p>
</div>
""", unsafe_allow_html=True)

        ejemplos = [
            "¿Cuántas ferreterías grandes hay en Antioquia?",
            "¿Cuál es el rating promedio de ferreterías en Bogotá?",
            "¿Cuántas ferreterías tienen teléfono y sitio web?",
            "¿Qué porcentaje de ferreterías validamos con IA?",
        ]
        cols_ej = st.columns(2)
        for j, ej in enumerate(ejemplos):
            with cols_ej[j % 2]:
                if st.button(f"💬  {ej}", key=f"ej_{j}", use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": ej})
                    st.rerun()

    # Input de chat
    pregunta = st.chat_input("Escribe tu consulta... ej: ¿Cuántas ferreterías en Medellín tienen teléfono?")

    if pregunta:
        st.session_state.chat_history.append({"role": "user", "content": pregunta})

        if gemini_ok and gemini_client:
            prompt_sistema = (
                "Eres el Asistente de Inteligencia de Mercado de Cementos Argos. "
                "Tienes acceso COMPLETO a un censo digital de ferreterías en Colombia con registros individuales. "
                "REGLAS CRÍTICAS:\n"
                "1. SIEMPRE usa los REGISTROS INDIVIDUALES de la base de datos para responder preguntas sobre ferreterías específicas. "
                "Los datos están en la sección 'REGISTROS INDIVIDUALES DE LAS 178 FERRETERÍAS ENRIQUECIDAS'.\n"
                "2. NUNCA digas que no tienes datos individuales — los tienes en la base de datos adjunta.\n"
                "3. Cuando pregunten por 'más grandes', muestra primero GRANDE, luego MEDIANA en ese orden.\n"
                "4. Cuando pregunten por teléfono, busca en el campo telefono= de los registros y lista los que tengan valor.\n"
                "5. Responde siempre con datos concretos: nombres, teléfonos, ratings, ciudades reales.\n"
                "6. Responde en español, de forma concisa y profesional.\n\n"
                f"BASE DE DATOS DISPONIBLE:\n{contexto_bd}"
            )
            historial_prompt = "\n".join([
                f"{'Usuario' if m['role']=='user' else 'Asistente'}: {m['content']}"
                for m in st.session_state.chat_history[-6:]
            ])
            prompt_completo = f"{prompt_sistema}\n\nHISTORIAL RECIENTE:\n{historial_prompt}\n\nAsistente:"
            try:
                with st.spinner("Consultando el censo..."):
                    from google import genai as _genai
                    resp = gemini_client.models.generate_content(
                        model=_GEMINI_MODEL, contents=prompt_completo
                    )
                    respuesta = resp.text
            except Exception as e:
                respuesta = f"Error consultando IA: {e}"
        else:
            respuesta = _respuesta_sin_ia(pregunta, df_geo, df_enr)

        st.session_state.chat_history.append({"role": "assistant", "content": respuesta})
        st.rerun()

    # Botón limpiar
    if st.session_state.chat_history:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️  Limpiar conversación", use_container_width=False):
            st.session_state.chat_history = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════
# TAB 5: PIPELINE APIFY
# ══════════════════════════════════════════════════════════════════
with tab5:

    RUTA_CRUCE   = os.path.join(_SCRIPT_DIR, "cruce_apify.py")
    RUTA_LOG     = os.path.join(_SCRIPT_DIR, "pipeline_log.txt")
    APIFY_TOKEN_DEFAULT = st.secrets.get("APIFY_TOKEN", "")

    # ── Helper: verificar si el proceso de scraping sigue vivo ──────
    def _proceso_vivo(pid: int) -> bool:
        try:
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
                capture_output=True, text=True, timeout=5
            )
            return str(pid) in result.stdout
        except Exception:
            return False

    # ── Estado del proceso en session_state ─────────────────────────
    if "scraping_pid" not in st.session_state:
        st.session_state["scraping_pid"] = None

    corriendo = (
        st.session_state["scraping_pid"] is not None
        and _proceso_vivo(st.session_state["scraping_pid"])
    )

    # ── Header del pipeline ─────────────────────────────────────────
    st.markdown("""
<div class="pipe-header" style="background:#1d1d1f;border-radius:18px;padding:24px;margin-bottom:20px;display:flex;gap:16px;align-items:center;">
  <div style="font-size:2rem;">⚙️</div>
  <div>
    <p class="pipe-title" style="font-size:21px;font-weight:600;letter-spacing:0.2px;margin:0 0 4px;line-height:1.19;">Pipeline de Enriquecimiento Apify</p>
    <p class="pipe-sub" style="font-size:12px;letter-spacing:-0.12px;margin:0;">
      Lanza el scraping Google Maps · Validación con IA Gemini · Geofencing Haversine
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Estado actual BD ────────────────────────────────────────────
    st.markdown('<div class="sec-title">📊 &nbsp; Estado actual de la base de datos</div>',
                unsafe_allow_html=True)

    sc1, sc2, sc3, sc4 = st.columns(4)

    total_rues_prio = len(df_geo) if TIENE_GEO else 14_642
    ya_procesados   = len(df_enr) if TIENE_ENR else 0
    pendientes      = max(0, total_rues_prio - ya_procesados)
    pct_avance      = round(ya_procesados / max(total_rues_prio, 1) * 100, 1)

    with sc1:
        st.markdown(kpi("🎯", f"{total_rues_prio:,}", "Ferreterías en universo",
                        badge="Regiones Argos", badge_style="b-blue"), unsafe_allow_html=True)
    with sc2:
        st.markdown(kpi("✅", f"{ya_procesados:,}", "Ya enriquecidas",
                        badge=f"{pct_avance}% avance", badge_style="b-green",
                        color="green"), unsafe_allow_html=True)
    with sc3:
        st.markdown(kpi("⏳", f"{pendientes:,}", "Pendientes de scraping",
                        badge="Por procesar", badge_style="b-yellow",
                        color="yellow"), unsafe_allow_html=True)
    with sc4:
        status_txt   = "🟢 CORRIENDO" if corriendo else "⚪ DETENIDO"
        status_badge = "b-green" if corriendo else "b-gray"
        pid_txt      = f"PID {st.session_state['scraping_pid']}" if corriendo else "Sin proceso activo"
        st.markdown(kpi("🔄", status_txt, "Estado del pipeline",
                        badge=pid_txt, badge_style=status_badge,
                        color="green" if corriendo else "blue"), unsafe_allow_html=True)

    # ── Formulario de configuración ─────────────────────────────────
    st.markdown('<div class="sec-title">🛠️ &nbsp; Configuración del scraping</div>',
                unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="filter-bar"><span class="filter-label">Parámetros del proceso</span>',
                    unsafe_allow_html=True)

        pc1, pc2 = st.columns([3, 1])
        with pc1:
            apify_token = st.text_input(
                "Token Apify",
                value=APIFY_TOKEN_DEFAULT,
                type="password",
                help="Tu token de Apify. Formato: apify_api_XXXX",
            )
        with pc2:
            tamano_lote = st.number_input(
                "Queries por lote",
                min_value=1, max_value=20, value=10, step=1,
                help="Número de ferreterías que se buscan en cada run de Apify (plan FREE: max 10 recomendado)"
            )

        pc3, pc4, pc5 = st.columns(3)
        with pc3:
            solo_grandes = st.checkbox(
                "Solo MEDIANA + GRANDE",
                value=True,
                help="Recomendado: procesa primero el target comercial de Argos"
            )
        with pc4:
            fila_inicio = st.number_input(
                "Fila de inicio (reanudar)",
                min_value=0, value=ya_procesados, step=1,
                help="Para reanudar desde donde se detuvo. Por defecto usa el total ya procesado."
            )
        with pc5:
            limite_registros = st.number_input(
                "Límite de registros (0 = sin límite)",
                min_value=0, value=0, step=10,
                help="Para pruebas: procesa solo N registros y se detiene"
            )

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Comando que se ejecutará ────────────────────────────────────
    cmd_parts = [
        sys.executable, RUTA_CRUCE,
        "--token", apify_token or "TU_TOKEN_AQUI",
        "--lote",  str(tamano_lote),
        "--inicio", str(fila_inicio),
    ]
    if solo_grandes:
        cmd_parts.append("--solo-grandes")
    if limite_registros > 0:
        cmd_parts += ["--limite", str(limite_registros)]

    cmd_preview = " ".join(
        f'"{p}"' if " " in p else p for p in cmd_parts
    )
    st.markdown("**Comando que se ejecutará:**")
    st.code(cmd_preview, language="bash")

    # ── Botones Iniciar / Detener ───────────────────────────────────
    btn1, btn2, btn3 = st.columns([2, 2, 4])

    with btn1:
        iniciar_disabled = corriendo or not apify_token
        if st.button(
            "▶️  Iniciar Scraping",
            disabled=iniciar_disabled,
            use_container_width=True,
            type="primary",
        ):
            if not os.path.exists(RUTA_CRUCE):
                st.error(f"No se encontró cruce_apify.py en {_SCRIPT_DIR}")
            else:
                log_file = open(RUTA_LOG, "w", encoding="utf-8")
                proc = subprocess.Popen(
                    cmd_parts,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    cwd=_SCRIPT_DIR,
                )
                st.session_state["scraping_pid"] = proc.pid
                st.session_state["scraping_log"] = RUTA_LOG
                st.success(f"✅ Pipeline iniciado — PID {proc.pid}")
                st.rerun()

    with btn2:
        detener_disabled = not corriendo
        if st.button(
            "⏹️  Detener proceso",
            disabled=detener_disabled,
            use_container_width=True,
        ):
            pid = st.session_state["scraping_pid"]
            try:
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
                st.session_state["scraping_pid"] = None
                st.warning(f"Proceso {pid} detenido.")
                st.rerun()
            except Exception as e:
                st.error(f"No se pudo detener: {e}")

    # ── Visor de logs ───────────────────────────────────────────────
    st.markdown('<div class="sec-title">📄 &nbsp; Log del proceso</div>',
                unsafe_allow_html=True)

    log_col1, log_col2 = st.columns([4, 1])
    with log_col2:
        if st.button("🔄  Actualizar log", use_container_width=True):
            st.rerun()

    if os.path.exists(RUTA_LOG):
        try:
            with open(RUTA_LOG, "r", encoding="utf-8", errors="replace") as f:
                contenido_log = f.read()
            if contenido_log.strip():
                # Mostrar las últimas 80 líneas
                lineas = contenido_log.splitlines()
                ultimas = "\n".join(lineas[-80:])
                st.code(ultimas, language="text")
                st.caption(f"Mostrando últimas {min(80, len(lineas))} de {len(lineas)} líneas · {RUTA_LOG}")
            else:
                st.info("El log está vacío. Inicia el scraping para ver la salida aquí.")
        except Exception as e:
            st.error(f"Error leyendo log: {e}")
    else:
        st.markdown("""
<div style="background:#ffffff;border-radius:18px;padding:32px;text-align:center;border:1px solid #e0e0e0;color:#98989d;">
  <div style="font-size:2rem;margin-bottom:10px;">📋</div>
  <p style="margin:0;font-size:17px;letter-spacing:-0.374px;">El log aparecerá aquí cuando inicies el scraping.</p>
</div>
""", unsafe_allow_html=True)

    # ── Instrucciones ───────────────────────────────────────────────
    with st.expander("ℹ️  ¿Cómo funciona el pipeline?"):
        st.markdown("""
**Flujo del scraping:**

1. Lee las ferreterías de `BD_Geocodificada.xlsx` (o `BD_Regiones_Prioritarias.xlsx`)
2. Por cada ferretería construye una query de búsqueda para Google Maps vía Apify
3. Procesa en lotes de N queries por run de Apify (plan FREE: 1 run concurrente)
4. Por cada resultado aplica la **cascada de validación IA**:
   - 📍 Distancia < 50m → **"Si"** automático
   - 🏷️ Categoría válida + < 500m → **"Si"** automático
   - 📊 Score FuzzyWuzzy ≥ 85% → **"Si"** automático
   - ❌ Score < 30% + categoría inválida → **"No"** automático
   - 🤖 Caso ambiguo → **Gemini decide** (Si / Parcial / No)
5. Guarda resultados incrementalmente en `BD_Enriquecida.xlsx`

**Tiempo estimado:** ~3-5 min por lote de 10 ferreterías (depende de Apify).

**Para reanudar** una sesión interrumpida, ajusta "Fila de inicio" al número de registros ya procesados.
""")


# ══════════════════════════════════════════════════════════════════
# TAB 6: CORREOS CEMENTO (N8N)
# ══════════════════════════════════════════════════════════════════
with tab6:
    import json as _json

    _N8N_TOKEN = (
        st.secrets.get("N8N_TOKEN", "")
        or os.environ.get("N8N_TOKEN", "")
        or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzODRiY2VhMC04MzdlLTRjNTktOGZiOS1jYzBhYzRjZjFjZGUiLCJpc3MiOiJuOG4iLCJhdWQiOiJtY3Atc2VydmVyLWFwaSIsImp0aSI6ImNhZmM3ZmNmLWE4NDQtNDk3ZS04YjhhLWZjZTBiMWQwZTIxNSIsImlhdCI6MTc3NzE0OTIwMX0.o2qBqjhZP3k3Bq4b90uZgy6TVNPG4rqoSplDCvvBYJA"
    )
    _N8N_MCP_URL       = "https://laurent395.app.n8n.cloud/mcp-server/http"
    _WORKFLOW_EMAIL_ID = "2OKf7u2ki2RdkEwC"
    _SHEETS_ID      = "1yNH3aJtlvMmedQfBxCmJXXxYQGw9OV1XLQ4UYAL6tbM"
    _SHEETS_GID     = "2100342099"
    _SHEETS_CSV_URL = f"https://docs.google.com/spreadsheets/d/{_SHEETS_ID}/export?format=csv&gid={_SHEETS_GID}"
    _SHEETS_URL     = f"https://docs.google.com/spreadsheets/d/{_SHEETS_ID}/edit?gid={_SHEETS_GID}#gid={_SHEETS_GID}"

    # ── Header ──────────────────────────────────────────────────────
    st.markdown("""
<div style="background:#003DA5;padding:24px 28px;border-radius:18px;margin-bottom:20px;
            display:flex;gap:16px;align-items:center;">
  <div style="font-size:2rem;">📧</div>
  <div>
    <p style="color:#fff;font-size:21px;font-weight:600;letter-spacing:0.2px;
              margin:0 0 4px;line-height:1.19;">Validación Cemento Argos</p>
    <p style="color:rgba(255,255,255,0.55);font-size:12px;letter-spacing:-0.12px;margin:0;">
      Envía consultas a ferreterías confirmadas · Captura respuestas en tiempo real vía N8N
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Ferreterías confirmadas ──────────────────────────────────────
    st.markdown('<div class="sec-title">✅ &nbsp; Ferreterías confirmadas — Listas para contactar</div>',
                unsafe_allow_html=True)

    if TIENE_ENR and "match_google" in df_enr.columns:
        df_match = df_enr[df_enr["match_google"] == "Si"].copy()
        n_match  = len(df_match)

        vende_col = "vende_cemento" if "vende_cemento" in df_match.columns else None
        n_enviado = int((df_match[vende_col] == "Enviado").sum()) if vende_col else 0
        n_conf_si = int((df_match[vende_col] == "Si").sum())      if vende_col else 0
        n_no_ver  = int((df_match[vende_col] == "No verificado").sum()) if vende_col else n_match

        em1, em2, em3, em4 = st.columns(4)
        with em1:
            st.markdown(kpi("✅", str(n_match), "Con match Google confirmado",
                            badge="Google Maps + IA", badge_style="b-green", color="green"),
                        unsafe_allow_html=True)
        with em2:
            st.markdown(kpi("📭", str(n_no_ver), "Sin contactar aún",
                            badge="Pendientes", badge_style="b-yellow", color="yellow"),
                        unsafe_allow_html=True)
        with em3:
            st.markdown(kpi("📨", str(n_enviado), "Correos enviados",
                            badge="Esperando respuesta", badge_style="b-blue"),
                        unsafe_allow_html=True)
        with em4:
            st.markdown(kpi("🎯", str(n_conf_si), "Confirmaron venta cemento",
                            badge="Respuesta: Sí", badge_style="b-green", color="green"),
                        unsafe_allow_html=True)

        cols_vis = [c for c in [
            "nombre_rues", "municipio", "departamento",
            "correo_rues", "telefono", "match_google", "vende_cemento",
        ] if c in df_match.columns]
        st.dataframe(df_match[cols_vis].reset_index(drop=True),
                     use_container_width=True, height=260)
    else:
        st.info("No hay ferreterías con match confirmado aún. Ejecuta el Pipeline Apify primero.")
        df_match = pd.DataFrame()
        n_match  = 0

    # ── Envío de correos ─────────────────────────────────────────────
    st.markdown('<div class="sec-title">📤 &nbsp; Enviar consulta "¿Vende cemento Argos?"</div>',
                unsafe_allow_html=True)

    modo_test = st.toggle("Modo TEST — solo envía a tu correo de demo", value=True,
                          key="toggle_correo_test")

    if modo_test:
        st.info(
            "**Modo TEST activo** — Se envía 1 correo de prueba a `desarrollandodatosia@gmail.com`. "
            "Perfecto para mostrar en la demo sin impactar ferreterías reales."
        )
    else:
        st.warning(
            f"**Modo PRODUCCIÓN** — Se enviarán correos a las {n_match if n_match else 24} ferreterías reales. "
            "Para activar esto, cambia `TEST_MODE = false` en el nodo Code del workflow en N8N."
        )

    import requests as _rq_email

    col_btn1, col_btn2 = st.columns([2, 5])
    with col_btn1:
        btn_enviar = st.button(
            "📧  Enviar correos ahora",
            type="primary",
            use_container_width=True,
            key="btn_enviar_correos",
        )

    if btn_enviar:
        with st.spinner("Ejecutando workflow en N8N..."):
            try:
                _payload = {
                    "jsonrpc": "2.0",
                    "id": 10,
                    "method": "tools/call",
                    "params": {
                        "name": "execute_workflow",
                        "arguments": {
                            "workflowId": _WORKFLOW_EMAIL_ID,
                            "executionMode": "manual",
                        },
                    },
                }
                _r = _rq_email.post(
                    _N8N_MCP_URL,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream",
                        "Authorization": f"Bearer {_N8N_TOKEN}",
                    },
                    json=_payload,
                    timeout=30,
                )
                _exec_id = None
                _exec_status = "unknown"
                for _line in _r.text.splitlines():
                    if _line.startswith("data:"):
                        _obj = _json.loads(_line[5:].strip())
                        _content = _obj.get("result", {}).get("content", [{}])
                        if _content:
                            _inner = _json.loads(_content[0].get("text", "{}"))
                            _exec_id     = _inner.get("executionId")
                            _exec_status = _inner.get("status", "unknown")
                        break

                if _exec_status == "started" or _exec_id:
                    st.success(
                        f"Workflow ejecutado correctamente — Execution ID: `{_exec_id or 'n/a'}`"
                    )
                    if modo_test:
                        st.info(
                            "Revisa **desarrollandodatosia@gmail.com** — "
                            "el correo debe llegar en los próximos segundos. "
                            "Haz clic en uno de los 3 botones del correo y la respuesta "
                            "aparecerá en la sección de abajo."
                        )
                elif _exec_status == "error":
                    _err = _inner.get("error", "Error desconocido")
                    st.error(f"N8N reportó error: {_err}")
                else:
                    st.warning(f"Respuesta inesperada de N8N: `{_exec_status}`")
            except Exception as _ex:
                st.error(f"Error de conexión con N8N: {_ex}")

    # ── Respuestas recibidas ─────────────────────────────────────────
    st.markdown('<div class="sec-title">📥 &nbsp; Respuestas recibidas — Tiempo real</div>',
                unsafe_allow_html=True)

    rh1, rh2, rh3 = st.columns([4, 1, 1])
    with rh2:
        if st.button("🔄  Actualizar", key="btn_refresh_resp", use_container_width=True):
            st.rerun()
    with rh3:
        if st.button("💾  Sync → Excel", key="btn_sync_excel", use_container_width=True,
                     help="Lee las respuestas del Sheet y actualiza vende_cemento en BD_Enriquecida.xlsx"):
            try:
                _df_sync = pd.read_csv(_SHEETS_CSV_URL)
                if len(_df_sync) == 0:
                    st.info("No hay respuestas en el Sheet todavía.")
                else:
                    _df_enr_edit = pd.read_excel(RUTA_ENR, engine="openpyxl")
                    _mapa = {"si": "Si", "no": "No", "parcial": "Parcialmente"}
                    _n_ok = 0
                    for _, _fila in _df_sync.iterrows():
                        _correo = str(_fila.get("correo", "")).strip().lower()
                        _val    = _mapa.get(str(_fila.get("respuesta", "")).strip().lower(), "")
                        if not _correo or not _val:
                            continue
                        _mask = _df_enr_edit["correo_rues"].astype(str).str.strip().str.lower() == _correo
                        if _mask.any():
                            _df_enr_edit.loc[_mask, "vende_cemento"] = _val
                            _n_ok += 1
                    _df_enr_edit.to_excel(RUTA_ENR, index=False, engine="openpyxl")
                    st.success(f"✅ {_n_ok} ferretería(s) actualizadas en BD_Enriquecida.xlsx")
                    st.rerun()
            except Exception as _sync_err:
                st.error(f"Error al sincronizar: {_sync_err}")

    try:
        _df_resp = pd.read_csv(_SHEETS_CSV_URL)
        if len(_df_resp) > 0:
            _n_total   = len(_df_resp)
            _resp_col  = "respuesta" if "respuesta" in _df_resp.columns else None
            _n_si      = int((_df_resp[_resp_col] == "si").sum())      if _resp_col else 0
            _n_parcial = int((_df_resp[_resp_col] == "parcial").sum()) if _resp_col else 0
            _n_no      = int((_df_resp[_resp_col] == "no").sum())      if _resp_col else 0

            rr1, rr2, rr3, rr4 = st.columns(4)
            with rr1:
                st.markdown(kpi("📩", str(_n_total), "Respuestas totales",
                                badge="Acumuladas", badge_style="b-blue"),
                            unsafe_allow_html=True)
            with rr2:
                st.markdown(kpi("✅", str(_n_si), "Venden cemento Argos",
                                badge="Respuesta: Sí", badge_style="b-green", color="green"),
                            unsafe_allow_html=True)
            with rr3:
                st.markdown(kpi("🔸", str(_n_parcial), "Venden ocasionalmente",
                                badge="Respuesta: Parcial", badge_style="b-orange", color="orange"),
                            unsafe_allow_html=True)
            with rr4:
                st.markdown(kpi("❌", str(_n_no), "No venden cemento",
                                badge="Respuesta: No", badge_style="b-gray"),
                            unsafe_allow_html=True)

            _sort_col = "timestamp" if "timestamp" in _df_resp.columns else _df_resp.columns[0]
            st.dataframe(
                _df_resp.sort_values(_sort_col, ascending=False).reset_index(drop=True),
                use_container_width=True,
                height=320,
            )
        else:
            st.markdown("""
<div style="background:#ffffff;border-radius:18px;padding:40px;text-align:center;
            border:1px solid #e0e0e0;color:#98989d;">
  <div style="font-size:2.4rem;margin-bottom:12px;">📭</div>
  <p style="margin:0;font-size:17px;letter-spacing:-0.374px;color:#6e6e73;">
    Aún no hay respuestas registradas.
  </p>
  <p style="margin:8px 0 0;font-size:13px;">
    Envía los correos y cuando la ferretería haga clic, la respuesta aparecerá aquí.
  </p>
</div>
""", unsafe_allow_html=True)

    except Exception:
        st.markdown("""
<div style="background:#ffffff;border-radius:18px;padding:40px;text-align:center;
            border:1px solid #e0e0e0;">
  <div style="font-size:2.4rem;margin-bottom:12px;">📊</div>
  <p style="font-size:15px;color:#6e6e73;margin:0 0 20px;">
    Las respuestas se almacenan en Google Sheets en tiempo real.<br>
    Haz clic para verlas directamente.
  </p>
</div>
""", unsafe_allow_html=True)
        st.markdown(
            f'<div style="text-align:center;">'
            f'<a href="{_SHEETS_URL}" target="_blank" '
            f'style="display:inline-block;background:#003DA5;color:#fff;padding:12px 28px;'
            f'border-radius:9999px;text-decoration:none;font-size:14px;font-weight:600;">'
            f'📊 &nbsp; Ver respuestas en Google Sheets</a></div>',
            unsafe_allow_html=True,
        )

    # ── Flujo explicado ──────────────────────────────────────────────
    with st.expander("ℹ️  ¿Cómo funciona este módulo?"):
        st.markdown("""
**Flujo completo de punta a punta:**

1. Las **24 ferreterías** listadas arriba tienen `match_google = "Si"` — confirmadas por IA + GPS
2. Al hacer clic en **"Enviar correos"**, esta app ejecuta el **Workflow N8N** directamente vía API
3. N8N envía un correo HTML a cada ferretería con **3 botones de un solo clic**:
   - ✅ Sí, vendemos cemento Argos
   - 🔸 Sí, pero de forma ocasional
   - ❌ No comercializamos cemento
4. El clic del ferretero activa el **Webhook** del segundo workflow (activo 24/7)
5. N8N captura nombre, ciudad y respuesta → los guarda en **Google Sheets** en tiempo real
6. Esta pantalla muestra las respuestas actualizadas al hacer clic en "Actualizar"

**Modo TEST vs Producción:**
- TEST (activo): envía 1 correo a `desarrollandodatosia@gmail.com` para demostración
- Producción: cambia `TEST_MODE = false` en el nodo Code del workflow en N8N
""")


# ══════════════════════════════════════════════════════════════════
# TAB 7: CARGA INCREMENTAL RUES (para equipo comercial Argos)
# ══════════════════════════════════════════════════════════════════
with tab7:
    import json as _json_t7
    import time as _time_t7
    from datetime import datetime as _dt_t7

    st.markdown("""
    <div class="argos-header">
      <div class="header-title">📥 Carga incremental RUES</div>
      <div class="header-sub">Sube una nueva base del RUES — el sistema detecta automáticamente las ferreterías nuevas, las geocodifica y las inserta en Supabase.</div>
    </div>
    """, unsafe_allow_html=True)

    _UPLOADS_DIR = os.path.join(_SCRIPT_DIR, "uploads")
    os.makedirs(_UPLOADS_DIR, exist_ok=True)
    _RUES_SCRIPT = os.path.join(_SCRIPT_DIR, "cargar_rues_incremental.py")
    _RUES_LOG    = os.path.join(_SCRIPT_DIR, "rues_incremental_log.txt")

    def _t7_vivo(pid: int) -> bool:
        if not pid:
            return False
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False

    for k in ("rues_uploaded_path", "rues_preview", "rues_pid"):
        if k not in st.session_state:
            st.session_state[k] = None

    # ── Fase A: upload ────────────────────────────────────────────
    st.markdown("### Paso 1 · Subir archivo del RUES")
    uploaded = st.file_uploader(
        "Formato esperado: xlsx o csv (encoding latin-1, sep ';'). "
        "Columnas mínimas: numero_identificacion, direccion_comercial, municipio, departamento, nombre_rues",
        type=["xlsx", "csv"],
        key="rues_file",
    )
    if uploaded is not None:
        ts = _dt_t7.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(_UPLOADS_DIR, f"rues_{ts}_{uploaded.name}")
        with open(path, "wb") as f:
            f.write(uploaded.getbuffer())
        st.session_state["rues_uploaded_path"] = path
        st.success(f"✅ Subido: **{uploaded.name}** ({uploaded.size/1024:.0f} KB) → guardado en `uploads/`")

    if not st.session_state.get("rues_uploaded_path"):
        st.info("Sube un archivo para continuar.")
        st.stop()

    # ── Fase B: análisis (dry-run) ────────────────────────────────
    st.markdown("### Paso 2 · Analizar (comparar con la BD)")
    if st.button("🔍 Analizar archivo", key="rues_analyze"):
        with st.spinner("Comparando numero_identificacion con Supabase..."):
            try:
                r = subprocess.run(
                    [sys.executable, _RUES_SCRIPT,
                     "--input", st.session_state["rues_uploaded_path"], "--dry-run"],
                    capture_output=True, text=True, timeout=180,
                )
                out = r.stdout or ""
                if "=== RESUMEN_JSON ===" in out:
                    json_line = out.split("=== RESUMEN_JSON ===")[1].strip().splitlines()[0]
                    st.session_state["rues_preview"] = _json_t7.loads(json_line)
                else:
                    st.error("El análisis no devolvió resumen JSON.")
                    with st.expander("Ver salida completa"):
                        st.code((r.stdout or "") + "\n--STDERR--\n" + (r.stderr or ""))
            except subprocess.TimeoutExpired:
                st.error("Timeout: el análisis tardó más de 3 min.")
            except Exception as e:
                st.error(f"Error: {e}")

    p = st.session_state.get("rues_preview")
    if p:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total en archivo", f"{p['total_input']:,}")
        c2.metric("Ya en BD", f"{p['total_input'] - p['nuevas_detectadas']:,}")
        c3.metric("Nuevas a procesar", f"{p['nuevas_detectadas']:,}", delta=f"+{p['nuevas_detectadas']}")

        if p["nuevas_detectadas"] == 0:
            st.success("🎉 Todas las ferreterías del archivo ya están en la BD. Nada que insertar.")
            if st.button("Cargar otro archivo"):
                for k in ("rues_uploaded_path", "rues_preview"):
                    st.session_state[k] = None
                st.rerun()
        else:
            est_min = p["nuevas_detectadas"] * 1.2 / 60
            st.warning(
                f"⚠️ Se geocodificarán **{p['nuevas_detectadas']:,}** ferreterías "
                f"con Nominatim (≈ {est_min:.1f} min) y se insertarán en Supabase. "
                f"El proceso corre en segundo plano. Puedes seguir trabajando en otros tabs."
            )

            # ── Fase C: confirmar + ejecutar ──────────────────────
            st.markdown("### Paso 3 · Confirmar e insertar")
            corriendo = _t7_vivo(st.session_state.get("rues_pid") or 0)
            jwt = st.session_state.get("auth_token", "")
            if not jwt:
                st.error("Necesitas estar autenticado para insertar (RLS exige JWT).")
            else:
                if st.button("✅ Confirmar e insertar en Supabase",
                             type="primary",
                             disabled=corriendo,
                             key="rues_confirm"):
                    cmd = [sys.executable, _RUES_SCRIPT,
                           "--input", st.session_state["rues_uploaded_path"],
                           "--token", jwt]
                    with open(_RUES_LOG, "w", encoding="utf-8") as f:
                        f.write(f"=== INICIO {_dt_t7.now().isoformat()} ===\n")
                    log_handle = open(_RUES_LOG, "a", encoding="utf-8")
                    proc = subprocess.Popen(
                        cmd, stdout=log_handle, stderr=subprocess.STDOUT,
                        cwd=_SCRIPT_DIR,
                    )
                    st.session_state["rues_pid"] = proc.pid
                    st.rerun()

    # ── Fase D: log en vivo ───────────────────────────────────────
    if st.session_state.get("rues_pid"):
        st.markdown("### Paso 4 · Progreso en vivo")
        corriendo = _t7_vivo(st.session_state["rues_pid"])
        estado = "🟢 Corriendo..." if corriendo else "✅ Finalizado"
        st.info(f"Carga RUES — **{estado}** | PID: {st.session_state['rues_pid']}")

        if os.path.exists(_RUES_LOG):
            with open(_RUES_LOG, encoding="utf-8", errors="replace") as f:
                contenido = f.readlines()
            ultimas = contenido[-100:]
            st.code("".join(ultimas), language="text")

        col_a, col_b = st.columns(2)
        if corriendo:
            col_a.info("Refresco automático cada 5s")
            _time_t7.sleep(5)
            st.rerun()
        else:
            if col_a.button("🔄 Recargar app con nuevos datos"):
                try:
                    cargar_datos.clear()
                except Exception:
                    pass
                st.session_state["rues_pid"] = None
                st.session_state["rues_uploaded_path"] = None
                st.session_state["rues_preview"] = None
                st.rerun()
            if col_b.button("Solo cerrar"):
                st.session_state["rues_pid"] = None
                st.rerun()

    with st.expander("ℹ️ ¿Cómo funciona la carga incremental?"):
        st.markdown("""
**Para el equipo comercial de Argos:**

Cada ~4 meses el RUES publica una versión actualizada. Para incorporar las ferreterías nuevas:

1. **Subir** el archivo Excel/CSV nuevo (mismo formato que el original que procesó Sebastián).
2. **Analizar** — el sistema lee `numero_identificacion` de Supabase y detecta cuáles del archivo no estaban antes.
3. **Confirmar** — solo las **nuevas** se geocodifican (Nominatim, gratis) y se insertan en Supabase con `match_google = NULL`.
4. **Enriquecer** — ir al Tab 5 (Pipeline Apify) que automáticamente recoge las que tienen `match_google IS NULL` y aplica el scraping de Google Maps.

**Seguridad (RLS):** Solo el usuario admin (`desarrollandodatosia@gmail.com`) puede insertar. Los usuarios demo solo pueden leer.

**Idempotencia:** Si subes el mismo archivo dos veces, la segunda vez detecta 0 nuevas y no hace nada.
""")

