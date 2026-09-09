# OE MLM Hub

Sitio del equipo de Excelencia Operacional (OE) MercadoLibre MX, desplegado
como sitio estático en **Vercel**: https://oe-hub-mu.vercel.app/. Cubre las
4 áreas de OE — FM + XD + SC + TOM, SVC + Last Mile, Quality y Management —
más contenido transversal del equipo (Directorio, Playbooks, Aprendizaje
Continuo, herramientas internas).

Este es un repositorio **separado** de `motor-oe` (la app de Streamlit que
genera los boletines mensuales). El hub y el generador de boletines son
proyectos independientes que conviven en el mismo equipo — el generador
vive EMBEBIDO dentro del Hub, como una pestaña más (ver `herramientas/`).

## Estructura real del repo

```
oe-hub/
├── index.html          # el sitio: shell de navegación + todas las páginas embebidas (HTML+CSS+JS en un solo archivo)
├── boletines/AAAA-MM/  # newsletters HTML de cada mes (los 4, cuando existen), enlazados desde la pestaña Boletines
├── playbooks/          # Playbook web de supervisores + carpeta de QR
├── aprendizaje/         # subpáginas de Aprendizaje Continuo: Glosario, Biblioteca, Tutoriales MELI Axis, Sesiones grabadas
├── management/          # Insights de Portafolio (mockup interactivo)
├── herramientas/        # Generador de Slide Ejecutivo (embebido en el Hub)
├── data/axis/           # datos/exports usados por Herramientas e Insights
├── apps-script/         # .gs del formulario de Sugerencias del Hub
├── media/               # imágenes y video usados en Inicio
└── NOMENCLATURA_OE.md   # referencia rápida de cómo se llama cada área (FM+XD+SC+TOM, SVC+Last Mile, Quality, Management)
```

## Contenido del Hub (secciones de `index.html`)

- **Inicio** — video del equipo, changelog de novedades, accesos rápidos.
- **Directorio** — organigrama completo del equipo (nombre, nivel, área).
- **Rutinas > Newsletter** — vista previa de los 4 boletines más recientes
  (más reciente + histórico por mes), enlazados desde `boletines/`.
- **Playbooks** — guía de administrador y de supervisores (web + PDF/QR).
- **Aprendizaje Continuo** — Glosario, Biblioteca, Tutoriales MELI Axis,
  Sesiones grabadas.
- **Herramientas** — Generador de Boletines (Streamlit, embebido),
  Generador de Slide Ejecutivo, Insights de Portafolio.
- Toggle de idioma ES/EN/PT funcional en todo el sitio, búsqueda rápida
  (Ctrl+K), navegación adaptada a mobile.

## Cómo agregar un mes nuevo de boletines

Instrucciones exactas (con ejemplo) dentro de `index.html`, buscar el
comentario `COMO AGREGAR UN MES NUEVO` cerca de `BOLETIN_MONTHS`. En resumen:
copiar los 4 HTML del motor a `boletines/AAAA-MM/` con los nombres
`Boletin_FirstMile.html`, `Boletin_ServiceCenter.html`, `Boletin_Quality.html`,
`Boletin_Management.html`, y agregar una entrada nueva al arreglo
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
`SVC + Last Mile`, `Quality`, `Management`. Ver `NOMENCLATURA_OE.md` para el
detalle — esta misma nomenclatura debe coincidir con la que usan `motor.py`
(repo `motor-oe`) y `Boletines_OE_Envio.gs` (envío por correo).
