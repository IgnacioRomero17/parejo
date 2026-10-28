import { etiquetaLado } from "./encuentros.js";

const LADOS_QUE_SE_REPITEN = ["DRIVE", "REVES"];

// Signo de a − b con la precisión de 4 decimales con que el motor guarda los puntajes.
function comparar(a, b) {
  return Math.sign(Math.round((a - b) * 10000));
}

function diferenciaDePromedios(combinacion) {
  const [pareja1, pareja2] = combinacion.parejas;
  return Math.abs(pareja1.promedio - pareja2.promedio);
}

// Como en el motor: una pareja repite lado si los dos son Drive o los dos son Revés.
// "una pareja repite lado (Drive + Drive)" / "ambas parejas repiten lado (… y …)".
function textoLadosRepetidos(combinacion) {
  const repetidos = combinacion.parejas
    .map((pareja) => pareja.integrantes.map((jugador) => jugador.lado))
    .filter(
      ([lado1, lado2]) =>
        lado1 === lado2 && LADOS_QUE_SE_REPITEN.includes(lado1),
    )
    .map(([lado1, lado2]) => `${etiquetaLado(lado1)} + ${etiquetaLado(lado2)}`);
  const cuales = repetidos.join(" y ");
  return repetidos.length === 1
    ? `una pareja repite lado (${cuales})`
    : `ambas parejas repiten lado (${cuales})`;
}

// Con el mismo puntaje guardado decide el desempate del motor: menor diferencia de
// promedios, mayor equilibrio de lado y menor número.
function notaDesempate(combinacion, elegida, referencia) {
  const criterios = [
    [
      comparar(
        diferenciaDePromedios(elegida),
        diferenciaDePromedios(combinacion),
      ),
      "por tener menos diferencia de nivel entre las parejas",
    ],
    [
      comparar(combinacion.equilibrio_lado, elegida.equilibrio_lado),
      "por tener mejor equilibrio de lado",
    ],
    [
      Math.sign(elegida.numero - combinacion.numero),
      "por ser la de menor número",
    ],
  ];
  const decisivo = criterios.findIndex(([signo]) => signo !== 0);
  const [signo, motivo] = criterios[decisivo];
  if (signo > 0) {
    return `Al formar las parejas, empató en puntaje con ${referencia} y se eligió ${referencia} por desempate; desde entonces cambió el nivel o el lado de algún jugador.`;
  }
  const porNumero = decisivo === criterios.length - 1;
  const inicio = porNumero
    ? `Empata en todo con ${referencia}`
    : `Mismo puntaje que ${referencia}`;
  return `${inicio}; se eligió ${referencia} por desempate, ${motivo}.`;
}

// Pantalla 16: por qué no se eligió una combinación, comparada con la elegida (null para la
// elegida). Promedios y equilibrios llegan recalculados y el puntaje es el guardado: si los
// datos ya no explican el puntaje, la nota avisa que cambió el nivel o el lado de alguien.
export function notaCombinacion(combinacion, elegida) {
  if (combinacion.numero === elegida.numero) return null;
  const referencia = `la n.º ${elegida.numero}`;
  if (
    comparar(combinacion.puntaje_equilibrio, elegida.puntaje_equilibrio) === 0
  ) {
    return notaDesempate(combinacion, elegida, referencia);
  }
  const nivel = comparar(
    combinacion.equilibrio_nivel,
    elegida.equilibrio_nivel,
  );
  const lado = comparar(combinacion.equilibrio_lado, elegida.equilibrio_lado);
  if (nivel < 0 && lado === 0) {
    return `Mismo equilibrio de lado que ${referencia}, pero más diferencia de nivel entre las parejas.`;
  }
  if (nivel === 0 && lado < 0) {
    return `Mismo nivel que ${referencia}, pero ${textoLadosRepetidos(combinacion)}.`;
  }
  if (nivel < 0 && lado < 0) {
    return `Más diferencia de nivel que ${referencia} y ${textoLadosRepetidos(combinacion)}.`;
  }
  if (nivel < 0 && lado > 0) {
    return `Mejor equilibrio de lado que ${referencia}, pero más diferencia de nivel entre las parejas, que pesa más en el puntaje.`;
  }
  if (nivel > 0 && lado < 0) {
    return `Menos diferencia de nivel que ${referencia}, pero ${textoLadosRepetidos(combinacion)}, y eso baja más el puntaje.`;
  }
  return `Al formar las parejas, su puntaje fue menor que el de ${referencia}; desde entonces cambió el nivel o el lado de algún jugador.`;
}
