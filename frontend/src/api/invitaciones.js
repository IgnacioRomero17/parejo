import { pedir } from "./cliente.js";

// Devuelve { pendientes, respondidas }, solo de encuentros que todavía no comenzaron. Cada
// invitación: { id, estado, fecha_envio, organizador, encuentro }.
export function obtenerInvitaciones() {
  return pedir("GET", "invitaciones");
}

export function aceptarInvitacion(id) {
  return pedir("POST", `invitaciones/${id}/aceptar`);
}

export function rechazarInvitacion(id) {
  return pedir("POST", `invitaciones/${id}/rechazar`);
}
