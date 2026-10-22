import { pedir } from "./cliente.js";

export function pedirCsrf() {
  return pedir("GET", "auth/csrf");
}

// Sin reacciones: un 401 acá solo significa que no hay sesión iniciada.
export function obtenerUsuarioActual() {
  return pedir("GET", "auth/yo", undefined, { reaccionar: false });
}

export function registrarse({ nombre, apellido, email, contrasena }) {
  return pedir("POST", "auth/registro", {
    nombre,
    apellido,
    email,
    contrasena,
  });
}
