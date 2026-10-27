import { StrictMode } from "react";
import { act, fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ErrorApi } from "../api/cliente.js";
import { formarParejas, obtenerEncuentro } from "../api/encuentros.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import FormandoParejas from "./FormandoParejas.jsx";

vi.mock("../api/encuentros.js", () => ({
  formarParejas: vi.fn(),
  obtenerEncuentro: vi.fn(),
}));

function jugador(id, nombre, apellido) {
  return {
    id,
    nombre,
    apellido,
    localidad: { id: 7, nombre: "Río Ceballos" },
    nivel: 4.5,
    lado: "DRIVE",
  };
}

const PARTICIPANTES = [
  jugador(1, "Tomás", "Ríos"),
  jugador(2, "Valentina", "Sosa"),
  jugador(4, "Camila", "Paz"),
  jugador(5, "Federico", "Luna"),
];

const COMPLETO = {
  id: 15,
  fecha: "2026-10-03",
  hora_inicio: "18:00",
  duracion_minutos: 90,
  localidad: { id: 7, nombre: "Río Ceballos" },
  ubicacion: "Av. San Martín 4500",
  tipo_encuentro: "COMPETITIVO",
  estado: "COMPLETO",
  confirmados: 4,
  lugares_libres: 0,
  participantes: PARTICIPANTES,
  invitaciones: [],
};

const MENSAJE_ERROR = "No pudimos generar la propuesta. Intentá de nuevo.";

// Duración mínima de cada uno de los 3 pasos de la animación.
const PASO_MS = 1300;

function renderizar({ estricto = false } = {}) {
  const sesion = {
    cargando: false,
    usuario: { id: 1, nombre: "Tomás", onboarding: null },
    establecerUsuario: vi.fn(),
  };
  const arbol = (
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={["/encuentros/15/formando"]}>
        <Routes>
          <Route
            path="/encuentros/:id/formando"
            element={<FormandoParejas />}
          />
          <Route
            path="/encuentros/:id/propuesta"
            element={<h1>Propuesta</h1>}
          />
          <Route path="/inicio" element={<h1>Inicio</h1>} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>
  );
  return render(estricto ? <StrictMode>{arbol}</StrictMode> : arbol);
}

function textoDe(elemento) {
  return elemento.textContent.replace(/\s+/g, " ").trim();
}

// Las listas de la página, sin las de la barra superior.
function principal() {
  return within(screen.getByRole("main"));
}

function pasos() {
  return principal().getAllByRole("listitem").map(textoDe);
}

function esperarPantalla15() {
  return screen.findByRole("heading", {
    level: 1,
    name: "Generando una propuesta equilibrada",
  });
}

// Avanza los timers falsos y deja que se resuelvan las promesas pendientes.
async function avanzar(milisegundos) {
  await act(() => vi.advanceTimersByTimeAsync(milisegundos));
}

function sinRespuesta() {
  return new Promise(() => {});
}

describe("FormandoParejas · pantalla 15 (HU-009)", () => {
  beforeEach(() => {
    obtenerEncuentro.mockReset().mockResolvedValue(COMPLETO);
    formarParejas.mockReset().mockReturnValue(sinRespuesta());
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("muestra los participantes y los pasos, el primero en curso", async () => {
    renderizar();
    await esperarPantalla15();

    expect(
      screen.getByText(
        "Tomás Ríos · Valentina Sosa · Camila Paz · Federico Luna",
      ),
    ).toBeTruthy();
    expect(screen.getByRole("status").textContent).toBe("Paso 1 de 3");
    expect(pasos()).toEqual([
      "Evaluando las 3 combinaciones posiblesEn curso",
      "Formando parejas equilibradasEn espera",
      "Generando la propuesta de encuentroEn espera",
    ]);
    expect(
      screen.getByText("La propuesta se abrirá automáticamente al terminar."),
    ).toBeTruthy();
  });

  it("C1: inicia la evaluación llamando al backend una sola vez", async () => {
    renderizar({ estricto: true });
    await esperarPantalla15();

    expect(obtenerEncuentro).toHaveBeenCalledTimes(1);
    expect(formarParejas).toHaveBeenCalledTimes(1);
    expect(formarParejas).toHaveBeenCalledWith("15");
  });

  it("P4: aunque el backend responda enseguida, cada paso dura 1,3 s", async () => {
    vi.useFakeTimers();
    formarParejas.mockResolvedValue({});
    renderizar();
    await avanzar(0);

    expect(screen.getByRole("status").textContent).toBe("Paso 1 de 3");
    await avanzar(PASO_MS - 1);
    expect(screen.getByRole("status").textContent).toBe("Paso 1 de 3");
    await avanzar(1);
    expect(screen.getByRole("status").textContent).toBe("Paso 2 de 3");
    expect(pasos()[0]).toBe("Evaluando las 3 combinaciones posiblesListo");
    await avanzar(PASO_MS);
    expect(screen.getByRole("status").textContent).toBe("Paso 3 de 3");

    await avanzar(PASO_MS - 1);
    expect(screen.queryByRole("heading", { name: "Propuesta" })).toBeNull();
    await avanzar(1);
    expect(screen.getByRole("heading", { name: "Propuesta" })).toBeTruthy();
  });

  it("P4: los pasos empiezan a contar cuando se muestra el encuentro", async () => {
    vi.useFakeTimers();
    let cargar;
    obtenerEncuentro.mockReturnValue(
      new Promise((resolver) => {
        cargar = resolver;
      }),
    );
    formarParejas.mockResolvedValue({});
    renderizar();
    await avanzar(2 * PASO_MS);

    cargar(COMPLETO);
    await avanzar(0);
    expect(screen.getByRole("status").textContent).toBe("Paso 1 de 3");
  });

  it("P4: si el backend responde a mitad de los pasos, abre la propuesta al terminar el último", async () => {
    vi.useFakeTimers();
    let responder;
    formarParejas.mockReturnValue(
      new Promise((resolver) => {
        responder = resolver;
      }),
    );
    renderizar();
    await avanzar(0);
    await avanzar(PASO_MS);

    responder({});
    await avanzar(0);
    expect(screen.getByRole("status").textContent).toBe("Paso 2 de 3");
    await avanzar(PASO_MS);
    await avanzar(PASO_MS - 1);
    expect(screen.queryByRole("heading", { name: "Propuesta" })).toBeNull();
    await avanzar(1);
    expect(screen.getByRole("heading", { name: "Propuesta" })).toBeTruthy();
  });

  it("P4: si el backend tarda más que los pasos, abre la propuesta apenas responde", async () => {
    vi.useFakeTimers();
    let responder;
    formarParejas.mockReturnValue(
      new Promise((resolver) => {
        responder = resolver;
      }),
    );
    renderizar();
    await avanzar(0);
    // De a un paso: cada uno se programa cuando React termina de mostrar el anterior.
    for (let paso = 0; paso < 6; paso += 1) await avanzar(PASO_MS);

    expect(pasos()[2]).toBe("Generando la propuesta de encuentroEn curso");
    expect(screen.queryByRole("heading", { name: "Propuesta" })).toBeNull();

    responder({});
    await avanzar(0);
    expect(screen.getByRole("heading", { name: "Propuesta" })).toBeTruthy();
  });

  it("con la propuesta ya generada la abre sin volver a evaluar", async () => {
    obtenerEncuentro.mockResolvedValue({
      ...COMPLETO,
      estado: "PROPUESTA_GENERADA",
    });
    renderizar();

    expect(
      await screen.findByRole("heading", { level: 1, name: "Propuesta" }),
    ).toBeTruthy();
    expect(formarParejas).not.toHaveBeenCalled();
  });

  it("si el backend devuelve error, ofrece reintentar y volver al encuentro", async () => {
    formarParejas.mockRejectedValueOnce(
      new ErrorApi({ estado: 409, detalle: "Este encuentro ya comenzó." }),
    );
    renderizar();

    const alerta = await screen.findByRole("alert");
    expect(textoDe(alerta)).toBe(MENSAJE_ERROR);
    expect(principal().queryByRole("list")).toBeNull();
    const volver = screen.getByRole("link", { name: "Volver al encuentro" });
    expect(volver.getAttribute("href")).toBe("/encuentros/15");

    fireEvent.click(screen.getByRole("button", { name: "Reintentar" }));

    expect(await screen.findByRole("status")).toBeTruthy();
    expect(screen.queryByRole("alert")).toBeNull();
    expect(obtenerEncuentro).toHaveBeenCalledTimes(2);
    expect(formarParejas).toHaveBeenCalledTimes(2);
  });

  it("si no puede cargar el encuentro, permite reintentar", async () => {
    obtenerEncuentro.mockRejectedValueOnce(
      new ErrorApi({ estado: 404, detalle: "El encuentro no existe." }),
    );
    renderizar();

    const alerta = await screen.findByRole("alert");
    expect(within(alerta).getByText("El encuentro no existe.")).toBeTruthy();
    expect(formarParejas).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Reintentar" }));

    await esperarPantalla15();
    expect(formarParejas).toHaveBeenCalledTimes(1);
  });

  it("a un participante que no organiza lo lleva al inicio", async () => {
    const { invitaciones: _, ...sinInvitaciones } = COMPLETO;
    obtenerEncuentro.mockResolvedValue(sinInvitaciones);
    renderizar();

    expect(
      await screen.findByRole("heading", { level: 1, name: "Inicio" }),
    ).toBeTruthy();
    expect(formarParejas).not.toHaveBeenCalled();
  });
});
