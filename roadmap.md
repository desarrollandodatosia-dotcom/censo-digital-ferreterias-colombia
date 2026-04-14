# Roadmap — Sistema de Ferreterías para Cementos Argos
**Cliente:** Cementos Argos | **Equipo:** 7 personas | **Duración:** 4 semanas | **Inicio:** 11 Abril 2026

---

## Objetivo General del Proyecto

> **Construir un sistema automatizado que mantenga una base de datos nacional de ferreterías colombianas actualizada, identificando cuáles venden cemento, con una interfaz simple que permita al equipo comercial de Argos actualizar la información bajo demanda o cada 3-4 meses.**

### Lo que Argos necesita en concreto

| Dimensión | Detalle |
|---|---|
| **Qué** | Base de datos de ferreterías con 12+ campos: NIT, nombre comercial, municipio, dirección, coords, teléfono, WA, correo, vende cemento, fuente, fecha |
| **Para quién** | Área comercial de Argos (no técnicos) |
| **Por qué** | Identificar ferreterías que venden cemento → ampliar cobertura de ventas Argos |
| **Cómo** | RUES (base) + Apify/Google Maps (enriquecimiento) + N8N (automatización) + IA (normalización) |
| **Frecuencia** | Cada 3-4 meses automático + botón on-demand |
| **Entregable mínimo (MVP)** | Excel/BD limpia + dashboard con mapa + botón actualización |
| **Diferenciador** | Segmentación por cemento + flujo N8N de verificación automática |

### Regiones prioritarias (definidas por Argos)
- Cundinamarca + Bogotá D.C.
- Antioquia
- Eje Cafetero (Risaralda, Caldas, Quindío)

---

## Niveles de Entrega

```
NIVEL 1 — OBLIGATORIO              NIVEL 2 — ESPERADO               NIVEL 3 — DIFERENCIADOR
───────────────────────            ──────────────────────           ────────────────────────
Base de datos limpia               Dashboard + Mapa                 Flujo N8N automatizado
(Excel / CSV)                      interactivo con filtros          + segmentación cemento
34k registros RUES                 por región, tamaño,              + correos verificación
+ enriquecido con                  vende cemento                    automáticos
Google Maps                        
Toda la BD con campos              Exportar a Excel                 Botón "Actualizar BD"
básicos                            desde la interfaz                on-demand
```

---

## Roadmap Visual — 4 Semanas

```
                 HOY           SEM 1           SEM 2           SEM 3           SEM 4
                 Apr 11        Apr 18          Apr 25          May 2           May 9
                   │             │               │               │               │
FUENTE RUES        ├─[34k limpio]────────────────────────────────────────────────┤
                   │             │               │               │               │
APIFY / GMAPS      │             ├──[Pilot Regiones]──[Escala Nacional]──────────┤
                   │             │               │               │               │
ETL + IA           │             ├──[Limpieza v1]─[Cruce RUES+Maps]─[QA final]──┤
                   │             │               │               │               │
N8N FLUJOS         │             │               ├──[Actualización]─[Cemento]────┤
                   │             │               │               │               │
DASHBOARD          │             │               ├──[Mapa v1]────[Dashboard OK]──┤
                   │             │               │               │               │
ENTREGABLES        ├[Arq+RUES]  [BD Parcial]   [BD+Mapa v1]   [N8N+Cemento]  [PRESENTACIÓN]
```

---

## Semana 0 — HOY (Reunión de equipo) `Apr 11`

### Objetivo: Presentar diagnóstico + alinear al equipo en el nuevo entregable

```
┌─────────────────────────────────────────────────────────────────────┐
│  LO QUE DEBE SALIR DE LA REUNIÓN DE HOY                            │
│                                                                     │
│  ✓ Presentar diagrama arquitectura (arquitectura_solucion.pptx)     │
│  ✓ Presentar diagnóstico de la base RUES (34k registros)            │
│  ✓ Confirmar regiones prioritarias: Antioquia, Cundinamarca, Eje    │
│  ✓ Asignar quién configura Apify esta semana (Ing. Datos)           │
│  ✓ Asignar quién instala N8N esta semana                            │
│  ✓ Confirmar: ¿Excel limpio RUES como entregable inmediato?         │
│  ✓ Fijar reunión de seguimiento en 2-3 días                         │
└─────────────────────────────────────────────────────────────────────┘
```

**Archivos listos para mostrar hoy:**
- `arquitectura_solucion.pptx` — diagrama de arquitectura completo
- `diagnostico_base_datos.md` — análisis del RUES con hallazgos clave
- `limpiar_datos.py` — pipeline ETL ya funcional

---

## Semana 1 — Limpieza y Base Inicial `Apr 12–18`

### Objetivo: Tener la base RUES limpia lista + Apify configurado

#### Hitos de la semana
```
Lun Apr 13  → Apify configurado para regiones prioritarias (Ing. Datos)
Mié Apr 15  → limpiar_datos.py procesando RUES completo (Daniel)
Jue Apr 16  → Excel inicial entregado al profe (base RUES limpia)
Vie Apr 18  → N8N instalado + primer flujo de prueba
```

#### Tareas por rol

**AI Developer (Daniel):**
- [ ] Adaptar `limpiar_datos.py` para procesar el CSV del RUES (actualmente está para JSON de Apify)
- [ ] Agregar clasificación de correo: Personal vs. Corporativo
- [ ] Normalizar nombres: eliminar sufijos SAS/LTDA, capitalizar correctamente
- [ ] Exportar subconjunto de regiones prioritarias como Excel inicial para el profe
- [ ] Documentar cada paso del pipeline en comentarios del código

**Ingeniero de Datos (Sebastián):**
- [ ] Configurar Apify actor "Google Maps Scraper" para búsquedas por municipio
- [ ] Estrategia: buscar cada ferretería RUES por `razon_social + municipio + direccion`
- [ ] Exportar JSON de Apify → compartir en Drive/GitHub
- [ ] Estimar créditos necesarios para las 14.642 ferreterías prioritarias

**N8N / Automatización:**
- [ ] Instalar N8N local (`docker run n8nio/n8n` o `npm install -g n8n`)
- [ ] Crear flujo de prueba: recibir trigger → ejecutar script Python → notificar
- [ ] Documentar la instalación paso a paso para el equipo

**Analista de Datos:**
- [ ] Revisar el Excel RUES limpio manualmente (muestra de 200 registros)
- [ ] Identificar los campos con más datos faltantes por región
- [ ] Proponer criterio de "registro completo mínimo"

#### Métricas de éxito semana 1
- [ ] Excel con RUES limpio entregado al profe (mínimo regiones prioritarias)
- [ ] 0 duplicados en el Excel entregado
- [ ] Apify funcionando con al menos 100 registros de prueba
- [ ] N8N instalado y corriendo

---

## Semana 2 — Enriquecimiento Google Maps `Apr 19–25`

### Objetivo: Cruzar RUES con Google Maps → obtener nombre comercial real, teléfono, coordenadas

#### Hitos de la semana
```
Lun Apr 19  → Reunión asesoría → presentar Excel RUES limpio + Apify corriendo
Mar Apr 21  → Cruce RUES + Apify implementado (Daniel)
Mié Apr 22  → Geocodificación de registros sin coords
Jue Apr 23  → 14.642 ferreterías prioritarias enriquecidas
Vie Apr 25  → Dashboard / Mapa v1 con datos reales
```

#### Tareas por rol

**AI Developer (Daniel):**
- [ ] Script de cruce: RUES + Apify usando fuzzywuzzy por nombre+municipio
- [ ] Lógica: si Google Maps encuentra match → tomar nombre comercial de Maps
- [ ] Geocodificación: dirección RUES → Latitud/Longitud (Google Geocoding API o Nominatim)
- [ ] IA Generativa (Claude Haiku) para normalizar nombres que no hacen match automático
- [ ] Agregar campo `match_google`: Sí / No / Parcial

**Ingeniero de Datos:**
- [ ] Escalar Apify a todas las regiones prioritarias
- [ ] Ejecutar búsquedas por municipio para los 14.642 registros prioritarios
- [ ] Gestionar los créditos de Apify (máximo $5 plan gratuito)

**Analista BI:**
- [ ] Mapa v1: plotear las ferreterías en mapa interactivo con Folium o Streamlit
- [ ] Filtros básicos: por departamento, por tamaño empresa, con/sin teléfono
- [ ] Publicar el mapa para que todo el equipo lo vea

**Analista de Datos:**
- [ ] Auditar el cruce RUES + Google Maps (muestra del 10%)
- [ ] Calcular métricas: % con nombre comercial, % con teléfono, % con coords

#### Métricas de éxito semana 2
- [ ] ≥ 80% de registros prioritarios con nombre comercial real de Google Maps
- [ ] ≥ 70% de registros prioritarios con coordenadas
- [ ] ≥ 50% de registros prioritarios con teléfono
- [ ] Mapa v1 funcionando con datos reales

---

## Semana 3 — N8N + Verificación Cemento `Apr 26 – May 2`

### Objetivo: Automatizar el pipeline + lanzar la campaña de verificación de cemento

#### Hitos de la semana
```
Lun Apr 26  → Reunión asesoría → demo mapa v1 + avance N8N
Mar Apr 27  → Flujo N8N #1: actualización automática de BD funcional
Mié Apr 28  → Flujo N8N #2: envío masivo de correos ¿Vende cemento?
Jue Apr 29  → Primeras respuestas de ferreterías recibidas y guardadas
Vie May 1   → Botón on-demand funcional + dashboard actualizado
```

#### Tareas por rol

**AI Developer (Daniel):**
- [ ] Integrar N8N con el pipeline Python (trigger N8N → ejecutar scripts)
- [ ] Implementar botón "Actualizar BD" en la interfaz
- [ ] Segmentar la BD: Ferreterías que venden cemento / No verificado / No venden

**N8N / Automatización:**
- [ ] Flujo correo ¿Vende cemento?:
  - Tomar ferreterías con correo disponible y sin campo `vende_cemento`
  - Enviar correo amable: "Estamos interesados en saber si comercializan cemento..."
  - Esperar respuesta (24-48h)
  - Si responde Sí → actualizar `vende_cemento = Sí`
  - Si responde No → actualizar `vende_cemento = No`
  - Si no responde en 48h → marcar `vende_cemento = No verificado` + retry 1 vez
- [ ] Flujo scheduler: ejecutar pipeline completo cada 3 meses (cron)

**Analista BI:**
- [ ] Dashboard completo con filtro por `vende_cemento`
- [ ] Mapa de calor por municipio mostrando densidad de ferreterías
- [ ] Botón "Exportar Excel" desde la interfaz del dashboard
- [ ] Estadísticas: total por región, % venden cemento, % verificado

**Analista de Datos:**
- [ ] QA final de la BD completa
- [ ] Validar que correos no sean duplicados antes del envío masivo
- [ ] Calcular cobertura: de 34k, cuántos tienen correo disponible para verificar

#### Métricas de éxito semana 3
- [ ] ≥ 500 correos enviados para verificación de cemento
- [ ] Botón on-demand funcional
- [ ] Dashboard con filtro de cemento operativo
- [ ] Scheduler N8N configurado (aunque no haya corrido aún)

---

## Semana 4 — Dashboard Final + Presentación `May 3–9`

### Objetivo: Pulir la solución y presentar ante Argos

#### Hitos de la semana
```
Lun May 4   → Reunión asesoría → ensayo presentación
Mar May 5   → BD final cerrada (no más cambios de datos)
Mié May 6   → Dashboard y botón pulidos + documentación completa
Jue May 7   → Ensayo general de presentación (30 min)
Vie May 8   → PRESENTACIÓN FINAL
```

#### Entregables finales

```
ENTREGABLE 1: BASE DE DATOS
  └─ ferreterias_argos_FINAL.xlsx / .db
     ├─ 34.135 registros nacionales (o subconjunto de calidad)
     ├─ 12+ campos completos (según disponibilidad por registro)
     ├─ Campo vende_cemento: Sí / No / No verificado
     ├─ Nombre comercial normalizado (de Google Maps donde aplique)
     ├─ Coordenadas para los que fue posible geocodificar
     └─ Sin duplicados verificados

ENTREGABLE 2: DASHBOARD + MAPA
  └─ Interfaz simple (Streamlit o app web local)
     ├─ Mapa interactivo con todos los puntos
     ├─ Filtros: región, vende cemento, tamaño empresa, tiene contacto
     ├─ Métricas: total registros, % verificados, % venden cemento
     ├─ Botón "Actualizar base de datos" (on-demand)
     └─ Exportar Excel/CSV desde la interfaz

ENTREGABLE 3: AUTOMATIZACIÓN N8N
  └─ Flujos documentados y funcionales
     ├─ Flujo actualización periódica (cada 3-4 meses)
     ├─ Flujo verificación cemento (correos automáticos)
     └─ Documentación de requerimientos para producción en Argos

ENTREGABLE 4: DOCUMENTACIÓN TÉCNICA
  └─ Manual completo del sistema
     ├─ Arquitectura y paso a paso del pipeline
     ├─ Herramientas usadas y por qué
     ├─ Requerimientos para llevar a producción (si Argos lo adopta)
     └─ Manual de usuario (para el equipo comercial no técnico)
```

#### Guión de presentación sugerido (para el equipo)
1. **El problema** (1 min): Argos no sabe cuáles ferreterías venden cemento de su competencia o potenciales clientes
2. **Nuestra solución** (2 min): Sistema automatizado que combina fuentes oficiales + Google Maps + IA
3. **Demo en vivo** (5 min): Mostrar BD → Mapa con filtros → Botón actualización → Correos N8N
4. **Resultados** (2 min): X ferreterías, Y% verifican vender cemento, Z regiones cubiertas
5. **Cómo escalar** (2 min): Requerimientos para llevar a producción, frecuencia de actualización
6. **Preguntas** (3 min)

---

## Dependencias Críticas

```
Si el RUES CSV tiene problemas de encoding → el script falla al cargar
    └─ MITIGACIÓN: Ya identificado encoding latin-1 con sep=';' ✅

Si Apify no encuentra la ferretería por nombre → registro sin nombre comercial
    └─ MITIGACIÓN: Marcar como "No encontrado" y dejar razón social RUES

Si las ferreterías no responden el correo de cemento → campo queda "No verificado"
    └─ MITIGACIÓN: Intentar 1 retry a los 7 días, luego cerrar como No verificado

Si N8N no puede enviar correos masivos → revisar SMTP y límites
    └─ MITIGACIÓN: Usar Gmail SMTP (500/día gratis) o Mailgun (1000/día gratis)

Si el equipo no comparte archivos en tiempo real → cuello de botella
    └─ MITIGACIÓN: Google Drive / GitHub compartido con carpeta Etapa3
```

---

## Resumen Ejecutivo del Roadmap

| Semana | Tema central | Entregable concreto | Meta numérica |
|---|---|---|---|
| **0 (hoy)** | Diagnóstico + alineación | Arquitectura + diagnóstico RUES presentados | Equipo alineado |
| **1** | Limpieza RUES + Apify setup | Excel RUES limpio entregado al profe | 34k registros procesados |
| **2** | Enriquecimiento Google Maps | BD enriquecida + Mapa v1 | ≥80% nombre comercial, ≥70% coords |
| **3** | N8N + Verificación cemento | Botón actualización + correos lanzados | ≥500 correos enviados |
| **4** | Presentación final | Demo en vivo + documentación completa | Presentación a Argos |
