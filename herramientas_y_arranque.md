# Herramientas, Fuentes y Arranque del Proyecto
> Guía técnica operativa completa — Proyecto Ferreterías Argos | Etapa 3
> Actualizado: 11 Abril 2026

---

## PARTE 1: Stack Tecnológico Completo

### Mapa del stack por capa

```
FUENTES DE DATOS    EXTRACCIÓN/ENRICH.   PROCESAMIENTO IA    AUTOMATIZACIÓN    ENTREGA FINAL
────────────────    ──────────────────   ────────────────    ──────────────    ─────────────
RUES (CSV)          Apify                Python + pandas     N8N               Streamlit App
(34k registros)     Google Maps          fuzzywuzzy          Gmail SMTP        Dashboard Web
                    Scraper              Claude API          Cron scheduler    Excel export
Google Places API   Google Geocoding     (normalización IA)  Botón on-demand   Mapa Folium
(enriquecimiento)   API (coords)
```

---

### Tabla de herramientas detallada

| Herramienta | Para qué sirve | Cuándo usarla | Costo | Link |
|---|---|---|---|---|
| **RUES** | Base de datos oficial del gobierno con 34.135 ferreterías (CIIU 4752 y 4663). Da NIT, razón social, municipio, dirección, correo | Fuente base — ya descargada | Gratis | rues.gov.co |
| **Apify** | Plataforma de scraping. Su actor "Google Maps Scraper" extrae nombre comercial, teléfono, coordenadas, web y rating de Google Maps de forma masiva | Enriquecimiento RUES: conseguir nombre real, teléfono, coords | $5 USD gratis ≈ 2.000 registros | apify.com |
| **Google Places API** | API oficial de Google para obtener datos de negocios. Alternativa directa a Apify si se tiene presupuesto | Si se agotan créditos de Apify | Pay-per-use ($17/1000 req) | developers.google.com |
| **Google Geocoding API** | Convierte dirección de texto en coordenadas GPS (latitud/longitud) | Para registros sin coords (los del RUES) | $5/1000 req | developers.google.com |
| **N8N** | Plataforma de automatización open-source. Conecta apps y crea flujos: trigger → acción. Reemplaza Zapier pero es gratis y local | Flujo de actualización de BD + flujo correos cemento | Gratis (self-hosted local) | n8n.io |
| **Python + pandas** | Manipular y transformar datos en tablas | Pipeline ETL central (`limpiar_datos.py`) | Gratis | — |
| **fuzzywuzzy** | Compara nombres parecidos para detectar duplicados y hacer cruces entre fuentes | Deduplicación + cruce RUES vs Google Maps | Gratis (pip) | — |
| **Claude API (Haiku)** | IA generativa para normalizar nombres complicados que el script básico no puede limpiar | Casos difíciles de normalización (~1k nombres) | ~$0.001/1k tokens | console.anthropic.com |
| **Nominatim** | Geocoding gratuito (pero lento). Convierte dirección en coords | Alternativa gratuita a Google Geocoding | Gratis (1 req/seg límite) | nominatim.org |
| **openpyxl** | Leer y escribir archivos `.xlsx` desde Python | Exportar la BD final a Excel | Gratis (pip) | — |
| **Folium** | Crear mapas interactivos en Python con pins y capas | Mapa visual de ferreterías | Gratis (pip) | — |
| **Streamlit** | Crear app web rápida en Python para el dashboard | Interfaz final: dashboard + mapa + botón | Gratis | streamlit.io |
| **python-dotenv** | Cargar variables de entorno desde archivo `.env` | Guardar API keys de forma segura | Gratis (pip) | — |

---

## PARTE 2: Apify — Guía Completa de Uso

### ¿Qué es Apify y por qué lo usamos?

Apify es una plataforma de web scraping en la nube. Su actor **"Google Maps Scraper"** (también llamado "Extractor de mapas de Google") extrae datos de Google Maps de forma masiva sin necesidad de manejar APIs directamente.

**Por qué Apify y no solo la Google API:**
- Configuración visual sin código
- $5 USD gratis al registrarse ≈ 2.000 registros
- Incluye nombre comercial (el que ve el cliente en Maps, no la razón social legal)
- Maneja paginación y errores automáticamente
- Exporta en JSON o CSV listo para procesar

### Registro y primer scraping

**Paso 1 — Registrarse (10 minutos)**
1. Ir a **apify.com** → "Sign Up" con email del equipo
2. Verificar email → entrar al dashboard
3. En el menú lateral: **"Actors"** → buscar: `Google Maps Scraper`
4. El actor correcto: **"Extractor de mapas de Google"** — tiene brújula como ícono, 4.7⭐, 347K usuarios
5. Hacer clic en **"Try for free"**

**Paso 2 — Configurar el scraping de enriquecimiento**

Estrategia para este proyecto: en lugar de buscar por ciudad genérica, buscar cada ferretería específica del RUES por nombre + municipio.

```json
{
  "searchStringsArray": [
    "Ferretería Los Molinos Medellín",
    "Ferretería El Tornillo Bogotá",
    "Materiales El Constructor Manizales"
  ],
  "maxCrawledPlacesPerSearch": 3,
  "language": "es",
  "maxImages": 0,
  "maxReviews": 0
}
```

Para búsquedas exploratorias por ciudad (para descubrir nuevas ferreterías):
```json
{
  "searchStringsArray": [
    "ferreterías Medellín",
    "depósito materiales construcción Bogotá",
    "ferreterías Manizales",
    "materiales construcción Pereira"
  ],
  "maxCrawledPlacesPerSearch": 100,
  "language": "es",
  "maxImages": 0,
  "maxReviews": 0
}
```

**Paso 3 — Descargar y usar el output**
1. Cuando termine el scraping: estado = `Succeeded` (verde)
2. Pestaña **"Dataset"** → botón **"Export"** → seleccionar **JSON**
3. Guardar como: `apify_output_[ciudad]_[fecha].json`
4. Mover a la carpeta `Etapa3/` del proyecto

**Campos que devuelve Apify (los más útiles para este proyecto):**
```
title           → nombre del negocio en Google Maps ⭐
address         → dirección completa
city            → ciudad
state           → departamento
phone           → teléfono ⭐
latitude        → coordenada lat ⭐
longitude       → coordenada lon ⭐
website         → página web
totalScore      → rating (1-5) → señal de negocio activo
categoryName    → categoría en Google Maps
```

### Gestión de créditos Apify

| Escenario | Registros | Costo estimado |
|---|---|---|
| Prueba piloto (100 ferreterías) | 100 | ~$0.25 |
| Regiones prioritarias (14.642) | 14.642 | ~$36 |
| Nacional completo (34.135) | 34.135 | ~$85 |
| Plan gratuito disponible | ≈2.000 | $0 |

**Estrategia con el plan gratuito ($5):**
1. Usar los 2.000 registros gratis en las ferreterías de Antioquia (4.138 → priorizar las de Medellín primero)
2. Si se necesita más, los integrantes del equipo pueden crear cuentas adicionales (cada cuenta tiene $5 gratis)
3. Alternativa: usar Nominatim para geocodificar gratuitamente (solo lat/lon, sin nombre ni teléfono)

---

## PARTE 3: N8N — Instalación y Flujos

### Instalación local (recomendado: Docker)

**Opción A — Con Docker (más estable):**
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```
Acceder en: **http://localhost:5678**

**Opción B — Con npm:**
```bash
npm install -g n8n
n8n start
```

**Opción C — Sin instalación (para pruebas rápidas):**
Usar **n8n.cloud** — tiene plan gratuito con 5.000 ejecuciones/mes.

---

### Flujo 1 — Actualización de Base de Datos

**Trigger:** Botón manual (on-demand) O scheduler (cada 3 meses)

```
[Trigger: Manual Button / Cron "0 0 1 */3 *"]
    │
    ▼
[Execute Command]
    └─ python limpiar_datos.py
    
    │
    ▼
[HTTP Request a Apify API]
    └─ POST /v2/acts/~google-maps-scraper/runs
    └─ Body: { searchStringsArray: [...ferreterías RUES] }
    
    │
    ▼
[Wait] (esperar 10-20 min que termine Apify)
    
    │
    ▼
[HTTP Request a Apify API]
    └─ GET /v2/datasets/{runId}/items
    └─ Descargar el JSON de resultados
    
    │
    ▼
[Execute Command]
    └─ python cruzar_rues_google.py
    
    │
    ▼
[Gmail / SMTP]
    └─ Enviar notificación al equipo:
       "✅ BD actualizada: X registros nuevos, Y actualizados"
```

### Flujo 2 — Verificación ¿Vende Cemento?

**Trigger:** Nueva ferretería en BD sin campo `vende_cemento` completado

```
[Trigger: Schedule / Webhook]
    │
    ▼
[Read Excel / DB]
    └─ Obtener ferreterías donde vende_cemento = NULL o ""
    └─ Filtrar las que tienen correo disponible
    
    │
    ▼
[Loop sobre cada ferretería]
    │
    ▼
[Gmail node - Enviar correo]
    └─ Para: {correo_rues}
    └─ Asunto: "Consulta sobre disponibilidad de productos"
    └─ Cuerpo:
       "Estimado equipo de {nombre_comercial},
        
        Mi nombre es [Nombre], del equipo de investigación de mercado.
        Estamos realizando un directorio de ferreterías y distribuidoras 
        de materiales de construcción en Colombia.
        
        ¿Su establecimiento comercializa cemento?
        
        Por favor responda simplemente: SÍ o NO
        
        Muchas gracias por su colaboración."
    
    │
    ▼
[Wait 48 horas]
    
    │
    ▼
[Check respuesta]
    ├─ Si respondió SÍ → actualizar vende_cemento = "Sí"
    ├─ Si respondió NO → actualizar vende_cemento = "No"  
    └─ Si no respondió → retry 1 vez → si sigue sin respuesta → "No verificado"
```

**Límites de envío para Gmail SMTP:**
- Gmail personal: 500 correos/día
- Gmail Workspace (G Suite): 2.000 correos/día
- Mailgun (gratis): 1.000 correos/día en plan gratuito
- SendGrid (gratis): 100 correos/día en plan gratuito

---

## PARTE 4: Códigos CIIU — Referencia

Los códigos que se usaron para extraer el RUES:

| CIIU | Descripción | Tipo de negocio | Registros en RUES |
|---|---|---|---|
| **4752** | Comercio al por menor de artículos de ferretería, pinturas y productos de vidrio | Ferreterías de barrio | 26.955 (79%) |
| **4663** | Comercio al por mayor de materiales de construcción, artículos de ferretería | Depósitos mayoristas | 7.180 (21%) |

**Palabras clave de búsqueda para Apify:**
```
ferreterías
depósito de materiales
venta de materiales de construcción
distribuidora de materiales
almacén de ferretería
pinturas y ferretería
materiales de construcción
bloques y cemento
distribuidora de cemento
```

---

## PARTE 5: Pipeline ETL — Paso a Paso Completo

### Arranque inmediato — Procesar el RUES

**Paso 1 — Instalar dependencias (solo primera vez)**
```bash
pip install pandas fuzzywuzzy python-Levenshtein openpyxl requests anthropic python-dotenv
```

**Paso 2 — Cargar el RUES**
```python
import pandas as pd

df = pd.read_csv(
    'RUES_Ferreterias_7-4-2026 16_5_4(in).csv',
    encoding='latin-1',
    sep=';'
)
# 34.135 registros, 16 columnas
print(f"Total registros: {len(df)}")
print(df.columns.tolist())
```

**Paso 3 — Ejecutar el pipeline completo**
```bash
python limpiar_datos.py
```

Output esperado:
```
Cargando CSV del RUES...
Total registros: 34135
Duplicados eliminados: 10
Correos personales clasificados: 32338 (94.7%)
Correos corporativos: 1797 (5.3%)
Exportado: ferreterias_base_limpia.xlsx
✅ Pipeline completado
```

---

### Cruce RUES + Apify (Semana 2)

```python
import pandas as pd
from fuzzywuzzy import fuzz

# Cargar ambas fuentes
df_rues  = pd.read_excel("ferreterias_base_limpia.xlsx")
df_apify = pd.read_json("apify_output.json")

# Función de cruce por nombre + municipio
def encontrar_match(nombre_rues, municipio_rues, df_apify, umbral=85):
    candidatos = df_apify[df_apify['city'].str.lower() == municipio_rues.lower()]
    
    mejor_score = 0
    mejor_match = None
    
    for _, row in candidatos.iterrows():
        score = fuzz.token_sort_ratio(nombre_rues, row['title'])
        if score > mejor_score:
            mejor_score = score
            mejor_match = row
    
    if mejor_score >= umbral:
        return mejor_match, mejor_score
    return None, 0

# Aplicar a toda la BD
resultados = []
for _, ferreteria in df_rues.iterrows():
    match, score = encontrar_match(
        ferreteria['razon_social'],
        ferreteria['municipio'],
        df_apify
    )
    if match is not None:
        resultados.append({
            'nombre_comercial': match['title'],  # ← nombre real de Google Maps
            'telefono':         match['phone'],
            'latitud':          match['latitude'],
            'longitud':         match['longitude'],
            'pagina_web':       match['website'],
            'calificacion':     match['totalScore'],
            'match_score':      score,
            'match_google':     'Sí'
        })
    else:
        resultados.append({
            'nombre_comercial': None,
            'match_google':     'No'
        })
```

---

### Normalización con IA (Claude Haiku) — Para nombres difíciles

```python
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def normalizar_nombre_con_ia(nombre_sucio: str) -> str:
    """Para nombres que el script básico no puede limpiar bien."""
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=60,
        messages=[{
            "role": "user",
            "content": (
                "Eres un normalizador de nombres de ferreterías colombianas. "
                "Devuelve SOLO el nombre comercial limpio. Sin sufijos legales "
                "(SAS, LTDA, EU, S.A.), sin ciudad, sin apellidos de persona si "
                "el nombre es una persona natural. Formato: 'Ferretería Nombre'. "
                f"Nombre a normalizar: '{nombre_sucio}'"
            )
        }]
    )
    return response.content[0].text.strip()

# Usar solo en casos donde no hay match de Google Maps
nombres_sin_match = df_rues[df_rues['match_google'] == 'No']['razon_social'].head(50)
for nombre in nombres_sin_match:
    print(f"ANTES: {nombre}")
    print(f"DESPUÉS: {normalizar_nombre_con_ia(nombre)}\n")
```

---

## PARTE 6: Fuentes de Datos Confiables

### Fuentes oficiales

| Fuente | URL | Qué tiene | Cómo usarla |
|---|---|---|---|
| **RUES** | rues.gov.co | Registro oficial de todas las empresas de Colombia con NIT y razón social | Ya descargado con CIIU 4752 y 4663 — 34.135 registros |
| **Confecámaras** | confecamaras.co | Estadísticas y datos regionales de Cámaras de Comercio | Contexto y validación |
| **DANE** | dane.gov.co | Clasificación CIIU oficial de Colombia | Verificar clasificaciones |
| **Datos Abiertos Colombia** | datos.gov.co | Datasets gubernamentales | Buscar "ferreterías" o CIIU 4752 |

### Fuentes comerciales

| Fuente | URL | Qué tiene | Limitación |
|---|---|---|---|
| **Google Maps via Apify** | apify.com | Nombre comercial, coords, teléfono, web, rating | Puede incluir negocios cerrados |
| **Google Places API** | developers.google.com | Mismo que Apify pero con API oficial | Pay-per-use |
| **Páginas Amarillas** | paginasamarillas.com.co | Directorio con teléfonos | Datos desactualizados, sin coords |

### Jerarquía de confianza para los datos

```
1° RUES (oficial, tiene NIT, validado por Cámara de Comercio)
2° Google Maps via Apify (masivo, nombre comercial, coordenadas)
3° Google Geocoding API (para convertir dirección en coords)
4° Páginas Amarillas (complementario para teléfonos extra)
5° Respuesta directa N8N (para campo vende_cemento)
```

---

## PARTE 7: Variables de Entorno

Crear archivo `.env` en la raíz del proyecto (NUNCA subir a GitHub):

```
# APIs principales
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxx
APIFY_TOKEN=apify_api_xxxxxxxxxxxxxxx
GOOGLE_MAPS_API_KEY=AIzaxxxxxxxxxxxxxxx

# Correo para N8N
SMTP_EMAIL=equipo.argos@gmail.com
SMTP_PASSWORD=xxxxxxxxxxxxxxx

# Configuración
RUES_CSV_PATH=RUES_Ferreterias_7-4-2026 16_5_4(in).csv
OUTPUT_EXCEL=ferreterias_argos_final.xlsx
REGIONES_PRIORITARIAS=BOGOTA,ANTIOQUIA,CUNDINAMARCA,RISARALDA,CALDAS,QUINDIO
```

Cargar en Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
```

Instalar: `pip install python-dotenv`

---

## PARTE 8: Checklist de Arranque

### Lo que debe pasar esta semana (Semana 1)

- [ ] **Daniel** — Adaptar `limpiar_datos.py` para cargar el CSV del RUES (encoding latin-1, sep=';')
- [ ] **Daniel** — Agregar columna `tipo_correo` (Personal vs. Corporativo)
- [ ] **Daniel** — Exportar subconjunto Excel de regiones prioritarias para el profe
- [ ] **Sebastián** — Crear cuenta Apify + configurar primer scraping de prueba
- [ ] **Equipo técnico** — Instalar N8N local y crear flujo de prueba simple
- [ ] **Todo el equipo** — Crear carpeta compartida en Google Drive o GitHub con los archivos del proyecto
- [ ] **Todo el equipo** — Crear archivo `.env` con sus propias keys (cada uno tiene las suyas)

### Tiempo estimado para tener datos reales

| Tarea | Tiempo |
|---|---|
| Adaptar y correr `limpiar_datos.py` con RUES | 30 min |
| Exportar Excel de regiones prioritarias | 10 min |
| Registrarse en Apify y primer scraping | 20 min |
| Esperar scraping Apify (automático) | 10-20 min |
| Instalar N8N con Docker | 15 min |
| **Total para tener el primer entregable** | **~90 min** |
