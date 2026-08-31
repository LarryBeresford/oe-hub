/**
 * Ideas y sugerencias — OE MLM Hub
 * ---------------------------------
 * Recibe las sugerencias enviadas desde la sección "Ideas y sugerencias"
 * del Hub (index.html > submitSuggestion()) y las guarda como fila nueva
 * en un Google Sheet.
 *
 * v2 — CAMBIO IMPORTANTE: ya no usa SpreadsheetApp.getActiveSpreadsheet().
 * Esa función solo funciona si el proyecto de Apps Script quedó LIGADO a la
 * Sheet (creado desde "Extensiones > Apps Script" dentro de ella); si el
 * proyecto quedó suelto por cualquier motivo, esa línea falla en silencio
 * (el try/catch la atrapa) y el "doPost" se ve "Completada" en el registro
 * de ejecuciones aunque no se haya guardado nada. Ahora abre la Sheet por
 * ID directo (SHEET_ID abajo), así funciona sin importar cómo se creó el
 * proyecto. También deja rastro en el Log (Ver > Registros) si algo falla.
 *
 * COMO DESPLEGAR (una sola vez):
 *   1. Crea un Google Sheet nuevo (ej. "OE Hub — Ideas y sugerencias").
 *   2. En esa hoja, agrega esta fila de encabezados en la fila 1:
 *      Fecha | Área | Tipo | Descripción | Idioma
 *   3. Copia el ID de esa Sheet desde su URL (la parte entre /d/ y /edit) y
 *      pégalo abajo en la constante SHEET_ID.
 *   4. Extensiones > Apps Script.
 *   5. Borra el contenido de Code.gs y pega este archivo completo.
 *   6. Guarda el proyecto (ej. "Ideas Sugerencias OE Hub").
 *   7. Implementar > Nueva implementación > tipo "Aplicación web".
 *        - Ejecutar como: Yo (tu cuenta)
 *        - Quién tiene acceso: Cualquier usuario (o "Cualquier usuario de
 *          <tu dominio>" si tu organización de Google Workspace no permite
 *          la opción totalmente pública)
 *   8. Autoriza los permisos que pida Google.
 *   9. Copia la URL que te da ("URL de la aplicación web").
 *  10. Pégala en oe-hub/index.html, en la constante SUGGESTIONS_ENDPOINT
 *      (busca "SUGGESTIONS_ENDPOINT" cerca de la función submitSuggestion()).
 *  11. git add, commit, push — listo, el formulario ya cae en el Sheet real.
 *
 * Si alguna vez necesitas cambiar de Sheet: actualiza SHEET_ID abajo, guarda,
 * y en "Implementar > Administrar implementaciones > editar" sube una
 * "Nueva versión" para que el cambio quede activo en la misma URL.
 */

// ID de la Sheet de datos (parte de la URL entre /d/ y /edit).
// Sheet "Sugerencias_HUB_OE" -- para consultar las sugerencias enviadas:
// https://docs.google.com/spreadsheets/d/1KF896f43oq1a_RF4xrJ5Cdgjw2GN6cwhg25d8Y5DbGA/edit
var SHEET_ID = '1KF896f43oq1a_RF4xrJ5Cdgjw2GN6cwhg25d8Y5DbGA'; // Sugerencias_HUB_OE

function doPost(e) {
  try {
    // El Hub manda los datos como formulario normal (e.parameter), no como
    // JSON -- eso permite enviarlo via un <form> a un iframe oculto en vez de
    // fetch(), lo cual evita el bloqueo de CORS / sesion de Google que da
    // Apps Script cuando el despliegue es "Cualquier usuario de <dominio>"
    // (Workspace) en vez de publico. Se deja el JSON como respaldo por si
    // algun dia se vuelve a llamar con fetch().
    var data;
    if (e && e.parameter && Object.keys(e.parameter).length) {
      data = e.parameter;
    } else if (e && e.postData && e.postData.contents) {
      data = JSON.parse(e.postData.contents);
    } else {
      data = {};
    }
    Logger.log('doPost recibido: ' + JSON.stringify(data));

    var sheet = SpreadsheetApp.openById(SHEET_ID).getSheets()[0];

    sheet.appendRow([
      data.fecha || new Date().toISOString(),
      data.area || '',
      data.tipo || '',
      data.descripcion || '',
      data.idioma || 'es',
    ]);

    Logger.log('Fila agregada correctamente.');

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    Logger.log('ERROR en doPost: ' + err);
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// Corre esta función manualmente UNA vez (seleccionala en el desplegable de
// arriba y dale Ejecutar) para probar que el ID de la Sheet es correcto y
// que los permisos de Sheets ya están autorizados -- a diferencia de correr
// doPost a mano, esta SÍ agrega una fila real de prueba, para que quede 100%
// claro si el amarre a la Sheet funciona.
function pruebaManual() {
  doPost({
    parameter: {
      fecha: new Date().toISOString(),
      area: 'General',
      tipo: 'Otro',
      descripcion: 'Fila de prueba desde pruebaManual()',
      idioma: 'es',
    },
  });
}
