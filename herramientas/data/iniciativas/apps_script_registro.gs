/**
 * Apps Script para el registro de Iniciativas Locales (OE Hub).
 * 1) Crear un Google Sheet con una hoja llamada "Iniciativas" y en la fila 1 estos encabezados (en este orden):
 *    id,nombre,owner,lider,pais,sitio,tech,tipo_mejora,facility,estandar_wow,okr,kpi,valor,alcance,prioridad,estatus,fecha_registro,fecha_gestion,fecha_mesa,fecha_proyecto,link
 * 2) Extensiones > Apps Script > pegar este codigo > Implementar > Aplicacion web
 *    (Ejecutar como: yo / Acceso: cualquier persona de la organizacion). Copiar la URL /exec
 *    y pegarla en APPS_SCRIPT_URL dentro de herramientas/iniciativas_locales.html.
 * 3) Mónica cambia el "estatus" y llena fecha_gestion / fecha_mesa / fecha_proyecto a mano conforme avanza el flujo.
 */
var COLS = ['id','nombre','owner','lider','pais','sitio','tech','tipo_mejora','facility','estandar_wow','okr','kpi','valor','alcance','prioridad','estatus','fecha_registro','fecha_gestion','fecha_mesa','fecha_proyecto','link'];
function doPost(e) {
  var sh = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Iniciativas');
  var p = e.parameter || {};
  var n = sh.getLastRow(); // filas existentes incluyendo encabezado
  p.id = 'IL-' + ('000' + n).slice(-3);
  p.estatus = '1 Propuesta de valor';
  p.fecha_registro = Utilities.formatDate(new Date(), 'America/Mexico_City', 'yyyy-MM-dd');
  sh.appendRow(COLS.map(function (c) { return p[c] || ''; }));
  return ContentService.createTextOutput('ok');
}
