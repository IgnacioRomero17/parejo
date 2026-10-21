# 16 · Propuesta de encuentro

Imagen: `16-propuesta.png` (con "Ver combinaciones evaluadas" desplegado) · Ruta: `/encuentros/:id/propuesta` · Acceso: los 4 participantes · HU: HU-011, HU-012

## Contenido
- Etiqueta "Propuesta generada", título "Propuesta de encuentro" y texto "Resultado generado automáticamente por el sistema: la combinación de parejas con mejor resultado de equilibrio."
- Botón "Volver al inicio" → `/inicio`.
- Fila de datos: Fecha ("Sábado 3 de octubre de 2026"), Hora, Duración, Tipo, Lugar (localidad · dirección).
- Bloque azul con las dos parejas, separadas por "VS":
  - Encabezado "Pareja 1" / "Pareja 2" y "PROMEDIO 4,75".
  - Cada integrante: iniciales, nombre, "localidad · lado preferido" y "Nivel 4,5".
- Tarjeta "RESULTADO DE EQUILIBRIO · INFORMATIVO": puntaje guardado con dos decimales ("1,00") y el texto: "Puntaje de equilibrio de la combinación seleccionada, entre 0 y 1 (1 = parejas perfectamente equilibradas). Considera la diferencia de nivel promedio entre las parejas y la complementariedad del lado preferido. Es el mejor resultado entre las 3 combinaciones evaluadas y se muestra solo como información."
- Sección desplegable "Ver combinaciones evaluadas" (**cerrada** al entrar). Tabla con las 3 combinaciones:

| Columna | Contenido |
|---|---|
| N.º | 1, 2, 3 |
| Parejas | "Tomás + Valentina vs Camila + Federico" |
| Promedios | "4,50 vs 5,00" |
| Equilibrio nivel | 0 a 1, dos decimales |
| Equilibrio lado | 0 a 1, dos decimales |
| Puntaje | puntaje guardado, dos decimales |

  La elegida va resaltada con la etiqueta "Seleccionada". La nota debajo de la combinación 3 que aparece en la imagen no se implementa.

## Datos
- Puntajes: los guardados en las combinaciones.
- Promedios, equilibrio de nivel y de lado: se recalculan con el motor a partir de los niveles y lados actuales (limitación aceptada, ver HU-012).

## Notas
- Pareja 1 y Pareja 2 corresponden al campo `numero` de cada pareja.
- No hay acciones para modificar ni rehacer la propuesta.
