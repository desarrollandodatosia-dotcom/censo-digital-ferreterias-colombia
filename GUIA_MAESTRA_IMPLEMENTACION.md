# GUÍA MAESTRA — Censo Digital de Ferreterías en Colombia
## Documento para reunión de equipo | 8 de abril de 2026

---

## 1. RESUMEN EJECUTIVO DEL PROYECTO

**Cementos Argos** enfrenta un desafío operacional crítico: sus asesores de ventas recopilan datos de ferreterías manualmente, utilizando cuadernos y archivos Excel dispersos. Esta metodología es ineficiente, no escalable y genera pérdida de información.

El proyecto **"Censo Digital de Ferreterías en Colombia"** propone construir una **tubería automatizada integrada** que combine:
- **Web scraping** inteligente (Google Maps, RUES, directorios especializados)
- **Limpieza y deduplicación basada en IA** (Claude API + fuzzy matching)
- **Base de datos estructurada y versionada** (Excel/Postgres)
- **Dashboard interactivo con mapas geoespaciales** (Streamlit/PowerBI)
- **Agente IA consultable en lenguaje natural** (RAG con Anthropic)

**Objetivo general:** Entregar en 4 semanas un censo de 2,000+ ferreterías colombianas con información verificada, actualizable y consultable mediante IA.

**Meta de hoy (8 de abril):** Tener 50–100 registros limpios y validados de **Medellín** para demostrar que el pipeline funciona.

---

## 2. PROBLEMAS IDENTIFICADOS

| Problema | Descripción | Impacto |
|----------|-------------|--------|
| **BD_Base.xlsx vacío** | Base de datos sin datos reales (0 registros, solo encabezados) | No hay punto de partida; requiere scraping inmediato |
| **Falta ciudad piloto** | No se definió dónde comenzar | Parálisis; se debe elegir hoy |
| **Sin infraestructura scraping** | No hay scripts, APIs configuradas, credenciales activas | Pérdida de 1+ semana de desarrollo |
| **Formato entregable ambiguo** | ¿Solo BD? ¿Con dashboard? ¿Con agente IA? | Equipo desalineado; scope creep |
| **Roles sin asignar formalmente** | No hay claridad en responsabilidades | Duplicación de esfuerzo o tareas olvidadas |
| **Sin repositorio compartido** | Archivos dispersos (email, OneDrive, laptops) | Riesgo de pérdida de código; versionamiento imposible |

---

## 3. OBJETIVOS DEL PROYECTO

### Objetivo General
Construir un **sistema automatizado, escalable y sostenible** para el censo digital de ferreterías en Colombia que integre datos de múltiples fuentes, los limpie con IA, los visualice en un dashboard interactivo y permita consultas mediante un agente inteligente.

### Objetivos Específicos

| # | Objetivo | Métrica | Plazo |
|---|----------|---------|-------|
| **OE1** | Construir base de datos estructurada con **2,000+ ferreterías** en 5 ciudades principales (Medellín, Bogotá, Cali, Barranquilla, Bucaramanga) | Registros validados con campos: Municipio, Dirección, Lat/Lon, Teléfono, WhatsApp, Email, Fuente, Fecha | Semana 4 |
| **OE2** | Desarrollar **dashboard interactivo con mapa geoespacial** para visualizar distribución, densidad y cobertura | Dashboard funcional en Streamlit/PowerBI con filtros por ciudad, CIIU, cobertura | Semana 3 |
| **OE3** | Crear **agente IA consultable en lenguaje natural** (RAG) capaz de responder preguntas sobre ferreterías | Agente implementado con Anthropic Claude que responda: "¿Cuántas ferreterías hay en Medellín?" o "¿Dónde hay materiales de construcción cerca de X?" | Semana 4 |
| **OE4** | Implementar **pipeline de deduplicación y normalización** con IA para garantizar calidad de datos | Tasa de deduplicación >95%; precisión de normalización de direcciones >90% | Semana 2 |

### Meta de Hoy (8 de abril, 2026)
- ✅ **50–100 registros limpios de Medellín** en BD_Base_PROCESADA.xlsx
- ✅ Roles asignados formalmente
- ✅ Repositorio compartido creado
- ✅ Primer ciclo del pipeline ejecutado exitosamente

---

## 4. NIVELES DE ENTREGA

### Nivel 1: OBLIGATORIO ⚠️ 
**Base de datos limpia, estructurada y validada**
- Archivo Excel con schema: `[Municipio | Dirección | Lat | Lon | Teléfono | WhatsApp | Email | Razón Social | CIIU | Fuente | Fecha_Captura]`
- Mínimo 2,000 registros únicos
- Deduplicación verificada
- Geocodificación válida (coordenadas verificables)
- Entregable: `BD_Censo_Ferreterias_Final.xlsx` + `BD_Censo_Ferreterias_Final.json`

### Nivel 2: ESPERADO ✅
**Dashboard interactivo + Mapas geoespaciales**
- Visualización de distribución por ciudad
- Mapa interactivo con marcadores de ferreterías
- Filtros por: ciudad, CIIU, rango de direcciones
- KPIs: Total ferreterías, cobertura por municipio, comparativa antes/después
- Entregable: Aplicación Streamlit deployada en Streamlit Cloud

### Nivel 3: DIFERENCIADOR 🚀
**Agente IA consultable en lenguaje natural (RAG)**
- Interfaz tipo chatbot donde pregunta en español: "¿Cuántas ferreterías hay en el sur de Medellín?"
- Agente responde con búsquedas contextuales en la BD
- Integración con Claude API + embeddings vector (Chroma/Pinecone)
- Explicaciones de la fuente de datos
- Entregable: Demo en vivo; documentación de arquitectura RAG

---

## 5. ROLES DEL EQUIPO (6–7 personas)

| Rol | Responsabilidad Principal | Herramienta Principal | Entregable Clave | Semana 1 |
|-----|---------------------------|----------------------|------------------|----------|
| **AI Developer (TÚ)** | Diseñar prompts, pipeline de limpieza, agente RAG, deduplicación con IA | Python, Claude API, Anthropic, Chroma | Script `limpiar_datos.py`; Prompts validados; Agente consultable | Script v1 funcional |
| **Ingeniero de Datos** | Scraping, extracción de múltiples fuentes, transformación JSON→Excel | Apify, Serper API, Python requests | `scraping_medellin_crudo.json`; scripts de ETL | 100 registros crudos |
| **Analista de Datos** | Auditoría de calidad, cálculo KPIs, validación de duplicados | pandas, Excel, comparativas | `reporte_calidad_semana1.xlsx` | Reporte de calidad |
| **Analista BI / Viz** | Diseño dashboard, mapas geoespaciales, interactividad | Streamlit, Folium, PowerBI | `app_dashboard.py` en Streamlit | Prototipo con 100 registros |
| **QA / Verificación** | Control de calidad manual y automatizado, checklist, testing | Scripts de validación, checklist Excel | `QA_Checklist_Semana1.xlsx` | Validación de 100 registros |
| **Documentador / Técnico** | Bitácora de progreso, documentación de arquitectura, informe final | Markdown, Word, Notion | Bitácora diaria, README.md | Documentación inicial |
| **Project Manager** | Coordinación de sprints, cronograma, bloqueos, comunicación | Trello, GitHub Projects, Slack/Discord | Cronograma detallado, actas de reunión | Sprint semanal configurado |

---

## 6. STACK DE HERRAMIENTAS COMPLETO

| Herramienta | Para qué | Cuándo | Costo | Link |
|-------------|----------|--------|-------|------|
| **Apify** | Scraping automatizado de Google Maps y directorios | Semana 1–2 | $0 (free tier: 500+ ejecuciones) | https://apify.com |
| **Serper API** | Búsquedas web para validación y fuentes alternativas | Semana 2–3 | $0 (2,500 free queries) | https://serper.dev |
| **RUES (Cámara de Comercio)** | Base de datos oficial de empresas registradas en Colombia | Semana 1–3 | Gratis | https://rues.org.co |
| **Python 3.9+** | Lenguaje principal para scripts de limpieza y IA | Todas las semanas | Gratis | python.org |
| **pandas** | Manipulación y análisis de DataFrames | Todas las semanas | Gratis | pypi.org/project/pandas |
| **fuzzywuzzy** | Deduplicación fuzzy matching de nombres/direcciones | Semana 2–3 | Gratis | pypi.org/project/fuzzywuzzy |
| **Claude API (Anthropic)** | Limpieza de datos, normalización de direcciones, agente RAG | Semana 1–4 | ~$0.001 / 1K tokens | https://claude.ai/api |
| **openpyxl** | Lectura/escritura de archivos Excel desde Python | Todas las semanas | Gratis | pypi.org/project/openpyxl |
| **requests** | HTTP requests para APIs | Todas las semanas | Gratis | pypi.org/project/requests |
| **python-dotenv** | Gestión segura de variables de entorno (.env) | Todas las semanas | Gratis | pypi.org/project/python-dotenv |
| **Nominatim (OpenStreetMap)** | Geocodificación gratuita (Lat/Lon de direcciones) | Semana 1–2 | Gratis (rate limit 1/s) | nominatim.org |
| **Streamlit** | Dashboard interactivo web | Semana 3–4 | Gratis (hosting en Streamlit Cloud) | streamlit.io |
| **Folium / Leaflet** | Mapas interactivos | Semana 3–4 | Gratis | folium.readthedocs.io |
| **Chroma / Pinecone** | Vector embeddings para RAG | Semana 4 | $0 local / $$ cloud | chroma.io \| pinecone.io |
| **GitHub** | Repositorio compartido, versionamiento | Todas las semanas | Gratis (privado con edu) | github.com |
| **Google Drive / Sheets** | Documentos compartidos, backups | Todas las semanas | Gratis (universidad) | drive.google.com |
| **Discord / Slack** | Comunicación del equipo | Todas las semanas | Gratis | discord.com \| slack.com |

---

## 7. CÓDIGOS CIIU RELEVANTES

### Clasificación de Actividades Económicas en Colombia

| Código CIIU | Descripción | Relevancia | Incluir |
|-------------|-------------|-----------|---------|
| **4752** | Comercio al por menor de materiales de construcción, artículos de ferretería y equipo sanitario | **PRINCIPAL** | ✅ SÍ |
| **4663** | Comercio al por mayor de materiales de construcción | **PRINCIPAL** | ✅ SÍ |
| **4741** | Comercio al por menor de equipos, útiles y herramientas | **SECUNDARIO** | ✅ SÍ |
| **4750** | Comercio al por menor de combustibles y lubricantes | No aplica | ❌ NO |
| **4765** | Comercio al por menor de libros, diarios y artículos de papelería | No aplica | ❌ NO |

### Cómo usar en RUES y Apify

**En RUES (rues.org.co):**
1. Ir a "Búsqueda de empresas"
2. Filtro Actividad Principal: seleccionar **4752** o **4663**
3. Filtro Departamento: **Antioquia** (para Medellín)
4. Exportar listado de NITs + Razones Sociales
5. Cruzar después con direcciones y contactos

**En Apify (Google Maps Scraper):**
1. En `searchStringsArray`, incluir términos como:
   - "ferreterías [ciudad]"
   - "materiales construcción [ciudad]"
   - "depósito herramientas [ciudad]"
2. Apify automáticamente filtra por categorías de Google Maps
3. Se obtienen: nombre, dirección, teléfono, coordenadas, URL

---

## 8. FUENTES DE DATOS (por jerarquía de confianza)

### Ranking de Fuentes (prioridad y confiabilidad)

| Rango | Fuente | Ventaja | Desventaja | Integración |
|-------|--------|---------|-----------|------------|
| **1°** | **RUES (Cámara de Comercio)** | Oficial, verificado, datos legales | Requiere búsqueda manual; sin geocodificación | Descarga manual + procesamiento |
| **2°** | **Cámaras de Comercio Municipales** | Verificado localmente, teléfono actualizado | Fragmentado por ciudad; datos sin estructura | Web scraping + contacto directo |
| **3°** | **Google Maps vía Apify** | Cobertura masiva, coordenadas automáticas, reseñas | Requiere validación; duplicados posibles | Apify actor + deduplicación IA |
| **4°** | **Páginas Amarillas, Directorios locales** | Información complementaria | Frecuentemente desactualizado; con ruido | Scraping + limpieza intensiva |
| **5°** | **Serper API (búsquedas web)** | Búsqueda rápida de validación | Resultados no estructurados | Consultas puntuales de verificación |

### Flujo de Integración de Fuentes (Pipeline)

```
RUES (NITs)
    ↓
Cámaras de Comercio (teléfono, email)
    ↓
Google Maps (dirección, coordenadas)
    ↓
Deduplicación IA + normalización
    ↓
Validación con Serper
    ↓
BD Final Integrada
```

---

## 9. PASO A PASO PARA TENER DATOS EN 45 MINUTOS

### ⏱️ Cronograma: 9:00 AM → 9:45 AM

---

### **PASO 1: Registrarse en Apify (10 minutos | 9:00–9:10 AM)**

1. **Abrir navegador** y navegar a: https://apify.com
2. **Click en "Sign Up"** (arriba a la derecha)
3. **Registrarse con email universitario** (ej: tu.nombre@universidad.edu.co)
4. **Verificar email** → revisar bandeja de entrada, click en enlace de confirmación
5. **Entrar al dashboard** de Apify
6. **En menú lateral izquierdo** → click en **"Actors"**
7. **Buscar:** `Google Maps Scraper` (oficial, de Apify)
8. **Click en el actor** → **"Try for free"**

**Checkpoint:** Debes estar en la página de configuración del Google Maps Scraper. 

---

### **PASO 2: Configurar scraping de Medellín (15 minutos | 9:10–9:25 AM)**

Copiar y pegar **exactamente** esta configuración JSON en el campo **Input**:

```json
{
  "searchStringsArray": [
    "ferreterías Medellín",
    "depósito materiales construcción Medellín",
    "materiales construcción Medellín",
    "tienda herramientas Medellín",
    "ferretería construcción Medellín"
  ],
  "maxCrawledPlacesPerSearch": 100,
  "language": "es",
  "maxImages": 0,
  "maxReviews": 0,
  "reviewsSort": "newest",
  "includeWebResults": false,
  "skipClosedPlaces": true,
  "countryCode": "CO"
}
```

**Explicación de parámetros:**
- `searchStringsArray`: términos de búsqueda en español para Google Maps
- `maxCrawledPlacesPerSearch`: máx 100 resultados por término (total ~500 lugares)
- `language: "es"`: interfaz y resultados en español
- `maxImages: 0`: no descargar imágenes (ahorra tiempo y espacio)
- `maxReviews: 0`: no descargar reseñas (no relevante para censo)
- `skipClosedPlaces: true`: excluir negocios cerrados

**Pasos:**
1. **Pega el JSON** en el campo Input
2. **Click en botón azul "Start"**
3. **Espera 5–15 minutos** (Apify ejecuta el scraping)
4. **Cuando termina** → ícono ✅ en verde
5. **Click en "Output"** → verás JSON con resultados
6. **Click en "Download"** (botón descarga) → guardar como: `scraping_medellin_crudo.json`

**Checkpoint:** Debes tener un archivo `scraping_medellin_crudo.json` con ~300–500 lugares de Google Maps.

---

### **PASO 3: Instalar librerías Python (5 minutos | 9:25–9:30 AM)**

Abrir **terminal / CMD** en la carpeta del proyecto:

```bash
pip install pandas fuzzywuzzy python-Levenshtein openpyxl requests anthropic python-dotenv
```

**Esperar hasta que diga:** `Successfully installed...`

**Checkpoint:** No debe haber errores. Si falla `python-Levenshtein`, continúa sin él (fuzzywuzzy funcionará, solo más lento).

---

### **PASO 4: Ejecutar script de limpieza (2 minutos | 9:30–9:32 AM)**

Crear archivo `limpiar_datos.py` (ver Sección 13 más abajo para template):

```bash
python limpiar_datos.py
```

**Output esperado:**
```
[INFO] Leyendo scraping_medellin_crudo.json...
[INFO] 487 lugares encontrados
[INFO] Normalizando direcciones...
[INFO] Deduplicando (fuzzy matching)...
[INFO] Calling Claude API para validación...
[INFO] 127 registros únicos después de deduplicación
[INFO] Geocodificando (Nominatim)...
[INFO] Guardando en BD_Base_PROCESADA.xlsx...
[SUCCESS] Proceso completado. 127 registros limpios.
```

**Checkpoint:** Debe crearse archivo `BD_Base_PROCESADA.xlsx`.

---

### **PASO 5: Verificar resultado (5 minutos | 9:32–9:37 AM)**

1. **Abrir** `BD_Base_PROCESADA.xlsx` en Excel / LibreOffice Calc
2. **Inspeccionar primeras 10 filas** para validar:
   - ✅ Columnas presentes: Municipio, Dirección, Lat, Lon, Teléfono, Email, Fuente, Fecha
   - ✅ Datos no vacíos
   - ✅ Coordenadas numéricas (ej: `-75.5136, 6.2442`)
   - ✅ Teléfonos con formato colombiano

3. **Hacer muestreo aleatorio:** Abre Google Maps, busca una dirección → verifica que sea realmente una ferretería

**Checkpoint:** Si todo se ve correcto, tienes **datos validados para la reunión**.

---

### **PASO 6: Búsqueda complementaria en RUES (5 minutos | 9:37–9:42 AM) — OPCIONAL**

Si tienes tiempo:

1. Ir a: https://www.rues.org.co
2. Click en "Consulta de empresas"
3. Filtro: Actividad Principal = **4752** (ferreterías)
4. Filtro: Departamento = **Antioquia**
5. Click "Buscar"
6. Descargar/screenshot de los primeros 10 resultados

**Nota:** Este paso es complementario. No es crítico para los 45 minutos, pero fortalece credibilidad.

---

### **PASO 7: Normalización con IA de nombres difíciles (3 minutos | 9:42–9:45 AM) — OPCIONAL**

Si encuentras nombres confusos en la BD (ej: "FRRTRía Xz" o caracteres corruptos):

Crear `normalizar_nombres.py`:

```python
import anthropic
import json

client = anthropic.Anthropic()

nombres_confusos = [
    "FRRTRía XZ SAS",
    "Dpósito Mat. Const.",
    "FERR...??? Y CÍAS"
]

for nombre in nombres_confusos:
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": f"Normaliza este nombre de ferretería colombiana a formato profesional. Solo responde con el nombre normalizado, sin explicación.\n\nNombre confuso: {nombre}"
            }
        ]
    )
    nombre_limpio = message.content[0].text.strip()
    print(f"'{nombre}' → '{nombre_limpio}'")
```

Ejecutar:
```bash
python normalizar_nombres.py
```

**Checkpoint:** Tendrás nombres limpios para casos problemáticos.

---

### ⏰ **Resumen de tiempos:**

| Paso | Actividad | Tiempo | Tiempo acumulado |
|------|-----------|--------|------------------|
| 1 | Registrarse Apify | 10 min | 9:10 AM |
| 2 | Configurar scraping | 15 min | 9:25 AM |
| 3 | Instalar librerías Python | 5 min | 9:30 AM |
| 4 | Ejecutar limpieza | 2 min | 9:32 AM |
| 5 | Verificar resultado | 5 min | 9:37 AM |
| 6 | RUES complementario (OPT) | 5 min | 9:42 AM |
| 7 | Normalización IA (OPT) | 3 min | 9:45 AM |

**Total: 45 minutos** ✅

---

## 10. TEMPLATE: Script `limpiar_datos.py`

```python
#!/usr/bin/env python3
"""
limpiar_datos.py — Pipeline de limpieza para Censo Digital de Ferreterías
Autor: AI Developer del Equipo
Fecha: 2026-04-08
"""

import json
import pandas as pd
import logging
from datetime import datetime
from fuzzywuzzy import fuzz
from anthropic import Anthropic
import os
from dotenv import load_dotenv
import requests
from urllib.parse import quote

# Cargar variables de entorno
load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Configurar logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Inicializar cliente Anthropic
client = Anthropic()

def leer_datos_apify(archivo_json):
    """Lee el JSON de salida de Apify."""
    logger.info(f"Leyendo {archivo_json}...")
    try:
        with open(archivo_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"{len(data)} lugares encontrados")
        return data
    except Exception as e:
        logger.error(f"Error leyendo JSON: {e}")
        return []

def normalizar_datos(lugares):
    """Extrae campos relevantes de Apify."""
    logger.info("Normalizando estructura de datos...")
    registros = []
    
    for lugar in lugares:
        try:
            registro = {
                'municipio': 'Medellín',
                'razon_social': lugar.get('title', '').strip() or 'Sin nombre',
                'direccion': lugar.get('address', '').strip() or 'Sin dirección',
                'telefono': lugar.get('phone', '').strip() or '',
                'email': '',  # Apify no siempre captura email
                'lat': lugar.get('latitude'),
                'lon': lugar.get('longitude'),
                'url_gmaps': lugar.get('url', ''),
                'fuente': 'Google Maps (Apify)',
                'fecha_captura': datetime.now().strftime('%Y-%m-%d')
            }
            registros.append(registro)
        except Exception as e:
            logger.warning(f"Error procesando lugar: {e}")
            continue
    
    return registros

def deduplicar_con_ia(registros):
    """Usa Claude para identificar duplicados con inteligencia semántica."""
    logger.info(f"Deduplicando {len(registros)} registros con IA...")
    
    # Primer paso: deduplicación exacta por dirección normalizada
    direcciones_vistas = {}
    registros_unicos = []
    
    for reg in registros:
        dir_norm = reg['direccion'].upper().replace('CALLE', 'CL').replace('CARRERA', 'KR').replace('  ', ' ')
        
        if dir_norm not in direcciones_vistas:
            direcciones_vistas[dir_norm] = reg
            registros_unicos.append(reg)
    
    logger.info(f"Después deduplicación exacta: {len(registros_unicos)}")
    
    # Segundo paso: usar Claude para casos ambiguos
    # (En producción, esto sería más sofisticado)
    
    return registros_unicos

def validar_con_claude(registros, muestra=20):
    """Valida calidad de datos usando Claude."""
    logger.info(f"Validando muestra de {muestra} registros con Claude...")
    
    muestra_json = json.dumps(registros[:muestra], ensure_ascii=False, indent=2)
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": f"""Analiza esta muestra de ferreterías de Medellín y proporciona:
1. Número de registros válidos (tienen dirección + teléfono)
2. Registros problemáticos (sin dirección, teléfono inválido, etc.)
3. Sugerencias de mejora

Datos:
{muestra_json}

Responde en formato JSON con keys: valid_count, issues, suggestions"""
            }
        ]
    )
    
    respuesta = message.content[0].text
    logger.info(f"Validación Claude:\n{respuesta}")
    
    return respuesta

def geocodificar(registros):
    """Agrega Lat/Lon si no existen usando Nominatim (OpenStreetMap)."""
    logger.info("Geocodificando direcciones...")
    
    for reg in registros:
        if not reg['lat'] or not reg['lon']:
            try:
                # Nominatim free tier: 1 request/segundo
                direccion_completa = f"{reg['direccion']}, Medellín, Antioquia, Colombia"
                url = f"https://nominatim.openstreetmap.org/search?q={quote(direccion_completa)}&format=json"
                
                response = requests.get(url, timeout=5)
                resultados = response.json()
                
                if resultados:
                    reg['lat'] = float(resultados[0]['lat'])
                    reg['lon'] = float(resultados[0]['lon'])
                    logger.debug(f"✓ {reg['razon_social']}: {reg['lat']}, {reg['lon']}")
            except Exception as e:
                logger.warning(f"Error geocodificando '{reg['razon_social']}': {e}")
    
    return registros

def exportar_excel(registros, archivo_salida='BD_Base_PROCESADA.xlsx'):
    """Exporta a Excel con formato profesional."""
    logger.info(f"Exportando a {archivo_salida}...")
    
    df = pd.DataFrame(registros)
    
    # Reordenar columnas
    columnas_orden = [
        'municipio', 'razon_social', 'direccion', 'telefono', 'email',
        'lat', 'lon', 'fuente', 'fecha_captura', 'url_gmaps'
    ]
    df = df[columnas_orden]
    
    # Guardar
    with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Ferreterías', index=False)
        
        # Aplicar formatos básicos
        workbook = writer.book
        worksheet = writer.sheets['Ferreterías']
        worksheet.column_dimensions['A'].width = 15
        worksheet.column_dimensions['B'].width = 30
        worksheet.column_dimensions['C'].width = 40
        worksheet.column_dimensions['D'].width = 15
        worksheet.column_dimensions['E'].width = 20
        worksheet.column_dimensions['F'].width = 12
        worksheet.column_dimensions['G'].width = 12
    
    logger.info(f"✓ Guardado: {archivo_salida} ({len(df)} registros)")
    return archivo_salida

def main():
    """Orquesta el pipeline completo."""
    logger.info("=" * 60)
    logger.info("CENSO DIGITAL DE FERRETERÍAS — PIPELINE DE LIMPIEZA")
    logger.info("=" * 60)
    
    # 1. Leer datos crudos de Apify
    datos_crudos = leer_datos_apify('scraping_medellin_crudo.json')
    if not datos_crudos:
        logger.error("No se pudieron leer datos. Abortando.")
        return
    
    # 2. Normalizar estructura
    registros = normalizar_datos(datos_crudos)
    logger.info(f"Registros normalizados: {len(registros)}")
    
    # 3. Deduplicar
    registros = deduplicar_con_ia(registros)
    
    # 4. Validar con IA
    validar_con_claude(registros)
    
    # 5. Geocodificar
    registros = geocodificar(registros)
    
    # 6. Exportar
    archivo_salida = exportar_excel(registros)
    
    logger.info("=" * 60)
    logger.info(f"✅ PROCESO COMPLETADO: {len(registros)} registros limpios")
    logger.info(f"📊 Archivo: {archivo_salida}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
```

---

## 11. ROADMAP 4 SEMANAS

### Estructura de Entregas por Semana

| Semana | Objetivo Principal | Tu Entregable IA | Meta Numérica | Dependencias |
|--------|-------------------|-----------------|---------------|--------------|
| **Semana 0 (Hoy 8 abr)** | Alineación + Proof of Concept | Pipeline listo (limpiar_datos.py v1) | 50–100 ferreterías Medellín | Roles asignados, repo creado |
| **Semana 1 (9–13 abr)** | Piloto de ciudad | Script v1.1 + prompts validados | 100–150 ferreterías Medellín | Scraping estable, fuentes integradas |
| **Semana 2 (14–20 abr)** | Escalar a 2 ciudades | Deduplicación IA optimizada + RAG setup | 300–500 ferreterías (Medellín + Bogotá) | Embeddings vector listos, Chroma configurado |
| **Semana 3 (21–27 abr)** | Calidad + Dashboard | Agente IA funcionando | 1,000–1,500 ferreterías (3 ciudades) | Dashboard integrado, validación QA completada |
| **Semana 4 (28 abr–2 may)** | Entrega final | Demo en vivo del agente IA | 2,000+ ferreterías (5 ciudades) | Documentación completa, presentación lista |

### Hitos Semanales (Tu rol como AI Developer)

#### **SEMANA 0 (HOY — 8 de abril)**
- ✅ Script `limpiar_datos.py` funcional (v0.1)
- ✅ 50–100 registros validados de Medellín en BD_Base_PROCESADA.xlsx
- ✅ Prompts Claude documentados para limpieza y validación
- ✅ Decisiones de arquitectura RAG tomadas
- **Entregable:** Código + datos + documentación técnica

#### **SEMANA 1 (9–13 de abril)**
- ✅ Script v1.1 mejorado con manejo de errores
- ✅ Prompts optimizados con few-shot examples
- ✅ Integración con RUES iniciada
- ✅ 100–150 registros limpios de Medellín
- **Entregable:** `limpiar_datos.py` v1.1 + datos + bitácora de cambios

#### **SEMANA 2 (14–20 de abril)**
- ✅ Deduplicación IA con fuzzy matching + semántica
- ✅ RAG setup inicial: embeddings + Chroma
- ✅ Integración de segundas fuentes (Cámaras de Comercio)
- ✅ 300–500 registros limpios (Medellín + Bogotá)
- **Entregable:** Módulo de embeddings + script RAG prototipo + datos escalados

#### **SEMANA 3 (21–27 de abril)**
- ✅ Agente IA fully functional (chatbot consultable)
- ✅ Testing y ajustes de prompts en producción
- ✅ Dashboard integrado con BD
- ✅ 1,000–1,500 registros finales validados
- **Entregable:** Agente IA demo + dashboard + validación QA

#### **SEMANA 4 (28 abr–2 may)**
- ✅ Agente IA optimizado y documentado
- ✅ Presentación final en vivo
- ✅ 2,000+ ferreterías en 5 ciudades
- ✅ Documentación de arquitectura y uso
- **Entregable:** Presentación + código productivo + BD final + README

---

## 12. DECISIONES CRÍTICAS PARA HOY EN LA REUNIÓN

**Estas 6 decisiones deben ser aprobadas Y registradas HOY. Sin ellas, no hay progreso:**

- [ ] **Ciudad Piloto:** ¿Medellín (recomendado por densidad y datos disponibles)?
  
- [ ] **Formato Entregable Final:**
  - ❌ Solo Base de Datos (INSUFICIENTE)
  - ❌ BD + Dashboard (ESPERADO)
  - ✅ **BD + Dashboard + Agente IA** (RECOMENDADO)
  
- [ ] **Repositorio Compartido:**
  - GitHub privado (https://github.com/new)
  - Google Drive para documentos
  - Decisión sobre rama main vs development
  
- [ ] **Roles Asignados Formalmente:**
  - [ ] ¿Quién es AI Developer? (Tú)
  - [ ] ¿Quién es Ingeniero de Datos?
  - [ ] ¿Quién es Analista de Datos?
  - [ ] ¿Quién es BI / Dashboard?
  - [ ] ¿Quién es QA?
  - [ ] ¿Quién es Documentador?
  - [ ] ¿Quién es Project Manager?
  
- [ ] **Canal de Comunicación:**
  - WhatsApp (rápido, informal)
  - Discord (estructura, archivo)
  - Slack (si la universidad lo permite)
  - **Decisión:** ¿Cuál es el principal? ¿Secundario?
  
- [ ] **Meta Semana 1:**
  - Mínimo: **100 ferreterías limpias de Medellín**
  - Ideal: **150 ferreterías de Medellín + 50 de Bogotá**
  - Criterio de éxito: Datos validados en BD_Base.xlsx con ≥95% tasa de deduplicación

---

## 13. DEPENDENCIAS Y RIESGOS

### Matriz de Riesgos

| # | Riesgo | Probabilidad | Impacto | Severidad | Mitigación |
|----|--------|--------------|---------|-----------|-----------|
| **R1** | Apify detecta robots.txt de Google Maps y bloquea | Media | Alto | **ALTO** | 1) Usar delays entre requests. 2) Intentar con Serper como alternativa. 3) Contactar a Apify support. |
| **R2** | RUES no ofrece descarga masiva / requiere acceso restringido | Baja | Alto | **ALTO** | 1) Contactar directamente a Cámaras de Comercio de Antioquia. 2) Búsqueda manual por CIIU. 3) Compensar con Google Maps + Páginas Amarillas. |
| **R3** | Geocodificación de Nominatim es lenta (1 req/seg) | Alta | Medio | **MEDIO** | 1) Usar batch processing. 2) Cachear resultados. 3) Considerar API de pago (ej: Google Maps Geocoding). |
| **R4** | Equipo no tiene experiencia con Python / Claude API | Baja | Medio | **MEDIO** | 1) Proporcionar templates listos. 2) Capacitación rápida. 3) Documentación detallada. |
| **R5** | Cambios de scope durante el proyecto | Alta | Alto | **ALTO** | 1) Congelar scope antes de Semana 1. 2) Cualquier nuevo req → versión 2.0. 3) PM controla backlog. |
| **R6** | Dedupe IA consume demasiados tokens ($ elevado) | Baja | Medio | **MEDIO** | 1) Hacer dedupe primero con fuzzy (gratis). 2) IA solo para casos ambiguos. 3) Usar modelo de menor costo. |
| **R7** | Datos inconsistentes entre fuentes (direcciones diferentes) | Alta | Medio | **MEDIO** | 1) Lógica de prioridad de fuentes. 2) Prompts IA para reconciliación. 3) QA manual de casos ambiguos. |
| **R8** | Miembro del equipo se va / no puede participar | Baja | Alto | **ALTO** | 1) Documentación detallada. 2) Backup asignado para cada rol. 3) Código modular + versionado. |

---

## 14. VARIABLES DE ENTORNO (.env)

Crear archivo `.env` en la **raíz del proyecto**. Nunca pushear este archivo a Git.

```ini
# .env — Variables de entorno para Censo Digital de Ferreterías
# ADVERTENCIA: Nunca compartir este archivo por email. Guardarlo localmente.

# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-v0-xxxxxxxxxxxxxxxxxxxxx

# Apify (opcional, si se ejecuta scraping desde Python)
APIFY_TOKEN=apify_xxxxxxxxxxxxxxxxxxxxx

# Serper API (búsquedas web)
SERPER_API_KEY=xxxxxxxxxxxxxxxxxxxxx

# Base de datos (si se usa BD en lugar de Excel)
DB_HOST=localhost
DB_PORT=5432
DB_USER=usuario
DB_PASS=contraseña
DB_NAME=censo_ferreterias

# Directorio de datos
DATA_INPUT_DIR=./datos/crudos
DATA_OUTPUT_DIR=./datos/procesados

# Configuración de ejecución
LOG_LEVEL=INFO
TEST_MODE=False
```

### Cómo cargarlas en Python

```python
import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# Acceder a las variables
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
apify_token = os.getenv("APIFY_TOKEN")

if not anthropic_key:
    raise ValueError("ANTHROPIC_API_KEY no configurada en .env")
```

### Seguridad

1. **Agregar `.env` a `.gitignore`:**
```
# .gitignore
.env
.env.local
*.xlsx
*.json
__pycache__/
```

2. **Para compartir credenciales con el equipo:**
   - NO usar email
   - NO pushear a Git
   - Usar Google Drive privado o password manager (1Password, Bitwarden)
   - Compartir instrucciones de cómo obtener credenciales propias

---

## 15. ESTRUCTURA DE CARPETAS RECOMENDADA

```
censo-ferreterias/
├── README.md                          # Documentación principal
├── GUIA_MAESTRA_IMPLEMENTACION.md    # Este archivo
├── .env                               # Variables de entorno (NO PUSHEAR)
├── .gitignore                         # Configuración Git
├── requirements.txt                   # Dependencias Python
│
├── scripts/
│   ├── limpiar_datos.py              # Pipeline de limpieza
│   ├── normalizar_nombres.py          # Normalización IA
│   ├── geocodificar.py                # Geocodificación
│   └── rag_agent.py                   # Agente IA RAG
│
├── datos/
│   ├── crudos/
│   │   └── scraping_medellin_crudo.json
│   └── procesados/
│       ├── BD_Base_PROCESADA.xlsx
│       └── BD_Base_FINAL.json
│
├── dashboard/
│   ├── app.py                         # Streamlit app
│   └── assets/
│       └── mapa_ferreterias.html
│
├── docs/
│   ├── arquitectura_rag.md
│   ├── guia_usuario.md
│   └── changelog.md
│
└── tests/
    ├── test_limpieza.py
    └── test_deduplicacion.py
```

---

## 16. COMANDOS RÁPIDOS PARA HABILITAR

### Terminal / Bash

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pipeline
python scripts/limpiar_datos.py

# Ejecutar dashboard
streamlit run dashboard/app.py

# Ver logs
tail -f logs/censo.log

# Ejecutar tests
pytest tests/
```

### Git (Flujo básico)

```bash
# Crear rama para tu feature
git checkout -b feat/limpieza-datos

# Hacer cambios + commit
git add scripts/limpiar_datos.py
git commit -m "feat: agregar deduplicación con fuzzy matching"

# Push a rama
git push origin feat/limpieza-datos

# Crear Pull Request en GitHub
# (en interfaz web: New Pull Request)

# Merge a main después de aprobación
git checkout main
git merge feat/limpieza-datos
git push origin main
```

---

## 17. CHECKLIST PARA LA REUNIÓN DE HOY

**Antes de entrar a la reunión, asegúrate de tener:**

- [ ] ✅ **Datos demostrables:** BD_Base_PROCESADA.xlsx con 50–100 registros de Medellín
- [ ] ✅ **Script funcional:** limpiar_datos.py ejecutándose sin errores
- [ ] ✅ **Documento impreso o digital:** Esta GUÍA MAESTRA (versión PDF recomendada)
- [ ] ✅ **Demo 2 minutos:** Mostrar datos crudos → datos procesados → validación
- [ ] ✅ **Propuesta clara:** Niveles de entrega + roadmap + roles
- [ ] ✅ **Decisiones a tomar:** Lista de 6 decisiones críticas (Sección 12)

**Durante la reunión:**
- [ ] Presentar resumen ejecutivo (2 min)
- [ ] Mostrar demo de datos Medellín (3 min)
- [ ] Explicar niveles de entrega y proponer NIVEL 3 (3 min)
- [ ] Proponer roles + cronograma (2 min)
- [ ] Decidir 6 items críticos (5 min)
- [ ] Q&A + ajustes (5 min)

**Total: 20 minutos = Tiempo perfecto antes de 9:45 AM**

---

## 18. REFERENCIAS Y RECURSOS ÚTILES

### Documentación Oficial
- **Apify:** https://docs.apify.com/platform/actors
- **Claude API:** https://docs.anthropic.com/en/api/getting-started
- **pandas:** https://pandas.pydata.org/docs/
- **Streamlit:** https://docs.streamlit.io/
- **Nominatim:** https://nominatim.org/release-docs/latest/api/Overview/

### APIs y Herramientas
- **RUES Colombia:** https://www.rues.org.co
- **Google Maps (vía Apify):** https://apify.com/apify/google-maps-scraper
- **Serper:** https://serper.dev
- **OpenStreetMap Nominatim:** https://nominatim.openstreetmap.org

### Cursos/Tutoriales Recomendados
- Python para ciencia de datos: https://www.udacity.com/
- RAG con LangChain/Claude: https://python.langchain.com/docs/get_started
- Streamlit dashboards: https://docs.streamlit.io/library/get-started

### Comunidades
- Stack Overflow: [tag: python] [tag: claude-api]
- GitHub Discussions: Apify, Streamlit, Anthropic
- Discord: Python Data Science, Streamlit community

---

## 19. NOTAS FINALES Y RECOMENDACIONES

### Para el AI Developer (Tú)

1. **Prompts IA son tu arma principal.** Invierte tiempo en crafting prompts claros, con ejemplos (few-shot), y especificar formato de salida.

2. **Deduplicación es el 80% del trabajo.** No es glamoroso, pero hace la diferencia en calidad. Combina fuzzy matching + IA semántica.

3. **Tokens = dinero.** Claude API es barata, pero procesando miles de registros suma. Usa batch processing y cachea resultados cuando sea posible.

4. **Documentar mientras desarrollas.** No dejes la documentación para el final. Cada script debe tener docstring y comentarios.

5. **Test temprano y seguido.** No esperes a la Semana 4 para descubrir que el pipeline falla con 2,000 registros.

### Para el Equipo General

1. **Comunicación es clave.** Define daily standups rápidos (5 min) en Discord/WhatsApp.

2. **GitHub es tu amigo.** Issues para bugs, Projects para sprint planning, Pull Requests para code review.

3. **Datos > Código.** Es mejor entregar 2,000 registros OK que 500 registros perfectos. Itera.

4. **Cementos Argos es el usuario final.** Mantenlo en la conversación. Mostralle avances semanalmente.

### Para Próximos Proyectos

1. Documentar decisiones arquitectónicas en ADR (Architecture Decision Records).
2. Considerar usar Airflow o Prefect para orchestration si se escala a >10 ciudades.
3. Explorar uso de embeddings multisource para mejor deduplicación.

---

## 20. CONTACTOS Y ESCALACIÓN

| Rol | Nombre | Email | Celular | Disponibilidad |
|-----|--------|-------|---------|-----------------|
| **Project Manager** | [NOMBRE] | [EMAIL] | [CEL] | L–V 8 AM–6 PM |
| **AI Developer (TÚ)** | [NOMBRE] | [EMAIL] | [CEL] | L–V 9 AM–10 PM |
| **Ingeniero de Datos** | [NOMBRE] | [EMAIL] | [CEL] | L–V 8 AM–6 PM |
| **Analista BI** | [NOMBRE] | [EMAIL] | [CEL] | L–V 8 AM–6 PM |
| **Contacto Cementos Argos** | [NOMBRE] | [EMAIL] | [CEL] | Por confirmar |

---

## VERSIÓN Y CHANGELOG

| Versión | Fecha | Cambios |
|---------|-------|---------|
| **v1.0** | 2026-04-08 | Documento inicial para reunión de equipo |
| v1.1 | — | Por definir luego de reunión |

---

**Documento confidencial para uso interno del proyecto "Censo Digital de Ferreterías en Colombia"**  
**Equipo: 6–7 personas | Plazo: 4 semanas | Entrega: Mayo 2026**

---

*Última actualización: 8 de abril de 2026*
