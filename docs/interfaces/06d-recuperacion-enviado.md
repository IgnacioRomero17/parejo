# 06d · Recuperación de contraseña · Paso 2 de 3

Imagen: `06d-recuperacion-enviado.png` · Ruta: `/recuperar/enviado` · Acceso: pública · HU: HU-003

## Contenido
- Panel izquierdo igual al paso 1.
- "PASO 2 DE 3", ícono de sobre, título "Revisá tu correo".
- Texto: "Te enviamos un enlace a **{correo}**. Abrilo para definir tu nueva contraseña."
- Recuadro informativo: "¿No lo encontrás? Revisá la carpeta de correo no deseado."

## Acciones
| Elemento | Resultado |
|---|---|
| Volver a iniciar sesión | `/ingresar` |
| Usar otro correo | `/recuperar` |

## Notas
- No hay botón de reenviar enlace (no está en la HU).
- Si se entra a esta ruta sin un correo previo, se redirige a `/recuperar`.

## Correo que se envía
- Asunto: "Restablecé tu contraseña de parejo".
- Cuerpo: saludo con el nombre, el enlace a `/recuperar/:uid/:token` y una línea que diga que, si no lo pidió, puede ignorar el correo.
