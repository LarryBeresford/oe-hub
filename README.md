# OE MLM Hub

Sitio del equipo de Excelencia Operacional (OE) MercadoLibre MX, desplegado
como sitio estático en **Vercel**: https://oe-hub-mu.vercel.app/. Cubre las
4 áreas de OE — FM + XD + SC + TOM, SVC + Last Mile, Quality y Gestión —
más contenido transversal del equipo (Directorio, Playbooks, Aprendizaje
Continuo) y un set creciente de **herramientas satélite** que el equipo va
agregando (generador de boletines, señalética, slides ejecutivos, Slip
Robots, y las que sigan).

Este es un repositorio **separado** de `motor-oe` (el proyecto original de
Streamlit/Python que generaba los boletines). Desde que se agregó el
Generador de Boletines embebido (ver abajo), **el flujo normal del usuario
final ya no pasa por Streamlit** — motor-oe-v2 se mantiene como generador
de referencia / CLI / respaldo, pero el Hub es autosuficiente para producir
los boletines mensuales.

**No hay backend ni build step.** Todo corre en el navegador de quien lo
usa: lectura/escritura de Excel con SheetJS (`lib/xlsx.full.min.js`) o
ExcelJS (`lib/exceljs.min.js`, necesaria para incrustar imágenes en el
Excel exportado), gráficas con Chart.js (`lib/chart.umd.js`) — todo
vendorizado localmente en `herramientas/lib/`, sin CDN, para que funcione
sin bloqueos de red corporativos.

## Estructura real del repo

```
oe-hub/
├── index.html            # el sitio: shell de navegación + todas las páginas embebidas (HTML+CSS+JS en un solo archivo)
├── boletines/AAAA-MM/    # newsletters HTML de cada mes (los 4, cuando existen), enlazados desde Rutinas > Newsletter
├── playbooks/            # Playbook web de supervisores + carpeta de QR
├── aprendizaje/           # subpáginas de Aprendizaje Continuo
│   ├── Playbooks.html             # playbooks como tarjetas (cuadros), escalable a futuros playbooks
│   ├── Glosario_OE.html           # "Glosario MeLi" -- una sola lista de 352 términos, sin clasificación
│   ├── Documentos_Referencia.html # "Documentos de interés" -- Master File + Biblioteca A-Z unificados, y la tabla de "Nueva Regionalización TTE MLM" (142 sitios) con columna "Ops Excellence / OE"
│   └── Sesiones_Grabadas.html     # grabaciones de equipo + Tutoriales MELI Axis (fusionado aquí)
├── gestion/               # Insights de Portafolio (mockup interactivo) -- usado por las tabs Proyectos e Indicadores
├── herramientas/          # herramientas satélite del equipo, cada una un HTML autocontenido embebido vía iframe
│   ├── boletines_oe.html               # Generador de Boletines (reemplaza Streamlit) -- ver detalle abajo
│   ├── generador_slide_ejecutivo.html  # Generador de Slide Ejecutivo (Lean Projects)
│   ├── senaletica_aperturas.html       # Señalética de Aperturas (SVC Transportes) -- wizard de 3 pasos
│   ├── slip_robots_rutas.html          # Slip Robots -- dashboard de la red LH Ground
│   ├── lib/                # librerías vendored: xlsx.full.min.js, chart.umd.js, exceljs.min.js -- sin CDN
│   ├── media/senaletica/   # 135 imágenes de referencia del catálogo de señalética (extraídas del Excel de David)
│   └── data/               # datos que leen las herramientas de arriba
│       ├── sliprobots/*.xlsx           # datos de Slip Robots (un solo Excel multi-hoja, editable por no técnicos)
│       └── boletines/directorio_oe.json # directorio OE (organigrama) que se pega al final de los 4 boletines
├── apps-script/           # .gs de Google Apps Script usados por el Hub (Sugerencias; ver detalle abajo)
├── media/                 # imágenes y video usados en Inicio
└── NOMENCLATURA_OE.md     # referencia rápida de cómo se llama cada área (FM+XD+SC+TOM, SVC+Last Mile, Quality, Gestión)
```

## Contenido del Hub (secciones de `index.html`)

- **Inicio** — en este orden: Accesos rápidos, Success stories, **Fechas
  relevantes** (calendario mensual, ver detalle abajo), Repositorio de
  proyectos, Herramientas de equipo, Ideas y sugerencias.
- **Gestión** (grupo de nav) — **Flujo de Iniciativas Locales** (una sola
  página con 4 tabs: Proyectos, Indicadores, Iniciativas y **Big Rocks**
  — Big Rocks agrupa los proyectos estratégicos por las 4 áreas de OE, con
  Slip Robots viviendo dentro de Big Rocks → FirstMile), Generador de
  Slides, Generador de Boletines.
- **Expansiones** (grupo de nav) — Señalética de Aperturas.
- **Rutinas** (grupo de nav) — BBR, MBR, Newsletter (vista previa de los 4
  boletines más recientes + histórico por mes, enlazados desde `boletines/`).
- **Directorio** (grupo de nav) — Directorio (líderes de OE por región, con
  correo directo) + Organigrama Completo.
- **Aprendizaje Continuo** (grupo de nav, colapsado por defecto) —
  Playbooks (tarjetas), Glosario MeLi (352 términos, sin clasificación),
  Documentos de interés (Master File + Biblioteca + tabla de
  Regionalización con columna Ops Excellence/OE), Sesiones Grabadas
  (incluye Tutoriales MELI Axis).
- **Ideas y sugerencias** — formulario que manda cada sugerencia a un
  Google Sheet (ver `apps-script/ideas_sugerencias.gs`).
- Toggle de idioma ES/EN/PT funcional en todo el sitio, búsqueda rápida
  (Ctrl+K), navegación adaptada a mobile. **Sin candado de acceso**: el
  sitio es público (ver "Acceso" abajo).

### Fechas relevantes (calendario en Inicio)

Calendario mensual con navegación por flechas, debajo de "Success
stories". Marca en color (celda completa, no solo un punto) dos tipos de
fecha:

- **Feriados oficiales de México** (Art. 74 LFT) — calculados
  año-agnóstico en JS (fijos + "n-ésimo día de la semana del mes").
- **5 fechas recurrentes del proceso de Newsletter/Axis**: Focales
  actualizan su proyecto y MELI Axis (último lunes del mes), Supervisores
  cargan el Form (primer miércoles), Managers revisan y autorizan (primer
  viernes), Miguel da la autorización final (segundo martes), y se publica
  a todo MLM (día siguiente). Cada una con su color por área (mismos
  colores `--tag-fm` / `--tag-svc` / `--tag-mgmt` / `--tag-quality` que el
  resto del Hub).

El panel lateral junto al calendario lista todas las fechas del mes activo
con el mismo color por fila (borde + fondo tenue) para que se distingan de
un vistazo. Función principal: `renderCalendar()` en `index.html` (buscar
`CAL_OE_LABELS` / `getOEDatesMonth`).

## Herramientas satélite (detalle)

Cada una vive como un HTML independiente en `herramientas/`, embebido en el
Hub vía `<iframe data-src="herramientas/....html">` (carga perezosa: el
`src` real solo se asigna cuando el usuario entra a esa página, no al cargar
el sitio). Mismo lenguaje visual entre todas: header negro (`.hdr`/`.app-bar`)
con acento amarillo `#FFD001`/`#FFE600`, sin build ni dependencias de CDN.

- **`boletines_oe.html` — Generador de Boletines.** Reemplaza el Streamlit
  de `motor-oe-v2` para el usuario final. Contiene `motor.js`, un **port 1:1
  de `motor-oe-v2/motor.py`** que corre 100% en el navegador (sube el Excel
  de cada área, genera el HTML del boletín, sin backend). Al final de los 4
  boletines se agrega automáticamente el **Directorio OE** (organigrama),
  alimentado por `herramientas/data/boletines/directorio_oe.json` —
  ramas/columnas con la misma nomenclatura oficial ("SVC + Last Mile",
  "FM + XD + SC + TOM"), niveles Manager/Supervisor alineados correctamente
  (las ramas sin Manager, como Quality y Gestión, quedan un escalón abajo
  vía un espaciador invisible en `_cboxSmGhost()`). Única diferencia real
  con `motor.py`: las fotos LOCALES con recorte de cara (poco usadas) no se
  pueden procesar en el navegador; en ese caso se muestra un aviso visible
  en vez de fallar en silencio. **Importante:** hay DOS implementaciones de
  la misma lógica de negocio (`motor.py` y `motor.js`) — cualquier cambio
  de regla/KPI/formato debe replicarse en ambos o se desalinean con el
  tiempo.
- **`senaletica_aperturas.html` — Señalética de Aperturas.** Wizard de 3
  pasos: **1) Datos del sitio** → **2) Artículos** (135 artículos: 93
  fijos + 16 variables + 26 opcionales, cada uno con su imagen de
  referencia real en tarjetas grandes, con un toggle "Imágenes
  grandes/Vista compacta"; clic en la imagen abre un lightbox en pantalla
  para verla en grande) → **3) Vista previa** de la orden de compra
  (líneas, piezas) + exportar Excel. La exportación usa **ExcelJS** (no
  SheetJS) para poder incrustar la imagen de cada artículo directamente en
  la fila de la hoja "Requerimiento", replicando el diseño real de la
  plantilla oficial de David (Carátula con estilos + Requerimiento +
  Observaciones). Las imágenes del catálogo son nativamente de baja
  resolución (~90px de alto, así vienen del levantamiento original) — si
  se necesita más nitidez hay que pedirle a David el archivo fuente en
  mejor resolución, no se puede mejorar solo re-extrayendo del Excel.
- **`generador_slide_ejecutivo.html` — Generador de Slide Ejecutivo.**
  Arma un slide ejecutivo de resultados para proyectos Lean. A propósito
  **abre con datos de ejemplo precargados** (no en blanco) — se intentó
  estandarizar a plantilla vacía y Larry pidió revertirlo explícitamente,
  prefiere el ejemplo prellenado como guía visual.
- **`slip_robots_rutas.html` — Slip Robots.** Dashboard de la red LH
  Ground: distribución de lanes, volumen por categoría, forecast MWH, top
  rutas origen-destino, y un scorecard con fórmula de scoring y benchmarks.
  Lee `herramientas/data/sliprobots/slip_robots_datos.xlsx` client-side
  (SheetJS) y grafica con Chart.js. Vive dentro de Big Rocks → FirstMile
  en la navegación (además de tener su propia página).

### Cómo agregar una herramienta satélite nueva

El patrón ya está probado varias veces — son ~7 puntos de integración
dentro de `index.html`, sin tocar nada más:

1. Crea el HTML autocontenido en `herramientas/tu_herramienta.html`
   (copia el `<style>` de header/tabs de otra herramienta para mantener el
   mismo lenguaje visual).
2. Botón de navegación: agrega un `<button class="nav-sub-item" id="navTuHerramienta" onclick="go('tuherramienta', this)">` en el grupo de nav que corresponda.
3. (Opcional) tarjeta de acceso rápido en Inicio: un `<a class="tool-card wide" onclick="go('tuherramienta', ...)">` dentro de "Herramientas de equipo".
4. Página + iframe: `<div class="page" id="page-tuherramienta">` con su
   botón de pantalla completa y `<iframe id="tuHerramientaFrame" data-src="herramientas/tu_herramienta.html" onload="if (window.syncFrameLang) syncFrameLang('tuHerramientaFrame')">`.
5. Agrega la clave `tuherramienta` a los 3 diccionarios `LABELS` / `LABELS_EN` / `LABELS_PT` (busca `const LABELS`).
6. Agrega una entrada al índice de búsqueda Ctrl+K (busca `label: 'Gestión ·`).
7. Agrega `pageId === 'tuherramienta'` a la condición de sub-nav (busca `pageId === 'senaletica'`) y el id del iframe al arreglo de sincronización de idioma (busca `senaleticaFrame'` en `syncFrameLang`).

git add, commit, push — listo.

## Acceso al Hub

El sitio **no tiene candado ni login** — es público para quien tenga el
link (se quitó a propósito; el que había antes causaba mala impresión).
Esto es una decisión consciente: los datos del Hub no son sensibles, así
que no vale la pena montar un login de verdad hoy. El plan de fondo es
gestionar SSO real de MELI; mientras eso no exista, si en algún momento se
necesita restringir el acceso, la opción es **Vercel Password Protection**
(configuración del proyecto en Vercel, fuera del código del sitio — no
tocar `index.html` para esto).

## Ideas y sugerencias

El formulario de "Ideas y sugerencias" del Hub manda cada envío a un Google
Sheet vía Apps Script (`apps-script/ideas_sugerencias.gs`, desplegado como
app web). El envío es vía `<form>` a un iframe oculto (no `fetch()`), a
propósito, para evitar el bloqueo de CORS que da Apps Script en
despliegues "Cualquier usuario de `<dominio>`" (Workspace). Instrucciones
completas de despliegue/redespliegue dentro del propio `.gs`.

## Cómo agregar un mes nuevo de boletines

Instrucciones exactas (con ejemplo) dentro de `index.html`, buscar el
comentario `COMO AGREGAR UN MES NUEVO` cerca de `BOLETIN_MONTHS`. En resumen:
copiar los 4 HTML del generador (ya sea `motor-oe-v2/motor.py` o el
Generador de Boletines embebido) a `boletines/AAAA-MM/` con los nombres
`Boletin_FirstMile.html`, `Boletin_ServiceCenter.html`, `Boletin_Quality.html`,
`Boletin_Gestion.html`, y agregar una entrada nueva al arreglo
`BOLETIN_MONTHS` — el mes más nuevo pasa solo a "Más reciente", el anterior
cae a "Histórico".

## Cómo actualizar el Directorio OE (organigrama de los boletines)

Vive en `herramientas/data/boletines/directorio_oe.json` (con un respaldo
embebido idéntico en `boletines_oe.html`, variable `_DIRECTORIO_RESPALDO`,
por si el `fetch()` del JSON falla). Cada persona es un objeto con `n`
(nombre), `niv` (`Sr Manager` / `Manager` / `Supervisor` — esto es lo único
que se muestra en su tarjeta), `rama` (el nombre de la columna donde
aparece — debe coincidir exactamente con la nomenclatura oficial de área),
`mail` y `foto` (URL, hoy son links de Imgur — **pendiente: Larry va a
subir las fotos reales del equipo** para reemplazar esas URLs). Para
actualizar a alguien o agregar/quitar personas, edita ambos archivos
(JSON + respaldo) y mantenlos idénticos.

## Correr en local

Es un solo archivo HTML estático (más las carpetas de contenido), sin build
ni dependencias:

```
python3 -m http.server 8000
```

y entrar a `http://localhost:8000`.

## Nomenclatura de áreas (importante)

Los nombres oficiales usan `+` como separador, siempre: `FM + XD + SC + TOM`,
`SVC + Last Mile`, `Quality`, `Gestión`. Ver `NOMENCLATURA_OE.md` para el
detalle — esta misma nomenclatura debe coincidir con la que usan `motor.py`
(repo `motor-oe`), `motor.js` (embebido en `herramientas/boletines_oe.html`)
y `Boletines_OE_Envio.gs` (envío por correo).

Nota: dentro de `index.html`, "Gestión" se usa con dos sentidos distintos
— como nombre de una de las 4 áreas del boletín, y como etiqueta del grupo
de navegación que agrupa Proyectos/Indicadores/Iniciativas/herramientas
satélite (ej. "Gestión · Slip Robots"). Es una ambigüedad heredada del
nombre del grupo de nav, no un error — tenlo presente si algo se lee raro
en el menú.

## Pendientes conocidos (a la fecha)

- **Layout de "sembrado"** (David): arrastrar señalética sobre el plano de
  planta para armar un checklist visual, exportable a PDF. Pausado a
  propósito — solo se construye cuando David/Larry pidan la propuesta de
  diseño.
- **Fotos del equipo**: Larry va a subir fotos reales para reemplazar las
  URLs de Imgur en `directorio_oe.json`.
- **Campaña de comunicación del Hub** (Ricardo): falta definir alcance
  (audiencia, tono, canal).
- **Imágenes de señalética en mejor resolución**: pendiente de que David
  mande archivos fuente en mayor resolución (ver detalle en la sección de
  Señalética arriba).
