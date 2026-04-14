# Notas Rápidas — Cheat Sheet del Proyecto | AI Developer Daniel
> Documento de referencia rápida para reuniones, trabajo diario y onboarding del equipo.
> Actualizado: 11 Abril 2026

---

## 1. EL PROYECTO EN UNA FRASE

> "Sistema automatizado que mantiene una base de datos nacional de ferreterías colombianas actualizada, identificando cuáles venden cemento, para que el equipo comercial de Argos amplíe su cobertura de ventas."

---

## 2. LO QUE CONFIRMÓ EL PROFE — Los 5 puntos más importantes

| # | Lo que dijo | Implicación práctica |
|---|---|---|
| 1 | Corre local, no necesitan hosting | Sin costos de VPS ni AWS. Todo en el computador del equipo |
| 2 | Frecuencia: cada 3-4 meses + botón on-demand | Dos modos: scheduler automático + botón manual |
| 3 | El campo más crítico es "vende cemento" | El flujo N8N de verificación NO es opcional |
| 4 | Presentación para no técnicos (área comercial) | Lenguaje simple, enfoque en resultados, no en código |
| 5 | Para esta semana: arquitectura + BD inicial | Tenemos arquitectura ✅. Falta: Excel subconjunto RUES |

---

## 3. LAS FUENTES DE DATOS — Qué da cada una

| Fuente | Lo que da | Lo que NO da | Estado |
|---|---|---|---|
| **RUES** (ya tenemos) | NIT, Razón social, Municipio, Dirección, Correo (94% personal), CIIU, Tamaño empresa | Nombre comercial real, Teléfono, Coordenadas, WhatsApp | ✅ 34.135 registros |
| **Apify (Google Maps)** | Nombre comercial real, Teléfono, Latitud/Longitud, Web, Rating | NIT, CIIU oficial, Estado legal | 🔄 Por configurar |
| **N8N correo** | Confirmación si vende cemento (Sí/No) | — | 🔄 Por implementar |

### Regla de oro para nombres
> Cuando Google Maps y RUES tienen el mismo negocio → **siempre usar el nombre de Google Maps** (es el nombre comercial real, lo que el cliente ve).

---

## 4. LA ESTRUCTURA DE DATOS FINAL

```
ferreterias_argos/
├── id_ferreteria          ← generado automáticamente
├── nombre_rues            ← razón social original del RUES
├── nombre_comercial       ← nombre normalizado de Google Maps ⭐
├── nit                    ← del RUES (si es persona jurídica)
├── tipo_identificacion    ← NIT / CC / otro
├── numero_identificacion  ← el número
├── org_juridica           ← Persona Natural / Jurídica
├── tamano_empresa         ← MICRO / PEQUEÑA / MEDIANA / GRANDE
├── departamento           ← del RUES ✅
├── municipio              ← del RUES ✅
├── direccion_comercial    ← del RUES ✅
├── latitud                ← de Google Maps / Geocoding ❌ pendiente
├── longitud               ← de Google Maps / Geocoding ❌ pendiente
├── telefono               ← de Google Maps ❌ pendiente
├── whatsapp               ← derivado del teléfono ❌ pendiente
├── correo_rues            ← correo original del RUES ⚠️ 94% personal
├── tipo_correo            ← Personal / Corporativo
├── vende_cemento          ← Sí / No / No verificado ❌ pendiente N8N
├── fecha_matricula_rues   ← fecha de registro en cámara de comercio
├── fecha_actualizacion    ← fecha del último enriquecimiento
├── fuente                 ← RUES / Google Maps / N8N Respuesta
└── notas                  ← campo libre para observaciones
```

**Campos resaltados en naranja en el diagrama de arquitectura:** nombre_comercial, latitud/longitud, vende_cemento → son los más críticos de conseguir.

---

## 5. CÓMO HABLAR CON CADA ROL DEL EQUIPO

**Con Sebastián (Ingeniero de Datos):**
> "Necesito que configures Apify para buscar cada ferretería del RUES por nombre+municipio+dirección. El output debe ser un JSON con: nombre, telefono, latitud, longitud, web. Yo me encargo de cruzarlo con el RUES."

**Con el Analista de Datos:**
> "Cuando yo limpie la base, te paso el Excel para que hagas QA: revisar 200 registros aleatorios y decirme qué campos tienen más problemas."

**Con el Analista BI:**
> "Necesito que montes el mapa con Folium o Streamlit. Los datos van a tener: municipio, latitud, longitud, nombre comercial, y si vende cemento. El filtro más importante es ese último."

**Con quien lleve N8N:**
> "El flujo principal es: cuando hay una ferretería sin campo vende_cemento → enviar correo con pregunta simple → registrar respuesta en la BD. Segundo flujo: botón que ejecuta todo el pipeline de actualización."

**Con el Documentador:**
> "Documenta todo lo que yo haga técnicamente: qué hace cada script, por qué usamos cada herramienta, y qué necesitaría Argos para llevar esto a producción."

---

## 6. PREGUNTAS CLAVE PARA LA REUNIÓN DE HOY

- [ ] ¿Sebastián ya tiene el Excel del RUES listo para mostrarle al profe?
- [ ] ¿Quién se encarga de instalar N8N esta semana?
- [ ] ¿Quién configura Apify para la búsqueda masiva?
- [ ] ¿Cómo compartimos los archivos en tiempo real? (Google Drive / GitHub)
- [ ] ¿Cuándo es la próxima reunión? (profe sugirió cada 2-3 días)
- [ ] ¿Tenemos algún correo del equipo para probar el flujo de N8N?

---

## 7. DECISIONES YA TOMADAS (no reabrir en la reunión)

| Decisión | Quién la tomó | Cuándo |
|---|---|---|
| Solución corre local (sin hosting) | Profe Diego | Reunión 10 Abr |
| Frecuencia: 3-4 meses + on-demand | Profe Diego | Reunión 10 Abr |
| Flujo N8N de correo cemento es obligatorio | Profe Diego | Reunión 10 Abr |
| Presentación en nivel básico/intermedio (no técnico) | Profe Diego | Reunión 10 Abr |
| RUES como fuente base (ya tenemos 34k) | Sebastián + equipo | Reunión 10 Abr |
| Regiones prioritarias: Cundinamarca, Antioquia, Eje Cafetero | Argos | Desde el inicio |

---

## 8. ALERTAS TÉCNICAS — Lo que puede salir mal

| Riesgo | Probabilidad | Solución |
|---|---|---|
| Apify no encuentra la ferretería por nombre | Alta (30%+ registros) | Marcar como "No encontrado en Google" y usar datos RUES |
| Correos masivos N8N bloqueados como spam | Media | Usar dominio propio o servicio SMTP confiable (Mailgun) |
| Ferretería sin respuesta al correo cemento | Alta (60%+) | Marcar como "No verificado" — es esperado y válido |
| RUES tiene nombre del dueño, no del negocio | Muy Alta (78%) | El cruce con Google Maps resuelve esto — es el propósito de Apify |
| Google Maps no tiene el negocio | Media (20%) | Aceptable — usar lo que da el RUES y marcar la fuente |

---

## 9. GLOSARIO RÁPIDO — Para explicarle a no técnicos

| Término | Explicación simple |
|---|---|
| **RUES** | Registro oficial del gobierno con todas las empresas de Colombia |
| **Apify** | Herramienta que extrae información de Google Maps automáticamente |
| **ETL** | "Extraer, Transformar, Cargar" — limpiar datos crudos y meterlos en una tabla ordenada |
| **fuzzywuzzy** | Detecta que "Ferretería El Tornillo" y "FERRETERIA EL TORNILLO SAS" son lo mismo |
| **N8N** | Sistema que conecta aplicaciones y automatiza flujos — como el correo de cemento |
| **Geocodificación** | Convertir una dirección en coordenadas GPS (latitud/longitud) |
| **Pipeline** | El proceso completo paso a paso: desde los datos crudos hasta el Excel limpio |
| **On-demand** | "A pedido" — cuando el usuario presiona el botón, se actualiza |

---

## 10. ESTADO ACTUAL DEL PROYECTO (11 Abril 2026)

| Artefacto | Estado | Archivo |
|---|---|---|
| Pipeline ETL (`limpiar_datos.py`) | ✅ Funcional | `limpiar_datos.py` |
| Diagnóstico base RUES | ✅ Completo | `diagnostico_base_datos.md` |
| Diagrama arquitectura | ✅ Listo | `arquitectura_solucion.pptx` |
| Roadmap 4 semanas | ✅ Actualizado | `roadmap.md` |
| Base de datos RUES (CSV crudo) | ✅ Disponible | `RUES_Ferreterias_7-4-2026...csv` |
| Base de datos RUES (Excel limpio) | 🔄 Pendiente | — |
| Configuración Apify | 🔄 Pendiente | — |
| N8N instalado | 🔄 Pendiente | — |
| Flujo correo cemento | 🔄 Pendiente | — |
| Dashboard/Mapa | 🔄 Pendiente | — |
