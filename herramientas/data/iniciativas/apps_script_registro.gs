/**
 * Apps Script para el registro de Iniciativas Locales (OE Hub).
 * 1) Crear un Google Sheet con una hoja llamada "Iniciativas" y en la fila 1 estos encabezados (en este orden):
 *    id,nombre,owner,focal,lider,pais,sitio,equipo,ambito,trimestre,tipo_iniciativa,tech,tipo_mejora,facility,estandar_wow,okr,kpi,valor,alcance,prioridad,clasificacion,estatus,estatus_ejec,meli_axis,avance,fecha_registro,fecha_gestion,fecha_mesa,fecha_proyecto,problema,contexto,propuesta,beneficios,link
 * 2) Extensiones > Apps Script > pegar este codigo > Implementar > Aplicacion web
 *    (Ejecutar como: yo / Acceso: cualquier persona de la organizacion). Copiar la URL /exec
 *    y pegarla en APPS_SCRIPT_URL dentro de herramientas/iniciativas_locales.html.
 * 3) Mónica ajusta a mano: estatus, fecha_gestion/fecha_mesa/fecha_proyecto, estatus_ejec (Done, Carry on Q4, On hold, Q1 2027, Backlog, Cancelado),
 *    meli_axis (Sí/No), avance (0-100), clasificacion (solo regionales: Priorizada/Tentativa/Despriorizada) y ambito (Local/Regional).
 *    Antes: Mónica cambia el "estatus" y llena fecha_gestion / fecha_mesa / fecha_proyecto a mano conforme avanza el flujo.
 */
var COLS = ['id','nombre','owner','focal','lider','pais','sitio','equipo','ambito','trimestre','tipo_iniciativa','tech','tipo_mejora','facility','estandar_wow','okr','kpi','valor','alcance','prioridad','clasificacion','estatus','estatus_ejec','meli_axis','avance','fecha_registro','fecha_gestion','fecha_mesa','fecha_proyecto','problema','contexto','propuesta','beneficios','link'];
function doPost(e) {
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Iniciativas');
  var p = e.parameter || {};
  var n = sh.getLastRow(); // filas existentes incluyendo encabezado
  p.id = 'IL-' + ('000' + n).slice(-3);
  p.estatus = '1 Propuesta de valor';
  p.ambito = p.ambito || 'Local';
  p.estatus_ejec = 'Backlog';
  p.meli_axis = 'No';
  p.avance = 0;
  var hoy = new Date();
  p.trimestre = 'Q' + (Math.floor(hoy.getMonth() / 3) + 1) + ' ' + hoy.getFullYear();
  p.fecha_registro = Utilities.formatDate(new Date(), 'America/Mexico_City', 'yyyy-MM-dd');
  sh.appendRow(COLS.map(function (c) { return p[c] || ''; }));
  return ContentService.createTextOutput('ok');
}
