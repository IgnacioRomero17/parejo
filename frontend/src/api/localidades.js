import { pedir } from "./cliente.js";

// Catálogo cerrado en orden alfabético: [{ id, nombre }].
export function listarLocalidades() {
  return pedir("GET", "localidades");
}
