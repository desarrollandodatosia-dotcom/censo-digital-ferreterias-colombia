# REUNIÓN 08 ABR + 10 ABR — Censo Digital Ferreterías | Cementos Argos
> Documento actualizado con las dos reuniones: equipo interno (10 abr) y con el profesor Diego (10 abr)

---

## RESUMEN EJECUTIVO — Lo que quedó definido en ambas reuniones

| Concepto | Respuesta confirmada |
|---|---|
| ¿Qué hacemos? | Sistema automatizado de base de datos nacional de ferreterías para Cementos Argos |
| ¿Fuente base de datos? | **RUES** ya tiene 34.135 registros (Sebastián los sacó con CIIU 4752 y 4663) |
| ¿Fuente para enriquecer? | **Apify (Google Maps Scraper)** → nombre comercial, teléfono, coords, web |
| ¿Qué entrega el profe? | Estructura de campos ya definida (NIT, Municipio, Dirección, Lat, Long, Tel, WA, Correo, Fecha, Fuente) |
| ¿Cómo automatizar? | N8N: workflow que ejecuta todo el pipeline + correos de verificación |
| ¿Con qué frecuencia? | Cada **3-4 meses** programado + botón **on-demand** cuando el equipo lo necesite |
| ¿Dónde corre la solución? | **Local** — no hay presupuesto para hosting. Documentar requerimientos si Argos quiere llevarlo a producción |
| ¿Quién la usa? | Equipo comercial de Argos (no técnicos → interfaz simple) |
| ¿Entregable MVP hoy? | Diagrama de arquitectura + base de datos inicial RUES (puede ser Excel) |
| Objetivo diferencial | Identificar qué ferreterías **venden cemento** — eso es lo que Argos realmente necesita |

---

## LO QUE DIJO EL PROFE DIEGO (Speaker 8) — Los puntos más importantes

### 1. La solución puede correr 100% local
> *"Sí, no hay problema... si no lo hacemos así, de pronto llegamos a que ustedes requieran pagar algunas cosas. Y la idea no es que ustedes tengan que pagar cosas porque pues no es la idea de la beca."*

✅ **Implicación:** No se necesita VPS, AWS ni Heroku. Todo corre en el computador del equipo durante la presentación.

### 2. Frecuencia de actualización: 3-4 meses + botón on-demand
> *"La empresa requiere la solución de dos posibles formas. Una, de tal forma que se programa automatizada, de que se ejecute al menos cada 3 o 4 meses. Pero por experiencias dentro de la empresa, también como requerimiento, que exista la posibilidad de que en un momento dado, si ellos requieren actualizar la información, tengan un botoncito, una necesidad, algo que puedan hacer."*

✅ **Implicación:** Dos modos: programado (cada 3-4 meses) + botón manual.

### 3. El campo más crítico: ¿Vende cemento?
> *"Lo que le interesa a las empresas que vendan cemento. Ojo, no cemento necesariamente Argos, sino como tal que vendan cemento."*
> 
> *"Hay como una idea que les estoy brindando a todos los equipos: si se tienen correos electrónicos, pues podrían validar escribiendo pues una automatización que mande correos electrónicos... '¿Estoy interesado en comprar cemento, quisiera saber si ustedes tienen disponibilidad de producto?'"*

✅ **Implicación:** El flujo N8N de correo automático para verificar cemento es OBLIGATORIO, no opcional.

### 4. La estructura de datos está definida pero es flexible
> *"Esos son los campos que son más o menos requeridos por la empresa. Recuerden que posiblemente no se pueda conseguir para todos el NIT, entonces pues se consigue el NIT para los que más se puede. Lo mismo con el correo y el teléfono de WhatsApp."*

✅ **Implicación:** Si no se consigue un campo para un registro, no es bloqueante. Lo que se consiga vale.

### 5. La presentación debe ser para no-técnicos
> *"Para la presentación, posiblemente se tenga que hablar de las plataformas y de cómo lo desarrollé, pero no con un nivel muy técnico porque posiblemente ellos no vayan a entender. Entonces, desglosarlo un poquito en un nivel intermedio, básico."*

✅ **Implicación:** Slides y demo pensadas para el área comercial de Argos, no para ingenieros.

### 6. Tarea asignada para ESTA semana
> *"Para la otra semana, tener una base de datos inicial. No tiene que ser de muchos registros, pero sí necesitamos una base de datos inicial. Puede ser en un Excel o como lo quieran entregar. Y presenten más o menos como en gráficas y descriptivamente cuál es la arquitectura y el paso a paso que haría la solución."*

✅ **Lo que llevar a la reunión de hoy:** 
- Diagrama de arquitectura ✅ (ya listo en `arquitectura_solucion.pptx`)
- Base de datos inicial ← **pendiente: definir subconjunto del RUES para mostrar**

---

## DIAGNÓSTICO DE LA BASE RUES — Lo que encontramos

> Sebastián extrajo 34.135 registros con CIIU 4752 y 4663. Aquí el resumen de calidad.

| Indicador | Valor | Estado |
|---|---|---|
| Total registros | 34.135 | ✅ |
| Municipio | 34.134 (99.99%) | ✅ |
| Dirección comercial | 34.134 (99.99%) | ✅ |
| Duplicados por NIT | 0 | ✅ |
| Correos personales (gmail/hotmail) | 94.7% | ⚠️ Esperado |
| Nombres de persona (no comercial) | 78.6% | ⚠️ Requiere Google Maps |
| Latitud / Longitud | 0% | ❌ Hay que geocodificar |
| Teléfono | 0% | ❌ Hay que conseguir via Apify |
| Vende cemento | 0% | ❌ Hay que verificar via N8N |

### El problema del nombre
El RUES registra la **razón social legal**, no el nombre comercial. Para personas naturales (71% de los registros), eso significa el nombre del dueño:

| En RUES | En Google Maps (nombre real) |
|---|---|
| GUTIERREZ MARTINEZ DANILO RAFAEL | Ferretería Gutiérrez |
| TORRES DUEÑAS PATRICIO | Materiales El Porvenir |
| JOSE ALFREDO RAMIREZ GRISALES | Ferreto El Clavo |

**Solución:** Cruzar con Apify (Google Maps) usando dirección + municipio como llave para obtener el nombre comercial real.

### Regiones prioritarias (según Argos)
| Región | Registros disponibles |
|---|---|
| Bogotá D.C. | 6.269 |
| Antioquia | 4.138 |
| Cundinamarca | 2.272 |
| Eje Cafetero (Risaralda + Caldas + Quindío) | 1.963 |
| **Total prioritarias** | **14.642 (43%)** |

---

## FLUJO COMPLETO DE DATOS — Actualizado

```
FUENTES DE ENTRADA
│
├── RUES (ya tenemos)          ├── Apify Google Maps Scraper
│   34.135 registros               (enriquecimiento)
│   NIT, Dirección, Correo         Nombre comercial, Tel,
│   Municipio, CIIU                Coords, Web, Rating
│
└──────────────┬───────────────────────────┘
               │
               ▼
        limpiar_datos.py
        ┌─────────────────────────────────────┐
        │ 1. Normalizar nombres (quitar SAS,  │
        │    LTDA, nombres de persona)        │
        │ 2. Deduplicación con fuzzywuzzy     │
        │ 3. Validar coordenadas Colombia     │
        │ 4. Clasificar correo: Personal vs   │
        │    Corporativo                      │
        │ 5. IA Generativa (Claude) para      │
        │    nombres difíciles                │
        └──────────────────┬──────────────────┘
                           │
                           ▼
              BASE DE DATOS CENTRAL
              ferreterias_argos.xlsx / DB
              (12 campos + campos extra)
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
       Dashboard      Botón de       N8N Workflow
       interactivo    actualización  Correo ¿Vende
       (mapa +        on-demand      cemento? →
        filtros)                     segmentación
```

---

## EL ROL DE APIFY EN EL PROYECTO

### ¿Qué es Apify?
Plataforma de web scraping en la nube. Su actor **"Google Maps Scraper"** extrae información de Google Maps de forma masiva y automática.

### ¿Por qué Apify y no la Google Places API directamente?
| | Apify | Google Places API directa |
|---|---|---|
| Configuración | Visual, sin código | Requiere código + manejo de paginación |
| Costo piloto | $5 USD gratis ≈ 2.000 registros | Pay-per-use desde el primer registro |
| Velocidad de arranque | 15 minutos | 1-2 horas de setup |
| Nombre comercial | ✅ Sí (el que aparece en Maps) | ✅ Sí |
| Teléfono | ✅ Sí | ✅ Sí |
| Coordenadas | ✅ Sí | ✅ Sí |
| Web | ✅ Sí | ✅ Sí |
| Rating / Reseñas | ✅ Sí (señal de negocio activo) | ✅ Sí |

### Cómo usar Apify para este proyecto
**Estrategia:** No scrapeamos aleatoriamente. Usamos la dirección del RUES para buscar el negocio específico en Google Maps.

```
Para cada ferretería en RUES:
  búsqueda = f"{razon_social} {municipio} {direccion}"
  resultado = Apify.buscar(búsqueda)
  
  si resultado encontrado:
    → tomar nombre_comercial, telefono, coordenadas, web
    → cruzar con registro RUES
  sino:
    → marcar como "No encontrado en Google Maps"
```

**Configuración básica en Apify:**
```json
{
  "searchStringsArray": [
    "ferreterías Medellín",
    "ferretería Bogotá",
    "materiales construcción Antioquia"
  ],
  "maxCrawledPlacesPerSearch": 100,
  "language": "es",
  "maxImages": 0,
  "maxReviews": 0
}
```

### Costo estimado
- Plan gratuito: $5 USD → ~2.000 registros
- Para las 14.642 ferreterías prioritarias: ~$36 USD
- Para las 34.135 nacionales: ~$85 USD

---

## EL ROL DE N8N EN EL PROYECTO

### ¿Qué es N8N?
Plataforma de automatización de flujos (similar a Zapier/Make, pero open-source). Se instala local.

### Dos flujos principales que necesitamos

**Flujo 1 — Actualización de base de datos (trigger: botón o scheduler)**
```
[Trigger: Botón / Cron 3-4 meses]
  → Ejecutar limpiar_datos.py
  → Llamar Apify API para nuevos registros
  → Actualizar Excel / BD
  → Notificar al equipo por email/Slack
```

**Flujo 2 — Verificación ¿Vende cemento? (trigger: nueva ferretería sin verificar)**
```
[Trigger: Nueva ferretería en BD sin campo "vende_cemento"]
  → Enviar correo amable a correo_rues
  → Asunto: "Consulta sobre disponibilidad de cemento"
  → Cuerpo: "Estimado, estamos interesados en saber si ustedes 
    comercializan cemento. Por favor responda Sí o No."
  → Esperar respuesta [24-48h]
  → Si responde: actualizar campo vende_cemento en BD
  → Si no responde: marcar como "No verificado" / re-intentar 1 vez
```

### Instalación N8N (local, gratis)
```bash
# Con Docker (recomendado)
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n

# Con npm
npm install -g n8n
n8n start
# Acceder en: http://localhost:5678
```

---

## CRUCE RUES + GOOGLE MAPS — Cómo funciona fuzzywuzzy

### El problema
```
En RUES:      "FERRETERIA EL TORNILLO S.A.S."
En Maps:      "Ferretería El Tornillo"
Python ==:    FALSE ❌
fuzzywuzzy:   92% similar → DUPLICADO ✅
```

### El umbral configurado: 85%
```python
score = fuzz.token_sort_ratio(nombre_rues, nombre_maps)
if score >= 85:
    # Son el mismo negocio → tomar el nombre de Maps (más comercial)
    nombre_final = nombre_maps
```

- **Umbral 85%:** equilibrio entre precisión y recall
- Si se baja a 70%: borra demasiado (falsos positivos)
- Si se sube a 95%: deja duplicados reales (falsos negativos)

---

## TAREAS INMEDIATAS — Para llevar hoy a la reunión

| Tarea | Responsable | Estado |
|---|---|---|
| Diagrama arquitectura | Daniel | ✅ Listo (`arquitectura_solucion.pptx`) |
| Diagnóstico base RUES | Daniel | ✅ Listo (`diagnostico_base_datos.md`) |
| Base datos inicial (Excel subconjunto RUES) | Sebastián / Daniel | 🔄 Pendiente |
| Configurar N8N local | Equipo técnico | 🔄 Pendiente |
| Configurar Apify para enriquecimiento | Ingeniero datos | 🔄 Pendiente |
| Definir roles actualizados del equipo | Todos | 🔄 Pendiente en reunión |

---

## ROLES DEL EQUIPO — Actualizado post-reunión

| Rol | Responsabilidad principal | Semana 1 | Semana 2 | Semana 3 | Semana 4 |
|---|---|---|---|---|---|
| **AI Developer (Daniel)** | Pipeline ETL, IA normalización, integración general | Limpieza RUES + normalización | Cruce Google Maps / Apify | Segmentación cemento | Demo + documentación |
| **Ingeniero de Datos (Sebastián)** | Scraping Apify, extracción masiva | Configurar Apify | Escalar regiones | Soporte técnico | Soporte |
| **Analista de Datos** | QA, validación, métricas | Revisar base RUES | Auditar cruce | Validar correos/tels | Estadísticas finales |
| **Analista BI** | Dashboard, mapa, visualizaciones | Explorar herramientas | Mapa v1 | Mapa completo | Dashboard final |
| **N8N / Automatización** | Flujos de automatización, correos | Instalar N8N | Flujo actualización | Flujo correos cemento | Botón on-demand |
| **Documentador** | Bitácora, manual técnico, informe | Glosario + bitácora | Documentar pipeline | Manual N8N | Informe Argos |
| **Project Manager** | Coordinación, reuniones cada 2-3 días | Definir hitos | Control de avance | QA final | Presentación |
