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

## Estructura real del repo

```
oe-hub/
├── index.html            # el sitio: shell de navegación + todas las páginas embebidas (HTML+CSS+JS en un solo archivo)
├── boletines/AAAA-MM/    # newsletters HTML de cada mes (los 4, cuando existen), enlazados desde la pestaña Boletines
├── playbooks/            # Playbook web de supervisores + carpeta de QR
├── aprendizaje/          # subpáginas de Aprendizaje Continuo: Glosario, Biblioteca, Tutoriales MELI Axis, Sesiones grabadas
├── gestion/               # Insights de Portafolio (mockup interactivo) -- usado por las pestañas Proyectos E Indicadores
├── herramientas/          # herramientas satélite del equipo, cada una un HTML autocontenido embebido vía iframe
│   ├── boletines_oe.html          # Generador de Boletines (reemplaza Streamlit) -- ver detalle abajo
│   ├── generador_slide_ejecutivo.html  # Generador de Slide Ejecutivo (Lean Projects)
│   ├── senaletica_aperturas.html  # Señalética de Aperturas (SVC Transportes)
│   ├── slip_robots_rutas.html     # Slip Robots -- dashboard de la red LH Ground
│   ├── lib/               # librerías vendored (xlsx.full.min.js, chart.umd.js) -- sin CDN, para que funcione offline/sin bloqueos
│   └── data/               # datos que leen las herramientas de arriba (ej. data/sliprobots/*.xlsx, data/boletines/directorio_oe.json)
├── apps-script/           # .gs de Google Apps Script usados por el Hub (Sugerencias; ver detalle abajo)
├── media/                 # imágenes y video usados en Inicio
└── NOMENCLATURA_OE.md     # referencia rápida de cómo se llama cada área (FM+XD+SC+TOM, SVC+Last Mile, Quality, Gestión)
```

## Contenido del Hub (secciones de `index.html`)

- **Inicio** — video del equipo, changelog de novedades, accesos rápidos.
- **Directorio** — organigrama completo del equipo (nombre, nivel, área) + Organigrama Completo.
- **Rutinas > Newsletter** — vista previa de los 4 boletines más recientes (más reciente + histórico por mes), enlazados desde `boletines/`.
- **Gestión** (grupo de nav) — Proyectos, Indicadores, Iniciativas, y las herramientas satélite: Generador de Slides, Señalética de Aperturas, Slip Robots, Generador de Boletines.
- **Playbooks** — guía de administrador y de supervisores (web + PDF/QR).
- **Aprendizaje Continuo** — Glosario, Biblioteca, Tutoriales MELI Axis, Sesiones grabadas.
- **Ideas y sugerencias** — formulario que manda cada sugerencia a un Google Sheet (ver `apps-script/ideas_sugerencias.gs`).
- Candado de contraseña simple a la entrada (ver "Seguridad" abajo), toggle de idioma ES/EN/PT funcional en todo el sitio, búsqueda rápida (Ctrl+K), navegación adaptada a mobile.

## Herramientas satélite (detalle)

Cada una vive como un HTML independiente en `herramientas/`, embebido en el
Hub vía `<iframe data-src="herramientas/....html">` (carga perezosa: el
`src` real solo se asigna cuando el usuario entra a esa página, no al cargar
el sitio). Mismo lenguaje visual entre todas: header negro (`.hdr`/`.app-bar`)
con acento amarillo `#FFD001`/`#FFE600`, sin build ni dependencias de CDN
(las librerías que usan viven vendored en `herramientas/lib/`).

- **`boletines_oe.html` — Generador de Boletines.** Reemplaza el Streamlit
  de `motor-oe-v2` para el usuario final. Contiene `motor.js`, un **port 1:1
  de `motor-oe-v2/motor.py`** que corre 100% en el navegador (sube el Excel
  de cada área, genera el HTML del boletín, sin backend). Única diferencia
  real: las fotos LOCALES con recorte de cara (poco usadas — casi todo el
  uso real es Imgur/Drive, que sí funciona igual que en Python) no se pueden
  procesar en el navegador; en ese caso se muestra un aviso visible en vez
  de fallar en silencio. **Importante:** esto significa que hay DOS
  implementaciones de la misma lógica de negocio (`motor.py` y `motor.js`)
  — cualquier cambio de regla/KPI/formato en el boletín debe replicarse en
  ambos archivos o se desalinean con el tiempo.
- **`senaletica_aperturas.html` — Señalética de Aperturas.** Formulario
  para generar la señalética de apertura de un sitio (SVC Transportes) +
  orden de compra en Excel.
- **`generador_slide_ejecutivo.html` — Generador de Slide Ejecutivo.**
  Arma un slide ejecutivo de resultados para proyectos Lean.
  Antes: "Generador de Slides" a secas — se cambió el nombre visible para
  que el enfoque (Lean Projects) quede claro desde el título.
- **`slip_robots_rutas.html` — Slip Robots.** Dashboard de la red LH
  Ground: distribución de lanes, volumen por categoría, forecast MWH, top
  rutas origen-destino, y un scorecard con fórmula de scoring y benchmarks.
  Lee `herramientas/data/sliprobots/slip_robots_datos.xlsx` client-side
  (SheetJS) y grafica con Chart.js (ambos vendored en `herramientas/lib/`).

### Cómo agregar una herramienta satélite nueva

El patrón ya está probado 3 veces (Señalética, Slip Robots, Slide
Ejecutivo) — son 7 puntos de integración dentro de `index.html`, sin tocar
nada más:

1. Crea el HTML autocontenido en `herramientas/tu_herramienta.html`
   (copia el `<style>` de header/tabs de otra herramienta para mantener el
   mismo lenguaje visual).
2. Botón de navegación: agrega un `<button class="nav-sub-item" id="navTuHerramienta" onclick="go('tuherramienta', this)">` en el grupo de nav que corresponda.
3. (Opcional) tarjeta de acceso rápido en Inicio: un `<a class="tool-card wide" onclick="go('tuherramienta', ...)">`.
4. Página + iframe: `<div class="page" id="page-tuherramienta">` con su
   botón de pantalla completa y `<iframe id="tuHerramientaFrame" data-src="herramientas/tu_herramienta.html" onload="if (window.syncFrameLang) syncFrameLang('tuHerramientaFrame')">`.
5. Agrega la clave `tuherramienta` a los 3 diccionarios `LABELS` / `LABELS_EN` / `LABELS_PT` (busca `const LABELS`).
6. Agrega una entrada al índice de búsqueda Ctrl+K (busca `label: 'Gestión ·`).
7. Agrega `pageId === 'tuherramienta'` a la condición de sub-nav (busca `pageId === 'senaletica'`) y el id del iframe al arreglo de sincronización de idioma (busca `senaleticaFrame'].forEach` / el arreglo que empieza con `insightsFrameProyectos`).

git add, commit, push — listo.

## Seguridad (candado de entrada)

El Hub pide una contraseña simple al entrar (`OE_GATE_PASS` en
`index.html`, buscar el comentario "CANDADO SIMPLE"). **No es protección
real** — la contraseña vive en el mismo archivo HTML y cualquiera con el
link directo a una herramienta se lo salta. Es una decisión consciente de
Larry: los datos del Hub no son sensibles, así que no vale la pena montar
un login de verdad. Se recuerda por navegador vía `localStorage`. Para
rotar la contraseña, cambia `OE_GATE_PASS` y avisa al equipo.

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
