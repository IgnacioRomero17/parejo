# 06a · Registro

Imagen: `06a-registro.png` (muestra dos errores a la vez como ejemplo) · Ruta: `/registro` · Acceso: pública · HU: HU-001

## Contenido
- Panel izquierdo: "Partidos parejos." + "Registrá tu perfil, recibí recomendaciones de jugadores compatibles y dejá que el sistema forme parejas equilibradas."
- Título "Crear cuenta" y subtítulo "Todos los campos son requeridos."

## Campos
| Campo | Control | Obligatorio | Validación | Mensaje de error |
|---|---|---|---|---|
| Nombre | texto | sí | 1 a 60 caracteres | "Completá este campo para poder guardar." |
| Apellido | texto | sí | 1 a 60 caracteres | "Completá este campo para poder guardar." |
| Correo electrónico | email | sí | formato válido; único (se compara en minúsculas) | "Ingresá un correo válido." / "Este correo ya está registrado." |
| Contraseña | contraseña (oculta) | sí | 8 a 64 caracteres, al menos una letra y un número | "La contraseña debe tener entre 8 y 64 caracteres, con al menos una letra y un número." |

## Acciones
| Elemento | Resultado |
|---|---|
| Registrarse | valida todo en el backend; si está bien, crea la cuenta, inicia sesión y lleva a `/onboarding/perfil` |
| ¿Ya tenés cuenta? Iniciar sesión | `/ingresar` |

## Estados
- Inicial: campos vacíos, sin errores.
- Con errores: cada campo muestra su propio mensaje; se pueden mostrar varios a la vez.
- Enviando: botón deshabilitado mientras espera la respuesta.
