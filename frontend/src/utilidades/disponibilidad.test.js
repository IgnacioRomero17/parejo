import { describe, expect, it } from "vitest";
import {
  clavesEnviadas,
  disponibilidadDeFormulario,
  erroresDeDisponibilidad,
  formularioDisponibilidad,
  franjaVacia,
  HORAS_FRANJA,
  validarDisponibilidad,
} from "./disponibilidad.js";
import { MENSAJE_CAMPO_VACIO } from "./validaciones.js";

const VACIA = {
  franjas: [],
  tipo_encuentro: null,
  lado_preferido: null,
  disponible_para_invitaciones: false,
};
const GUARDADA = {
  franjas: [
    { dia_semana: 3, hora_inicio: "19:00", hora_fin: "22:00" },
    { dia_semana: 6, hora_inicio: "17:00", hora_fin: "21:00" },
  ],
  tipo_encuentro: "COMPETITIVO",
  lado_preferido: "DRIVE",
  disponible_para_invitaciones: true,
};

function franja(dia_semana, hora_inicio, hora_fin) {
  return { ...franjaVacia(), dia_semana, hora_inicio, hora_fin };
}

describe("disponibilidad en el formulario (HU-005)", () => {
  it("P2: las horas van de 08:00 a 23:30 en pasos de 30 minutos", () => {
    const horas = HORAS_FRANJA.map((hora) => hora.valor);

    expect(horas).toHaveLength(32);
    expect(horas.slice(0, 3)).toEqual(["08:00", "08:30", "09:00"]);
    expect(horas.at(-1)).toBe("23:30");
    expect(horas).not.toContain("07:30");
  });

  it("el primer ingreso arranca con una fila vacía y nada elegido", () => {
    const valores = formularioDisponibilidad(VACIA, { conFilaVacia: true });

    expect(valores.franjas).toHaveLength(1);
    expect(valores.franjas[0]).toMatchObject({
      dia_semana: "",
      hora_inicio: "",
      hora_fin: "",
    });
    expect(valores.tipo_encuentro).toBe("");
    expect(valores.lado_preferido).toBe("");
    expect(valores.disponible_para_invitaciones).toBe(false);
    expect(formularioDisponibilidad(VACIA).franjas).toEqual([]);
  });

  it("ida y vuelta conserva los valores de la API, con una clave por fila", () => {
    const valores = formularioDisponibilidad(GUARDADA, { conFilaVacia: true });

    expect(valores.franjas[0].dia_semana).toBe("3");
    expect(new Set(valores.franjas.map((fila) => fila.clave)).size).toBe(2);
    expect(disponibilidadDeFormulario(valores)).toEqual(GUARDADA);
  });

  it("no envía las filas sin ningún dato", () => {
    const valores = {
      ...formularioDisponibilidad(GUARDADA),
      franjas: [franjaVacia(), franja("6", "17:00", "21:00"), franjaVacia()],
    };

    expect(disponibilidadDeFormulario(valores).franjas).toEqual([
      { dia_semana: 6, hora_inicio: "17:00", hora_fin: "21:00" },
    ]);
    expect(clavesEnviadas(valores)).toEqual([valores.franjas[1].clave]);
  });

  it("marca los campos vacíos de las filas a medio completar y de las preferencias", () => {
    const incompleta = franja("6", "17:00", "");
    const valores = {
      ...formularioDisponibilidad(VACIA),
      franjas: [franjaVacia(), incompleta],
    };

    expect(validarDisponibilidad(valores)).toEqual({
      franjas: { [incompleta.clave]: { hora_fin: [MENSAJE_CAMPO_VACIO] } },
      tipo_encuentro: [MENSAJE_CAMPO_VACIO],
      lado_preferido: [MENSAJE_CAMPO_VACIO],
    });
    expect(validarDisponibilidad(formularioDisponibilidad(GUARDADA))).toEqual(
      {},
    );
  });

  it("ubica los errores del backend en la fila enviada en esa posición", () => {
    const claves = ["franja-a", "franja-b"];
    const errores = {
      franjas: {
        1: { hora_fin: ["La franja debe durar al menos 60 minutos."] },
      },
      tipo_encuentro: ["Elegí una opción del listado."],
    };

    expect(erroresDeDisponibilidad(errores, claves)).toEqual({
      franjas: {
        "franja-b": { hora_fin: ["La franja debe durar al menos 60 minutos."] },
      },
      tipo_encuentro: ["Elegí una opción del listado."],
    });
    expect(erroresDeDisponibilidad(undefined, claves)).toEqual({});
  });
});
