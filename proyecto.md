# Censo Digital de Ferreterías en Colombia — Briefing Etapa 3
**Rol:** AI Developer | **Primera reunión de equipo** | **Fecha:** 2026-04-06

---

## 1. Diagnóstico: ¿Qué tenemos y qué falta?

### Lo que tenemos
| Artefacto | Estado | Descripción |
|---|---|---|
| `Bd_Base.xlsx` | Plantilla vacía | 12 columnas definidas, **cero registros reales** |
| PDF Briefing (Censo) | Completo | Define el problema, alcance y campos requeridos |
| Herramientas sugeridas | Identificadas | Apify ($5 gratis), Serper, Google Maps API |
| Equipo | 7 personas | Perfiles definidos: Documentador, Analista de Datos, Ing. de Datos, AI Developer, etc. |

### Lo que falta (crítico — arrancar hoy)
- **Ciudad/región piloto** — No atacar todo Colombia de entrada; definir piloto hoy.
- **Entregable Final Definido** — Argos pide una BD centralizada y "visualizada en un mapa". Hay que decidir si entregamos solo un Excel + PowerBI, o una **Aplicación Web interactiva / Custom GPT** para consultar las ferreterías.
- **Scraper funcional** — Delegar al Ingeniero de Datos la extracción de la info.

---

## 2. Requerimientos Técnicos — Perspectiva IA (Tu Rol)

Como **AI Developer** en un equipo de 7 personas, no tienes que hacerlo todo. Tu trabajo vital se centra en la "inteligencia" del proceso y de la entrega final:

#### 2.1 Banco de Plantillas de Prompts (Prompt Templates)
Debes crear y documentar prompts avanzados que el equipo usará.
*   **Prompt de Normalización:** Para limpiar nombres de empresas.
*   **Prompt de Deduplicación:** Para que la IA evalúe si el registro A y B son la misma ferretería.
*   **Prompt de Enriquecimiento:** Para inferir municipios basándose en otras columnas.

#### 2.2 Agente de Consulta (Custom GPT / Modo Agente)
No basta con entregar un Excel. Como AI Developer, puedes brillar construyendo un **Agente (ej. usando ChatGPT Custom GPT o Assistants API)** donde el cliente (Argos) pueda preguntar en lenguaje natural:
*   *"¿Cuántas ferreterías tenemos en Envigado?"*
*   *"Muéstrame las ferreterías que están a menos de 5km y no tienen correo electrónico."*

#### 2.3 Solución de Entity Resolution (IA)
En trabajo conjunto con el Analista de Datos, integrar llamadas a APIs de LLMs o usar NLP (`fuzzywuzzy`) para limpiar los duplicados antes de que la data llegue a la vista final.

---

## 3. Plan de Acción 24h (Meeting de Hoy)

Estos puntos deben quedar **decididos al salir de la reunión de hoy**:

| # | Tema | Tu contribución sugerida |
|---|---|---|
| 1 | **Formato del Entregable Final** | Propón entregar una BD limpia (Ing. de Datos) + un **Dashboard/App** interactiva guiada o consultable por IA (tu rol + Analistas). |
| 2 | **Ciudad piloto** | Sugiere arrancar por Medellín o una zona específica. |
| 3 | **División de Roles (Sinergia)** | Ver tabla abajo para alinear tareas entre los 7 miembros. |
| 4 | **Herramientas de IA a usar** | Poner sobre la mesa ChatGPT (Custom GPTs), Anthropic API, o herramientas similares para el flujo. |

### Alineación de los 7 Roles (Propuesta)

| Rol | Responsabilidad en el proyecto |
|---|---|
| **AI Developer (TÚ)** | Crea Prompts avanzados de limpieza, desarrolla el Agente/Chatbot de consulta final, implementa NLP para deduplicar. |
| **Ingeniero de Datos** | Maneja la infraestructura de Scraping (Apify/Serper), corre los scripts de extracción y monta la base de datos (BD). |
| **Analista de Datos** | Audita la calidad del Excel/BD, detecta inconsistencias, define los KPIs y visualiza los datos geoespaciales. |
| **Documentador** | Bitácora del proyecto, escribe el informe técnico para Argos y documenta cómo usar el Agente de IA. |
| **Visualizador/Analista BI** | Crea el mapa (ej. PowerBI o integración HTML) para Argos. |
| **QA / Revisión** | Verifica que no se filtren datos privados o falsos al Excel final. |
| **Project Manager** | Coordina que las integraciones entre Ingeniería, IA y Análisis se logren en 4 semanas. |

---

## 4. Estrategia de Implementación y Entregable (Desde tu rol)

### Flujo de Trabajo en equipo
1.  El **Ingeniero de Datos** programa Apify y corre la extracción masiva. Te pasa el JSON crudo.
2.  Tú (**AI Developer**) tomas el JSON crudo y lo pasas por tu de **Plantillas de Prompts** a través de código Python, limpiando y deduplicando.
3.  El **Analista de Datos** recibe tu JSON limpio, lo audita, lo carga en el Excel final `Bd_Base.xlsx`.
4.  El **Documentador y Visualizador** montan esto en un mapa.

### Definición del Entregable Final (Para que Argós se sorprenda)
Teniendo un equipo de 7 personas, entregar solo un archivo de Excel es muy básico. Propónganlo hoy así:
- **Nivel 1 (Obligatorio - Ingeniero/Analista):** Base de datos relacional/Excel perfectamente limpia.
- **Nivel 2 (Visualización - Analista BI):** Un Dashboard (PowerBI/Looker) con un mapa de calor geográfico de las ferreterías.
- **Nivel 3 (Valor Agregado IA - TÚ):** Un **Custom GPT o App** (Streamlit) alimentado con esa base de datos (Retrieval-Augmented Generation / RAG), especializado como "Asistente de Mercado Argos", que interactúe por texto con el usuario final para responder consultas sobre la distribución de las ferreterías.
