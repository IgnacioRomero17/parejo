import { pedir } from "./cliente.js";

export function obtenerPerfil() {
  return pedir("GET", "perfil");
}

// Recibe solo las secciones que cambian: { datos_personales?, perfil_deportivo?, disponibilidad? }.
export function actualizarPerfil(secciones) {
  return pedir("PATCH", "perfil", secciones);
}
