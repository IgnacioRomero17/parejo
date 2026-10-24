import { pedir } from "./cliente.js";

// Recibe las condiciones { fecha, hora_inicio, duracion_minutos, localidad, ubicacion,
// tipo_encuentro } y devuelve el encuentro creado, con su id, estado y confirmados.
export function crearEncuentro(condiciones) {
  return pedir("POST", "encuentros", condiciones);
}

export function obtenerEncuentro(id) {
  return pedir("GET", `encuentros/${id}`);
}
