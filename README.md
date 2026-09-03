# OE MLM Hub

Sitio de portafolio e indicadores de Excelencia Operacional (OE) MercadoLibre MX,
pensado para desplegarse como sitio estático en **Vercel**. Alcance exclusivo de
OE (FM + XD + SC + TOM, SVC + Last Mile, Quality) — no incluye Transporte ni Control Tower.

Este es un repositorio **separado** de `motor-oe` (la app de Streamlit que genera
los boletines mensuales). El hub y el generador de boletines son proyectos
independientes que conviven en el mismo equipo.

## Estado actual (Sprint 2 — Contenido y portafolio, en curso)

- [x] Shell de navegación (sidebar + topbar + páginas) adaptado del diseño de referencia aprobado.
- [x] Arquitectura de secciones: Inicio, Proyectos, Boletines, Directorio, Indicadores.
- [x] Directorio poblado con el equipo real de OE.
- [x] Repositorio en GitHub + despliegue en Vercel (https://oe-hub-mu.vercel.app/).
- [x] Boletines: los 3 newsletters de julio 2026 (FM + XD + SC + TOM, SVC + Last Mile, Quality) enlazados desde `boletines/2026-07/`. Para agregar un mes nuevo: copiar los 3 HTML del motor a una carpeta `boletines/AAAA-MM/` y agregar sus tarjetas en la página Boletines de `index.html`.
- [ ] Proyectos: pendiente de la tabla de portafolio (ver `Propuesta_Datos_Indicadores_OE_Hub.docx`).
- [ ] Indicadores: placeholder "en construcción" — se conecta en el Sprint 3.

## Correr en local

Es un solo archivo HTML estático, sin build ni dependencias. Basta con abrir
`index.html` en el navegador, o servirlo con cualquier servidor estático:

```
python3 -m http.server 8000
```

y entrar a `http://localhost:8000`.

## Estructura

```
oe-hub/
├── index.html   # todo el sitio: HTML + CSS + JS en un solo archivo
└── README.md
```

## Próximos sprints

- **Sprint 2:** portafolio de proyectos real + histórico de boletines enlazado.
- **Sprint 3:** dashboard de indicadores (% avance, riesgos, top proyectos, comparativa entre áreas).
- **Sprint 4:** pulido, validación de responsividad y lanzamiento.

Ver el plan completo en `Flujo_Sprints_OE_Hub.html` (carpeta raíz del proyecto).
