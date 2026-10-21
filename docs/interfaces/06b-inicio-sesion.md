# 06b · Inicio de sesión

Imagen: `06b-inicio-sesion.png` (estado con error) · Ruta: `/ingresar` · Acceso: pública · HU: HU-002

## Contenido
- Panel izquierdo: "Partidos parejos." + "Ingresá para organizar un encuentro o responder tus invitaciones."
- Título "Iniciar sesión".

## Campos
| Campo | Control | Obligatorio |
|---|---|---|
| Correo electrónico | email | sí |
| Contraseña | contraseña (oculta) | sí |

## Acciones
| Elemento | Resultado |
|---|---|
| Ingresar | si las credenciales son correctas: `/inicio`, o el paso de onboarding pendiente |
| ¿Olvidaste tu contraseña? | `/recuperar` |
| ¿No tenés cuenta? Registrate | `/registro` |

## Estados
- Credenciales incorrectas **o** correo no registrado: recuadro de error arriba del formulario con "Las credenciales ingresadas no son válidas." Mismo mensaje en ambos casos.
- Campo vacío: "Completá este campo para poder guardar." debajo del campo.
- Enviando: botón deshabilitado.
