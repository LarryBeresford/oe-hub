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
  <h1>Insights de Portafolio — OE MLM (México)</h1>
  <div class="sub">Generado con el export "vista completa" de MELI Axis (lista_projetos.csv), filtrado a proyectos con CAD de México.</div>
  <div class="scope-badge">✓ Alcance real: __TOTAL__ proyectos de México</div>
</header>
<main>
  <div class="findings">
    <h2>Hallazgos clave</h2>
    <ul id="findingsList"></ul>
  </div>
  <div class="kpis">
    <div class="kpi"><div class="val" id="kpiTotal">–</div><div class="lbl">Proyectos (México)</div></div>
    <div class="kpi alert"><div class="val" id="kpiAtrasados">–</div><div class="lbl">% Atrasados</div></div>
    <div class="kpi"><div class="val" id="kpiSaving">–</div><div class="lbl">Savings acumulados (USD)</div></div>
    <div class="kpi"><div class="val" id="kpiCentros">–</div><div class="lbl">Centros / CAD distintos</div></div>
    <div class="kpi"><div class="val" id="kpiRollout">–</div><div class="lbl">En Roll Out</div></div>
  </div>
  <h3 class="section">Proyectos — México</h3>
  <div class="filters">
    <div><label>Buscar proyecto</label><input type="text" id="fBusqueda" placeholder="nombre del proyecto..."></div>
    <div><label>Centro / CAD</label><select id="fCad"><option value="">Todos</option></select></div>
    <div><label>Equipo</label><select id="fTime"><option value="">Todos</option></select></div>
    <div><label>Etapa actual</label><select id="fEtapa"><option value="">Todas</option></select></div>
    <div><label>Prioridad</label><select id="fPrioridad"><option value="">Todas</option></select></div>
    <div class="chkwrap"><input type="checkbox" id="fSoloAtrasados"><label for="fSoloAtrasados" style="margin:0;">Solo atrasados</label></div>
    <div class="chkwrap"><input type="checkbox" id="fSoloRollout"><label for="fSoloRollout" style="margin:0;">Solo Roll Out</label></div>
  </div>
  <div class="count" id="countLbl"></div>
  <div class="tablewrap">
  <table id="tblProyectos">
    <thead><tr>
      <th>Proyecto</th><th>CAD</th><th>Etapa actual</th><th>Prioridad</th><th>Tags</th>
      <th>Atrasado</th><th>Success Rate</th><th>Saving (USD)</th><th>Equipo</th>
    </tr></thead>
    <tbody></tbody>
  </table>
  </div>
</main>
<footer>OE MLM · datos exportados de MELI Axis (vista completa) · filtrado a CAD de México</footer>
<script>
const proyectos = __DATA__;

function badge(value, type){
  if(type==='atraso'){ return value==='Sí' ? '<span class="badge si">Sí</span>' : '<span class="badge no">No</span>'; }
  if(type==='prioridad'){ return value ? `<span class="badge p">${value}</span>` : '<span class="badge blank">–</span>'; }
  return value;
}
function fillSelect(id, values){
  const sel = document.getElementById(id);
  [...new Set(values)].filter(v=>v).sort().forEach(v=>{
    const opt = document.createElement('option'); opt.value=v; opt.textContent=v; sel.appendChild(opt);
  });
}
function render(){
  const busqueda = document.getElementById('fBusqueda').value.trim().toLowerCase();
  const cad = document.getElementById('fCad').value;
  const time = document.getElementById('fTime').value;
  const etapa = document.getElementById('fEtapa').value;
  const prioridad = document.getElementById('fPrioridad').value;
  const soloAtrasados = document.getElementById('fSoloAtrasados').checked;
  const soloRollout = document.getElementById('fSoloRollout').checked;
  const filtered = proyectos.filter(p =>
    (!busqueda || p.proyecto.toLowerCase().includes(busqueda)) &&
    (!cad || p.cad===cad) && (!time || p.time===time) && (!etapa || p.etapa===etapa) &&
    (!prioridad || p.prioridad===prioridad) && (!soloAtrasados || p.atrasado==='Sí') && (!soloRollout || p.rollout)
  );
  document.getElementById('countLbl').textContent = `Mostrando ${filtered.length} de ${proyectos.length} proyectos`;
  const tbody = document.querySelector('#tblProyectos tbody');
  tbody.innerHTML = filtered.length ? filtered.slice(0,500).map(p => `
    <tr>
      <td>${p.proyecto}</td><td>${p.cad}</td><td>${p.etapa}</td><td>${badge(p.prioridad,'prioridad')}</td>
      <td style="color:var(--muted);font-size:11px;">${p.tags}</td>
      <td>${badge(p.atrasado,'atraso')}</td><td>${p.successRate}</td><td>$${p.saving.toLocaleString()}</td><td>${p.time}</td>
    </tr>`).join('') : '<tr class="empty-row"><td colspan="9">Sin proyectos que coincidan con el filtro.</td></tr>';
}
function renderKpis(){
  const total = proyectos.length;
  const atrasados = proyectos.filter(p=>p.atrasado==='Sí').length;
  const savingTotal = proyectos.reduce((a,p)=>a+p.saving,0);
  const centros = new Set(proyectos.map(p=>p.cad)).size;
  const rollout = proyectos.filter(p=>p.rollout).length;
  document.getElementById('kpiTotal').textContent = total;
  document.getElementById('kpiAtrasados').textContent = Math.round(100*atrasados/total)+'%';
  document.getElementById('kpiSaving').textContent = '$'+Math.round(savingTotal).toLocaleString();
  document.getElementById('kpiCentros').textContent = centros;
  document.getElementById('kpiRollout').textContent = rollout;
  document.getElementById('findingsList').innerHTML = `
    <li><strong>${atrasados} de ${total} proyectos de México están atrasados (${Math.round(100*atrasados/total)}%)</strong>.</li>
    <li><strong>$${Math.round(savingTotal).toLocaleString()} USD</strong> en savings reportados por los proyectos de México.</li>
    <li>El export cubre <strong>${centros} centros/CAD distintos</strong> de México.</li>
    <li><strong>${rollout} proyectos</strong> están etiquetados como "Roll Out" (despliegue en curso).</li>
  `;
}
fillSelect('fCad', proyectos.map(p=>p.cad));
fillSelect('fTime', proyectos.map(p=>p.time));
fillSelect('fEtapa', proyectos.map(p=>p.etapa));
fillSelect('fPrioridad', proyectos.map(p=>p.prioridad));
['fCad','fTime','fEtapa','fPrioridad','fSoloAtrasados','fSoloRollout'].forEach(id =>
  document.getElementById(id).addEventListener('change', render));
document.getElementById('fBusqueda').addEventListener('input', render);
renderKpis();
render();
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
