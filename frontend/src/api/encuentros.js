import { pedir } from "./cliente.js";

// Recibe las condiciones { fecha, hora_inicio, duracion_minutos, localidad, ubicacion,
// tipo_encuentro } y devuelve el encuentro creado, con su id, estado y confirmados.
export function crearEncuentro(condiciones) {
  return pedir("POST", "encuentros", condiciones);
}

// Devuelve el encuentro con `lugares_libres`, `participantes` y, solo para el organizador,
// `invitaciones` (en orden de envío).
export function obtenerEncuentro(id) {
  return pedir("GET", `encuentros/${id}`);
}

// Recibe los ids de los jugadores elegidos y devuelve las invitaciones creadas.
export function enviarInvitaciones(id, usuarios) {
  return pedir("POST", `encuentros/${id}/invitaciones`, { usuarios });
}

// Evalúa las 3 combinaciones, forma las parejas y genera la propuesta. Devuelve la propuesta:
// { encuentro, combinacion_elegida, puntaje_equilibrio, combinaciones }.
export function formarParejas(id) {
  return pedir("POST", `encuentros/${id}/formar-parejas`);
}

// Devuelve la propuesta ya generada, con el mismo formato que formarParejas. Responde 409 si
// el encuentro todavía no tiene propuesta.
export function obtenerPropuesta(id) {
  return pedir("GET", `encuentros/${id}/propuesta`);
}

// Devuelve { lugares_libres, suficientes, recomendados }, en el orden del motor. Cada
// recomendado: { id, nombre, apellido, localidad, nivel, franja }.
export function obtenerRecomendados(id) {
  return pedir("GET", `encuentros/${id}/recomendados`);
}
