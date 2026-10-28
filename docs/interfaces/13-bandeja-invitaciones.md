# 13 · Bandeja de invitaciones

Imagen: `13-bandeja-invitaciones.png` · Ruta: `/invitaciones` · Acceso: sesión + onboarding · HU: HU-008

## Contenido
- Título "Invitaciones recibidas" y texto "Al aceptar una invitación pasás a ser participante confirmado de ese encuentro."

### "Pendientes · N"
Tarjeta por invitación pendiente de encuentros que todavía no comenzaron, más reciente primero:
- Iniciales, "{organizador} te invitó a un encuentro", "Organizador · enviada {hoy/ayer/fecha} {hora}", etiqueta Pendiente.
- Datos: Fecha, Hora, Duración, Tipo, Lugar (localidad · dirección) y casilleros de lugares ocupados.
- Botones "Rechazar" y "Aceptar invitación".

### "Respondidas"
Tarjetas de invitaciones aceptadas o rechazadas de encuentros que todavía no pasaron:
- Organizador, fecha · hora · duración · localidad · dirección, etiqueta Aceptada / Rechazada.
- Aceptada: estado actual del encuentro (por ejemplo "Completo · Esperando que la organizadora forme las parejas."; con propuesta: enlace "Ver propuesta").
- Rechazada: "Rechazaste esta invitación."

## Acciones
| Elemento | Resultado |
|---|---|
| Aceptar invitación | invitación Aceptada, el jugador pasa a participante confirmado; si es el 4.º, el encuentro pasa a Completo. Aviso "Te sumaste al encuentro." |
| Rechazar | invitación Rechazada. Aviso "Rechazaste la invitación." |

## Estados
- Sin pendientes: "No tenés invitaciones pendientes."
- Sin ninguna invitación: estado vacío con el mismo patrón que el panel 08. Ícono de sobre en círculo azul y título "Todavía no recibiste invitaciones". Si el usuario no está disponible: "Para recibirlas, activá «Disponible para recibir invitaciones» en tu perfil." y botón "Ir a mi perfil" → /perfil. Si está disponible: "Estás disponible para recibir invitaciones. Cuando te inviten a un encuentro, van a aparecer acá.", sin botón.
- Una invitación pendiente siempre tiene su lugar reservado (los lugares libres descuentan las pendientes), así que aceptar nunca supera los 4 participantes. El backend igual lo verifica.
