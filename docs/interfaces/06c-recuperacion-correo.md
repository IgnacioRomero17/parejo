# 06c · Recuperación de contraseña · Paso 1 de 3

Imagen: `06c-recuperacion-correo.png` (estado con error) · Ruta: `/recuperar` · Acceso: pública · HU: HU-003

## Contenido
- Panel izquierdo: "Recuperá tu acceso." + "Te enviamos un enlace a tu correo para que definas una nueva contraseña."
- "PASO 1 DE 3", título "¿Olvidaste tu contraseña?", texto "Ingresá el correo de tu cuenta y te enviaremos un enlace para restablecerla."

## Campos
| Campo | Control | Obligatorio | Mensaje de error |
|---|---|---|---|
| Correo electrónico | email | sí | "La cuenta no existe. Revisá el correo ingresado." si no está registrado |

## Acciones
| Elemento | Resultado |
|---|---|
| Enviar enlace | si el correo existe: envía el correo y lleva a `/recuperar/enviado` (pasando el correo para mostrarlo) |
| Volver a iniciar sesión | `/ingresar` |
