# 🔍 Diagnóstico Base de Datos RUES — Ferreterías Colombia
**Fuente:** RUES_Ferreterias_7-4-2026 (códigos CIIU 4752 y 4663)  
**Fecha análisis:** 11 de abril de 2026  
**Total registros:** 34.135 ferreterías

---

## 1. Lo que SÍ tenemos (campos disponibles en RUES)

| Campo RUES | Campo requerido por Argos | Estado |
|---|---|---|
| `municipio` | Municipio | ✅ Completo (0 nulos) |
| `direccion_comercial` | Dirección | ✅ Casi completo (1 nulo) |
| `numero_identificacion` | NIT | ⚠️ Parcial — 30.4% son NIT, 69.2% son Cédula de Ciudadanía |
| `correo_comercial` | Correo Electrónico | ⚠️ Disponible pero 94.7% son correos **personales** (gmail, hotmail) |
| `fecha_matricula` | Fecha Actualización | ⚠️ Es fecha de matrícula en Cámara de Comercio, no fecha de actualización del dato |
| `departamento` | (implícito en municipio) | ✅ Completo |
| — | Latitud | ❌ No disponible — requiere geocodificación |
| — | Longitud | ❌ No disponible — requiere geocodificación |
| — | Teléfono | ❌ No disponible en RUES |
| — | WhatsApp | ❌ No disponible |
| — | Fuente | ❌ No está como campo — agregar manualmente: "RUES / Cámara de Comercio" |

### Campos adicionales de valor en RUES (bonus)
- `org_juridica`: Persona Natural (71.2%) vs Persona Jurídica (28.8%)
- `actividad_economica`: Descripción CIIU completa
- `desc_tamano_empresa`: MICRO (92.5%), PEQUEÑA (6.5%), MEDIANA (0.8%), GRANDE (0.1%)
- `rep_legal`: Representante legal (71% vacío)

---

## 2. El problema grande: Nombres de negocios

**78.6% de los registros (26.838) son nombres de persona, NO nombre comercial.**

Esto pasa porque en RUES las personas naturales registran su nombre completo, no el de su ferretería. Ejemplos:

| Nombre en RUES (lo que tenemos) | Nombre comercial real (lo que queremos) |
|---|---|
| GUTIERREZ MARTINEZ DANILO RAFAEL | Ferretería Gutiérrez |
| TORRES DUEÑAS PATRICIO | Ferretería Torres |
| JOSE ALFREDO RAMIREZ GRISALES | Ferreto Eje Cafetero *(solo Google sabe)* |

**Solo 21.4% (7.297 registros) tienen nombre tipo empresa** (incluye "FERRETERIA", "DISTRIBUIDORA", "S.A.S", etc.)

### Estrategia de normalización de nombres:
1. **Personas Jurídicas (9.846):** Limpiar sufijos legales (S.A.S, LTDA, E.U) y normalizar capitalización → "Ferretería Quil" en lugar de "FERRETERIA QUIL S.A.S."
2. **Personas Naturales con nombre comercial (aprox. 3.000):** Extraer el keyword ferretería + apellido
3. **Personas Naturales sin nombre comercial (~23.000):** **Cruzar con Google Maps** usando dirección + municipio para obtener el nombre comercial real → Este es el trabajo clave del scraping

---

## 3. El problema del correo electrónico

- **94.7% son correos personales** (gmail.com, hotmail.com, yahoo.com, outlook.com)
- Solo **1.797 correos corporativos** (dominio propio tipo `@ferreteria.com.co`)
- Muchos correos personales pueden ser del dueño, no de la ferretería
- Algunos correos tienen **múltiples emails en un campo** (ej: `gerencia@edemco.co notificacionesjudiciales@edemco.co`) — necesita limpieza

### Estrategia correos:
- Conservar todos los correos disponibles como `correo_rues`
- Marcar si es personal o corporativo con campo `tipo_correo` (Personal / Corporativo)
- Vía Google Places API intentar obtener el correo/website del negocio
- Para la campaña de verificación de cemento (N8N), usar el correo disponible como primer contacto

---

## 4. Cobertura geográfica — Regiones prioritarias

| Departamento | Registros | % del total |
|---|---|---|
| Bogotá D.C. | 6.269 | 18.4% |
| Antioquia | 4.138 | 12.1% |
| Valle del Cauca | 3.352 | 9.8% |
| Cundinamarca | 2.272 | 6.7% |
| Santander | 1.899 | 5.6% |
| **Subtotal Bogotá + Antioquia + Cundinamarca** | **12.679** | **37.1%** |
| **Eje Cafetero (Risaralda + Caldas + Quindío)** | **1.963** | **5.7%** |
| **TOTAL REGIONES PRIORITARIAS** | **14.642** | **42.9%** |

---

## 5. Calidad general del dataset

| Indicador | Valor |
|---|---|
| Total registros | 34.135 |
| Duplicados por NIT | 0 ✅ |
| Duplicados por Cédula | 1 (mínimo) |
| Duplicados por razón social | 9 (mínimo) |
| Registros con dirección | 34.134 (99.99%) |
| Rango fechas matrícula | 1962 – abril 2026 |
| Registros activos recientes (2020-2026) | 17.089 (50.1%) |

---

## 6. Lo que falta conseguir (vía Google Maps / scraping)

| Campo faltante | Cómo conseguirlo | Prioridad |
|---|---|---|
| Nombre comercial real | Google Places API (buscar por dirección+municipio) | 🔴 Alta |
| Teléfono | Google Places API | 🔴 Alta |
| Latitud / Longitud | Google Geocoding API (desde dirección) | 🔴 Alta |
| Página web | Google Places API | 🟡 Media |
| WhatsApp | Derivar del teléfono (prefijo local) | 🟡 Media |
| Vende cemento (Sí/No) | Flujo N8N (correo automático) + scraping web | 🔴 Alta |
| Calificación Google | Google Places API (señal de negocio activo) | 🟢 Baja |
| Horarios | Google Places API | 🟢 Baja |

---

## 7. Plan de acción inmediato

### Fase 1 — Limpieza RUES (esta semana, `limpiar_datos.py`)
- [ ] Eliminar 10 duplicados
- [ ] Normalizar `razon_social`: eliminar sufijos legales, capitalización correcta
- [ ] Agregar campo `tipo_correo`: Personal / Corporativo
- [ ] Agregar campo `fuente`: "RUES"
- [ ] Agregar campo `fecha_actualizacion`: usar `fecha_matricula` como proxy + nota
- [ ] Separar campo `numero_identificacion` en NIT vs CC
- [ ] Filtrar subconjunto regiones prioritarias para el MVP

### Fase 2 — Enriquecimiento Google Maps (semana 2)
- [ ] Geocodificación: dirección + municipio → Latitud/Longitud
- [ ] Google Places API: nombre comercial, teléfono, web, calificación
- [ ] Normalización de nombres: cruzar RUES vs Google → tomar nombre más comercial
- [ ] Marcar registros donde Google no encontró match (datos a verificar)

### Fase 3 — Verificación cemento con N8N (semana 2-3)
- [ ] Flujo N8N: enviar correo amable a ferreterías con correo disponible
- [ ] Pregunta: ¿Vende cemento? Sí / No
- [ ] Registrar respuestas en base de datos
- [ ] Para las sin respuesta: marcar como "No verificado"

### Fase 4 — Dashboard MVP (semana 3)
- [ ] Dashboard con mapa de calor por municipio
- [ ] Filtros por región, tamaño, vende cemento
- [ ] Botón "Actualizar base de datos" (trigger N8N o script)
- [ ] Exportar Excel / CSV desde la interfaz

---

## 8. Estructura propuesta de la base de datos final

```
ferreterias_argos/
├── id_ferreteria          (generado)
├── nombre_rues            (razón social original RUES)
├── nombre_comercial       (normalizado desde Google Maps)
├── nit                    (si aplica)
├── tipo_identificacion    (NIT / CC / otro)
├── numero_identificacion  (número)
├── org_juridica           (Natural / Jurídica)
├── tamano_empresa         (MICRO / PEQUEÑA / MEDIANA / GRANDE)
├── departamento
├── municipio
├── direccion_comercial
├── latitud
├── longitud
├── telefono
├── whatsapp
├── correo_rues            (correo original RUES)
├── tipo_correo            (Personal / Corporativo)
├── correo_verificado      (si se consiguió uno mejor)
├── pagina_web
├── vende_cemento          (Sí / No / No verificado)
├── fecha_matricula_rues
├── fecha_actualizacion    (fecha del último enriquecimiento)
├── fuente                 (RUES / Google Maps / Scraping / Respuesta N8N)
├── calificacion_google    (opcional)
└── notas
```

---

*Documento generado para reunión equipo — Etapa 3 Proyecto Argos*
