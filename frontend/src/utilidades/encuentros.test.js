import { describe, expect, it } from "vitest";
import {
  encuentroDeFormulario,
  fechaMaximaEncuentro,
  formularioEncuentro,
  HORAS_INICIO,
  hoyEnCordoba,
  validarEncuentro,
} from "./encuentros.js";

const MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar.";

describe("HORAS_INICIO", () => {
  it("va de 08:00 a 22:30 en pasos de 30 minutos", () => {
    const horas = HORAS_INICIO.map((hora) => hora.valor);

    expect(horas).toHaveLength(30);
    expect(horas.slice(0, 3)).toEqual(["08:00", "08:30", "09:00"]);
    expect(horas.at(-1)).toBe("22:30");
    expect(horas).not.toContain("23:00");
  });
});

describe("formularioEncuentro y encuentroDeFormulario", () => {
  it("precarga la localidad del jugador y deja el resto vacío", () => {
    expect(formularioEncuentro({ localidad: 7 })).toEqual({
      fecha: "",
      hora_inicio: "",
      duracion_minutos: "",
      localidad: "7",
      tipo_encuentro: "",
      ubicacion: "",
    });
    expect(formularioEncuentro({ localidad: null }).localidad).toBe("");
  });

  it("convierte los valores al formato de la API", () => {
    expect(
      encuentroDeFormulario({
        fecha: "2026-10-03",
        hora_inicio: "18:00",
        duracion_minutos: "90",
        localidad: "7",
        tipo_encuentro: "COMPETITIVO",
        ubicacion: "  Av. San Martín 4500 ",
      }),
    ).toEqual({
      fecha: "2026-10-03",
      hora_inicio: "18:00",
      duracion_minutos: 90,
      localidad: 7,
      ubicacion: "Av. San Martín 4500",
      tipo_encuentro: "COMPETITIVO",
    });
  });

  it("manda null en los campos vacíos", () => {
    expect(
      encuentroDeFormulario(formularioEncuentro({ localidad: null })),
    ).toEqual({
      fecha: null,
      hora_inicio: null,
      duracion_minutos: null,
      localidad: null,
      ubicacion: null,
      tipo_encuentro: null,
    });
  });
});

describe("validarEncuentro", () => {
  it("marca solo los campos vacíos", () => {
    const valores = {
      ...formularioEncuentro({ localidad: 7 }),
      fecha: "2026-10-03",
      ubicacion: "   ",
    };

    expect(validarEncuentro(valores)).toEqual({
      hora_inicio: [MENSAJE_CAMPO_VACIO],
      duracion_minutos: [MENSAJE_CAMPO_VACIO],
      tipo_encuentro: [MENSAJE_CAMPO_VACIO],
      ubicacion: [MENSAJE_CAMPO_VACIO],
    });
  });
});

describe("hoyEnCordoba", () => {
  it("usa la fecha de Córdoba, no la de UTC", () => {
    // 01:30 UTC del 4 de octubre son las 22:30 del 3 de octubre en Córdoba.
    expect(hoyEnCordoba(new Date("2026-10-04T01:30:00Z"))).toBe("2026-10-03");
    expect(hoyEnCordoba(new Date("2026-10-03T12:00:00Z"))).toBe("2026-10-03");
  });
});

describe("fechaMaximaEncuentro", () => {
  it("es hoy en Córdoba + 60 días", () => {
    // 3 de octubre + 60 días = 2 de diciembre (cruza meses de 31 y 30 días).
    expect(fechaMaximaEncuentro(new Date("2026-10-03T12:00:00Z"))).toBe(
      "2026-12-02",
    );
    expect(fechaMaximaEncuentro(new Date("2026-12-15T15:00:00Z"))).toBe(
      "2027-02-13",
    );
  });

  it("cuenta desde la fecha de Córdoba, no desde la de UTC", () => {
    // 01:30 UTC del 4 de octubre todavía es 3 de octubre en Córdoba.
    expect(fechaMaximaEncuentro(new Date("2026-10-04T01:30:00Z"))).toBe(
      "2026-12-02",
    );
  });
});
