import { pedir } from "./cliente.js";

export function obtenerPerfil() {
  return pedir("GET", "perfil");
}

// Recibe solo las secciones que cambian: { datos_personales?, perfil_deportivo? }.
export function actualizarPerfil(secciones) {
  return pedir("PATCH", "perfil", secciones);
}
