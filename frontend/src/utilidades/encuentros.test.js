import { describe, expect, it } from "vitest";
import {
  avisoInvitacionesEnviadas,
  encuentroDeFormulario,
  etiquetaLado,
  fechaMaximaEncuentro,
  formularioEncuentro,
  HORAS_INICIO,
  hoyEnCordoba,
  listarNombres,
  nombresDePareja,
  rolOrganizador,
  textoEsperandoFormacion,
  textoEsperandoParejas,
  textoInvitacionesEnviadas,
  textoInvitacionesPendientes,
  textoJugadores,
  textoLimiteSeleccion,
  textoLugaresACompletar,
  textoLugaresLibres,
  textoLugaresRestantes,
  textoPendientes,
  textoSeleccionados,
  validarEncuentro,
} from "./encuentros.js";

const MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar.";

describe("textos con cantidades", () => {
  it("usan singular con 1 y plural con el resto", () => {
    expect(textoJugadores(1)).toBe("1 jugador");
    expect(textoJugadores(3)).toBe("3 jugadores");
    expect(textoLugaresLibres(1)).toBe("1 lugar libre");
    expect(textoLugaresLibres(2)).toBe("2 lugares libres");
    expect(textoLugaresACompletar(1)).toBe("el lugar libre");
    expect(textoLugaresACompletar(3)).toBe("los 3 lugares libres");
    expect(textoLugaresRestantes(1)).toBe("1 lugar restante");
    expect(textoLugaresRestantes(2)).toBe("2 lugares restantes");
    expect(textoInvitacionesEnviadas(1)).toBe("1 invitación enviada");
    expect(textoInvitacionesEnviadas(3)).toBe("3 invitaciones enviadas");
    expect(textoSeleccionados(0)).toBe("0 seleccionados");
    expect(textoSeleccionados(1)).toBe("1 seleccionado");
    expect(textoPendientes(1)).toBe("1 pendiente");
    expect(textoPendientes(2)).toBe("2 pendientes");
    expect(textoInvitacionesPendientes(1)).toBe("1 invitación pendiente");
    expect(textoInvitacionesPendientes(3)).toBe("3 invitaciones pendientes");
  });
});

describe("textos de la propuesta (HU-012)", () => {
  it("nombra el lado preferido como en el glosario", () => {
    expect(etiquetaLado("DRIVE")).toBe("Drive");
    expect(etiquetaLado("REVES")).toBe("Revés");
    expect(etiquetaLado("INDIFERENTE")).toBe("Indiferente");
  });

  it("nombra una pareja por los nombres de sus integrantes", () => {
    const pareja = {
      integrantes: [
        { nombre: "Tomás", apellido: "Ríos" },
        { nombre: "Camila", apellido: "Paz" },
      ],
    };
    expect(nombresDePareja(pareja)).toBe("Tomás + Camila");
  });

  it.each([
    [
      "FEMENINO",
      "Esperando que la organizadora inicie la formación automática de parejas.",
    ],
    [
      "MASCULINO",
      "Esperando que el organizador inicie la formación automática de parejas.",
    ],
    [
      "NO_DECLARA",
      "Esperando que se inicie la formación automática de parejas.",
    ],
  ])("en el panel, con organizador %s dice «%s»", (genero, texto) => {
    expect(textoEsperandoFormacion(genero)).toBe(texto);
  });
});

describe("textos de invitaciones (HU-008)", () => {
  it("avisa el envío en singular o plural", () => {
    expect(avisoInvitacionesEnviadas(1)).toBe("Invitación enviada.");
    expect(avisoInvitacionesEnviadas(2)).toBe("2 invitaciones enviadas.");
  });

  it("explica el límite de selección según los lugares libres", () => {
    expect(textoLimiteSeleccion(1)).toBe(
      "Como queda 1 lugar libre, podés seleccionar 1 jugador. Para elegir a otro, quitá la selección actual.",
    );
    expect(textoLimiteSeleccion(3)).toBe(
      "Como quedan 3 lugares libres, podés seleccionar 3 jugadores. Para elegir a otro, quitá la selección actual.",
    );
  });

  it("lista los nombres con comas y «y»", () => {
    const ana = { nombre: "Ana", apellido: "Paz" };
    const bruno = { nombre: "Bruno", apellido: "Castro" };
    const federico = { nombre: "Federico", apellido: "Luna" };
    expect(listarNombres([])).toBe("");
    expect(listarNombres([ana])).toBe("Ana Paz");
    expect(listarNombres([ana, bruno])).toBe("Ana Paz y Bruno Castro");
    expect(listarNombres([ana, bruno, federico])).toBe(
      "Ana Paz, Bruno Castro y Federico Luna",
    );
  });

  it.each([
    [
      "FEMENINO",
      "Organizadora",
      "Esperando que la organizadora forme las parejas.",
    ],
    [
      "MASCULINO",
      "Organizador",
      "Esperando que el organizador forme las parejas.",
    ],
    [
      "NO_DECLARA",
      "Organiza el encuentro",
      "Esperando que se inicie la formación automática de parejas.",
    ],
  ])("con organizador %s usa «%s» y «%s»", (genero, rol, esperando) => {
    expect(rolOrganizador(genero)).toBe(rol);
    expect(textoEsperandoParejas(genero)).toBe(esperando);
  });
});

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
