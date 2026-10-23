export const NIVEL_MINIMO = 1;
export const NIVEL_MAXIMO = 7;
export const PASO_NIVEL = 0.5;

// Tabla de la pantalla 07a.
export const NIVELES = [
  {
    numero: 1,
    nombre: "Iniciación",
    descripcion: "Recién empezás: aprendés los golpes y las reglas básicas.",
  },
  {
    numero: 2,
    nombre: "Principiante",
    descripcion: "Mantenés peloteos cortos y empezás a usar las paredes.",
  },
  {
    numero: 3,
    nombre: "Intermedio bajo",
    descripcion:
      "Sostenés el peloteo, pero la volea y la bandeja todavía fallan.",
  },
  {
    numero: 4,
    nombre: "Intermedio",
    descripcion:
      "Controlás los golpes básicos, jugás bien las paredes y entendés el juego en pareja.",
  },
  {
    numero: 5,
    nombre: "Intermedio alto",
    descripcion:
      "Ejecutás casi todos los golpes con consistencia y construís los puntos.",
  },
  {
    numero: 6,
    nombre: "Avanzado",
    descripcion:
      "Jugás con potencia, táctica y poco error. Competís en torneos.",
  },
  {
    numero: 7,
    nombre: "Élite",
    descripcion: "Nivel profesional o de competición de alto rendimiento.",
  },
];

// Todas las posiciones del selector: 1; 1,5; 2; … 7 (13 posiciones, índices 0 a 12).
export const POSICIONES_NIVEL = Array.from(
  { length: (NIVEL_MAXIMO - NIVEL_MINIMO) / PASO_NIVEL + 1 },
  (_, indice) => NIVEL_MINIMO + indice * PASO_NIVEL,
);

// Índice de un nivel entre las posiciones del selector: 1 → 0, 1,5 → 1, … 7 → 12.
export function indiceNivel(valor) {
  return Math.round((valor - NIVEL_MINIMO) / PASO_NIVEL);
}

// Niveles que describen un valor: ninguno sin elegir, uno si es entero y dos si termina en ,5.
export function nivelesDescriptos(valor) {
  if (valor === null || valor === undefined) return [];
  const inferior = Math.floor(valor);
  const superior = Math.ceil(valor);
  return NIVELES.filter(
    (nivel) => nivel.numero === inferior || nivel.numero === superior,
  );
}
