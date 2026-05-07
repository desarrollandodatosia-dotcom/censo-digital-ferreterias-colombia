# Automatizaciones N8N — CEMANTIX

Flujos de automatización del sistema CEMANTIX exportados en formato JSON.
Para importarlos en N8N: **Settings → Import Workflow → subir el archivo .json**.

---

## WF1 — CEMANTIX: Vende Cemento?

**Archivo:** `WF1_CEMANTIX_VendeCemento.json`  
**ID original:** `2OKf7u2ki2RdkEwC`  
**Tipo:** Disparo manual  
**Credencial requerida:** Gmail OAuth2 (cuenta con acceso de envío configurada en N8N)

### Flujo
```
[Manual Trigger: "Iniciar Envio TEST"]
       ↓
[Code Node: "Cargar Ferreterias"]
  - TEST_MODE = true  → envía solo a desarrollandodatosia@gmail.com (prueba)
  - TEST_MODE = false → itera sobre 19 ferreterías reales con correos verificados
       ↓
[Gmail Node: "Enviar Email"]
  - Asunto: "Consulta rapida — Directorio de Ferreterias Colombia"
  - Remitente: "Equipo CEMANTIX | EAFIT"
  - Cuerpo HTML con 3 botones de respuesta
```

### Botones del correo
| Botón | Texto | Parámetro URL |
|---|---|---|
| Verde | ✅ Si, comercializamos cemento | `respuesta=si` |
| Naranja | 🔸 Si, pero de forma ocasional | `respuesta=parcial` |
| Rojo | ❌ No comercializamos cemento | `respuesta=no` |

Los botones apuntan al webhook de **WF2**: `https://laurent395.app.n8n.cloud/webhook/respuesta-cemento-argos`

### Para activar modo producción
Cambiar en el nodo **"Cargar Ferreterias"**:
```javascript
const TEST_MODE = false;  // ← de true a false
```

---

## WF2 — CEMANTIX: Receptor Respuestas Cemento

**Archivo:** `WF2_CEMANTIX_ReceptorRespuestas.json`  
**ID original:** `r3fnPmm8gUAiJ6Gw`  
**Tipo:** Webhook activo 24/7  
**Credencial requerida:** Google Sheets OAuth2

### Webhook URL
```
https://laurent395.app.n8n.cloud/webhook/respuesta-cemento-argos
```

### Parámetros recibidos (query string)
```
?nombre={nombre_ferreteria}&correo={email}&ciudad={ciudad}&respuesta=si|no|parcial
```

### Flujo
```
[Webhook GET /respuesta-cemento-argos]
       ↓
[Responde inmediatamente con página HTML "Gracias"]   (responseMode: onReceived)
       ↓ (asíncrono, en segundo plano)
[Google Sheets: Guardar fila]
  - Sheet ID: 1yNH3aJtlvMmedQfBxCmJXXxYQGw9OV1XLQ4UYAL6tbM
  - Pestaña: "CEMANTIX — Respuestas Vende Cemento Argos"
  - Columnas: fecha_respuesta, nombre_ferreteria, correo, ciudad, respuesta, timestamp
```

### Google Sheets — URL de lectura pública (CSV)
La aplicación Streamlit lee las respuestas directamente desde:
```
https://docs.google.com/spreadsheets/d/1yNH3aJtlvMmedQfBxCmJXXxYQGw9OV1XLQ4UYAL6tbM/export?format=csv&gid=2100342099
```

---

## Configuración de credenciales en N8N (al importar)

Después de importar los workflows, configurar las credenciales:

1. **Gmail OAuth2** (para WF1):
   - Ir a Credentials → New → Gmail OAuth2
   - Conectar con la cuenta de Gmail del proyecto
   - Asignar la credencial al nodo "Enviar Email"

2. **Google Sheets OAuth2** (para WF2):
   - Ir a Credentials → New → Google Sheets OAuth2
   - Conectar con la misma cuenta Google
   - Asignar la credencial al nodo "Guardar en Google Sheets"

---

*CEMANTIX — Equipo Desarrollando Datos IA | EAFIT 2026*
