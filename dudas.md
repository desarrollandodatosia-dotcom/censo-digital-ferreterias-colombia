# Resolución de Dudas: Preparación Express y Scraping con Apify
# ⏰ REUNIÓN EN 30 MINUTOS — LEE ESTO PRIMERO

---

## CONFIRMACIÓN IMAGEN: ¿"Extractor de mapas de Google" es el correcto?

**SÍ, es el actor correcto.** 

En la interfaz en español de Apify, "Google Maps Scraper" aparece traducido como **"Extractor de mapas de Google"** del equipo **Brújula**. Es el actor más usado de toda la plataforma:
- ⭐ 4.7 estrellas con 1,109 reseñas
- 347K usuarios — es el estándar de la industria
- Extrae: nombre, dirección, teléfono, web, reseñas, coordenadas GPS, horario

> **Acción inmediata:** Haz clic en ese actor → presiona **"Try for free"** (o "Probar gratis").

---

## DIÁLOGO PARA EXPLICAR AL EQUIPO: ¿Apify o RUES o ambos?

> **"Equipo, para el scraping tenemos dos fuentes principales y son complementarias, no competidoras. Déjenme explicar la diferencia:"**

### Fuente 1 — Apify (Google Maps Scraper)

> *"Apify nos da los datos operativos reales: el nombre del negocio como aparece en Google, dirección exacta, teléfono, sitio web, horario, número de reseñas, coordenadas GPS para el mapa. Es rápido, tiene $5 gratis de crédito y en 10 minutos tenemos 100-200 ferreterías de Medellín. La limitación es que no nos da el NIT ni información fiscal oficial."*

**Qué entrega:**
- Nombre comercial (como aparece en Google Maps)
- Dirección formateada
- Teléfono / WhatsApp
- Web / redes
- Coordenadas lat/lng (para el mapa interactivo)
- Rating y número de reseñas
- Horario de atención
- Categoría del negocio

**Limitaciones:**
- No tiene NIT / RUT
- Puede tener datos desactualizados
- No filtra por CIIU oficial

---

### Fuente 2 — RUES (Registro Único Empresarial y Social)

> *"El RUES es la fuente oficial del Estado colombiano. Nos da el NIT, la razón social legal, el CIIU (código de actividad económica), la ciudad de matrícula y el estado de la empresa (activa/inactiva). El problema es que no tiene teléfono ni coordenadas GPS, y la consulta masiva es lenta o requiere pagar por el dataset completo."*

**URL:** [https://www.rues.org.co/](https://www.rues.org.co/)

**Qué entrega:**
- NIT / cédula empresarial
- Razón social legal (nombre oficial)
- CIIU exacto (4752 = ferreterías, 4663 = distribuidoras)
- Ciudad y departamento de matrícula
- Estado: Activa / Cancelada / Suspendida
- Fecha de matrícula (antigüedad del negocio)

**Limitaciones:**
- Sin teléfono, sin web, sin coordenadas
- La búsqueda masiva requiere scraping manual o API de pago
- Solo empresas formalizadas (deja por fuera informales)

---

### La Estrategia Ganadora: AMBAS + Cruce por Nombre/Dirección

> *"La estrategia correcta es usar ambas. Apify nos da el 80% de los datos operativos rápido. Luego, con fuzzywuzzy (similitud de texto), cruzamos los nombres de Google Maps contra los del RUES para enriquecer cada registro con el NIT y el CIIU oficial. Eso es exactamente lo que hace nuestro script `limpiar_datos.py`. El resultado final es una base de datos híbrida: datos operativos de Google + validación jurídica del RUES."*

```
Google Maps (Apify)          RUES
━━━━━━━━━━━━━━━━━            ━━━━━━━━━━━━━━
Nombre comercial     ←→ cruce por nombre ←→  Razón social
Teléfono                                     NIT
Web                                          CIIU
Coordenadas GPS                              Estado (activa/no)
Reseñas / Rating                             Antigüedad
```

**Flujo completo:**
1. Apify extrae 200 ferreterías de Medellín (10 min)
2. `limpiar_datos.py` limpia y normaliza (2 min)
3. Cruce opcional con RUES para validar NIT (puede ser manual en piloto)
4. `BD_Base_PROCESADA.xlsx` lista para mostrar al equipo

---

## PASO A PASO COMPLETO PARA HACER LA PRUEBA AHORA

### Paso 1 — Entrar a Apify y abrir el actor (2 min)

1. Ve a [https://console.apify.com/store](https://console.apify.com/store)
2. Ya estás autenticado como Daniel (Personal)
3. Haz clic en **"Extractor de mapas de Google"** (Brújula, 4.7 ⭐, 347K usuarios) — **ESE ES EL CORRECTO**
4. Presiona **"Try for free"** / **"Probar gratis"**

### Paso 2 — Configurar el actor (2 min)

Cuando abra el panel de configuración (*Input*):

- Busca el modo **JSON** o el campo de texto de búsqueda
- Usa esta configuración mínima para el piloto:

```json
{
  "searchStringsArray": [
    "ferreterías Medellín",
    "materiales de construcción Medellín",
    "ferreterías Bogotá"
  ],
  "maxCrawledPlacesPerSearch": 100,
  "language": "es",
  "maxImages": 0,
  "maxReviews": 0,
  "includeWebResults": false,
  "skipClosedPlaces": true,
  "countryCode": "CO"
}
```

> **Tip:** Si el panel no muestra JSON, busca una pestaña que diga "JSON" o "Raw input" en la parte superior del formulario.

---

### Filtros adicionales para el JSON — Guía de opciones

#### A) Más términos de búsqueda (`searchStringsArray`)

**Por tipo de negocio** — captura negocios relacionados que el CIIU 4752/4663 incluye:
```json
"searchStringsArray": [
  "ferreterías Medellín",
  "depósito de materiales Medellín",
  "distribuidora materiales construcción Medellín",
  "pinturas y ferretería Medellín",
  "cerrajería y ferretería Medellín",
  "plomería y ferretería Medellín",
  "eléctricos y ferretería Medellín",
  "herramientas industriales Medellín",
  "tornillería Medellín",
  "ferretería industrial Medellín",
  "materiales para construcción Cali",
  "ferreterías Cali",
  "ferreterías Barranquilla",
  "ferreterías Bucaramanga",
  "ferreterías Pereira"
]
```

**Regla práctica:** 1 término = ~100 resultados con el plan gratis. Con $5 puedes lanzar ~10 búsquedas antes de agotar el crédito. Para el **piloto de semana 1**, usa máximo 3-5 términos de Medellín.

---

#### B) Parámetros de precisión geográfica

Para delimitar a una zona exacta (barrio, zona industrial) en lugar de toda la ciudad:

```json
{
  "searchStringsArray": ["ferreterías"],
  "customGeolocation": {
    "type": "Point",
    "coordinates": [-75.5636, 6.2442]
  },
  "geolocationRadiusKm": 15,
  "countryCode": "CO"
}
```
> Coordenadas del ejemplo: centro de Medellín. Cambia el radio (`geolocationRadiusKm`) para ampliar o reducir.

---

#### C) Parámetros de calidad del resultado

```json
{
  "minimumStars": 3.5,
  "skipClosedPlaces": true,
  "includeOpeningHours": true,
  "additionalInfo": true
}
```

| Parámetro | Qué hace | Cuándo usarlo |
|---|---|---|
| `minimumStars` | Solo negocios con X+ estrellas | Filtrar negocios casi abandonados |
| `skipClosedPlaces` | Omite lugares cerrados permanentemente | Siempre activar |
| `includeOpeningHours` | Incluye horario de atención | Útil para los asesores comerciales |
| `additionalInfo` | Sección "About" del lugar | Captura accesibilidad, métodos de pago |

---

#### D) JSON completo para Semana 2 (escalado real)

Cuando ya pasaste el piloto y quieres extraer en serio:

```json
{
  "searchStringsArray": [
    "ferreterías Medellín",
    "depósito de materiales Medellín",
    "ferreterías Bogotá",
    "ferreterías Cali",
    "ferreterías Barranquilla",
    "ferreterías Bucaramanga",
    "materiales de construcción Colombia"
  ],
  "maxCrawledPlacesPerSearch": 200,
  "language": "es",
  "countryCode": "CO",
  "maxImages": 0,
  "maxReviews": 0,
  "includeWebResults": false,
  "skipClosedPlaces": true,
  "includeOpeningHours": true,
  "additionalInfo": true,
  "minimumStars": 0
}
```

---

#### E) Lo que NO vale la pena filtrar en JSON (mejor hacerlo en Python)

- Filtrar por nombre exacto → usa `fuzzywuzzy` en `limpiar_datos.py`
- Eliminar duplicados → ya lo hace el pipeline ETL
- Filtrar por CIIU → el RUES lo resuelve, Apify no tiene ese dato

### Paso 3 — Ejecutar (10-15 min)

- Presiona el botón verde **"Start"** (abajo a la izquierda del panel)
- El estado cambiará: `Running` → `Succeeded`
- El actor debería extraer ~100-200 registros con el plan gratuito ($5)

### Paso 4 — Descargar los datos (1 min)

- Ve a la pestaña **"Output"** o **"Export"**
- Selecciona formato **JSON** o **CSV**
- Descarga el archivo y guárdalo como:
  ```
  c:\Users\CORE 7 5050\Downloads\Etapa3\scraping_medellin_crudo.json
  ```

### Paso 5 — Limpiar los datos (2 min)

En terminal (CMD o PowerShell en la carpeta Etapa3):

```bash
# Instalar dependencias si no están
pip install pandas fuzzywuzzy python-Levenshtein openpyxl requests anthropic python-dotenv

# Ejecutar el script de limpieza
python limpiar_datos.py
```

Resultado: archivo **`BD_Base_PROCESADA.xlsx`** con datos limpios y normalizados.

---

## RESUMEN EJECUTIVO PARA LA REUNIÓN (1 minuto de presentación)

| Concepto | Respuesta rápida |
|---|---|
| ¿Qué extrae Apify? | Datos operativos de Google Maps (teléfono, web, coordenadas, reseñas) |
| ¿Qué da el RUES? | Datos legales oficiales (NIT, CIIU, estado empresa) |
| ¿Cuál usamos primero? | **Apify** — rápido, automático, $5 gratis = ~200 registros |
| ¿Cuándo usamos RUES? | Para validar y enriquecer los registros en semanas 2-3 |
| ¿Se pueden cruzar? | Sí — fuzzywuzzy cruza por nombre/dirección |
| ¿Actor correcto en Apify? | "Extractor de mapas de Google" de Brújula (4.7⭐, 347K) = ✅ SÍ |
| ¿Costo estimado piloto? | $0.50-$1.00 de los $5 del plan gratuito |

---

## GUION DE PRESENTACIÓN PARA LA REUNIÓN

> "Hola equipo, buenas tardes. Mi rol es el de **AI Developer** — me encargo de la parte técnica: limpieza IA, deduplicación y el Agente consultable final.
>
> Para hoy quise llegar con algo concreto. Hice un **piloto técnico** usando Apify (Google Maps Scraper). Extraje ferreterías reales de Medellín en menos de 15 minutos. Ya tenemos una muestra de datos reales con nombre, teléfono, dirección y coordenadas GPS.
>
> **Sobre las fuentes de datos:** Vamos a usar dos fuentes complementarias. Apify nos da los datos operativos (Google Maps) y el RUES nos da la validación legal (NIT, CIIU). Las cruzamos por nombre usando inteligencia artificial para tener la base de datos más completa posible.
>
> Lo que propongo que definamos hoy: roles exactos, ciudad piloto confirmada (Medellín), y el formato final del Excel. ¡Arranquemos!"
