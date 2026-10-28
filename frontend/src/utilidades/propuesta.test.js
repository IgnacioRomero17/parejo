import { describe, expect, it } from "vitest";
import { notaCombinacion } from "./propuesta.js";

const LADOS_COMPLEMENTARIOS = ["DRIVE", "REVES", "DRIVE", "REVES"];

// Combinación como la devuelve la API; `lados` va en el orden Pareja 1 → Pareja 2.
function combinacion({
  numero,
  puntaje,
  nivel = 1,
  lado = 1,
  promedios = [4.75, 4.75],
  lados = LADOS_COMPLEMENTARIOS,
}) {
  return {
    numero,
    puntaje_equilibrio: puntaje,
    equilibrio_nivel: nivel,
    equilibrio_lado: lado,
    parejas: [0, 1].map((posicion) => ({
      numero: posicion + 1,
      promedio: promedios[posicion],
      integrantes: lados
        .slice(posicion * 2, posicion * 2 + 2)
        .map((ladoJugador) => ({ lado: ladoJugador })),
    })),
  };
}

const ELEGIDA = combinacion({ numero: 2, puntaje: 1 });

describe("notaCombinacion (pantalla 16)", () => {
  it("la elegida no lleva nota", () => {
    expect(notaCombinacion(ELEGIDA, ELEGIDA)).toBeNull();
  });

  it("peor nivel con el mismo lado", () => {
    const peor = combinacion({
      numero: 1,
      puntaje: 0.8,
      nivel: 0.75,
      promedios: [4.5, 5],
    });

    expect(notaCombinacion(peor, ELEGIDA)).toBe(
      "Mismo equilibrio de lado que la n.º 2, pero más diferencia de nivel entre las parejas.",
    );
  });

  it("mismo nivel y una pareja repite lado", () => {
    const peor = combinacion({
      numero: 3,
      puntaje: 0.9,
      lado: 0.5,
      lados: ["DRIVE", "DRIVE", "REVES", "INDIFERENTE"],
    });

    expect(notaCombinacion(peor, ELEGIDA)).toBe(
      "Mismo nivel que la n.º 2, pero una pareja repite lado (Drive + Drive).",
    );
  });

  it("mismo nivel y ambas parejas repiten lado, como en la imagen", () => {
    const peor = combinacion({
      numero: 3,
      puntaje: 0.8,
      lado: 0,
      lados: ["DRIVE", "DRIVE", "REVES", "REVES"],
    });

    expect(notaCombinacion(peor, ELEGIDA)).toBe(
      "Mismo nivel que la n.º 2, pero ambas parejas repiten lado (Drive + Drive y Revés + Revés).",
    );
  });

  it("peor nivel y una pareja repite lado", () => {
    const peor = combinacion({
      numero: 1,
      puntaje: 0.7,
      nivel: 0.75,
      lado: 0.5,
      lados: ["DRIVE", "REVES", "REVES", "REVES"],
    });

    expect(notaCombinacion(peor, ELEGIDA)).toBe(
      "Más diferencia de nivel que la n.º 2 y una pareja repite lado (Revés + Revés).",
    );
  });

  it("peor nivel y ambas parejas repiten lado", () => {
    const peor = combinacion({
      numero: 1,
      puntaje: 0.6,
      nivel: 0.75,
      lado: 0,
      lados: ["DRIVE", "DRIVE", "REVES", "REVES"],
    });

    expect(notaCombinacion(peor, ELEGIDA)).toBe(
      "Más diferencia de nivel que la n.º 2 y ambas parejas repiten lado (Drive + Drive y Revés + Revés).",
    );
  });

  it("mejor lado pero peor nivel", () => {
    const elegida = combinacion({
      numero: 2,
      puntaje: 0.9,
      lado: 0.5,
      lados: ["DRIVE", "DRIVE", "REVES", "DRIVE"],
    });
    const peor = combinacion({ numero: 1, puntaje: 0.8, nivel: 0.75 });

    expect(notaCombinacion(peor, elegida)).toBe(
      "Mejor equilibrio de lado que la n.º 2, pero más diferencia de nivel entre las parejas, que pesa más en el puntaje.",
    );
  });

  it("mejor nivel pero peor lado", () => {
    const elegida = combinacion({ numero: 2, puntaje: 0.92, nivel: 0.9 });
    const peor = combinacion({
      numero: 1,
      puntaje: 0.9,
      lado: 0.5,
      lados: ["DRIVE", "DRIVE", "REVES", null],
    });

    expect(notaCombinacion(peor, elegida)).toBe(
      "Menos diferencia de nivel que la n.º 2, pero una pareja repite lado (Drive + Drive), y eso baja más el puntaje.",
    );
  });

  it("mismo puntaje decidido por la diferencia de nivel", () => {
    const elegida = combinacion({
      numero: 1,
      puntaje: 0.9,
      lado: 0.5,
      lados: ["DRIVE", "DRIVE", "REVES", "DRIVE"],
    });
    const empatada = combinacion({
      numero: 2,
      puntaje: 0.9,
      nivel: 0.875,
      promedios: [4.5, 4.75],
    });

    expect(notaCombinacion(empatada, elegida)).toBe(
      "Mismo puntaje que la n.º 1; se eligió la n.º 1 por desempate, por tener menos diferencia de nivel entre las parejas.",
    );
  });

  it("mismo puntaje decidido por el equilibrio de lado", () => {
    const elegida = combinacion({ numero: 1, puntaje: 0.8 });
    const empatada = combinacion({
      numero: 2,
      puntaje: 0.8,
      lado: 0.5,
      lados: ["DRIVE", "DRIVE", "REVES", "DRIVE"],
    });

    expect(notaCombinacion(empatada, elegida)).toBe(
      "Mismo puntaje que la n.º 1; se eligió la n.º 1 por desempate, por tener mejor equilibrio de lado.",
    );
  });

  it("empate total decidido por el número", () => {
    const elegida = combinacion({ numero: 1, puntaje: 1 });
    const empatada = combinacion({ numero: 3, puntaje: 1 });

    expect(notaCombinacion(empatada, elegida)).toBe(
      "Empata en todo con la n.º 1; se eligió la n.º 1 por desempate, por ser la de menor número.",
    );
  });

  it("avisa el cambio si los datos recalculados ya no explican el puntaje menor", () => {
    const igualEnTodo = combinacion({ numero: 1, puntaje: 0.8 });

    expect(notaCombinacion(igualEnTodo, ELEGIDA)).toBe(
      "Al formar las parejas, su puntaje fue menor que el de la n.º 2; desde entonces cambió el nivel o el lado de algún jugador.",
    );
  });

  it("avisa el cambio si los datos recalculados ya no explican el desempate", () => {
    const empatada = combinacion({ numero: 1, puntaje: 1 });

    expect(notaCombinacion(empatada, ELEGIDA)).toBe(
      "Al formar las parejas, empató en puntaje con la n.º 2 y se eligió la n.º 2 por desempate; desde entonces cambió el nivel o el lado de algún jugador.",
    );
  });
});
