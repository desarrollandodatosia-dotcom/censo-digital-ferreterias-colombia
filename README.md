# Censo Digital de Ferreterías en Colombia
> Proyecto universitario para **Cementos Argos S.A.** | Equipo de 7 | 4 semanas

Sistema automatizado que extrae, limpia, enriquece y mantiene una base de datos nacional de ferreterías colombianas, identificando cuáles comercializan cemento.

---

## Estado actual — Semana 1/4

| Componente | Estado |
|---|---|
| Base de datos RUES (34.133 registros, 25 campos) | ✅ Completado |
| Filtro regiones prioritarias (14.642 registros) | ✅ Completado |
| Pipeline ETL `limpiar_datos.py` | ✅ Funcional |
| Geocodificación GPS (Nominatim) | 🔄 En proceso |
| Enriquecimiento Google Maps (Apify) | 🔄 Configurando |
| Mapa interactivo Folium (3 capas) | ✅ v1 generada |
| Flujos N8N (actualización + campaña cemento) | ✅ Probados |
| Dashboard Streamlit | 📐 Semana 3 |
| Agente IA con RAG | 📐 Semana 3-4 |

---

## Estructura del repositorio

```
Etapa3/
├── limpiar_datos.py              # ETL: RUES CSV → Excel limpio (34k registros)
├── cruce_apify.py                # Enriquecimiento con Google Maps vía Apify (modo batch)
├── geocodificar_addresses.py     # Geocodificación dirección → GPS con Nominatim
├── mapa_v1.py                   # Generador de mapa interactivo Folium
├── analyze_files.py             # Script de análisis de archivos
│
├── BD_Regiones_Prioritarias.xlsx # 14.642 ferreterías regiones prioritarias (25 cols)
├── BD_Enriquecida.xlsx          # Muestra piloto enriquecida con Google Maps (50 regs)
├── Bd_Base.xlsx                 # Base inicial de trabajo
├── muestra_datos_preliminar.csv # Muestra de 22 registros para entrega académica
│
├── informe_avance_preliminar.html # Informe académico semana 1 (abrir en navegador → PDF)
├── arquitectura_solucion_v3.pptx  # Diagrama de arquitectura del sistema
├── Roadmap_Proyecto.xlsx          # Cronograma visual del proyecto
│
├── MEMORIA_PROYECTO.md          # Bitácora técnica completa del proyecto
├── GUIA_MAESTRA_IMPLEMENTACION.md # Documento de diseño y guía del equipo
├── roadmap.md                   # Roadmap detallado por semana y rol
│
└── .gitignore
```

---

## Fuentes de datos

| Fuente | Tipo | Registros | Estado |
|---|---|---|---|
| **RUES** (rues.org.co) | Oficial / Gobierno | 34.133 | ✅ Procesado |
| **Google Maps** (vía Apify) | Web scraping | 178 medianas/grandes | 🔄 En proceso |
| **OpenStreetMap / Nominatim** | Geocodificación | 14.642 | 🔄 En proceso |
| **Correos verificación** (N8N) | Campo | 500+ planeados | 📐 Semana 3 |

---

## Regiones prioritarias (definidas por Argos)

| Región | Registros |
|---|---|
| Bogotá D.C. | 6.269 |
| Antioquia | 4.138 |
| Cundinamarca | 2.272 |
| Eje Cafetero (Risaralda + Caldas + Quindío) | 1.963 |
| **Total** | **14.642** |

---

## Stack tecnológico

**Extracción:** RUES · Apify (Google Maps) · Nominatim  
**Procesamiento:** Python 3.11 · Pandas · FuzzyWuzzy · Claude API (Haiku)  
**Automatización:** N8N Cloud (`laurent365.app.n8n.cloud`) · Gmail SMTP  
**Visualización:** Folium · Streamlit · PowerBI  
**IA / RAG:** Anthropic Claude Sonnet · Chroma (vector DB)

---

## Niveles de entrega

```
NIVEL 1 — OBLIGATORIO     NIVEL 2 — ESPERADO        NIVEL 3 — DIFERENCIADOR
──────────────────────    ──────────────────────    ──────────────────────
BD limpia y estructurada  Dashboard + Mapa          Agente IA consultable
34k registros RUES        interactivo con filtros   en lenguaje natural
+ enriquecido Maps        por región, tamaño,       (RAG con Claude API)
                          vende cemento
```

---

## Cómo ejecutar el pipeline

```bash
# 1. Limpiar RUES y generar BD base
python limpiar_datos.py
# Output: BD_RUES_Limpia.xlsx + BD_Regiones_Prioritarias.xlsx

# 2. Geocodificar (gratis, sin API key)
python geocodificar_addresses.py               # todos los registros (~8h)
python geocodificar_addresses.py --limite 500  # prueba rápida (~17 min)

# 3. Enriquecer con Google Maps
python cruce_apify.py --token TU_TOKEN_APIFY --solo-grandes

# 4. Generar mapa interactivo
python mapa_v1.py
# Output: mapa_v1.html (abrir en navegador)
```

---

## Equipo

| Rol | Responsabilidad |
|---|---|
| AI Developer | Pipeline ETL, normalización IA, Agente RAG |
| Ingeniero de Datos | Scraping Apify, extracción fuentes |
| Analista de Datos | QA, KPIs, auditoría de BD |
| Analista BI | Dashboard, mapa interactivo |
| QA / Revisión | Validación de calidad |
| Documentador | Informe, bitácora, manual |
| Project Manager | Coordinación, sprints |

---

## Cronograma

| Semana | Fechas | Entregable |
|---|---|---|
| Semana 1 | Apr 12–18 | BD RUES limpia + Apify configurado + Mapa v1 |
| Semana 2 | Apr 19–25 | BD enriquecida + coordenadas + Mapa v2 |
| Semana 3 | Apr 26 – May 2 | N8N activo + campaña cemento + Dashboard |
| Semana 4 | May 3–9 | Agente IA + Demo final Argos |

---

*Proyecto universitario — Abril 2026*
