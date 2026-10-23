import { describe, expect, it } from "vitest";
import { nivelesDescriptos } from "./niveles.js";
import {
  cuerpoActualizacion,
  formularioPerfil,
  formularioPerfilDeportivo,
  perfilDeportivoDeFormulario,
  seccionesModificadas,
  textoCamposPendientes,
} from "./perfil.js";

const PERFIL = {
  datos_personales: {
    nombre: "Tomás",
    apellido: "Ríos",
    email: "tomas.rios@example.com",
  },
  perfil_deportivo: {
    edad: 29,
    genero: "MASCULINO",
    localidad: 3,
    frecuencia_juego: "2_3_SEMANA",
    nivel_estimado: 4.5,
  },
  disponibilidad: { disponible_para_invitaciones: true },
};

describe("perfil deportivo en el formulario", () => {
  it("un perfil vacío deja todo sin elegir", () => {
    expect(
      formularioPerfilDeportivo({
        edad: null,
        genero: null,
        localidad: null,
        frecuencia_juego: null,
        nivel_estimado: null,
      }),
    ).toEqual({
      edad: "",
      genero: "",
      localidad: "",
      frecuencia_juego: "",
      nivel_estimado: null,
    });
  });

  it("ida y vuelta conserva los valores de la API", () => {
    const valores = formularioPerfilDeportivo(PERFIL.perfil_deportivo);

    expect(valores.edad).toBe("29");
    expect(valores.localidad).toBe("3");
    expect(perfilDeportivoDeFormulario(valores)).toEqual(
      PERFIL.perfil_deportivo,
    );
  });
});

describe("secciones de la pantalla 17", () => {
  it("detecta solo las secciones que cambiaron", () => {
    const guardados = formularioPerfil(PERFIL);
    const valores = {
      ...guardados,
      datos_personales: { ...guardados.datos_personales, nombre: "Tomi" },
    };

    expect(seccionesModificadas(guardados, guardados)).toEqual([]);
    expect(seccionesModificadas(valores, guardados)).toEqual([
      "datos_personales",
    ]);
    expect(cuerpoActualizacion(valores, ["datos_personales"])).toEqual({
      datos_personales: { nombre: "Tomi", apellido: "Ríos" },
    });
  });

  it("el perfil deportivo se envía con el formato de la API", () => {
    const valores = formularioPerfil(PERFIL);

    expect(cuerpoActualizacion(valores, ["perfil_deportivo"])).toEqual({
      perfil_deportivo: PERFIL.perfil_deportivo,
    });
  });
});

describe("textos y niveles", () => {
  it("usa el plural correcto en el contador de pendientes", () => {
    expect(textoCamposPendientes(1)).toBe("1 campo pendiente");
    expect(textoCamposPendientes(5)).toBe("5 campos pendientes");
  });

  it("describe ningún nivel sin elegir, uno si es entero y dos con ,5", () => {
    expect(nivelesDescriptos(null)).toEqual([]);
    expect(nivelesDescriptos(6).map((nivel) => nivel.numero)).toEqual([6]);
    expect(nivelesDescriptos(2.5).map((nivel) => nivel.numero)).toEqual([2, 3]);
  });
});
