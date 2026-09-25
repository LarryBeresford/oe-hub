// api/migrar-imagen.js -- funcion serverless de Vercel (se despliega sola al
// hacer "git push", no requiere Node instalado en tu laptop).
//
// Recibe POST { url, nombre } desde herramientas/boletines_oe.html (pestana
// "Migrar fotos") y:
//   - Si "url" ya es de ImgBB           -> responde { skip: true }.
//   - Si es de Imgur o de Google Drive  -> la descarga AQUI (del lado del
//     servidor, sin la restriccion de CORS que sí bloquea a Google Drive
//     cuando se intenta leer directo desde el navegador) y la vuelve a
//     subir a ImgBB usando la API key guardada en la variable de entorno
//     IMGBB_API_KEY de este proyecto en Vercel (Settings -> Environment
//     Variables) -- la key NUNCA se manda al navegador.
//   - Si esta vacia o no se reconoce    -> responde { skip: true }.
//
// Es el equivalente en JS de motor-oe-v2/scripts/fotos/drive_a_imgbb.py
// (mismas reglas de clasificacion / mismo manejo de la pantalla de "no se
// puede escanear por virus" de Drive en archivos grandes).

const YA_EN_IMGBB = ["i.ibb.co", "ibb.co"];
const ORIGEN_IMGUR = ["i.imgur.com", "imgur.com"];
const ORIGEN_DRIVE = ["drive.google.com"];
const RE_DRIVE_ID = /(?:\/file\/d\/|[?&]id=|\/d\/)([a-zA-Z0-9_-]{20,})/;

function clasificar(url) {
  if (!url) return null;
  url = String(url).trim();
  if (!url) return null;
  if (YA_EN_IMGBB.some((h) => url.indexOf(h) !== -1)) return "imgbb";
  if (ORIGEN_DRIVE.some((h) => url.indexOf(h) !== -1) || ORIGEN_IMGUR.some((h) => url.indexOf(h) !== -1)) return "migrar";
  return null;
}

function extraerIdDrive(url) {
  const m = url.match(RE_DRIVE_ID);
  return m ? m[1] : null;
}

async function descargarDeDrive(fileId) {
  const base = "https://drive.google.com/uc?export=download&id=" + fileId;
  let resp = await fetch(base, { redirect: "follow" });
  const contentType = resp.headers.get("content-type") || "";
  if (contentType.indexOf("text/html") !== -1) {
    const html = await resp.text();
    const m = html.match(/confirm=([0-9A-Za-z_-]+)/) || html.match(/name="confirm"\s+value="([0-9A-Za-z_-]+)"/);
    if (!m) {
      throw new Error(
        "Google Drive regreso una pagina HTML en vez de la foto (revisa que el " +
        "archivo este compartido como 'Cualquiera con el enlace puede ver')."
      );
    }
    resp = await fetch(base + "&confirm=" + m[1], { redirect: "follow" });
  }
  if (!resp.ok) throw new Error("HTTP " + resp.status + " descargando de Drive");
  return Buffer.from(await resp.arrayBuffer());
}

async function descargarGenerico(url) {
  const resp = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0" } });
  if (!resp.ok) throw new Error("HTTP " + resp.status + " descargando " + url);
  return Buffer.from(await resp.arrayBuffer());
}

async function descargarImagen(url) {
  if (ORIGEN_DRIVE.some((h) => url.indexOf(h) !== -1)) {
    const fileId = extraerIdDrive(url);
    if (!fileId) throw new Error("no pude extraer el ID de Drive de: " + url);
    return descargarDeDrive(fileId);
  }
  return descargarGenerico(url);
}

async function subirAImgbb(buffer, nombre, apiKey) {
  const form = new FormData();
  form.append("key", apiKey);
  form.append("name", nombre);
  form.append("image", new Blob([buffer]), nombre + ".jpg");
  const resp = await fetch("https://api.imgbb.com/1/upload", { method: "POST", body: form });
  const payload = await resp.json();
  if (!payload.success) {
    throw new Error((payload.error && payload.error.message) || "error desconocido de ImgBB");
  }
  return payload.data.url;
}

function slug(texto) {
  return String(texto).replace(/[^\w\s-]/gu, "").trim().replace(/[\s-]+/g, "_");
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "Metodo no permitido" });
    return;
  }
  const { url, nombre } = req.body || {};
  const estado = clasificar(url);
  if (estado === null) {
    res.status(200).json({ skip: true, razon: "vacio o no reconocido" });
    return;
  }
  if (estado === "imgbb") {
    res.status(200).json({ skip: true, razon: "ya esta en ImgBB" });
    return;
  }
  const apiKey = process.env.IMGBB_API_KEY;
  if (!apiKey) {
    res.status(500).json({ error: "Falta IMGBB_API_KEY en las variables de entorno de este proyecto en Vercel." });
    return;
  }
  try {
    const buffer = await descargarImagen(url);
    const link = await subirAImgbb(buffer, slug(nombre || "foto"), apiKey);
    res.status(200).json({ url: link });
  } catch (e) {
    res.status(200).json({ error: String((e && e.message) || e) });
  }
};
