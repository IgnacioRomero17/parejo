# 06e · Recuperación de contraseña · Paso 3 de 3

Imagen: `06e-recuperacion-nueva.png` · Ruta: `/recuperar/:uid/:token` (enlace del correo) · Acceso: pública con enlace válido · HU: HU-003

## Contenido
- Panel izquierdo: "Recuperá tu acceso." + "Definí una nueva contraseña y volvé a ingresar."
- "PASO 3 DE 3", título "Nueva contraseña", "Cuenta: **{correo}**". Al entrar se valida el enlace con `GET auth/recuperar/{uid}/{token}`, que devuelve el correo.

## Campos
| Campo | Control | Obligatorio | Validación | Texto de ayuda / error |
|---|---|---|---|---|
| Nueva contraseña | contraseña (oculta) | sí | igual que en el registro | ayuda: "Entre 8 y 64 caracteres, con al menos una letra y un número." En error, el mismo texto en rojo. |

## Acciones
| Elemento | Resultado |
|---|---|
| Guardar e iniciar sesión | guarda la contraseña, inicia sesión y lleva a `/inicio` (o al onboarding pendiente) |

## Estados
- Enlace inválido o ya usado (no dibujado): en lugar del formulario, título "El enlace no es válido", texto "Puede que ya lo hayas usado. Pedí uno nuevo." y botón "Pedir un nuevo enlace" a `/recuperar`.
