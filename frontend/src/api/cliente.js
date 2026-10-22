const PREFIJO = "/api/";
const METODOS_QUE_ESCRIBEN = ["POST", "PUT", "PATCH", "DELETE"];
const MENSAJE_SIN_CONEXION =
  "No pudimos conectar con el servidor. Probá de nuevo en unos minutos.";
const MENSAJE_INESPERADO = "Algo salió mal. Probá de nuevo en unos minutos.";

export class ErrorApi extends Error {
  constructor({ estado = 0, errores = {}, detalle = "", onboarding = null }) {
    super(detalle || "Error de la API");
    this.name = "ErrorApi";
    this.estado = estado;
    this.errores = errores;
    this.detalle = detalle;
    this.onboarding = onboarding;
  }
}

const reacciones = {
  alNoAutenticado: () => {},
  alFaltarOnboarding: () => {},
};

export function configurarReacciones({ alNoAutenticado, alFaltarOnboarding }) {
  if (alNoAutenticado) reacciones.alNoAutenticado = alNoAutenticado;
  if (alFaltarOnboarding) reacciones.alFaltarOnboarding = alFaltarOnboarding;
}

function leerCookie(nombre) {
  const par = document.cookie
    .split("; ")
    .find((cookie) => cookie.startsWith(`${nombre}=`));
  return par ? decodeURIComponent(par.slice(nombre.length + 1)) : "";
}

async function leerCuerpo(respuesta) {
  const texto = await respuesta.text();
  if (!texto) return null;
  try {
    return JSON.parse(texto);
  } catch {
    return null;
  }
}

/**
 * Hace un pedido a la API y devuelve el cuerpo JSON (o null si no tiene).
 * Lanza ErrorApi con los errores de campo o el detalle que mande el backend.
 * Con `reaccionar: false` no dispara las reacciones de 401 y 403 con onboarding.
 */
export async function pedir(metodo, ruta, datos, { reaccionar = true } = {}) {
  const cabeceras = { Accept: "application/json" };
  if (datos !== undefined) cabeceras["Content-Type"] = "application/json";
  if (METODOS_QUE_ESCRIBEN.includes(metodo)) {
    cabeceras["X-CSRFToken"] = leerCookie("csrftoken");
  }

  let respuesta;
  try {
    respuesta = await fetch(`${PREFIJO}${ruta}`, {
      method: metodo,
      credentials: "include",
      headers: cabeceras,
      body: datos === undefined ? undefined : JSON.stringify(datos),
    });
  } catch {
    throw new ErrorApi({ detalle: MENSAJE_SIN_CONEXION });
  }

  const cuerpo = await leerCuerpo(respuesta);
  if (respuesta.ok) return cuerpo;

  const errores = cuerpo?.errores ?? {};
  const sinMensajes = Object.keys(errores).length === 0 && !cuerpo?.detalle;
  const error = new ErrorApi({
    estado: respuesta.status,
    errores,
    detalle: sinMensajes ? MENSAJE_INESPERADO : (cuerpo?.detalle ?? ""),
    onboarding: cuerpo?.onboarding ?? null,
  });
  if (reaccionar && error.estado === 401) reacciones.alNoAutenticado(error);
  if (reaccionar && error.estado === 403 && error.onboarding) {
    reacciones.alFaltarOnboarding(error.onboarding);
  }
  throw error;
}
