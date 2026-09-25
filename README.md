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

**Prácticamente no hay backend ni build step.** Casi todo corre en el navegador
de quien lo usa: lectura/escritura de Excel con SheetJS (`lib/xlsx.full.min.js`)
o ExcelJS (`lib/exceljs.min.js`, necesaria para incrustar imágenes en el Excel
exportado), gráficas con Chart.js (`lib/chart.umd.js`) — todo vendorizado
localmente en `herramientas/lib/`, sin CDN, para que funcione sin bloqueos de
red corporativos. La única excepción es `api/migrar-imagen.js` (ver detalle
abajo): una función serverless de Vercel, porque Google Drive bloquea por CORS
que se lea un archivo suyo desde JavaScript de otro sitio -- ese único paso sí
necesita correr del lado del servidor. Vercel la despliega sola al hacer
`git push`, sin build step manual ni Node instalado en la laptop de nadie.

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
├── api/                   # funciones serverless de Vercel (la UNICA parte con "backend" del Hub)
│   └── migrar-imagen.js    # descarga una foto de Drive/Imgur y la re-sube a ImgBB -- usada por
│                           # la pestaña "Migrar fotos" de boletines_oe.html (ver detalle abajo)
├── media/                 # imágenes y video usados en Inicio
├── comunicacion/          # plan y pieza de comunicación del lanzamiento del Hub (ver detalle abajo)
└── NOMENCLATURA_OE.md     # referencia rápida de cómo se llama cada área (FM+XD+SC+TOM, SVC+Last Mile, Quality, Gestión)
```

## Contenido del Hub (secciones de `index.html`)

- **Inicio** — en este orden: Accesos rápidos, Success stories, **Fechas
  relevantes** (calendario mensual, ver detalle abajo), Repositorio de
  proyectos, Herramientas de equipo, Ideas y sugerencias.
- **Gestión** (grupo de nav) — **Flujo de Iniciativas Locales** (una sola
  página con 5 tabs: Actualización de Proyectos, Indicadores,
  **Iniciativas Regionales**, **Iniciativas Locales** y **Big Rocks** —
  Big Rocks agrupa los proyectos estratégicos por las 4 áreas de OE, con
  Slip Robots viviendo dentro de Big Rocks → "FM + XD + SC + TOM"), más
  Generador de Slides, Generador de Boletines y **Expansiones · Señalética
  de Aperturas** (antes era su propio grupo de nav; se movió aquí adentro
  como sub-item de Gestión, a petición de Ricardo). Nota: "Iniciativas
  Regionales" e "Iniciativas Locales" eran un solo tab combinado
  ("Iniciativas") hasta sep-2026; se separaron en dos tabs independientes
  para que cada alcance (regional vs. local) tenga su propio espacio,
  igual que Indicadores o Big Rocks.
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
- **Botón "Volver a Inicio"** (`.page-back`) arriba de cada página/herramienta
  del Hub (Gestión, Rutinas, Directorio, Organigrama, Slides, Señalética,
  Slip Robots, Boletines, Aprendizaje) — antes no había forma de regresar a
  Inicio sin usar el nav lateral; ahora hay un botón directo en cada página.
- Toggle de idioma ES/EN/PT funcional en todo el sitio (auditado
  end-to-end en sep-2026, ver "Traducción ES/EN/PT" abajo), búsqueda rápida
  (Ctrl+K), navegación adaptada a mobile. **Sin candado de acceso**: el
  sitio es público (ver "Acceso" abajo).

### Fechas relevantes (calendario en Inicio)

Calendario mensual con navegación por flechas, debajo de "Success
stories". Rediseñado en sep-2026 (feedback de Ricardo: el calendario es
para todo el equipo, no para trackear el proceso interno de Gestión).
Marca en color (celda completa, no solo un punto) tres tipos de fecha:

- **Fechas conmemorativas** — feriados oficiales de México (Art. 74 LFT),
  calculados año-agnóstico en JS (fijos + "n-ésimo día de la semana del
  mes"). Se muestran con la etiqueta "Fecha conmemorativa" (antes decían
  solo el nombre del feriado a secas) para dejar claro que son
  informativas, no un día libre real de la operación.
- **2 hitos de Gestión** (ya no 5): "Actualización de proyectos en
  MeliAxis" (último lunes del mes) y "Publicación nacional de newsletter"
  (día siguiente a la autorización del Sr. Manager). Las 4 fechas
  intermedias de revisión interna (Focales/Supervisores/Managers/Sr.
  Manager) se quitaron del calendario a propósito — siguen documentadas
  como flow interno en el tab "Actualización de Proyectos", solo que ya
  no aparecen como fechas del calendario.
- **Eventos en Puerta** (nuevo) — se leen EN VIVO de la sección "Eventos en
  Puerta" de cada boletín ya publicado (`fetch()` + `DOMParser`, mismo
  origen, sin problema de CORS) y se colocan en el mes del calendario que
  corresponda a la fecha de cada evento — no necesariamente el mes de
  publicación del boletín (ej. un boletín de agosto puede anunciar un
  evento de septiembre, y ese evento aparece en septiembre). Áreas sin esa
  sección en su boletín simplemente no aportan eventos ese mes; no hay que
  hacer nada distinto al generar boletines para que esto funcione. El
  parser (`parseEventosPuertaHtml` / `eventosFindContainer` en
  `index.html`) NO asume una estructura HTML fija — detecta el patrón
  "día + abreviatura de mes en español" entre los nodos de texto final del
  documento, porque el generador de newsletters ha usado más de una
  plantilla HTML con el tiempo.

El panel lateral junto al calendario lista todas las fechas del mes activo
con el mismo color por fila (borde + fondo tenue) para que se distingan de
un vistazo. Funciones clave en `index.html`: `renderCalendar()`,
`getOEDatesMonth()`, `loadAllEventosPuerta()` (carga y cachea en memoria
los eventos de TODOS los boletines publicados, una sola vez).

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
  tiempo. El fix de `_HOSTS_FOTO_OK` (reconocer `ibb.co` como host valido de
  foto) debe replicarse igual en ambos si se toca.
  **Pestaña "Migrar fotos"** (dentro de la misma herramienta, junto a
  "Generar"/"Historial"): paso previo y separado -- se sube el Excel recien
  bajado del Apps Script (con fotos de Drive/Imgur) y se descarga el mismo
  Excel con esas fotos ya migradas a ImgBB, listo para la pestaña "Generar".
  Usa SheetJS para leer/escribir el Excel **celda por celda por direccion
  exacta** (nunca reconstruyendo la hoja via `sheet_to_json`+`sheet_add_json`
  compactados en un arreglo) -- se probo ese camino primero y tenia un bug
  real: `sheet_to_json` omite filas en blanco intercaladas, asi que al
  reescribir con `sheet_add_json` todo se recorre una posicion y la ultima
  fila original queda duplicada con datos viejos. Ver
  `mapaEncabezados`/`leerCelda`/`escribirCelda` en el script de
  `boletines_oe.html`. La descarga/subida real de cada foto la hace
  `api/migrar-imagen.js` (ver arriba): Imgur si se puede leer directo desde el
  navegador (permite CORS), pero Google Drive no, asi que ambos casos pasan
  por esa funcion serverless para no duplicar logica segun el origen. La API
  key de ImgBB vive SOLO ahi (variable de entorno `IMGBB_API_KEY` en Vercel),
  nunca se manda al navegador.
- **`senaletica_aperturas.html` — Señalética de Aperturas.** Wizard de 4
  pasos: **1) Datos del sitio** → **2) Artículos** (135 artículos: 93
  fijos + 16 variables + 26 opcionales, cada uno con su imagen de
  referencia real en tarjetas grandes, con un toggle "Imágenes
  grandes/Vista compacta", flag Estándar/Variable, artículos opcionales
  como sección comodín, y un campo de comentario por artículo — obligatorio
  solo en Corpóreo Letras MELI 3D y Vinilo MELI — que se incluye en el
  Excel final; clic en la imagen abre un lightbox en pantalla para verla en
  grande) → **3) Vista previa** de la orden de compra (líneas, piezas) +
  exportar Excel → **4) Sembrado**: sube el layout del sitio (JPG, PNG, o
  PDF — se convierte a imagen automáticamente en el navegador con pdf.js),
  arrastra los artículos seleccionados como pines sobre el plano para armar
  la guía visual de instalación, mueve/quita pines, botón "Marcar como
  listo" para bloquear edición, y exporta la guía final como PNG (canvas
  con los pines y su etiqueta) para el contratista instalador. Etapa 1
  (manual, sin ML) — ver "Pendientes conocidos" para el roadmap de
  Etapa 2/3. La exportación de Excel usa **ExcelJS** (no SheetJS) para
  poder incrustar la imagen de cada artículo directamente en la fila de la
  hoja "Requerimiento", replicando el diseño real de la plantilla oficial
  de David (Carátula con estilos + Requerimiento + Observaciones). Las
  imágenes del catálogo son nativamente de baja resolución (~90px de alto,
  así vienen del levantamiento original) — si se necesita más nitidez hay
  que pedirle a David el archivo fuente en mejor resolución, no se puede
  mejorar solo re-extrayendo del Excel.
- **`generador_slide_ejecutivo.html` — Generador de Slide Ejecutivo.**
  Arma un slide ejecutivo de resultados para proyectos Lean. A propósito
  **abre con datos de ejemplo precargados** (no en blanco) — se intentó
  estandarizar a plantilla vacía y Larry pidió revertirlo explícitamente,
  prefiere el ejemplo prellenado como guía visual.
- **`slip_robots_rutas.html` — Slip Robots.** Dashboard de la red LH
  Ground: distribución de lanes, volumen por categoría, forecast MWH, top
  rutas origen-destino, y un scorecard con fórmula de scoring y benchmarks.
  Lee `herramientas/data/sliprobots/slip_robots_datos.xlsx` client-side
  (SheetJS) y grafica con Chart.js. Vive dentro de Big Rocks →
  "FM + XD + SC + TOM" en la navegación (además de tener su propia
  página). **Ojo con la nomenclatura:** los nombres de archivo/claves
  internas (`Boletin_FirstMile.html`, `firstmile:` como key de mapa, etc.)
  siguen usando "FirstMile"/"ServiceCenter" a propósito — son identificadores
  internos y renombrarlos rompería los links a los boletines ya publicados.
  Lo que se estandarizó en sep-2026 fue solo el TEXTO VISIBLE al usuario
  (headers de Big Rocks, tarjetas), que ahora usa la nomenclatura oficial
  ("FM + XD + SC + TOM", "SVC + Last Mile") en vez de los nombres internos.

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
`mail` y `foto` (URL directa de **ImgBB**, `https://i.ibb.co/CODE/archivo.jpg`
— las fotos reales del equipo ya se subieron). Para actualizar a alguien o
agregar/quitar personas, edita ambos archivos (JSON + respaldo) y mantenlos
idénticos. **Ojo:** `motor-oe-v2` (repo separado) tiene su PROPIA copia de
este mismo directorio en `directorio_oe.json` (raíz de ese repo) + su propio
respaldo embebido en `motor.py` — si cambias una foto o un dato de alguien,
hay que replicarlo en los DOS repos (4 lugares en total) o se desalinean.
Si necesitas volver a subir una foto (por ejemplo porque alguien la borró
por error de la galería de ImgBB, lo cual rompe el link al instante), usa
`motor-oe-v2/scripts/fotos/imgbb_upload.py` o la pestaña "Migrar fotos" de
`boletines_oe.html` — ver el README de `motor-oe-v2` para el detalle
completo del pipeline de fotos.

## Correr en local

Es un solo archivo HTML estático (más las carpetas de contenido), sin build
ni dependencias:

```
python3 -m http.server 8000
```

y entrar a `http://localhost:8000`. **Ojo:** la pestaña "Migrar fotos" de
`boletines_oe.html` necesita `api/migrar-imagen.js`, que solo corre bajo
`vercel dev` (o ya desplegado en Vercel) -- con `http.server` esa pestaña no
va a funcionar (el resto del sitio si).

## Variables de entorno (Vercel)

Este proyecto es 100% estático salvo por `api/migrar-imagen.js` (ver detalle
en "Herramientas satélite" arriba), que necesita:

- `IMGBB_API_KEY` -- API key de ImgBB (misma que usa `motor-oe-v2` para sus
  scripts de fotos). Configúrala en el dashboard de Vercel del proyecto:
  **Settings → Environment Variables**. Sin esto, la pestaña "Migrar fotos"
  de `boletines_oe.html` responde con error pero el resto del Hub sigue
  funcionando normal.

## Traducción ES/EN/PT

El toggle de idioma (`applyLang()` en `index.html`) usa dos diccionarios,
`TEXT_EN` y `TEXT_PT`, y un selector CSS (`I18N_SELECTOR`) que enumera
todas las clases/elementos que se traducen. Auditado end-to-end en
sep-2026: se verificó con un script real (jsdom simulando el selector
completo contra el archivo) que el 100% de los textos que toca el
selector tienen traducción — no fue una revisión visual, fue una
comparación automática.

Dos cosas importantes si se agrega contenido nuevo:

1. **Cualquier texto visible nuevo necesita dos cosas:** (a) que su
   elemento (o un ancestro suyo) esté en `I18N_SELECTOR`, y (b) una
   entrada en `TEXT_EN`/`TEXT_PT` con el texto en español EXACTO como
   clave. Si falta cualquiera de las dos, el texto se queda en español al
   cambiar de idioma (sin error visible, así que es fácil que pase
   desapercibido).
2. **El mecanismo traduce CADA corrida de texto entre tags, no solo la
   primera.** Antes de sep-2026 solo traducía el texto ANTES del primer
   tag anidado, así que una frase como "**Nota:** el equipo comparte..."
   solo traducía la palabra en negritas y dejaba el resto en español (o,
   si el texto empezaba con un ícono/SVG antes del texto, no traducía
   nada en absoluto). Esto ya se arregló — ahora cada fragmento de texto
   entre etiquetas se busca por separado en el diccionario — pero si algún
   texto nuevo se ve raro al cambiar de idioma, ese ya no debería ser el
   motivo.

**Fuera del toggle a propósito:** el Glosario MeLi
(`aprendizaje/Glosario_OE.html`) y Documentos de Referencia
(`aprendizaje/Documentos_Referencia.html`) — sus tablas grandes (300+ y
270+ filas respectivamente) siguen siendo 100% español. Traducirlas
implicaría construir un sistema de i18n nuevo para esos dos archivos
independientes (no reutilizan el de `index.html`), es un proyecto aparte,
no un ajuste rápido — ver "Pendientes conocidos".

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

## Comunicación de lanzamiento del Hub

Carpeta `comunicacion/`, generada en sep-2026:

- `Plan_Comunicacion_Lanzamiento_OE_Hub.md` — plan original (objetivo,
  audiencia, cronograma). **Ojo:** este archivo todavía refleja el alcance
  inicial (solo equipo OE MLM); el alcance real cambió a mitad de proceso
  — ver siguiente punto — y este doc no se ha actualizado para reflejarlo.
- `Correo_Lanzamiento_OE_Hub.html` — v1 del correo de lanzamiento (enfoque
  "herramienta del equipo OE"). **Superada por la v2**, se deja solo de
  referencia.
- `Correo_Lanzamiento_OE_Hub_v2.html` — versión vigente: reenfocada como
  comunicado para **todo Mercado Libre México, incluyendo gerencia** (no
  solo OE), con un bloque de "Sesiones en vivo" para las capacitaciones que
  van a dar Ricardo Almanza y Larry. HTML compatible con clientes de
  correo (tablas + estilos inline, sin CSS externo, probado con
  `<meta charset="UTF-8">` y sin tags sin cerrar).

**Estado a la fecha:** el 25-sep-2026 Larry mandó esta propuesta (correo +
vista previa del HTML embebida, no como adjunto) a Ricardo Almanza
(`carlosricardo.almanzaloo@mercadolibre.com.mx`) y Mónica, pidiendo
retroalimentación antes del envío masivo real a todo MLM México. Sigue en
espera de esa respuesta — ver "Pendientes conocidos".

## Pendientes conocidos (a la fecha)

- **Retroalimentación de Ricardo Almanza y Mónica** sobre la propuesta de
  comunicación de lanzamiento (ver sección de arriba) — en cuanto
  respondan, hay que pulir esa versión antes del envío masivo real.
- **Sesiones de capacitación en vivo** del Hub (Ricardo Almanza + Larry):
  falta definir fecha y liga, una vez que se apruebe el lanzamiento.
- **Fotos de Miguel Hernández, Steven Seedorf, Oscar Manuel Piña y David
  Lumbreras** en el Directorio/Organigrama: pendiente a propósito, las
  maneja Larry directamente (no tocar sin que él lo pida).
- **Traducir Glosario MeLi y Documentos de Referencia a EN/PT**: fuera de
  alcance de la auditoría de sep-2026 (ver "Traducción ES/EN/PT" arriba) —
  proyecto aparte si se decide hacerlo.
- **Sembrado — Etapa 2/3** (David): la Etapa 1 (manual: subir layout
  JPG/PNG/PDF, arrastrar pines, exportar guía PNG) ya está construida y
  confirmada por Larry — ver paso 4 de `senaletica_aperturas.html`. Lo que
  sigue pendiente es a futuro y sin fecha: Etapa 2 (sugerir ubicación de
  zonas con un modelo de visión, sin entrenar nada) y Etapa 3 (detector de
  objetos entrenado a la medida, solo si se acumula suficiente dataset de
  sitios reales) — ninguna de las dos está agendada.
- **Imágenes de señalética en mejor resolución**: pendiente de que David
  mande archivos fuente en mayor resolución (ver detalle en la sección de
  Señalética arriba).
