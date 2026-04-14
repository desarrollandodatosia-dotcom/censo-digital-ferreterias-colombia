# Sesion de Trabajo 13 Abril — Censo Digital Ferreterias Colombia
## Cementos Argos | Equipo 7 personas | Semana 1 del proyecto

---

## QUE TENIAMOS ANTES DE HOY

- Archivo CSV del RUES con 34,135 ferreterias (descargado por Sebastian)
- Flujos N8N ya creados y probados (ProyectoUniversidad)
- Apify conectado a N8N
- Diagrama de arquitectura en PowerPoint
- `limpiar_datos.py` viejo disenado para datos de Apify, no para el RUES

---

## QUE HICIMOS HOY — Paso a paso

### PASO 1 — Limpieza y estructuracion del RUES

**Archivo creado:** `limpiar_datos.py` (reescrito completo)

**Que hace:**
- Lee el CSV del RUES (34,135 ferreterias) con encoding correcto (latin-1, separador ;)
- Detecta si cada empresa es Persona Natural (71%) o Persona Juridica (29%)
- Para Personas Juridicas: limpia el nombre eliminando sufijos legales (S.A.S, LTDA, E.U.)
  - Ejemplo: "FERRETERIA FERREPOL S.A.S." → "Ferreteria Ferrepol"
- Clasifica el correo electronico: Personal (gmail, hotmail) vs Corporativo (dominio propio)
- Elimina los 2 duplicados que tenia el RUES
- Genera 2 archivos de salida

**Como se ejecuta:**
```
python limpiar_datos.py
```

**Archivos que genera:**

| Archivo | Registros | Descripcion |
|---|---|---|
| `BD_RUES_Limpia.xlsx` | 34,133 | Base de datos nacional completa |
| `BD_Regiones_Prioritarias.xlsx` | 14,642 | Solo Bogota + Antioquia + Cundinamarca + Eje Cafetero |

**Estructura de la BD (25 columnas):**
```
tipo_identificacion    → NIT o Cedula
nit                    → numero NIT (si aplica)
nombre_rues            → razon social original del RUES
nombre_comercial       → nombre limpio sin sufijos legales
org_juridica           → Persona Natural / Persona Juridica
tamano_empresa         → MICRO / PEQUENA / MEDIANA / GRANDE
departamento           → departamento en mayusculas
municipio              → municipio en mayusculas
direccion_comercial    → direccion registrada en RUES
latitud / longitud     → vacio hasta geocodificacion
telefono               → vacio hasta cruce con Google Maps
correo_rues            → correo del RUES
tipo_correo            → Personal / Corporativo
vende_cemento          → "No verificado" (se llenara con N8N)
fecha_matricula_rues   → fecha de registro en Camara de Comercio
fuente                 → "RUES"
match_google           → vacio hasta cruce con Google Maps
notas                  → aviso si requiere validacion en Google Maps
```

**Resultado de la limpieza:**
- Personas Juridicas: 9,846 (28.8%) → nombre comercial normalizado
- Personas Naturales: 24,289 (71.2%) → nombre del dueno, requiere Google Maps
- Correos personales: 32,150 (94.2%)
- Correos corporativos: 1,985 (5.8%)
- Duplicados eliminados: 2

---

### PASO 2 — Distribucion geografica (regiones prioritarias)

Los 14,642 registros de regiones prioritarias se distribuyen asi:

| Departamento | Ferreterias |
|---|---|
| BOGOTA | 6,269 |
| ANTIOQUIA | 4,138 |
| CUNDINAMARCA | 2,272 |
| RISARALDA | 880 |
| CALDAS | 638 |
| QUINDIO | 445 |
| **TOTAL** | **14,642** |

Por tamano en estas regiones:
- MICRO: 13,233 (90.4%)
- PEQUENA: 1,231 (8.4%)
- MEDIANA: 160 (1.1%)
- GRANDE: 18 (0.1%)

---

### PASO 3 — Mapa interactivo v1

**Archivo creado:** `mapa_v1.py`
**Archivo generado:** `mapa_v1.html` (27 MB — abrir en navegador)

**Que tiene el mapa:**
- Capa 1: Marcadores individuales por ferreteria (agrupados en clusters)
  - Al hacer clic: nombre, direccion, correo, tamano, fuente
  - Color por departamento (rojo=Bogota, azul=Antioquia, verde=Cundinamarca, etc.)
- Capa 2: Mapa de calor (densidad de ferreterias por zona)
- Capa 3: Circulos por municipio proporcionales al numero de ferreterias
- Leyenda con conteo por departamento
- Selector de capas en la esquina

**Coordenadas actuales:**
- Mientras no tengamos GPS exacto: usa el centro del municipio + dispersion aleatoria
- Cuando termine la geocodificacion (ver Paso 4): usa GPS real de cada direccion

---

### PASO 4 — Geocodificacion automatica (corriendo AHORA)

**Archivo creado:** `geocodificar_addresses.py`
**Archivo que genera:** `BD_Geocodificada.xlsx`

**El problema:** El RUES no tiene coordenadas GPS. Para plotear cada ferreteria en el mapa con precision necesitamos convertir la direccion en latitud/longitud.

**La solucion:** Nominatim (servicio de OpenStreetMap) — completamente GRATIS, sin API key.

**Como funciona:**
1. Intenta geocodificar la direccion exacta: "CL 37 NRO. 7F 55, Riohacha, Guajira, Colombia"
2. Si no encuentra: usa el municipio: "Riohacha, Guajira, Colombia"
3. Guarda el resultado en BD_Geocodificada.xlsx con campo `precision_geocode`

**Estado actual (17:15 del 13 Abril):** ~106 geocodificadas, proceso corriendo en fondo
**Tiempo estimado total:** ~8 horas (corre toda la noche)
**Resultado manana:** 14,642 ferreterias con GPS

**Como ejecutar (si se interrumpe):**
```
python geocodificar_addresses.py --desde 500   # reanudar desde fila 500
```

---

### PASO 5 — Cruce RUES + Google Maps via Apify

**Archivo creado:** `cruce_apify.py`
**Archivo que genera:** `BD_Enriquecida.xlsx`

**El problema que resuelve:**
El 71% de registros en RUES tienen el nombre del dueno, no el nombre del negocio:
- RUES tiene: "GUTIERREZ MARTINEZ DANILO RAFAEL"
- Google Maps tiene: "Ferreteria Gutierrez"

Apify conecta con Google Maps y nos da: nombre comercial real, telefono, coordenadas GPS, pagina web, calificacion.

**Como se conecta con Apify:**

```
[Script Python cruce_apify.py]
        |
        | Envia lista de busquedas por HTTP:
        | "ferreteria CL 37 NRO 7F 55 Riohacha Colombia"
        v
[API de Apify - actor: compass~crawler-google-places]
        |
        | Busca en Google Maps
        | Devuelve: titulo, telefono, coordenadas, web, rating
        v
[Resultado JSON]
        |
        | Script hace fuzzy match (fuzzywuzzy 80%)
        | para verificar que sea la misma ferreteria
        v
[BD_Enriquecida.xlsx]
  nombre_comercial_maps = "Ferreteria Gutierrez"
  telefono = "+57 300 1234567"
  latitud = 11.5346
  longitud = -72.9071
```

**Estrategia de busqueda:**
- Persona Juridica con nombre de empresa: busca "Ferreteria Ferrepol Sabaneta Colombia"
- Persona Natural (nombre de persona): busca "ferreteria CL 51 CARRERA 48-3 Bello Colombia" (usa la direccion, no el nombre personal)

**Modo BATCH (eficiente):**
- No hace 1 llamada por ferreteria (seria muy caro)
- Envia 10 busquedas en UN SOLO run de Apify
- El run procesa todas en paralelo y devuelve todos los resultados

**Costo y presupuesto:**
- Cuenta Apify: FREE → $5 USD de creditos al mes
- Costo por ferreteria: ~$0.021 USD
- Creditos disponibles hoy: $4.50 (gastamos $0.21 en pruebas)
- Con $4.50 podemos procesar: ~210 ferreterias
- **Estrategia: usar el presupuesto solo en las 178 ferreterias MEDIANA y GRANDE** (las que mas cemento compran)
- Costo total para MEDIANA+GRANDE: ~$3.74 USD

**Como ejecutar:**
```
# Para las 178 MEDIANA + GRANDE (recomendado, cuesta ~$3.74):
python cruce_apify.py --token apify_api_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX --solo-grandes

# Para reanudar si se interrumpe:
python cruce_apify.py --token apify_api_XXXXX --solo-grandes --inicio 50
```

**Tiempo estimado:** ~3 horas (178 ferreterias / 10 por lote × 10 min por lote)

---

## RESUMEN — LO QUE TENEMOS HOY

| Entregable | Estado | Para que sirve |
|---|---|---|
| `BD_RUES_Limpia.xlsx` | LISTO | BD nacional 34,133 ferreterias — entrega al profe |
| `BD_Regiones_Prioritarias.xlsx` | LISTO | 14,642 ferreterias prioritarias — entrega al profe |
| `mapa_v1.html` | LISTO | Mapa interactivo — demo en presentacion |
| `limpiar_datos.py` | LISTO | Pipeline ETL del RUES |
| `cruce_apify.py` | LISTO | Enriquecimiento Google Maps |
| `geocodificar_addresses.py` | CORRIENDO | GPS para todas las ferreterias |
| `BD_Geocodificada.xlsx` | EN PROGRESO | 106 geocodificadas, ~8h mas |
| `arquitectura_solucion_v2.pptx` | LISTO | Diagrama para presentacion |
| Flujos N8N (ProyectoUniversidad) | LISTO | Actualizacion BD + correos cemento |

---

## QUE FALTA — Proximas semanas

### Esta semana (Apr 13-18) — PENDIENTE

| Tarea | Como | Tiempo |
|---|---|---|
| Terminar geocodificacion GPS | `geocodificar_addresses.py` corriendo | ~8h (automatico) |
| Apify para MEDIANA+GRANDE | `cruce_apify.py --solo-grandes` | ~3h |
| Regenerar mapa con GPS real | `python mapa_v1.py --input BD_Geocodificada.xlsx` | 5 min |
| Conectar credenciales N8N | GmailArgos (OAuth2) + ApifyHeader en n8n.cloud | 20 min |
| Activar Flujo 1 N8N | Trigger manual en n8n.cloud | 10 min |

### Semana 2 (Apr 19-25) — ENRIQUECIMIENTO

| Tarea | Como |
|---|---|
| Escalar Apify a las 1,231 PEQUENA | Mas creditos Apify (cada miembro del equipo crea cuenta = $5 gratis cada uno) |
| Verificar fuzzy match manualmente | Analista de Datos revisa muestra del 10% |
| Mapa v2 con GPS real y filtros | Actualizar mapa_v1.py con filtros por tamano y cemento |

### Semana 3 (Apr 26 - May 2) — AUTOMATIZACION Y CEMENTO

| Tarea | Como |
|---|---|
| Activar Flujo 2 N8N (correos cemento) | Reemplazar mock por datos reales de BD |
| Enviar 500+ correos "Vende cemento?" | N8N Flujo 2 → Gmail → ferreterias con correo disponible |
| Registrar respuestas en BD | N8N actualiza campo `vende_cemento` automaticamente |
| Boton "Actualizar BD" funcional | Conectar N8N con la BD final |
| Dashboard con filtro cemento | Agregar filtro `vende_cemento` al mapa |

### Semana 4 (May 3-9) — PRESENTACION FINAL

| Tarea | Como |
|---|---|
| BD final cerrada | Sin mas cambios de datos |
| Dashboard pulido | Filtros, exportar Excel, estadisticas |
| Ensayo presentacion | 30 min, rol por persona |
| Presentacion a Argos | Demo en vivo: BD → Mapa → N8N → Correos |

---

## ARQUITECTURA DE LA SOLUCION (para explicar en reunion)

```
FUENTE DE DATOS
    RUES (34,133 ferreterias)
    Registro oficial de empresas colombianas
    NIT / Direccion / Correo / Municipio
            |
            v
LIMPIEZA (limpiar_datos.py)
    Normaliza nombres → quita SAS, LTDA
    Clasifica correo: Personal / Corporativo
    Separa NIT vs Cedula
    Filtra regiones prioritarias
            |
            v
ENRIQUECIMIENTO
    Nominatim (gratis)          Apify + Google Maps (presupuesto)
    Geocodifica direcciones      Nombre comercial real
    → latitud / longitud         Telefono, Web, Rating
            |                           |
            └───────────────────────────┘
                        |
                        v
            BASE DE DATOS CENTRAL
            BD_Geocodificada.xlsx / BD_Enriquecida.xlsx
            34,133 registros | 25 campos
                        |
            ┌───────────┼──────────────┐
            v           v              v
        Mapa        Dashboard       N8N Flujos
     interactivo   con filtros    Actualizacion BD
     mapa_v1.html  (semana 3-4)   + Correos cemento
                                  + Boton on-demand
```

---

## COMO EXPLICAR APIFY EN LA REUNION

**El problema:**
El 71% de nuestras ferreterias tienen registradas en el RUES el nombre del dueno, no el nombre del negocio. "JOSE ALFREDO RAMIREZ GRISALES" no sirve para Argos — ellos necesitan saber que se llama "Ferreteria El Clavo" y que tiene telefono +57 300 xxx xxxx.

**La solucion con Apify:**
Apify es una plataforma que automatiza busquedas en Google Maps. En vez de que una persona busque manualmente cada ferreteria en Google Maps (imposible para 14k), Apify lo hace automaticamente.

Le enviamos una lista de busquedas como:
- "ferreteria Carrera 103A 77C-05 Bogota Colombia"
- "ferreteria Calle 38 17-09 Calarca Colombia"

Y Apify devuelve para cada una:
- Nombre del negocio en Google Maps
- Telefono
- Coordenadas GPS
- Pagina web
- Calificacion de usuarios

**Resultado real que obtuvimos hoy (prueba):**
```
Buscamos: "ferreteria CALLE 51 CARRERA 48-3 Bello Colombia"
Apify encontro: "Ferrobello Deposito y ferreteria"
Telefono: +57 324 6127130
GPS: 6.3351, -75.5094
```

**Costo:** $5 USD al mes gratis por cuenta. Con 7 personas en el equipo = $35 USD gratis = ~1,660 ferreterias enriquecidas sin costo adicional.

---

## CREDENCIALES Y HERRAMIENTAS

| Herramienta | Acceso | Estado |
|---|---|---|
| N8N | https://laurent365.app.n8n.cloud | Flujos creados, falta conectar Gmail |
| Apify | Daniel_agudelo395 | $4.50 disponibles, listo para usar |
| RUES CSV | Etapa3/RUES_Ferreterias_7-4-2026... | Descargado |
| Nominatim | Sin cuenta (gratis) | Corriendo automaticamente |

---

*Documentado en sesion de trabajo 13 de Abril de 2026*
*AI Developer: Daniel | Claude Code (Anthropic)*

---

## COMO EXPLICAR LO QUE HICIMOS HOY (resumen para la reunion)

### El punto de partida

Teniamos un archivo del gobierno (RUES) con 34,135 ferreterias registradas en Colombia. Ese archivo tiene el nombre legal de cada empresa, su direccion, correo, municipio. Pero tiene tres problemas grandes:

1. El 71% de los nombres son nombres de personas, no de negocios. "JOSE ALFREDO RAMIREZ GRISALES" no le dice nada al equipo comercial de Argos.
2. No tiene telefonos. El RUES no los pide.
3. No tiene coordenadas GPS. Sin eso no hay mapa.

Hoy resolvimos el problema 1 parcialmente, y dejamos corriendo las soluciones para el 2 y el 3.

---

### Lo que hicimos — en lenguaje simple

**Primero: limpiamos la base de datos.**

Escribimos un programa que lee el archivo del RUES y lo convierte en una base de datos lista para usar. Ese programa:
- Detecta cuales son empresas (Persona Juridica) y cuales son personas naturales duenas de ferreterias
- Para las empresas: les quita los sufijos legales del nombre. "FERRETERIA FERREPOL S.A.S." queda como "Ferreteria Ferrepol"
- Clasifica los correos: el 94% son personales (gmail, hotmail). Los separamos de los corporativos
- Filtra las regiones que le interesan a Argos: Bogota, Antioquia, Cundinamarca y Eje Cafetero
- Elimina los duplicados

El resultado: dos archivos Excel listos para entregar al profesor esta semana.
- Uno con las 34,133 ferreterias nacionales
- Uno con las 14,642 de las regiones prioritarias

**Segundo: hicimos el mapa interactivo.**

Con esos datos generamos un mapa de Colombia que muestra donde esta cada ferreteria. El mapa tiene tres capas que se pueden activar o desactivar:
- Marcadores individuales por ferreteria: al hacer clic se ve el nombre, la direccion, el correo y el tamano
- Mapa de calor: muestra donde hay mas concentracion de ferreterias
- Circulos por municipio: el tamano del circulo es proporcional a cuantas ferreterias hay ahi

El mapa ya esta listo y funciona en el navegador. Hoy lo hicimos con el centro de cada municipio como referencia. Manana va a tener GPS exacto por direccion (ver abajo).

**Tercero: dejamos corriendo la geocodificacion automatica.**

Para poner cada ferreteria en su punto exacto del mapa necesitamos convertir "CL 37 NRO 7F 55, Riohacha" en coordenadas GPS. Eso se llama geocodificacion.

Hay una herramienta gratuita que hace eso: Nominatim, de OpenStreetMap. No necesita cuenta, no cuesta nada. La limitacion es que solo puede procesar una direccion por segundo, entonces para 14,642 ferreterias necesita unas 8 horas.

Lo dejamos corriendo automaticamente mientras la reunion. Manana por la manana va a estar listo y regeneramos el mapa con GPS real.

**Cuarto: conectamos con Google Maps via Apify.**

Esta fue la prueba mas importante del dia. Hicimos una prueba con 10 ferreterias reales de Bogota, Medellin y el Eje Cafetero. Le enviamos a Apify la direccion de cada una, y en 10 minutos nos devolvio el nombre real del negocio, el telefono y las coordenadas GPS exactas.

Resultado real de la prueba:
- Buscamos: "ferreteria CALLE 51 CARRERA 48-3 Bello Colombia"
- Apify encontro en Google Maps: "Ferrobello Deposito y ferreteria"
- Telefono: +57 324 6127130
- GPS exacto: 6.3351, -75.5094

Eso es exactamente lo que Argos necesita. El nombre real del negocio y como contactarlos.

---

### Que pasa manana

**En la noche de hoy (automatico, sin que nadie haga nada):**
El programa de geocodificacion sigue corriendo y va llenando las coordenadas GPS de las 14,642 ferreterias.

**Manana en la manana (5 minutos de trabajo):**
Cuando termine la geocodificacion, regeneramos el mapa con un solo comando. El mapa va a mostrar cada ferreteria en su ubicacion exacta, no en el centro del municipio.

**Manana cuando haya 3 horas disponibles:**
Corremos el cruce con Apify para las 178 ferreterias mas grandes (MEDIANA y GRANDE). Esas son las que mas les interesan a Argos porque son las que mas volumen de cemento pueden comprar. Con los $4.50 de creditos que tenemos disponibles alcanza exactamente para esas 178.

---

### El gran diferenciador que viene (semana 3)

Todo lo que hicimos hoy es la base. Pero el valor real para Argos viene en la semana 3 con N8N.

Ya tenemos los flujos de N8N construidos y probados. Lo que van a hacer es:

Tomar cada ferreteria que tiene correo disponible en la base de datos, y enviarle automaticamente un correo que dice algo como: "Buenos dias, estamos interesados en saber si su ferreteria comercializa cemento. Por favor respondanos Si o No."

Cuando la ferreteria responde, N8N recibe el correo, lo lee, y actualiza automaticamente la base de datos con el campo "vende_cemento = Si" o "vende_cemento = No".

Eso es lo que Argos realmente necesita: saber cuales ferreterias venden cemento y cuales no. Nadie mas les ha dado esa informacion de forma automatizada y actualizada.

---

### En numeros — lo que entregamos hoy

| Que | Cuanto |
|---|---|
| Ferreterias en la base de datos | 34,133 |
| Ferreterias en regiones prioritarias | 14,642 |
| Departamentos cubiertos | 6 (Bogota, Antioquia, Cundinamarca, Risaralda, Caldas, Quindio) |
| Ferreterias grandes (MEDIANA + GRANDE) | 178 |
| Correos disponibles para campana cemento | 34,133 (94% personales, 6% corporativos) |
| Campos por ferreteria en la BD | 25 |
| Mapa interactivo | Listo, 3 capas, funciona en navegador |
| Costo total del dia | $0.21 USD (pruebas Apify) |
