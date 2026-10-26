import { HORAS_FRANJA, TIPOS_ENCUENTRO } from "./disponibilidad.js";
import { segunGenero } from "./perfil.js";
import { validarCamposRequeridos } from "./validaciones.js";

export const LUGARES_POR_ENCUENTRO = 4;

export const DURACIONES = [60, 90, 120].map((minutos) => ({
  valor: String(minutos),
  etiqueta: `${minutos} minutos`,
}));

// Hasta las 22:30: es la última hora que, con la duración mínima (60 minutos), permite
// terminar a las 23:30. El backend igual valida que el fin no pase de las 23:30.
const ULTIMA_HORA_INICIO = "22:30";
export const HORAS_INICIO = HORAS_FRANJA.filter(
  (hora) => hora.valor <= ULTIMA_HORA_INICIO,
);

export const ESTADOS_ENCUENTRO = {
  CREADO: { etiqueta: "Creado", color: "gris" },
  BUSCANDO_PARTICIPANTES: { etiqueta: "Buscando participantes", color: "azul" },
  COMPLETO: { etiqueta: "Completo", color: "lima" },
  PROPUESTA_GENERADA: { etiqueta: "Propuesta generada", color: "lima" },
};

export const ESTADOS_INVITACION = {
  PENDIENTE: { etiqueta: "Pendiente", color: "amarillo" },
  ACEPTADA: { etiqueta: "Aceptada", color: "verde" },
  RECHAZADA: { etiqueta: "Rechazada", color: "rojo" },
};

export function etiquetaTipoEncuentro(tipo) {
  return TIPOS_ENCUENTRO.find((opcion) => opcion.valor === tipo)?.etiqueta;
}

export function textoJugadores(cantidad) {
  return cantidad === 1 ? "1 jugador" : `${cantidad} jugadores`;
}

export function textoLugaresLibres(cantidad) {
  return cantidad === 1 ? "1 lugar libre" : `${cantidad} lugares libres`;
}

export function textoLugaresRestantes(cantidad) {
  return cantidad === 1 ? "1 lugar restante" : `${cantidad} lugares restantes`;
}

export function textoInvitacionesEnviadas(cantidad) {
  return cantidad === 1
    ? "1 invitación enviada"
    : `${cantidad} invitaciones enviadas`;
}

export function textoSeleccionados(cantidad) {
  return cantidad === 1 ? "1 seleccionado" : `${cantidad} seleccionados`;
}

export function textoPendientes(cantidad) {
  return cantidad === 1 ? "1 pendiente" : `${cantidad} pendientes`;
}

// Aviso de la pantalla 12 al enviar: "Invitación enviada." / "3 invitaciones enviadas.".
export function avisoInvitacionesEnviadas(cantidad) {
  return cantidad === 1
    ? "Invitación enviada."
    : `${textoInvitacionesEnviadas(cantidad)}.`;
}

// Pantalla 12, al llegar al límite de selección.
export function textoLimiteSeleccion(lugaresLibres) {
  const queda = lugaresLibres === 1 ? "queda" : "quedan";
  return `Como ${queda} ${textoLugaresLibres(lugaresLibres)}, podés seleccionar ${textoJugadores(lugaresLibres)}. Para elegir a otro, quitá la selección actual.`;
}

// "Federico Luna", "Federico Luna y Bruno Castro", "Ana Paz, Federico Luna y Bruno Castro".
export function listarNombres(jugadores) {
  const nombres = jugadores.map(
    (jugador) => `${jugador.nombre} ${jugador.apellido}`,
  );
  if (nombres.length <= 1) return nombres.join("");
  return `${nombres.slice(0, -1).join(", ")} y ${nombres.at(-1)}`;
}

// Cómo se nombra al organizador de una invitación recibida, según el género de su perfil.
export function rolOrganizador(genero) {
  return segunGenero(
    genero,
    "Organizadora",
    "Organizador",
    "Organiza el encuentro",
  );
}

// Encuentro completo, visto por quien aceptó la invitación (pantallas 08 y 13).
export function textoEsperandoParejas(genero) {
  return segunGenero(
    genero,
    "Esperando que la organizadora forme las parejas.",
    "Esperando que el organizador forme las parejas.",
    "Esperando que se inicie la formación automática de parejas.",
  );
}

// Pantalla 11: "completar el lugar libre" / "completar los 3 lugares libres".
export function textoLugaresACompletar(cantidad) {
  return cantidad === 1 ? "el lugar libre" : `los ${cantidad} lugares libres`;
}

// Fecha de hoy en Córdoba como "AAAA-MM-DD", el formato de <input type="date">.
export function hoyEnCordoba(ahora = new Date()) {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Argentina/Cordoba",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(ahora);
}

// Un encuentro se puede crear hasta 60 días después de hoy (HU-006); el backend lo valida igual.
const DIAS_MAXIMOS_ANTICIPACION = 60;

// Última fecha permitida para un encuentro, "AAAA-MM-DD": hoy en Córdoba + 60 días.
export function fechaMaximaEncuentro(ahora = new Date()) {
  // Se suman días sobre la fecha ya resuelta en Córdoba, en UTC para que no influya la zona
  // horaria del navegador.
  const fecha = new Date(`${hoyEnCordoba(ahora)}T00:00:00Z`);
  fecha.setUTCDate(fecha.getUTCDate() + DIAS_MAXIMOS_ANTICIPACION);
  return fecha.toISOString().slice(0, 10);
}

// Valores iniciales de la pantalla 09: la localidad del jugador precargada y el resto vacío.
export function formularioEncuentro(perfilDeportivo) {
  return {
    fecha: "",
    hora_inicio: "",
    duracion_minutos: "",
    localidad:
      perfilDeportivo.localidad === null
        ? ""
        : String(perfilDeportivo.localidad),
    tipo_encuentro: "",
    ubicacion: "",
  };
}

function numeroONull(texto) {
  return texto === "" ? null : Number(texto);
}

// Inversa de formularioEncuentro, con el formato que espera `POST encuentros`.
export function encuentroDeFormulario(valores) {
  return {
    fecha: valores.fecha || null,
    hora_inicio: valores.hora_inicio || null,
    duracion_minutos: numeroONull(valores.duracion_minutos),
    localidad: numeroONull(valores.localidad),
    ubicacion: valores.ubicacion.trim() || null,
    tipo_encuentro: valores.tipo_encuentro || null,
  };
}

// En el navegador solo se avisan los campos vacíos; fechas pasadas y el horario de fin los
// valida el backend.
export function validarEncuentro(valores) {
  return validarCamposRequeridos(valores);
}
