import { validarCamposRequeridos } from "./validaciones.js";

export const DIAS_SEMANA = [
  { valor: "1", etiqueta: "Lunes" },
  { valor: "2", etiqueta: "Martes" },
  { valor: "3", etiqueta: "Miércoles" },
  { valor: "4", etiqueta: "Jueves" },
  { valor: "5", etiqueta: "Viernes" },
  { valor: "6", etiqueta: "Sábado" },
  { valor: "7", etiqueta: "Domingo" },
];

export const TIPOS_ENCUENTRO = [
  { valor: "RECREATIVO", etiqueta: "Recreativo" },
  { valor: "COMPETITIVO", etiqueta: "Competitivo" },
  { valor: "INDIFERENTE", etiqueta: "Indiferente" },
];

export const LADOS_PREFERIDOS = [
  { valor: "DRIVE", etiqueta: "Drive" },
  { valor: "REVES", etiqueta: "Revés" },
  { valor: "INDIFERENTE", etiqueta: "Indiferente" },
];

// Horas de las franjas: de 08:00 a 23:30, en pasos de 30 minutos (HU-005).
const PRIMERA_HORA = 8;
export const HORAS_FRANJA = Array.from({ length: 32 }, (_, posicion) => {
  const horas = String(PRIMERA_HORA + Math.floor(posicion / 2)).padStart(
    2,
    "0",
  );
  const hora = `${horas}:${posicion % 2 === 0 ? "00" : "30"}`;
  return { valor: hora, etiqueta: hora };
});

const CAMPOS_FRANJA = ["dia_semana", "hora_inicio", "hora_fin"];

// Cada fila lleva una clave propia, estable mientras se edita: las filas se agregan y se
// quitan, así que la posición no sirve como `key` ni para ubicar sus errores.
let ultimaClave = 0;
function nuevaClave() {
  ultimaClave += 1;
  return `franja-${ultimaClave}`;
}

export function franjaVacia() {
  return { clave: nuevaClave(), dia_semana: "", hora_inicio: "", hora_fin: "" };
}

function franjaSinDatos(franja) {
  return CAMPOS_FRANJA.every((campo) => franja[campo] === "");
}

// Pasa la sección `disponibilidad` de la API a los valores del formulario: "" es "sin elegir".
// Con `conFilaVacia`, si no hay franjas guardadas se arranca con una fila vacía (pantalla 07b).
export function formularioDisponibilidad(
  disponibilidad,
  { conFilaVacia = false } = {},
) {
  const franjas = disponibilidad.franjas.map((franja) => ({
    clave: nuevaClave(),
    dia_semana: String(franja.dia_semana),
    hora_inicio: franja.hora_inicio,
    hora_fin: franja.hora_fin,
  }));
  return {
    franjas: franjas.length === 0 && conFilaVacia ? [franjaVacia()] : franjas,
    tipo_encuentro: disponibilidad.tipo_encuentro ?? "",
    lado_preferido: disponibilidad.lado_preferido ?? "",
    disponible_para_invitaciones: disponibilidad.disponible_para_invitaciones,
  };
}

function franjasEnviadas(valores) {
  return valores.franjas.filter((franja) => !franjaSinDatos(franja));
}

// Inversa de formularioDisponibilidad, con el formato que espera `PATCH perfil`.
// Las filas sin ningún dato no se envían.
export function disponibilidadDeFormulario(valores) {
  return {
    franjas: franjasEnviadas(valores).map((franja) => ({
      dia_semana: Number(franja.dia_semana),
      hora_inicio: franja.hora_inicio,
      hora_fin: franja.hora_fin,
    })),
    tipo_encuentro: valores.tipo_encuentro || null,
    lado_preferido: valores.lado_preferido || null,
    disponible_para_invitaciones: valores.disponible_para_invitaciones,
  };
}

// Claves de las filas que se envían, en el orden en que van en `franjas`.
export function clavesEnviadas(valores) {
  return franjasEnviadas(valores).map((franja) => franja.clave);
}

// El backend marca los errores de cada franja por su posición en la lista enviada
// ({ "1": { hora_fin: [...] } }); acá pasan a la clave de su fila.
export function erroresDeDisponibilidad(errores, claves) {
  const { franjas, ...resto } = errores ?? {};
  const porFila = {};
  for (const [posicion, erroresFila] of Object.entries(franjas ?? {})) {
    const clave = claves[Number(posicion)];
    if (clave) porFila[clave] = erroresFila;
  }
  return Object.keys(porFila).length > 0
    ? { ...resto, franjas: porFila }
    : resto;
}

// En el navegador solo se avisan los campos vacíos: de las filas a medio completar y de las
// preferencias. El resto (horarios, duración, franjas para estar disponible) lo valida el backend.
export function validarDisponibilidad(valores) {
  const porFila = {};
  for (const franja of franjasEnviadas(valores)) {
    const erroresFila = validarCamposRequeridos({
      dia_semana: franja.dia_semana,
      hora_inicio: franja.hora_inicio,
      hora_fin: franja.hora_fin,
    });
    if (Object.keys(erroresFila).length > 0)
      porFila[franja.clave] = erroresFila;
  }
  const errores = validarCamposRequeridos({
    tipo_encuentro: valores.tipo_encuentro,
    lado_preferido: valores.lado_preferido,
  });
  return Object.keys(porFila).length > 0
    ? { ...errores, franjas: porFila }
    : errores;
}
