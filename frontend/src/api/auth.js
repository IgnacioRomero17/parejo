import { pedir } from "./cliente.js";

export function pedirCsrf() {
  return pedir("GET", "auth/csrf");
}

// Sin reacciones: un 401 acá solo significa que no hay sesión iniciada.
export function obtenerUsuarioActual() {
  return pedir("GET", "auth/yo", undefined, { reaccionar: false });
}

export function ingresar({ email, contrasena }) {
  return pedir("POST", "auth/ingresar", { email, contrasena });
}

export function salir() {
  return pedir("POST", "auth/salir");
}

export function solicitarRecuperacion({ email }) {
  return pedir("POST", "auth/recuperar", { email });
}

// Devuelve { email } si el enlace sirve; con un enlace inválido o usado responde 400.
export function validarEnlaceRecuperacion(uid, token) {
  return pedir(
    "GET",
    `auth/recuperar/${encodeURIComponent(uid)}/${encodeURIComponent(token)}`,
  );
}

export function confirmarRecuperacion({ uid, token, contrasena }) {
  return pedir("POST", "auth/recuperar/confirmar", { uid, token, contrasena });
}

export function registrarse({ nombre, apellido, email, contrasena }) {
  return pedir("POST", "auth/registro", {
    nombre,
    apellido,
    email,
    contrasena,
  });
}
