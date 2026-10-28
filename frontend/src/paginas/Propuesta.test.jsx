import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ErrorApi } from "../api/cliente.js";
import { obtenerPropuesta } from "../api/encuentros.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import Propuesta from "./Propuesta.jsx";

vi.mock("../api/encuentros.js", () => ({ obtenerPropuesta: vi.fn() }));

function jugador(id, nombre, apellido, localidad, nivel, lado) {
  return {
    id,
    nombre,
    apellido,
    localidad: { id: id + 10, nombre: localidad },
    nivel,
    lado,
  };
}

const TOMAS = jugador(1, "Tomás", "Ríos", "Río Ceballos", 4.5, "DRIVE");
const VALENTINA = jugador(2, "Valentina", "Sosa", "Río Ceballos", 4.5, "REVES");
const CAMILA = jugador(4, "Camila", "Paz", "Mendiolaza", 5, "REVES");
const FEDERICO = jugador(5, "Federico", "Luna", "Villa Allende", 5, "DRIVE");

function combinacion(numero, puntaje, niveles, parejas) {
  return {
    numero,
    puntaje_equilibrio: puntaje,
    equilibrio_nivel: niveles[0],
    equilibrio_lado: niveles[1],
    parejas: parejas.map(([promedio, integrantes], posicion) => ({
      numero: posicion + 1,
      promedio,
      integrantes,
    })),
  };
}

// El caso de ejemplo de la regla del motor: se elige la combinación 2.
const PROPUESTA = {
  encuentro: {
    id: 15,
    fecha: "2026-10-03",
    hora_inicio: "18:00",
    duracion_minutos: 90,
    localidad: { id: 7, nombre: "Río Ceballos" },
    ubicacion: "Av. San Martín 4500",
    tipo_encuentro: "COMPETITIVO",
    estado: "PROPUESTA_GENERADA",
    confirmados: 4,
  },
  combinacion_elegida: 2,
  puntaje_equilibrio: 1,
  combinaciones: [
    combinacion(
      1,
      0.8,
      [0.75, 1],
      [
        [4.5, [TOMAS, VALENTINA]],
        [5, [CAMILA, FEDERICO]],
      ],
    ),
    combinacion(
      2,
      1,
      [1, 1],
      [
        [4.75, [TOMAS, CAMILA]],
        [4.75, [VALENTINA, FEDERICO]],
      ],
    ),
    combinacion(
      3,
      0.8,
      [1, 0],
      [
        [4.75, [TOMAS, FEDERICO]],
        [4.75, [VALENTINA, CAMILA]],
      ],
    ),
  ],
};

function renderizar() {
  const sesion = {
    cargando: false,
    usuario: { id: 2, nombre: "Valentina", onboarding: null },
    establecerUsuario: vi.fn(),
  };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={["/encuentros/15/propuesta"]}>
        <Routes>
          <Route path="/encuentros/:id/propuesta" element={<Propuesta />} />
          <Route path="/inicio" element={<h1>Inicio</h1>} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

function textoDe(elemento) {
  return elemento.textContent.replace(/\s+/g, " ").trim();
}

async function esperarPropuesta() {
  return screen.findByRole("heading", {
    level: 1,
    name: "Propuesta de encuentro",
  });
}

function pareja(numero) {
  return screen.getByRole("region", { name: `Pareja ${numero}` });
}

describe("Propuesta (HU-011, HU-012)", () => {
  beforeEach(() => {
    obtenerPropuesta.mockReset().mockResolvedValue(PROPUESTA);
  });

  it("pide la propuesta del encuentro de la ruta y titula la pestaña", async () => {
    renderizar();

    await esperarPropuesta();
    expect(obtenerPropuesta).toHaveBeenCalledWith("15");
    expect(document.title).toBe("Propuesta de encuentro · parejo");
    expect(screen.getByText("Propuesta generada")).toBeTruthy();
  });

  it("HU-011 C2, HU-012 C2: muestra fecha, horario, localidad y dirección", async () => {
    renderizar();
    await esperarPropuesta();

    const datos = screen
      .getAllByRole("term")
      .map((rotulo) => [textoDe(rotulo), textoDe(rotulo.nextElementSibling)]);
    expect(datos).toEqual([
      ["Fecha", "Sábado 3 de octubre de 2026"],
      ["Hora", "18:00"],
      ["Duración", "90 minutos"],
      ["Tipo", "Competitivo"],
      ["Lugar", "Río Ceballos · Av. San Martín 4500"],
    ]);
  });

  it("HU-011 C3, HU-012 C2: muestra las dos parejas elegidas con sus integrantes", async () => {
    renderizar();
    await esperarPropuesta();

    expect(within(pareja(1)).getByText("Promedio 4,75")).toBeTruthy();
    expect(within(pareja(1)).getAllByRole("listitem").map(textoDe)).toEqual([
      "TRTomás RíosRío Ceballos · DriveNivel 4,5",
      "CPCamila PazMendiolaza · RevésNivel 5,0",
    ]);
    expect(within(pareja(2)).getAllByRole("listitem").map(textoDe)).toEqual([
      "VSValentina SosaRío Ceballos · RevésNivel 4,5",
      "FLFederico LunaVilla Allende · DriveNivel 5,0",
    ]);
  });

  it("HU-012 C2, P2: muestra el resultado de equilibrio guardado como información", async () => {
    renderizar();
    await esperarPropuesta();

    const resultado = screen.getByRole("region", {
      name: "Resultado de equilibrio · informativo",
    });
    expect(within(resultado).getByText("1,00")).toBeTruthy();
    expect(
      within(resultado).getByText(/se muestra solo como información\.$/),
    ).toBeTruthy();
    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("HU-012 P3: las combinaciones evaluadas arrancan cerradas y muestran las 3 con su nota", async () => {
    renderizar();
    await esperarPropuesta();

    const resumen = screen.getByText("Ver combinaciones evaluadas");
    const desplegable = resumen.closest("details");
    expect(desplegable.open).toBe(false);

    fireEvent.click(resumen);

    expect(desplegable.open).toBe(true);
    const tabla = within(desplegable).getByRole("table");
    expect(within(tabla).getAllByRole("columnheader").map(textoDe)).toEqual([
      "N.º",
      "Parejas",
      "Promedios",
      "Equilibrio nivel",
      "Equilibrio lado",
      "Puntaje",
    ]);
    const [, ...filas] = within(tabla).getAllByRole("row");
    expect(
      filas.map((fila) => within(fila).getAllByRole("cell").map(textoDe)),
    ).toEqual([
      [
        "1",
        "Tomás + Valentina vs Camila + Federico" +
          "Mismo equilibrio de lado que la n.º 2, pero más diferencia de nivel entre las parejas.",
        "4,50 vs 5,00",
        "0,75",
        "1,00",
        "0,80",
      ],
      [
        "2",
        "Tomás + Camila vs Valentina + Federico",
        "4,75 vs 4,75",
        "1,00",
        "1,00",
        "1,00Seleccionada",
      ],
      [
        "3",
        "Tomás + Federico vs Valentina + Camila" +
          "Mismo nivel que la n.º 2, pero ambas parejas repiten lado (Drive + Drive y Revés + Revés).",
        "4,75 vs 4,75",
        "1,00",
        "0,00",
        "0,80",
      ],
    ]);
  });

  it("ofrece volver al inicio", async () => {
    renderizar();
    await esperarPropuesta();

    const enlace = within(screen.getByRole("main")).getByRole("link", {
      name: "Volver al inicio",
    });
    expect(enlace.getAttribute("href")).toBe("/inicio");
  });

  it("si el encuentro todavía no tiene propuesta, lleva al inicio", async () => {
    obtenerPropuesta.mockRejectedValue(
      new ErrorApi({
        estado: 409,
        detalle: "Este encuentro todavía no tiene una propuesta.",
      }),
    );
    renderizar();

    expect(
      await screen.findByRole("heading", { level: 1, name: "Inicio" }),
    ).toBeTruthy();
  });

  it("HU-012 P1: a quien no participa le muestra el error del backend", async () => {
    obtenerPropuesta.mockRejectedValue(
      new ErrorApi({ estado: 404, detalle: "El encuentro no existe." }),
    );
    renderizar();

    expect(await screen.findByText("El encuentro no existe.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Reintentar" })).toBeTruthy();
  });
});
