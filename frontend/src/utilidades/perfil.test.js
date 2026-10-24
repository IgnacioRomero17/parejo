import { describe, expect, it } from "vitest";
import { nivelesDescriptos } from "./niveles.js";
import {
  cuerpoActualizacion,
  formularioPerfil,
  formularioPerfilDeportivo,
  perfilDeportivoDeFormulario,
  seccionesModificadas,
  segunGenero,
  textoCamposPendientes,
  validarSecciones,
} from "./perfil.js";
import { MENSAJE_CAMPO_VACIO } from "./validaciones.js";

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
  disponibilidad: {
    franjas: [{ dia_semana: 6, hora_inicio: "17:00", hora_fin: "21:00" }],
    tipo_encuentro: "COMPETITIVO",
    lado_preferido: "DRIVE",
    disponible_para_invitaciones: true,
  },
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

  it("HU-005: la disponibilidad se envía con el formato de la API", () => {
    const valores = formularioPerfil(PERFIL);

    expect(cuerpoActualizacion(valores, ["disponibilidad"])).toEqual({
      disponibilidad: PERFIL.disponibilidad,
    });
  });

  it("HU-005: las claves de las franjas no cuentan como cambio", () => {
    // Dos lecturas del mismo perfil dan claves distintas a las mismas franjas.
    expect(
      seccionesModificadas(formularioPerfil(PERFIL), formularioPerfil(PERFIL)),
    ).toEqual([]);
  });

  it("HU-005: valida cada sección con sus reglas", () => {
    const valores = formularioPerfil(PERFIL);
    valores.perfil_deportivo.genero = "";
    valores.disponibilidad.lado_preferido = "";

    expect(
      validarSecciones(valores, [
        "datos_personales",
        "perfil_deportivo",
        "disponibilidad",
      ]),
    ).toEqual({
      perfil_deportivo: { genero: [MENSAJE_CAMPO_VACIO] },
      disponibilidad: { lado_preferido: [MENSAJE_CAMPO_VACIO] },
    });
  });
});

describe("textos y niveles", () => {
  it("usa el plural correcto en el contador de pendientes", () => {
    expect(textoCamposPendientes(1)).toBe("1 campo pendiente");
    expect(textoCamposPendientes(5)).toBe("5 campos pendientes");
  });

  it("elige la palabra según el género del perfil", () => {
    expect(segunGenero("FEMENINO", "registrada", "registrado")).toBe(
      "registrada",
    );
    for (const genero of ["MASCULINO", "NO_DECLARA", null]) {
      expect(segunGenero(genero, "registrada", "registrado")).toBe(
        "registrado",
      );
    }
  });

  it("describe ningún nivel sin elegir, uno si es entero y dos con ,5", () => {
    expect(nivelesDescriptos(null)).toEqual([]);
    expect(nivelesDescriptos(6).map((nivel) => nivel.numero)).toEqual([6]);
    expect(nivelesDescriptos(2.5).map((nivel) => nivel.numero)).toEqual([2, 3]);
  });
});
