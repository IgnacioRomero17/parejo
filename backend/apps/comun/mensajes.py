MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar."
MENSAJE_LARGO_MAXIMO = "Usá como máximo {max_length} caracteres."
MENSAJE_OPCION_INVALIDA = "Elegí una opción del listado."

# Mensajes de los campos de DRF, para pasar como `error_messages`.
MENSAJES_CAMPO_OBLIGATORIO = {
    "required": MENSAJE_CAMPO_VACIO,
    "blank": MENSAJE_CAMPO_VACIO,
    "null": MENSAJE_CAMPO_VACIO,
}
MENSAJES_OPCION = {**MENSAJES_CAMPO_OBLIGATORIO, "invalid_choice": MENSAJE_OPCION_INVALIDA}
