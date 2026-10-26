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

// Devuelve { lugares_libres, suficientes, recomendados }, en el orden del motor. Cada
// recomendado: { id, nombre, apellido, localidad, nivel, franja }.
export function obtenerRecomendados(id) {
  return pedir("GET", `encuentros/${id}/recomendados`);
}
