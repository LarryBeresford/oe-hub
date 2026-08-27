"""
Refresca el tablero Insights_Portafolio_MX.html a partir de un CSV nuevo
exportado de MELI Axis (lista_projetos.csv, vista completa/organizacion).

USO (cada vez que quieras actualizar el tablero del Hub):
  1. Entra a MELI Axis > Mi portafolio > exporta "lista_projetos.csv" (vista completa).
  2. Sobrescribe el archivo data/axis/lista_projetos.csv con el nuevo export.
  3. Corre:  python3 data/axis/build_insights_mx.py
  4. Se regenera management/Insights_Portafolio_MX.html con los datos frescos.
  5. git add data/axis/lista_projetos.csv management/Insights_Portafolio_MX.html
     git commit -m "Actualizar Insights de Portafolio (Axis)"
     git push origin main
  6. Vercel despliega automaticamente y el tablero en Management > Indicadores
     y Management > Proyectos queda actualizado.

Nota: este archivo y su salida SI se publican en el Hub (repo publico + Vercel),
por decision explicita del equipo. Contiene el portafolio completo de OE MLM
(no solo los proyectos de un owner), asi que antes de subir un CSV nuevo
confirma que sigue siendo correcto exponerlo publicamente.

No requiere Sheets, GCP, ni cuenta de servicio: es 100% local + git push.
"""
import csv, json, re, sys
from pathlib import Path

HERE = Path(__file__).parent
CSV_IN = HERE / "lista_projetos.csv"
HTML_OUT = HERE.parent.parent / "management" / "Insights_Portafolio_MX.html"

PAIS_PREFIX = "MX"  # cambia esto si un dia quieres otro pais/scope


def priority(tags: str) -> str:
    m = re.search(r"P([1-3])\b", tags)
    return f"P{m.group(1)}" if m else ""


def load_rows(csv_path: Path):
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)
    return rows


def clean_rows(rows):
    out = []
    for r in rows:
        cad = (r.get("CAD") or "").strip()
        if not cad.startswith(PAIS_PREFIX):
            continue

        def g(k):
            return (r.get(k) or "").strip()

        saving_raw = g("Saving (U$)")
        try:
            saving = float(saving_raw.replace(",", "")) if saving_raw else 0.0
        except ValueError:
            saving = 0.0

        tags = g("Tags") or "(sin tag)"
        out.append({
            "proyecto": g("Projeto"),
            "cad": cad,
            "owner": g("Owner") or "(sin owner)",
            "papel": g("Papel"),
            "etapa": g("Etapa Atual") or "(sin etapa)",
            "atrasado": g("Atrasado") or "No",
            "inconsistente": g("Inconsistente") or "No",
            "successRate": g("Success Rate") or "No Evaluado",
            "tags": tags,
            "time": g("Time") or "Sin equipo",
            "saving": round(saving, 2),
            "prioridad": priority(tags),
            "rollout": "Roll Out" in tags,
        })
    return out


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Insights de Portafolio — OE MLM (México)</title>
<style>
  :root{
    --bg:#111111; --panel:#1b1b1b; --panel2:#232323; --yellow:#FFE600;
    --text:#f2f2f2; --muted:#9a9a9a; --red:#e74c3c; --green:#2ecc71; --border:#333;
  }
  *{box-sizing:border-box;}
  body{margin:0;background:radial-gradient(circle at 15% 0%, #171717 0%, var(--bg) 45%);color:var(--text);font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased;}
  header{background:#000;border-bottom:4px solid var(--yellow);padding:22px 32px;}
  header h1{margin:0;font-size:22px;letter-spacing:.01em;}
  header .sub{color:var(--muted);font-size:13px;margin-top:6px;}
  .scope-badge{display:inline-block;margin-top:10px;background:#123524;color:var(--green);border:1px solid var(--green);
    padding:5px 12px;border-radius:20px;font-size:12px;transition:transform .15s ease;}
  .scope-badge:hover{transform:translateY(-1px);}
  main{padding:26px 32px;max-width:1300px;margin:0 auto;}
  .findings{background:var(--panel);border-left:4px solid var(--yellow);border-radius:10px;padding:16px 20px;margin-bottom:24px;
    box-shadow:0 4px 16px rgba(0,0,0,.35);}
  .findings h2{margin:0 0 10px;font-size:15px;color:var(--yellow);}
  .findings ul{margin:0;padding-left:18px;font-size:14px;line-height:1.7;}
  .kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:14px;margin-bottom:28px;}
  .kpi{background:linear-gradient(180deg, var(--panel2) 0%, var(--panel) 100%);border-radius:12px;padding:18px 16px;text-align:center;
    border:1px solid var(--border);cursor:default;
    transition:transform .18s ease, box-shadow .18s ease, border-color .18s ease;}
  .kpi:hover{transform:translateY(-4px);border-color:rgba(255,230,0,.5);
    box-shadow:0 10px 28px rgba(0,0,0,.5), 0 0 0 1px rgba(255,230,0,.08);}
  .kpi .val{font-size:27px;font-weight:700;color:var(--yellow);transition:color .18s ease;}
  .kpi .lbl{font-size:11px;color:var(--muted);margin-top:4px;letter-spacing:.02em;}
  .kpi.alert .val{color:var(--red);}
  .filters{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;background:var(--panel);
    padding:14px 16px;border-radius:10px;margin-bottom:14px;border:1px solid var(--border);
    box-shadow:0 4px 14px rgba(0,0,0,.3);}
  .filters label{font-size:11px;color:var(--muted);display:block;margin-bottom:4px;}
  select, input[type=text]{background:var(--panel2);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:7px 9px;font-size:13px;
    transition:border-color .15s ease, box-shadow .15s ease;}
  select:hover, input[type=text]:hover{border-color:#555;}
  select:focus, input[type=text]:focus{outline:none;border-color:var(--yellow);box-shadow:0 0 0 3px rgba(255,230,0,.12);}
  .chkwrap{display:flex;align-items:center;gap:6px;font-size:13px;transition:color .15s ease;}
  .chkwrap:hover{color:var(--yellow);}
  .chkwrap input[type=checkbox]{accent-color:var(--yellow);cursor:pointer;}
  .msFilter{position:relative;}
  .msBtn{background:var(--panel2);color:var(--text);border:1px solid var(--border);border-radius:6px;padding:7px 10px;
    font-size:13px;cursor:pointer;min-width:150px;text-align:left;font-family:inherit;
    transition:border-color .15s ease, transform .12s ease, box-shadow .15s ease;}
  .msBtn:hover{border-color:#555;transform:translateY(-1px);}
  .msBtn.active{border-color:var(--yellow);color:var(--yellow);box-shadow:0 0 0 2px rgba(255,230,0,.1);}
  .msPanel{display:none;position:absolute;top:calc(100% + 6px);left:0;background:var(--panel2);
    border:1px solid var(--border);border-radius:8px;padding:8px;min-width:210px;max-height:230px;
    overflow-y:auto;z-index:30;box-shadow:0 14px 34px rgba(0,0,0,.55);}
  .msPanel.open{display:block;}
  .msOption{display:flex;align-items:center;gap:8px;padding:5px 6px;border-radius:5px;font-size:12.5px;
    cursor:pointer;transition:background-color .12s ease, transform .12s ease;}
  .msOption:hover{background:#2a2a2a;transform:translateX(2px);}
  .msOption input[type=checkbox]{accent-color:var(--yellow);cursor:pointer;}
  .clearBtn{background:transparent;color:var(--muted);border:1px solid var(--border);border-radius:6px;
    padding:7px 12px;font-size:12px;cursor:pointer;font-family:inherit;
    transition:border-color .15s ease, color .15s ease, transform .12s ease;}
  .clearBtn:hover{border-color:var(--yellow);color:var(--yellow);transform:translateY(-1px);}
  .count{font-size:12px;color:var(--muted);margin-bottom:8px;}
  h3.section{font-size:15px;border-bottom:2px solid var(--yellow);padding-bottom:6px;margin:30px 0 12px;}
  .tablewrap{max-height:520px;overflow-y:auto;border-radius:10px;border:1px solid var(--border);box-shadow:0 4px 16px rgba(0,0,0,.3);}
  table{width:100%;border-collapse:collapse;background:var(--panel);font-size:12.5px;}
  th{background:var(--panel2);text-align:left;padding:10px 10px;color:var(--yellow);font-size:11px;text-transform:uppercase;
     letter-spacing:.04em;position:sticky;top:0;}
  td{padding:9px 10px;border-top:1px solid var(--border);transition:background-color .12s ease;}
  tbody tr{transition:transform .12s ease;}
  tbody tr:hover{transform:scale(1.003);}
  tr:hover td{background:#212121;box-shadow:inset 3px 0 0 var(--yellow);}
  .badge{padding:2px 8px;border-radius:12px;font-size:10.5px;font-weight:600;white-space:nowrap;transition:transform .12s ease;}
  tr:hover .badge{transform:scale(1.05);}
  .badge.si{background:rgba(231,76,60,.18);color:var(--red);}
  .badge.no{background:rgba(46,204,113,.18);color:var(--green);}
  .badge.p{background:rgba(255,230,0,.15);color:var(--yellow);}
  .badge.blank{background:#333;color:var(--muted);}
  .empty-row td{text-align:center;color:var(--muted);padding:18px;}
  footer{color:var(--muted);font-size:11px;text-align:center;padding:24px;}
</style>
</head>
<body>
<header>
  <h1 id="txtTitle">Insights de Portafolio — OE MLM (México)</h1>
  <div class="sub" id="txtSub">Generado con el export "vista completa" de MELI Axis (lista_projetos.csv), filtrado a proyectos con CAD de México.</div>
  <div class="scope-badge" id="txtScope">✓ Alcance real: __TOTAL__ proyectos de México</div>
</header>
<main>
  <div class="findings">
    <h2 id="txtFindingsTitle">Hallazgos clave</h2>
    <ul id="findingsList"></ul>
  </div>
  <div class="kpis">
    <div class="kpi"><div class="val" id="kpiTotal">–</div><div class="lbl" id="lblTotal">Proyectos (México)</div></div>
    <div class="kpi alert"><div class="val" id="kpiAtrasados">–</div><div class="lbl" id="lblAtrasados">% Atrasados</div></div>
    <div class="kpi"><div class="val" id="kpiSaving">–</div><div class="lbl" id="lblSaving">Savings acumulados (USD)</div></div>
    <div class="kpi"><div class="val" id="kpiCentros">–</div><div class="lbl" id="lblCentros">Centros / CAD distintos</div></div>
    <div class="kpi"><div class="val" id="kpiRollout">–</div><div class="lbl" id="lblRollout">En Roll Out</div></div>
  </div>
  <h3 class="section" id="txtSection">Proyectos — México</h3>
  <div class="filters">
    <div>
      <label id="lblBusqueda">Buscar proyecto</label>
      <input type="text" id="fBusqueda" list="fBusquedaList" placeholder="nombre del proyecto..." autocomplete="off">
      <datalist id="fBusquedaList"></datalist>
    </div>
    <div class="msFilter">
      <label id="lblCad">Centro / CAD</label>
      <button type="button" class="msBtn" id="msBtnCad" onclick="toggleMS('Cad')">Todos ▾</button>
      <div class="msPanel" id="msPanelCad"></div>
    </div>
    <div class="msFilter">
      <label id="lblTime">Equipo</label>
      <button type="button" class="msBtn" id="msBtnTime" onclick="toggleMS('Time')">Todos ▾</button>
      <div class="msPanel" id="msPanelTime"></div>
    </div>
    <div class="msFilter">
      <label id="lblEtapa">Etapa actual</label>
      <button type="button" class="msBtn" id="msBtnEtapa" onclick="toggleMS('Etapa')">Todas ▾</button>
      <div class="msPanel" id="msPanelEtapa"></div>
    </div>
    <div class="msFilter">
      <label id="lblPrioridad">Prioridad</label>
      <button type="button" class="msBtn" id="msBtnPrioridad" onclick="toggleMS('Prioridad')">Todas ▾</button>
      <div class="msPanel" id="msPanelPrioridad"></div>
    </div>
    <div class="chkwrap"><input type="checkbox" id="fSoloAtrasados"><label for="fSoloAtrasados" id="lblSoloAtrasados" style="margin:0;">Solo atrasados</label></div>
    <div class="chkwrap"><input type="checkbox" id="fSoloRollout"><label for="fSoloRollout" id="lblSoloRollout" style="margin:0;">Solo Roll Out</label></div>
    <div><button type="button" class="clearBtn" id="fClear" onclick="clearFilters()">Limpiar filtros</button></div>
  </div>
  <div class="count" id="countLbl"></div>
  <div class="tablewrap">
  <table id="tblProyectos">
    <thead><tr>
      <th id="thProyecto">Proyecto</th><th id="thCad">CAD</th><th id="thEtapa">Etapa actual</th><th id="thPrioridad">Prioridad</th><th id="thTags">Tags</th>
      <th id="thAtrasado">Atrasado</th><th id="thSuccess">Success Rate</th><th id="thSaving">Saving (USD)</th><th id="thEquipo">Equipo</th>
    </tr></thead>
    <tbody></tbody>
  </table>
  </div>
</main>
<footer id="txtFooter">OE MLM · datos exportados de MELI Axis (vista completa) · filtrado a CAD de México</footer>
<script>
const proyectos = __DATA__;

function esc(s){
  return String(s==null?'':s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function badge(value, type){
  if(type==='atraso'){ return value==='Sí' ? '<span class="badge si">Sí</span>' : '<span class="badge no">No</span>'; }
  if(type==='prioridad'){ return value ? `<span class="badge p">${esc(value)}</span>` : '<span class="badge blank">–</span>'; }
  return esc(value);
}

// ==================== ES / EN / PT ====================
// El Hub (index.html) envia el idioma via postMessage cuando esta embebido en un iframe.
let currentLang = 'es';
const I18N = {
  es: {
    title: 'Insights de Portafolio — OE MLM (México)',
    sub: 'Generado con el export "vista completa" de MELI Axis (lista_projetos.csv), filtrado a proyectos con CAD de México.',
    scope: (n) => `✓ Alcance real: ${n} proyectos de México`,
    findingsTitle: 'Hallazgos clave',
    lblTotal: 'Proyectos (México)', lblAtrasados: '% Atrasados', lblSaving: 'Savings acumulados (USD)',
    lblCentros: 'Centros / CAD distintos', lblRollout: 'En Roll Out',
    section: 'Proyectos — México',
    lblBusqueda: 'Buscar proyecto', phBusqueda: 'nombre del proyecto...',
    lblCad: 'Centro / CAD', lblTime: 'Equipo', lblEtapa: 'Etapa actual', lblPrioridad: 'Prioridad',
    lblSoloAtrasados: 'Solo atrasados', lblSoloRollout: 'Solo Roll Out',
    clear: 'Limpiar filtros',
    thProyecto:'Proyecto', thCad:'CAD', thEtapa:'Etapa actual', thPrioridad:'Prioridad', thTags:'Tags',
    thAtrasado:'Atrasado', thSuccess:'Success Rate', thSaving:'Saving (USD)', thEquipo:'Equipo',
    footer: 'OE MLM · datos exportados de MELI Axis (vista completa) · filtrado a CAD de México',
    allM: 'Todos', allF: 'Todas',
    nSel: (n) => n + ' seleccionado' + (n > 1 ? 's' : ''),
    count: (shown, total) => `Mostrando ${shown} de ${total} proyectos`,
    emptyRow: 'Sin proyectos que coincidan con los filtros.',
    findingsEmpty: 'Sin proyectos que coincidan con los filtros actuales.',
    findings: (atrasados, total, pct, saving, centros, rollout) => `
      <li><strong>${atrasados} de ${total} proyectos están atrasados (${pct}%)</strong> con los filtros actuales.</li>
      <li><strong>$${saving} USD</strong> en savings reportados en esta selección.</li>
      <li>Cubre <strong>${centros} centros/CAD distintos</strong>.</li>
      <li><strong>${rollout} proyectos</strong> están etiquetados como "Roll Out" (despliegue en curso).</li>
    `,
  },
  en: {
    title: 'Portfolio Insights — OE MLM (Mexico)',
    sub: 'Generated from the "full view" export of MELI Axis (lista_projetos.csv), filtered to projects with a Mexico CAD.',
    scope: (n) => `✓ Real scope: ${n} projects from Mexico`,
    findingsTitle: 'Key findings',
    lblTotal: 'Projects (Mexico)', lblAtrasados: '% Delayed', lblSaving: 'Cumulative savings (USD)',
    lblCentros: 'Distinct centers / CAD', lblRollout: 'In Roll Out',
    section: 'Projects — Mexico',
    lblBusqueda: 'Search project', phBusqueda: 'project name...',
    lblCad: 'Center / CAD', lblTime: 'Team', lblEtapa: 'Current stage', lblPrioridad: 'Priority',
    lblSoloAtrasados: 'Delayed only', lblSoloRollout: 'Roll Out only',
    clear: 'Clear filters',
    thProyecto:'Project', thCad:'CAD', thEtapa:'Current stage', thPrioridad:'Priority', thTags:'Tags',
    thAtrasado:'Delayed', thSuccess:'Success Rate', thSaving:'Saving (USD)', thEquipo:'Team',
    footer: 'OE MLM · data exported from MELI Axis (full view) · filtered to Mexico CAD',
    allM: 'All', allF: 'All',
    nSel: (n) => n + ' selected',
    count: (shown, total) => `Showing ${shown} of ${total} projects`,
    emptyRow: 'No projects match the filters.',
    findingsEmpty: 'No projects match the current filters.',
    findings: (atrasados, total, pct, saving, centros, rollout) => `
      <li><strong>${atrasados} of ${total} projects are delayed (${pct}%)</strong> with the current filters.</li>
      <li><strong>$${saving} USD</strong> in savings reported in this selection.</li>
      <li>Covers <strong>${centros} distinct centers/CAD</strong>.</li>
      <li><strong>${rollout} projects</strong> are tagged "Roll Out" (in deployment).</li>
    `,
  },
  pt: {
    title: 'Insights de Portfólio — OE MLM (México)',
    sub: 'Gerado com o export "visão completa" do MELI Axis (lista_projetos.csv), filtrado a projetos com CAD do México.',
    scope: (n) => `✓ Alcance real: ${n} projetos do México`,
    findingsTitle: 'Principais achados',
    lblTotal: 'Projetos (México)', lblAtrasados: '% Atrasados', lblSaving: 'Savings acumulados (USD)',
    lblCentros: 'Centros / CAD distintos', lblRollout: 'Em Roll Out',
    section: 'Projetos — México',
    lblBusqueda: 'Buscar projeto', phBusqueda: 'nome do projeto...',
    lblCad: 'Centro / CAD', lblTime: 'Equipe', lblEtapa: 'Etapa atual', lblPrioridad: 'Prioridade',
    lblSoloAtrasados: 'Só atrasados', lblSoloRollout: 'Só Roll Out',
    clear: 'Limpar filtros',
    thProyecto:'Projeto', thCad:'CAD', thEtapa:'Etapa atual', thPrioridad:'Prioridade', thTags:'Tags',
    thAtrasado:'Atrasado', thSuccess:'Success Rate', thSaving:'Saving (USD)', thEquipo:'Equipe',
    footer: 'OE MLM · dados exportados do MELI Axis (visão completa) · filtrado a CAD do México',
    allM: 'Todos', allF: 'Todas',
    nSel: (n) => n + ' selecionado' + (n > 1 ? 's' : ''),
    count: (shown, total) => `Mostrando ${shown} de ${total} projetos`,
    emptyRow: 'Sem projetos que coincidam com os filtros.',
    findingsEmpty: 'Sem projetos que coincidam com os filtros atuais.',
    findings: (atrasados, total, pct, saving, centros, rollout) => `
      <li><strong>${atrasados} de ${total} projetos estão atrasados (${pct}%)</strong> com os filtros atuais.</li>
      <li><strong>$${saving} USD</strong> em savings reportados nesta seleção.</li>
      <li>Cobre <strong>${centros} centros/CAD distintos</strong>.</li>
      <li><strong>${rollout} projetos</strong> estão marcados como "Roll Out" (em implantação).</li>
    `,
  },
};

function applyDashboardLang(lang){
  if (!I18N[lang]) return;
  currentLang = lang;
  const t = I18N[lang];
  document.getElementById('txtTitle').textContent = t.title;
  document.getElementById('txtSub').textContent = t.sub;
  document.getElementById('txtScope').textContent = t.scope(proyectos.length);
  document.getElementById('txtFindingsTitle').textContent = t.findingsTitle;
  document.getElementById('lblTotal').textContent = t.lblTotal;
  document.getElementById('lblAtrasados').textContent = t.lblAtrasados;
  document.getElementById('lblSaving').textContent = t.lblSaving;
  document.getElementById('lblCentros').textContent = t.lblCentros;
  document.getElementById('lblRollout').textContent = t.lblRollout;
  document.getElementById('txtSection').textContent = t.section;
  document.getElementById('lblBusqueda').textContent = t.lblBusqueda;
  document.getElementById('fBusqueda').setAttribute('placeholder', t.phBusqueda);
  document.getElementById('lblCad').textContent = t.lblCad;
  document.getElementById('lblTime').textContent = t.lblTime;
  document.getElementById('lblEtapa').textContent = t.lblEtapa;
  document.getElementById('lblPrioridad').textContent = t.lblPrioridad;
  document.getElementById('lblSoloAtrasados').textContent = t.lblSoloAtrasados;
  document.getElementById('lblSoloRollout').textContent = t.lblSoloRollout;
  document.getElementById('fClear').textContent = t.clear;
  document.getElementById('thProyecto').textContent = t.thProyecto;
  document.getElementById('thCad').textContent = t.thCad;
  document.getElementById('thEtapa').textContent = t.thEtapa;
  document.getElementById('thPrioridad').textContent = t.thPrioridad;
  document.getElementById('thTags').textContent = t.thTags;
  document.getElementById('thAtrasado').textContent = t.thAtrasado;
  document.getElementById('thSuccess').textContent = t.thSuccess;
  document.getElementById('thSaving').textContent = t.thSaving;
  document.getElementById('thEquipo').textContent = t.thEquipo;
  document.getElementById('txtFooter').textContent = t.footer;
  Object.keys(FIELD_MAP).forEach(name => updateMsLabel(name));
  update();
}
window.addEventListener('message', (e) => {
  if (e.data && e.data.type === 'oeHubLang') applyDashboardLang(e.data.lang);
});

// Filtros con seleccion multiple (CAD, Equipo, Etapa, Prioridad) + busqueda por nombre (dropdown alfabetico)
const FIELD_MAP = {
  Cad:       { key:'cad',       allKey:'allM' },
  Time:      { key:'time',      allKey:'allM' },
  Etapa:     { key:'etapa',     allKey:'allF' },
  Prioridad: { key:'prioridad', allKey:'allF' },
};
const state = { cad:new Set(), time:new Set(), etapa:new Set(), prioridad:new Set() };

function buildMultiSelects(){
  Object.keys(FIELD_MAP).forEach(name => {
    const { key } = FIELD_MAP[name];
    const values = [...new Set(proyectos.map(p => p[key]))].filter(v => v).sort((a,b)=>a.localeCompare(b,'es'));
    const panel = document.getElementById('msPanel'+name);
    panel.innerHTML = values.map(v => `<label class="msOption"><input type="checkbox" value="${esc(v)}"> ${esc(v)}</label>`).join('');
    panel.querySelectorAll('input[type=checkbox]').forEach(cb => {
      cb.addEventListener('change', () => {
        const set = state[key];
        if (cb.checked) set.add(cb.value); else set.delete(cb.value);
        updateMsLabel(name);
        update();
      });
    });
  });
}
function updateMsLabel(name){
  const { key, allKey } = FIELD_MAP[name];
  const t = I18N[currentLang];
  const btn = document.getElementById('msBtn'+name);
  const n = state[key].size;
  btn.textContent = (n===0 ? t[allKey] : t.nSel(n)) + ' ▾';
  btn.classList.toggle('active', n>0);
}
function toggleMS(name){
  const target = document.getElementById('msPanel'+name);
  const isOpen = target.classList.contains('open');
  document.querySelectorAll('.msPanel').forEach(p => p.classList.remove('open'));
  if (!isOpen) target.classList.add('open');
}
document.addEventListener('click', (e) => {
  if (!e.target.closest('.msFilter')) {
    document.querySelectorAll('.msPanel').forEach(p => p.classList.remove('open'));
  }
});
function fillDatalist(){
  const dl = document.getElementById('fBusquedaList');
  const names = [...new Set(proyectos.map(p => p.proyecto))].filter(v => v).sort((a,b)=>a.localeCompare(b,'es'));
  dl.innerHTML = names.map(n => `<option value="${esc(n)}"></option>`).join('');
}

function getFiltered(){
  const busqueda = document.getElementById('fBusqueda').value.trim().toLowerCase();
  const soloAtrasados = document.getElementById('fSoloAtrasados').checked;
  const soloRollout = document.getElementById('fSoloRollout').checked;
  return proyectos.filter(p =>
    (!busqueda || p.proyecto.toLowerCase().includes(busqueda)) &&
    (state.cad.size===0 || state.cad.has(p.cad)) &&
    (state.time.size===0 || state.time.has(p.time)) &&
    (state.etapa.size===0 || state.etapa.has(p.etapa)) &&
    (state.prioridad.size===0 || state.prioridad.has(p.prioridad)) &&
    (!soloAtrasados || p.atrasado==='Sí') &&
    (!soloRollout || p.rollout)
  );
}
function render(filtered){
  const t = I18N[currentLang];
  document.getElementById('countLbl').textContent = t.count(filtered.length, proyectos.length);
  const tbody = document.querySelector('#tblProyectos tbody');
  tbody.innerHTML = filtered.length ? filtered.slice(0,500).map(p => `
    <tr>
      <td>${esc(p.proyecto)}</td><td>${esc(p.cad)}</td><td>${esc(p.etapa)}</td><td>${badge(p.prioridad,'prioridad')}</td>
      <td style="color:var(--muted);font-size:11px;">${esc(p.tags)}</td>
      <td>${badge(p.atrasado,'atraso')}</td><td>${esc(p.successRate)}</td><td>$${p.saving.toLocaleString()}</td><td>${esc(p.time)}</td>
    </tr>`).join('') : `<tr class="empty-row"><td colspan="9">${t.emptyRow}</td></tr>`;
}
function renderKpis(filtered){
  const t = I18N[currentLang];
  const total = filtered.length;
  const atrasados = filtered.filter(p=>p.atrasado==='Sí').length;
  const savingTotal = filtered.reduce((a,p)=>a+p.saving,0);
  const centros = new Set(filtered.map(p=>p.cad)).size;
  const rollout = filtered.filter(p=>p.rollout).length;
  document.getElementById('kpiTotal').textContent = total;
  document.getElementById('kpiAtrasados').textContent = total ? Math.round(100*atrasados/total)+'%' : '0%';
  document.getElementById('kpiSaving').textContent = '$'+Math.round(savingTotal).toLocaleString();
  document.getElementById('kpiCentros').textContent = centros;
  document.getElementById('kpiRollout').textContent = rollout;
  document.getElementById('findingsList').innerHTML = total
    ? t.findings(atrasados, total, Math.round(100*atrasados/total), Math.round(savingTotal).toLocaleString(), centros, rollout)
    : `<li>${t.findingsEmpty}</li>`;
}
function update(){
  const filtered = getFiltered();
  render(filtered);
  renderKpis(filtered);
}
function clearFilters(){
  document.getElementById('fBusqueda').value = '';
  document.getElementById('fSoloAtrasados').checked = false;
  document.getElementById('fSoloRollout').checked = false;
  Object.keys(FIELD_MAP).forEach(name => {
    state[FIELD_MAP[name].key].clear();
    document.querySelectorAll('#msPanel'+name+' input[type=checkbox]').forEach(cb => cb.checked = false);
    updateMsLabel(name);
  });
  update();
}

buildMultiSelects();
fillDatalist();
document.getElementById('fBusqueda').addEventListener('input', update);
['fSoloAtrasados','fSoloRollout'].forEach(id =>
  document.getElementById(id).addEventListener('change', update));
update();
</script>
</body>
</html>
"""


def main():
    if not CSV_IN.exists():
        print(f"ERROR: no encuentro {CSV_IN}")
        print("Pon ahi el CSV recien exportado de Axis con ese nombre exacto.")
        sys.exit(1)

    rows = load_rows(CSV_IN)
    data = clean_rows(rows)
    if not data:
        print("ADVERTENCIA: 0 proyectos con CAD de MX encontrados. Revisa el CSV.")

    html = HTML_TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    html = html.replace("__TOTAL__", str(len(data)))

    HTML_OUT.parent.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"OK: {len(data)} proyectos de México -> {HTML_OUT}")


if __name__ == "__main__":
    main()
