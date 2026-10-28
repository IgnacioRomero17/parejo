import { DIAS_SEMANA } from "./disponibilidad.js";

const FORMATO_NIVEL = new Intl.NumberFormat("es-AR", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const FORMATO_FECHA_COMPACTA = new Intl.DateTimeFormat("es-AR", {
  timeZone: "America/Argentina/Cordoba",
  weekday: "short",
  day: "numeric",
  month: "short",
  year: "numeric",
});

const FORMATO_FECHA_LARGA = new Intl.DateTimeFormat("es-AR", {
  timeZone: "America/Argentina/Cordoba",
  weekday: "long",
  day: "numeric",
  month: "long",
  year: "numeric",
});

const FORMATO_PUNTAJE = new Intl.NumberFormat("es-AR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

// Niveles con coma decimal y siempre un decimal: "4,5", "4,0".
export function formatearNivel(nivel) {
  return FORMATO_NIVEL.format(nivel);
}

// Puntajes, equilibrios y promedios de la propuesta con dos decimales: "1,00", "4,75".
export function formatearPuntaje(valor) {
  return FORMATO_PUNTAJE.format(valor);
}

function sinPunto(texto) {
  return texto.replace(".", "");
}

// Partes de una fecha "AAAA-MM-DD" de la API según `formato`, como objeto { weekday, day… }.
function partesDeFecha(formato, fecha) {
  // Al mediodía de Córdoba: la medianoche UTC todavía es el día anterior en Córdoba.
  const instante = new Date(`${fecha}T12:00:00-03:00`);
  return Object.fromEntries(
    formato.formatToParts(instante).map((parte) => [parte.type, parte.value]),
  );
}

function conMayuscula(texto) {
  return `${texto.charAt(0).toUpperCase()}${texto.slice(1)}`;
}

// Fecha "AAAA-MM-DD" de la API como en títulos: "Sábado 3 de octubre".
export function formatearFechaTitulo(fecha) {
  const partes = partesDeFecha(FORMATO_FECHA_LARGA, fecha);
  return `${conMayuscula(partes.weekday)} ${partes.day} de ${partes.month}`;
}

// Fecha "AAAA-MM-DD" de la API completa, con el año: "Sábado 3 de octubre de 2026".
export function formatearFechaLarga(fecha) {
  const partes = partesDeFecha(FORMATO_FECHA_LARGA, fecha);
  return `${formatearFechaTitulo(fecha)} de ${partes.year}`;
}

// Fecha "AAAA-MM-DD" de la API como en encabezados y listas: "Sáb 3 oct 2026".
export function formatearFechaCompacta(fecha) {
  const partes = partesDeFecha(FORMATO_FECHA_COMPACTA, fecha);
  const dia = sinPunto(partes.weekday);
  // Siempre tres letras: Intl abrevia septiembre como "sept".
  const mes = sinPunto(partes.month).slice(0, 3);
  return `${conMayuscula(dia)} ${partes.day} ${mes} ${partes.year}`;
}

const FORMATO_HORA = new Intl.DateTimeFormat("es-AR", {
  timeZone: "America/Argentina/Cordoba",
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
});

// Día en Córdoba de un instante, como "AAAA-MM-DD".
function diaEnCordoba(instante) {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Argentina/Cordoba",
  }).format(instante);
}

// Fecha y hora de envío de una invitación (ISO 8601 de la API): "hoy 18:42", "ayer 09:05" o
// "Sáb 3 oct 2026 18:42", según el día en Córdoba.
export function formatearEnvio(fechaHora, ahora = new Date()) {
  const instante = new Date(fechaHora);
  const dia = diaEnCordoba(instante);
  const hora = FORMATO_HORA.format(instante);
  // Mediodía de Córdoba de hoy menos 24 horas cae siempre en el día anterior (sin horario
  // de verano en Argentina).
  const mediodiaDeHoy = new Date(`${diaEnCordoba(ahora)}T12:00:00-03:00`);
  const ayer = diaEnCordoba(
    new Date(mediodiaDeHoy.getTime() - 24 * 60 * 60 * 1000),
  );
  if (dia === diaEnCordoba(ahora)) return `hoy ${hora}`;
  if (dia === ayer) return `ayer ${hora}`;
  return `${formatearFechaCompacta(dia)} ${hora}`;
}

// Día de la semana de la API (1 = lunes … 7 = domingo) abreviado: "sáb", "mié".
export function formatearDiaAbreviado(diaSemana) {
  const dia = DIAS_SEMANA.find((opcion) => opcion.valor === String(diaSemana));
  return dia.etiqueta.slice(0, 3).toLowerCase();
}

// Franja { dia_semana, hora_inicio, hora_fin } de la API: "sáb 17:00–21:00".
export function formatearFranja(franja) {
  return `${formatearDiaAbreviado(franja.dia_semana)} ${franja.hora_inicio}–${franja.hora_fin}`;
}
