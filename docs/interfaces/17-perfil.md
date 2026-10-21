# 17 · Perfil del usuario

Imagen: `17-perfil.png` (con cambios sin guardar) · Ruta: `/perfil` · Acceso: sesión + onboarding · HU: HU-004, HU-005

## Contenido
- Título "Mi perfil" y texto "Actualizá tus datos cuando quieras. Los cambios se usan en las próximas recomendaciones."
- Arriba a la derecha: iniciales, nombre, correo y etiqueta Disponible / No disponible.

### Datos personales ("Los datos con los que te registraste.")
- Nombre y Apellido: editables (1 a 60 caracteres).
- Correo electrónico: **solo lectura** (no hay HU para cambiarlo).
- Contraseña: puntos fijos y enlace "Cambiar contraseña", que inicia el flujo de recuperación (HU-003): llama a `POST auth/recuperar` con el correo del usuario y lleva a `/recuperar/enviado` (pantalla 06d), sin cerrar la sesión.

### Perfil deportivo
Texto: "Tu nivel y tu localidad se usan para calcular la compatibilidad; tu lado preferido, para el equilibrio entre parejas." Mismos campos y validaciones que la pantalla 07a; el selector de nivel muestra el valor guardado.

### Disponibilidad y preferencias
Texto: "Define en qué encuentros aparecés como jugador compatible." Mismas franjas, preferencias e interruptor que la pantalla 07b. Texto del interruptor: "Si lo desactivás, el sistema deja de recomendarte a otros organizadores."

### Cuenta
- "Cerrar sesión" — "Salís de tu cuenta en este dispositivo. Tus datos se conservan." Botón "Cerrar sesión" → cierra la sesión y lleva a `/`.

## Guardado
- Un solo guardado para toda la pantalla. Al modificar cualquier campo aparece la barra inferior oscura: "Tenés cambios sin guardar" con "Descartar" (vuelve a los valores guardados) y "Guardar cambios".
- Guardar valida todo en el backend; si hay errores se marcan en cada campo y no se guarda nada.
- Éxito: la barra desaparece y aparece el aviso "Cambios guardados correctamente."
