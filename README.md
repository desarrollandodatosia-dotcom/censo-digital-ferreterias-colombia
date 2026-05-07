# CEMANTIX — Sistema de Inteligencia Comercial para el Sector Ferretero en Colombia

> **Proyecto Final · EAFIT 2026 · Equipo Desarrollando Datos IA**  
> Cliente: Cementos Argos S.A. · Duración: 4 semanas · Entrega: Mayo 2026

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red)](https://streamlit.io)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green)](https://supabase.com)
[![N8N](https://img.shields.io/badge/N8N-Cloud-orange)](https://n8n.io)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-yellow)](https://ai.google.dev)

---

## ¿Qué es CEMANTIX?

CEMANTIX digitaliza, enriquece y analiza el censo de ferreterías en Colombia, convirtiendo datos públicos del RUES en inteligencia de mercado accionable para Cementos Argos. Combina web scraping automatizado (Apify + Google Maps), validación por IA (Gemini 2.5 Flash), geocodificación masiva y un agente conversacional con acceso a datos en tiempo real.

**Problema resuelto:** Argos no tenía visibilidad digital sobre su canal ferretero. El RUES tiene 34.133 ferreterías registradas sin datos de contacto verificados, ubicación GPS ni información sobre qué establecimientos venden cemento.

---

## Resultados al cierre del proyecto

| Métrica | Resultado |
|---|---|
| Ferreterías geocodificadas (GPS) | **14.642** — regiones prioritarias Argos |
| Ferreterías enriquecidas con Google Maps | **178** — MEDIANA y GRANDE (Fase 1) |
| Match confirmado como ferretería real | **21** (11.8%) — validados por IA + GPS |
| Teléfonos recuperados | **30** — dato inexistente en RUES original |
| Sitios web identificados | **25** |
| Rating promedio Google Maps | **4.47 / 5.0** |
| Costo de enriquecimiento Fase 1 | **$3.74 USD** (vs ~$500–$2.000 métodos tradicionales) |

---

## Arquitectura del sistema

```
RUES (34.133 ferreterías)
        │
        ▼
geocodificar_addresses.py  ─── Nominatim OSM ──► coordenadas GPS
        │
        ▼
cruce_apify.py  ─── Apify (Google Maps) ──► enriquecimiento por lotes
                 ─── FuzzyWuzzy + Haversine + Gemini 2.5 Flash ──► validación
        │
        ▼
importar_a_supabase.py ──► Supabase PostgreSQL (14.642 filas, 33 cols)
        │
        ▼
app.py (Streamlit :8501) ──► Dashboard · Mapa · Agente IA · Correos
        │
        ├── Tab 4: Agente IA ── Gemini 2.5 Flash (RAG con 178 registros)
        └── Tab 6: Correos  ── N8N Cloud
                                ├── WF1: envío masivo (Gmail)
                                └── WF2: receptor respuestas (Webhook → Sheets)
```

---

## Estructura del repositorio

```
Etapa3/
├── app.py                              # Aplicación web principal (Streamlit)
├── cruce_apify.py                      # Pipeline de enriquecimiento Google Maps
├── geocodificar_addresses.py           # Geocodificación RUES → GPS (Nominatim)
├── importar_a_supabase.py              # Carga inicial a Supabase (solo una vez)
├── mapa_v1.py                          # Generador de mapa Folium standalone
├── requirements.txt                    # Dependencias Python
├── INICIAR_CEMANTIX.bat                # Script de arranque rápido (Windows)
│
├── n8n_workflows/                      # Automatizaciones N8N exportadas
│   ├── WF1_CEMANTIX_VendeCemento.json  # Envío de correos a ferreterías
│   ├── WF2_CEMANTIX_ReceptorRespuestas.json  # Captura de respuestas (webhook)
│   └── README_N8N.md                   # Guía de importación y configuración
│
├── BD_Enriquecida.xlsx                 # 178 ferreterías MEDIANA+GRANDE enriquecidas
├── BD_Enriquecida_backup_v1.xlsx       # Backup versión anterior
│
├── wf1_sdk.js                          # Código SDK N8N del WF1 (referencia)
├── generar_guion.js                    # Generador del guión demo en Word
├── generar_manual.js                   # Generador del manual universitario en Word
├── queries_apify.json                  # Plantillas de consultas para Apify
│
├── DOCUMENTACION_MASTER_CEMANTIX.md    # Documentación técnica completa del proyecto
├── MANUAL_UNIVERSITARIO_CEMANTIX.docx  # Manual universitario formal (Word)
├── GUION_DEMO_CEMANTIX.docx            # Guión del demo en vivo (pitch 3 min)
├── GUION_PITCH_v2_IA.pdf               # Guión completo del pitch
├── informe_avance_preliminar.html      # Informe de avance académico
│
└── .gitignore
```

---

## Cómo ejecutar la aplicación

### Requisitos previos
- Python 3.11+
- Conexión a internet

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/desarrollandodatosia-dotcom/Etapa3.git
cd Etapa3

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar credenciales (crear archivo)
mkdir .streamlit
```

Crear `.streamlit/secrets.toml` con:
```toml
GEMINI_API_KEY = "tu-api-key-de-google-ai-studio"
SUPABASE_URL = "https://asaknpdzozkpexfrvlzw.supabase.co"
SUPABASE_KEY = "eyJhbGci..."
N8N_TOKEN = "eyJhbGci..."
```

### Iniciar la aplicación

```bash
streamlit run app.py
# → Abre http://localhost:8501
```

**O doble clic en:** `INICIAR_CEMANTIX.bat` (Windows)

### Credenciales de acceso

| Perfil | Email | Contraseña |
|---|---|---|
| Demo (solo lectura) | demo.argos@gmail.com | Argos2026# |
| Admin (acceso completo) | desarrollandodatosia@gmail.com | Admin2026# |

---

## Módulos de la aplicación

| Tab | Nombre | Descripción |
|---|---|---|
| 1 | Dashboard | KPIs, nube de palabras, Top 10 municipios, distribución por tamaño |
| 2 | Mapa Interactivo | 14.642 ferreterías con GPS, filtros por departamento y tamaño |
| 3 | Directorio | Tabla filtrable con exportación a Excel |
| 4 | Agente IA | Chat con Gemini 2.5 Flash — consultas sobre el censo en lenguaje natural |
| 5 | Pipeline Apify | Ejecución del enriquecimiento desde la interfaz web |
| 6 | Correos Cemento | Envío a ferreterías y respuestas en tiempo real (N8N + Google Sheets) |

---

## Pipeline de enriquecimiento

```bash
# Enriquecer MEDIANA y GRANDE (178 ferreterías — Fase 1 completa)
python cruce_apify.py --token apify_api_XXX --solo-grandes

# Reanudar desde fila 80
python cruce_apify.py --token apify_api_XXX --solo-grandes --inicio 80

# Rango específico
python cruce_apify.py --token apify_api_XXX --inicio 0 --limite 50 --lote 10
```

**Costo:** ~$0.021 USD por ferretería · Ciclo Apify renueva el día 8 de cada mes

---

## Automatizaciones N8N

Los flujos están exportados en `n8n_workflows/`. Para importar:

1. Ir a N8N → **Settings → Import Workflow**
2. Subir el archivo `.json` correspondiente
3. Configurar credenciales (Gmail OAuth2 para WF1, Google Sheets OAuth2 para WF2)

| Workflow | Archivo | Función |
|---|---|---|
| WF1 | `WF1_CEMANTIX_VendeCemento.json` | Envía correo HTML con 3 botones de respuesta a ferreterías |
| WF2 | `WF2_CEMANTIX_ReceptorRespuestas.json` | Captura clics de botones → guarda en Google Sheets (webhook 24/7) |

Ver `n8n_workflows/README_N8N.md` para instrucciones detalladas.

---

## Base de datos — Supabase

- **Proyecto:** `asaknpdzozkpexfrvlzw`
- **Tabla principal:** `ferreterias` (14.642 filas · 33 columnas)
- **Columnas clave:** `nombre_rues`, `tamano_empresa`, `departamento`, `municipio`, `latitud`, `longitud`, `telefono`, `pagina_web`, `calificacion_google`, `match_google`, `vende_cemento`

El archivo `BD_Enriquecida.xlsx` en este repositorio contiene las 178 ferreterías MEDIANA y GRANDE ya enriquecidas con Google Maps — el subconjunto de mayor valor comercial para Argos.

---

## Stack tecnológico

| Capa | Tecnologías |
|---|---|
| **Backend / Pipeline** | Python 3.11, pandas, FuzzyWuzzy, requests, geopy |
| **Frontend / App** | Streamlit, Folium, Plotly, WordCloud, Pillow |
| **IA** | Google Gemini 2.5 Flash (validación + agente RAG) |
| **Base de datos** | Supabase (PostgreSQL) + Excel como fallback |
| **Automatización** | N8N Cloud, Gmail API, Google Sheets API |
| **Web scraping** | Apify — actor `compass~crawler-google-places` |
| **Geocodificación** | Nominatim / OpenStreetMap (gratuito) |

---

## Documentación completa

| Documento | Descripción |
|---|---|
| `DOCUMENTACION_MASTER_CEMANTIX.md` | Referencia técnica completa: arquitectura, código, credenciales, resultados |
| `MANUAL_UNIVERSITARIO_CEMANTIX.docx` | Manual universitario formal (12 secciones, ~50 páginas) |
| `GUION_DEMO_CEMANTIX.docx` | Guión del demo en vivo de 3 minutos para el pitch |
| `GUION_PITCH_v2_IA.pdf` | Guión completo de la presentación |
| `informe_avance_preliminar.html` | Informe de avance académico entregado durante el proyecto |

---

## Equipo

**Desarrollando Datos IA · EAFIT 2026**  
📧 desarrollandodatosia@gmail.com

---

*Proyecto final · Mayo 2026 · Universidad EAFIT · Cliente: Cementos Argos S.A.*
