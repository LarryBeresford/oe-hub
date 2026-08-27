/**
 * Ideas y sugerencias — OE MLM Hub
 * ---------------------------------
 * Recibe las sugerencias enviadas desde la sección "Ideas y sugerencias"
 * del Hub (index.html > submitSuggestion()) y las guarda como fila nueva
 * en un Google Sheet.
 *
 * COMO DESPLEGAR (una sola vez):
 *   1. Crea un Google Sheet nuevo (ej. "OE Hub — Ideas y sugerencias").
 *   2. En esa hoja, agrega esta fila de encabezados en la fila 1:
 *      Fecha | Área | Tipo | Descripción | Idioma
 *   3. Extensiones > Apps Script.
 *   4. Borra el contenido de Code.gs y pega este archivo completo.
 *   5. Guarda el proyecto (ej. "Ideas Sugerencias OE Hub").
 *   6. Implementar > Nueva implementación > tipo "Aplicación web".
 *        - Ejecutar como: Yo (tu cuenta)
 *        - Quién tiene acceso: Cualquier usuario
 *   7. Autoriza los permisos que pida Google.
 *   8. Copia la URL que te da ("URL de la aplicación web").
 *   9. Pégala en oe-hub/index.html, en la constante SUGGESTIONS_ENDPOINT
 *      (busca "SUGGESTIONS_ENDPOINT" cerca de la función submitSuggestion()).
 *  10. git add, commit, push — listo, el formulario ya cae en el Sheet real.
 *
 * Si alguna vez necesitas cambiar de Sheet o re-desplegar, usa
 * "Implementar > Administrar implementaciones > editar" para mantener
 * la misma URL, o genera una nueva implementación y actualiza la constante.
 */

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

    sheet.appendRow([
      data.fecha || new Date().toISOString(),
      data.area || '',
      data.tipo || '',
      data.descripcion || '',
      data.idioma || 'es',
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: String(err) }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
