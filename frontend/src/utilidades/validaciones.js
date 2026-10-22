export const MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar.";

// Devuelve los errores con el mismo formato que el backend: { campo: [mensaje] }.
export function validarCamposRequeridos(valores) {
  const errores = {};
  for (const [campo, valor] of Object.entries(valores)) {
    if (String(valor ?? "").trim() === "") {
      errores[campo] = [MENSAJE_CAMPO_VACIO];
    }
  }
  return errores;
}
