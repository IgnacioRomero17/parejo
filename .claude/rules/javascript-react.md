---
paths:
  - "frontend/**/*.{js,jsx}"
---

# Convenciones de JavaScript y React

## Versión y herramientas
- Node.js LTS, proyecto creado con la plantilla `react` de Vite (JavaScript, sin TypeScript).
- oxlint de la plantilla de Vite y Prettier. El código se entrega sin advertencias.
- Dependencias permitidas: `react`, `react-dom`, `react-router-dom`, `lucide-react` (íconos), `@fontsource/inter` y `@fontsource/space-grotesk`. Las de testing, en su regla. Ninguna otra sin consultar (sin axios, Redux, librerías de formularios, de componentes ni de estilos).

## Estructura de `frontend/src/`
```
main.jsx            # monta la app
App.jsx             # proveedores + rutas
rutas.jsx           # tabla de rutas (las de docs/interfaces/README.md)
api/                # cliente.js + un archivo por recurso (auth.js, perfil.js, encuentros.js, invitaciones.js, localidades.js)
contexto/           # SesionContexto.jsx (usuario logueado)
paginas/            # una por pantalla: Registro.jsx, CrearEncuentro.jsx, Propuesta.jsx…
componentes/        # piezas reutilizables: SelectorNivel.jsx, TarjetaEncuentro.jsx, EtiquetaEstado.jsx…
hooks/              # hooks propios (useCargarDatos.js…)
utilidades/         # formato.js (fechas, horas, niveles con coma), validaciones.js
estilos/            # variables.css (tokens), base.css
```
Cada página o componente tiene al lado su `.module.css` con el mismo nombre.

## Componentes
- Solo componentes de función con hooks. Un componente por archivo, `PascalCase.jsx`, con nombre en español.
- Props desestructuradas en la firma. Componentes chicos: si uno pasa de unas 150 líneas, dividirlo.
- Las páginas cargan datos y manejan estados; los componentes reciben datos por props y avisan con callbacks (`onSeleccionar`, `onGuardar`).
- Listas con `key` estable (el id), nunca el índice.

## Datos y API
- **Ningún componente llama a `fetch` directo:** todo pasa por `src/api/`.
- `cliente.js` centraliza: prefijo `/api/`, `credentials: "include"`, cabecera `X-CSRFToken` en métodos que escriben, JSON en ambos sentidos y conversión de errores (`{"errores": {...}}` o `{"detalle": "..."}`) a un objeto de error común.
- Al iniciar la app se pide `auth/csrf` y `auth/yo` para saber si hay sesión y qué paso de onboarding falta.
- Respuesta 401: limpiar la sesión y llevar a `/ingresar`. Respuesta 403 con `onboarding`: llevar al paso pendiente.
- El frontend **no calcula reglas de negocio**: lugares libres, recomendados, puntajes, permisos y estados vienen del backend. Solo valida en el navegador lo que da una respuesta inmediata (campo vacío, largo, formato), y el backend valida igual.

## Estado
- `useState` / `useReducer` locales. El único estado global es la sesión, en `SesionContexto`.
- Sin caché de datos del servidor: cada página pide sus datos al entrar.
- Toda carga de datos maneja tres estados: cargando, error (con opción de reintentar) y datos.

## Formularios
- Controlados. Errores del backend mostrados en su campo (con el mensaje textual que llega) o arriba del formulario si son generales.
- Botón de envío deshabilitado mientras se envía.
- Al éxito, aviso de confirmación (componente `Aviso`) y navegación según `docs/interfaces/`.

## Rutas
- React Router con las rutas de `docs/interfaces/README.md`.
- Componentes de protección: `RutaPublica` (si hay sesión, va a `/inicio`; solo para `/`, `/registro` e `/ingresar`), `RutaPrivada` (sin sesión, va a `/ingresar`) y `RutaConOnboarding` (si falta un paso, va a ese paso).
- Las rutas `/recuperar/*` no llevan protección: se usan con o sin sesión ("Cambiar contraseña" del perfil las usa con sesión).

## Formato
- Fechas y horas con `Intl.DateTimeFormat("es-AR", { timeZone: "America/Argentina/Cordoba" })`, en los formatos de `docs/interfaces/README.md`.
- Niveles y puntajes con coma decimal (`4,5`, `1,00`) mediante funciones de `utilidades/formato.js`.

## Nombres
- `camelCase` en español y sin tildes ni ñ para variables y funciones (`lugaresLibres`, `enviarInvitaciones`); `PascalCase` para componentes; handlers con prefijo `manejar` (`manejarEnvio`).
- Los textos visibles van en el JSX tal como figuran en `docs/interfaces/`, con tildes y en español rioplatense.
