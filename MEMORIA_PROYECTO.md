# MEMORIA PROYECTO — Cementos Argos
> Ultima actualizacion: 2026-04-13 (sesion tarde)
> Archivo de contexto para continuar el trabajo en proximas sesiones

---

## CONTEXTO GENERAL

**Proyecto universitario** para Cementos Argos.
**Objetivo:** Sistema automatizado para mantener una base de datos nacional de ferreterias colombianas, identificando cuales venden cemento.

**Integrante principal:** Daniel (desarrollandodatosia@gmail.com)
**Carpeta de trabajo:** `Etapa3/`
**N8N:** https://laurent365.app.n8n.cloud
**Apify:** cuenta Daniel_agudelo395 | Token: apify_api_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
**Actor Apify usado:** `compass~crawler-google-places`

---

## ESTADO ACTUAL — 13 Abril 2026

### Lo que esta LISTO

| Archivo | Descripcion | Registros |
|---|---|---|
| `BD_RUES_Limpia.xlsx` | BD nacional completa, 25 columnas | 34,133 |
| `BD_Regiones_Prioritarias.xlsx` | Bogota + Antioquia + Cundinamarca + Eje Cafetero | 14,642 |
| `mapa_v1.html` | Mapa interactivo Folium, 3 capas, 27MB | 14,642 puntos |
| `limpiar_datos.py` | Pipeline ETL RUES CSV → Excel | Funcional |
| `cruce_apify.py` | Enriquecimiento batch via Apify async | Funcional |
| `geocodificar_addresses.py` | Geocodificacion Nominatim (gratis) | Funcional |
| `mapa_v1.py` | Generador de mapa Folium | Funcional |

### Lo que esta CORRIENDO AHORA

| Proceso | Archivo | Estado | Tiempo restante |
|---|---|---|---|
| Geocodificacion GPS | `geocodificar_addresses.py` | ~106/14,642 | ~8 horas (toda la noche) |
| Output: `BD_Geocodificada.xlsx` | Se actualiza cada 100 registros | - | - |

### Lo que esta PENDIENTE (proximos pasos inmediatos)

```
1. Manana: verificar BD_Geocodificada.xlsx (debe tener 14,642 con GPS)
2. Manana: regenerar mapa con GPS real:
   python mapa_v1.py --input BD_Geocodificada.xlsx

3. Cuando haya tiempo (~3h):
   python cruce_apify.py --token apify_api_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX --solo-grandes
   (enriquece las 178 MEDIANA+GRANDE con nombre comercial + telefono de Google Maps)

4. En N8N: conectar credenciales
   - GmailArgos → Settings > Credentials > Google OAuth2
   - ApifyHeader → Settings > Credentials > HTTP Header Auth (Bearer TOKEN)
```

---

## DATOS CLAVE DEL RUES

- **Archivo:** `RUES_Ferreterias_7-4-2026 16_5_4(in).csv`
- **Encoding:** `latin-1` | **Separador:** `;`
- **Cargar con:** `pd.read_csv(..., encoding='latin-1', sep=';', low_memory=False)`
- **CIIU:** 4752 (ferreterias minorista) y 4663 (materiales mayorista)
- **Truco encoding:** `org_juridica` tiene "Persona Juridica" con acento en i → buscar con `str.contains("Natural")` y negar, no buscar "JURIDICA"

### Distribucion por tamano (regiones prioritarias, 14,642 total)
- MICRO: 13,233 (90.4%)
- PEQUENA: 1,231 (8.4%)
- MEDIANA: 160 (1.1%)
- GRANDE: 18 (0.1%)
- **MEDIANA + GRANDE total: 178** ← target prioritario para Apify

### Distribucion por departamento (regiones prioritarias)
- BOGOTA: 6,269
- ANTIOQUIA: 4,138
- CUNDINAMARCA: 2,272
- RISARALDA: 880
- CALDAS: 638
- QUINDIO: 445

---

## SCHEMA DE LA BD (25 columnas)

```
tipo_identificacion    → "NIT" o "CEDULA DE CIUDADANIA"
numero_identificacion  → numero
nit                    → solo si es NIT, else vacio
nombre_rues            → razon social original del RUES (no tocar)
nombre_comercial       → nombre limpio (de limpiar_datos.py o de Apify)
nombre_comercial_maps  → nombre exacto que aparece en Google Maps (de Apify)
org_juridica           → "Persona Natural" o "Persona Juridica" (con acento)
tamano_empresa         → MICRO / PEQUENA / MEDIANA / GRANDE
departamento           → mayusculas
municipio              → mayusculas
direccion_comercial    → direccion RUES
latitud                → vacio hasta geocodificacion
longitud               → vacio hasta geocodificacion
precision_geocode      → "direccion" / "municipio" / "municipio_cache"
telefono               → vacio hasta Apify
whatsapp               → derivar del telefono
correo_rues            → primer correo del RUES
tipo_correo            → "Personal" / "Corporativo" / "Sin correo"
correo_verificado      → si se consigue uno mejor
pagina_web             → de Apify
vende_cemento          → "No verificado" | "Si" | "No" (N8N lo llena)
fecha_matricula_rues   → fecha de registro en Camara de Comercio
fecha_actualizacion    → fecha del ultimo enriquecimiento
fuente                 → "RUES" | "RUES + Nominatim" | "RUES + Google Maps"
match_google           → "Si" | "Parcial" | "No encontrado"
calificacion_google    → rating de Google Maps
score_fuzzy            → % de similitud del nombre (fuzzywuzzy)
notas                  → observaciones del registro
```

---

## APIFY — Como funciona en este proyecto

**Cuenta:** Daniel_agudelo395 | Plan FREE ($5/mes)
**Creditos disponibles:** ~$4.50 (gaste $0.21 en pruebas)
**Costo real medido:** ~$0.021 por ferreteria
**Actor:** `compass~crawler-google-places`

**Estrategia BATCH (la correcta):**
- NO hacer 1 llamada por ferreteria (agota creditos en 8 llamadas)
- Enviar 10 queries en UN run async de Apify
- Cada run tarda ~10 minutos, cuesta ~$0.21
- Script: `cruce_apify.py --lote 10`

**Para las 178 MEDIANA+GRANDE:**
```bash
python cruce_apify.py \
  --token apify_api_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX \
  --solo-grandes
# Costo: ~$3.74 | Tiempo: ~3 horas
```

**Para escalar a mas registros (semana 2):**
- Cada miembro del equipo crea cuenta Apify gratis = $5 adicionales
- 7 personas × $5 = $35 = ~1,660 ferreterias enriquecidas

**Como construye la query de busqueda:**
- Persona Juridica con nombre de empresa: `"Ferreteria Ferrepol Sabaneta Colombia"`
- Persona Natural (nombre de persona): `"ferreteria CL 51 CARRERA 48-3 Bello Colombia"` (usa la direccion)

---

## N8N — Flujos listos

**Instancia:** https://laurent365.app.n8n.cloud
**Workflow:** ProyectoUniversidad | ID: `0VXLs7QfpMZZHxE4`
**Nodos:** 31 (14 funcionales + 17 sticky notes)
**Estado:** Probados con test_workflow = success

**Flujo 1 — Actualizacion DB:**
```
[Boton manual o Cron 3 meses]
    → Apify Scraper (busca ferreterias nuevas)
    → ETL Normalizar datos
    → Notificar equipo por Gmail
```

**Flujo 2 — Campana cemento:**
```
[Boton manual]
    → Cargar ferreterias con correo disponible y vende_cemento=null
    → Enviar Gmail: "Estamos interesados en saber si comercializan cemento..."
    → Esperar 48h
    → Revisar respuesta Gmail
    → Si responde Si → vende_cemento = Si
    → Si responde No → vende_cemento = No
    → Si no responde → vende_cemento = No verificado
```

**Credenciales pendientes de conectar:**
```
GmailArgos    → N8N > Settings > Credentials > Google OAuth2
ApifyHeader   → N8N > Settings > Credentials > HTTP Header Auth
              → Name: "Authorization" | Value: "Bearer apify_api_XXX"
```

---

## HERRAMIENTAS — Comandos clave

```bash
# 1. Generar BD limpia desde el RUES:
python limpiar_datos.py
# Output: BD_RUES_Limpia.xlsx (34k) + BD_Regiones_Prioritarias.xlsx (14k)

# 2. Geocodificar con Nominatim (gratis, sin API key):
python geocodificar_addresses.py               # todos (14k, ~8h)
python geocodificar_addresses.py --limite 500  # primeros 500 (~17 min)
python geocodificar_addresses.py --desde 500   # reanudar desde fila 500

# 3. Enriquecer con Google Maps via Apify:
python cruce_apify.py --token apify_api_XXX --solo-grandes  # 178 MEDIANA+GRANDE (~3h)
python cruce_apify.py --token apify_api_XXX                  # todos (costoso)

# 4. Generar mapa interactivo:
python mapa_v1.py                                    # usa BD_Geocodificada si existe
python mapa_v1.py --input BD_Regiones_Prioritarias.xlsx  # forzar archivo

# 5. Cargar RUES en Python (referencia):
import pandas as pd
df = pd.read_csv('RUES_Ferreterias_7-4-2026 16_5_4(in).csv', encoding='latin-1', sep=';', low_memory=False)

# 6. Verificar progreso geocodificacion:
python -c "
import pandas as pd
df = pd.read_excel('BD_Geocodificada.xlsx')
v = df['latitud'].apply(lambda x: 1.0 <= float(x) <= 13.0 if str(x) not in ('nan','') else False).sum()
print(f'{v:,} / {len(df):,} geocodificadas ({v/len(df)*100:.1f}%)')
"
```

---

## ROADMAP ACTUALIZADO

### Semana 1 (Apr 12-18) — EN CURSO
- [x] Reescribir `limpiar_datos.py` para RUES CSV
- [x] Generar `BD_RUES_Limpia.xlsx` (34,133 registros)
- [x] Generar `BD_Regiones_Prioritarias.xlsx` (14,642 registros)
- [x] Generar `mapa_v1.html` con 3 capas
- [x] Crear `cruce_apify.py` modo batch
- [x] Crear `geocodificar_addresses.py`
- [ ] Terminar geocodificacion GPS (corriendo en fondo, ~8h)
- [ ] Correr Apify para MEDIANA+GRANDE
- [ ] Conectar credenciales N8N

### Semana 2 (Apr 19-25)
- [ ] Apify para ferreterias PEQUENA (con cuentas adicionales del equipo)
- [ ] Cruce RUES + Apify con fuzzywuzzy verificado manualmente
- [ ] Mapa v2 con GPS real y filtros por tamano y cemento
- [ ] Presentar: BD enriquecida + Mapa v2 al profesor

### Semana 3 (Apr 26 - May 2)
- [ ] Activar N8N Flujo 2 con datos reales (campana cemento)
- [ ] Enviar 500+ correos "Vende cemento?"
- [ ] Boton "Actualizar BD" funcional
- [ ] Dashboard con filtro vende_cemento

### Semana 4 (May 3-9)
- [ ] BD final cerrada
- [ ] Presentacion final a Argos (demo en vivo)
- [ ] Documentacion tecnica completa

---

## DECISIONES TECNICAS TOMADAS

1. **Apify modo batch** — No 1 llamada por registro sino 10 queries por run ($0.021/registro)
2. **Nominatim para coordenadas** — Completamente gratis, sin API key, buena cobertura municipal
3. **fuzzywuzzy 80%** — Umbral de similitud para cruce RUES vs Google Maps (mas permisivo que 85% original para capturar mas matches)
4. **Prioridad Apify a MEDIANA+GRANDE** — Las 178 ferreterias mas grandes son el target mas valioso para Argos
5. **N8N en nube** — `laurent365.app.n8n.cloud` (no local, mas estable para la presentacion)
6. **Regiones prioritarias** — Bogota, Antioquia, Cundinamarca, Eje Cafetero (definidas por Argos)

---

## LECCION APRENDIDA HOY

**Apify sync vs async:**
- `run-sync-get-dataset-items` = 1 run por llamada = muy caro ($0.21 por 10 registros en modo sync)
- Solucion: usar `POST /v2/acts/{actor}/runs` (async) + esperar + `GET dataset/items`
- Cada query de Google Maps tarda ~30-60 segundos en el actor
- Maximo 10-15 queries por run para no exceder timeouts

---

*Actualizado automaticamente por Claude Code — Sesion 13 Abril 2026*
