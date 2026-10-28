---
paths:
  - "frontend/src/**"
---

# Estilo visual

Referencia visual: las imágenes de `docs/interfaces/` (mirar solo la de la pantalla que se construye). Los valores exactos son los de esta regla; si la imagen y la regla difieren, manda la regla.

## Tokens (`src/estilos/variables.css`)
Todos los colores, radios y sombras salen de estas variables. Ningún color escrito a mano en los componentes.

```css
:root {
  /* Marca */
  --azul: #1F5EFF;            /* acción principal, enlaces, selección */
  --lima: #CDF23F;            /* acento: estados positivos, marcas activas */
  --marino: #0E1628;          /* barra superior, paneles oscuros, avisos */

  /* Superficies y texto */
  --fondo: #F4F6FA;
  --superficie: #FFFFFF;
  --texto: #0F172A;
  --texto-secundario: #5E6E85; /* apenas más oscuro que en las imágenes, para mejor lectura */
  --texto-sobre-oscuro: #C3CCD9;
  --linea: #E4E8EE;            /* separadores y bordes de tarjeta */
  --borde-campo: #D5DBE4;      /* bordes de campos y controles */
  --error: #DC2626;
  --error-fondo: #FEE2E2;

  /* Etiquetas: fondo / texto */
  --etq-azul: #E3E9FF;  --etq-azul-texto: #2340B8;
  --etq-verde: #DCFCE7; --etq-verde-texto: #166534;
  --etq-rojo: #FEE2E2;  --etq-rojo-texto: #B91C1C;
  --etq-amarillo: #FEF3C7; --etq-amarillo-texto: #92400E;
  --etq-gris: #EEF1F5;  --etq-gris-texto: #475569;
  --etq-lima: #CDF23F;  --etq-lima-texto: #1A2E05;

  /* Forma */
  --radio-tarjeta: 16px;
  --radio-control: 10px;
  --radio-pildora: 999px;
  --sombra-aviso: 0 8px 24px rgba(15, 23, 42, .25);

  /* Tipografía */
  --fuente-texto: "Inter", system-ui, sans-serif;
  --fuente-titulos: "Space Grotesk", "Inter", sans-serif;
}
```

## Tipografía
- **Inter** (400, 500, 600, 700) para todo el texto; **Space Grotesk** (500, 700) solo para títulos y números destacados. Cargadas con `@fontsource`.
- Escala:

| Uso | Fuente | Tamaño / peso |
|---|---|---|
| Título de página (h1) | Space Grotesk | 32px / 700, interletrado -0,01em |
| Título de pantallas de acceso | Space Grotesk | 32px / 700 (formulario), 40px / 700 (panel oscuro) |
| Título de tarjeta | Inter | 16–18px / 700 |
| Texto | Inter | 15–16px / 400 |
| Etiqueta de campo | Inter | 14px / 500 |
| Ayuda y datos secundarios | Inter | 13–13,5px / 400, `--texto-secundario` |
| Rótulo en mayúsculas ("PASO 1 DE 2") | Inter | 12px / 700, mayúsculas, interletrado 0,1em |
| Números destacados ("2 de 4", "1,00") | Space Grotesk | 21–44px / 700 |

## Componentes (en `src/componentes/`)
| Componente | Especificación |
|---|---|
| `Boton` | alto 44px, padding 0 20px, radio 10px, 15px/700. Variantes: **primario** (fondo azul, texto blanco), **secundario** (fondo blanco, borde `--borde-campo`), **deshabilitado** (fondo #E5E9F0, texto `--texto-secundario`). Ícono opcional a la izquierda, 16px, separación 8px. |
| `Campo` / `Desplegable` | alto 42px, radio 9px, borde 1px `--borde-campo`, padding 0 14px, 16px. Error: borde 1,5px `--error` + mensaje debajo (ícono de alerta 14px + texto 13px en `--error`). |
| `SelectorSegmentado` | contenedor #EEF1F5, radio 10px, padding 4px; opción elegida en blanco con sombra suave y texto 700. El selector segmentado de tres opciones va siempre a todo el ancho del formulario o la tarjeta, nunca en media columna. Las opciones tienen anchos iguales y nunca se corta el texto. |
| `Interruptor` | 46 × 26px; encendido azul, apagado `--borde-campo`. |
| `Etiqueta` | píldora, 11px/700, mayúsculas, interletrado 0,06em, padding 5px 10px, colores `--etq-*`. Estados: Buscando participantes = azul; Completo y Propuesta generada = lima; Pendiente = amarillo; Aceptada y Disponible = verde; Rechazada = rojo; resto = gris. |
| `Tarjeta` | fondo blanco, borde 1px `--linea`, radio 16px, padding 20–28px. Sin sombra. |
| `Aviso` | arriba a la derecha (top 84px, right 40px), fondo marino, texto blanco 14px/600, ícono de check lima, radio 10px, `--sombra-aviso`; se oculta a los 4 segundos. |
| `Avatar` | círculo 44px (38px en listas), iniciales 15px/700, fondo `--etq-azul` y texto #2A44B8 Excepción: en la propuesta (pantalla 16), los avatares de la Pareja 2 usan --etq-verde y --etq-verde-texto para distinguir las dos parejas. |
| `Casilleros` | 4 cuadrados de 22px, radio 5px: confirmado azul (o lima si el encuentro está completo), libre con borde punteado. Siempre acompañados del texto "N de 4". |
| `BarraSuperior` | alto 64px, fondo marino; logo a la izquierda; enlaces 15px/600 `--texto-sobre-oscuro`, activo en blanco con línea lima de 3px abajo; indicador de pendientes: círculo lima 19px con número marino. |
| `PanelAcceso` | pantallas 06a–06e: panel izquierdo marino de 520px (logo, ilustración de cancha, título 40px, texto) y formulario centrado de 420–460px a la derecha sobre `--fondo`. |
| `SelectorNivel` | ver `docs/interfaces/07a-onboarding-perfil.md`: barra de 4px, puntos enteros de 30px con número, medios puntos de 8px; avance en azul; valor elegido en medio punto: círculo lima de 26px con borde marino; en entero: círculo azul de 38px con halo lima; etiqueta flotante marina con texto lima. |

## Logo
`docs/recursos/parejo-logo.svg`: copiarlo a `src/assets/` y usarlo como componente o `<img>`. 30px en la barra superior, junto a "parejo" en Space Grotesk 22px/700 blanco. No redibujarlo ni cambiar sus colores.

## Íconos
`lucide-react`, trazo 2, 16–18px en botones y datos, 14px en mensajes de error. Los mismos que en las imágenes (calendario, reloj, temporizador, pin, trofeo, sobre, check, alerta, info, más, candado, salir).

## Diseño de página
- **Solo escritorio** en el prototipo: ancho de contenido 1280px centrado, márgenes laterales 40px, pensado para pantallas de 1280px o más. La versión para celulares no se implementa (trabajo futuro).
- **Preparado para adaptarse después:** maquetar con CSS Grid y Flexbox, columnas en fracciones (`1fr`, `minmax`) y anchos máximos (`max-width`) en lugar de anchos fijos. Sin posiciones absolutas para ubicar bloques de contenido. Así, adaptarlo a celulares sería solo agregar reglas de CSS.
- Espaciado en múltiplos de 4px. Separación entre tarjetas 14–24px.
- Fondo de página `--fondo`; tarjetas blancas encima.
