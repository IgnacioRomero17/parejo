import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ErrorApi } from "../api/cliente.js";
import { obtenerEncuentro, obtenerRecomendados } from "../api/encuentros.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import JugadoresRecomendados from "./JugadoresRecomendados.jsx";

vi.mock("../api/encuentros.js", () => ({
  obtenerEncuentro: vi.fn(),
  obtenerRecomendados: vi.fn(),
}));

const ENCUENTRO = {
  id: 15,
  fecha: "2026-10-03",
  hora_inicio: "18:00",
  duracion_minutos: 90,
  localidad: { id: 7, nombre: "Río Ceballos" },
  ubicacion: "Av. San Martín 4500",
  tipo_encuentro: "COMPETITIVO",
  estado: "BUSCANDO_PARTICIPANTES",
  confirmados: 1,
};

function recomendado(id, nombre, apellido, localidad, nivel, inicio, fin) {
  return {
    id,
    nombre,
    apellido,
    localidad: { id: id + 100, nombre: localidad },
    nivel,
    franja: { dia_semana: 6, hora_inicio: inicio, hora_fin: fin },
  };
}

const RECOMENDADOS = [
  recomendado(2, "Valentina", "Sosa", "Río Ceballos", 4.5, "17:00", "21:00"),
  recomendado(3, "Joaquín", "Medina", "Unquillo", 4.5, "16:00", "20:00"),
  recomendado(4, "Camila", "Paz", "Mendiolaza", 5, "18:00", "22:00"),
  recomendado(5, "Federico", "Luna", "Villa Allende", 5, "15:00", "20:00"),
];

const SUFICIENTES = {
  lugares_libres: 3,
  suficientes: true,
  recomendados: RECOMENDADOS,
};

function renderizar(entrada = "/encuentros/15/recomendados") {
  const sesion = {
    cargando: false,
    usuario: { id: 1, nombre: "Tomás", onboarding: null },
    establecerUsuario: vi.fn(),
  };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={[entrada]}>
        <Routes>
          <Route
            path="/encuentros/:id/recomendados"
            element={<JugadoresRecomendados />}
          />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

async function esperarPantalla() {
  return screen.findByRole("heading", {
    level: 1,
    name: "Jugadores recomendados para este encuentro",
  });
}

function tarjetas() {
  const grilla = screen.getByRole("list", { name: "Jugadores recomendados" });
  return within(grilla).getAllByRole("listitem");
}

function textoDe(elemento) {
  return elemento.textContent.replace(/\s+/g, " ").trim();
}

describe("JugadoresRecomendados", () => {
  beforeEach(() => {
    obtenerEncuentro.mockReset().mockResolvedValue(ENCUENTRO);
    obtenerRecomendados.mockReset().mockResolvedValue(SUFICIENTES);
  });

  it("muestra las condiciones del encuentro", async () => {
    renderizar();
    await esperarPantalla();

    expect(obtenerEncuentro).toHaveBeenCalledWith("15");
    expect(obtenerRecomendados).toHaveBeenCalledWith("15");
    for (const texto of [
      "Buscando participantes",
      "Sáb 3 oct 2026",
      "18:00",
      "90 min",
      "Río Ceballos · Av. San Martín 4500",
      "Competitivo",
      "1 de 4",
      "· faltan 3",
    ]) {
      expect(screen.getByText(texto)).toBeTruthy();
    }
  });

  it("C3: muestra la grilla en el orden del backend, con posición, nivel y franja", async () => {
    renderizar();
    await esperarPantalla();

    expect(tarjetas().map(textoDe)).toEqual([
      "1VSValentina SosaRío CeballosNivel 4,5Disponible sáb 17:00–21:00",
      "2JMJoaquín MedinaUnquilloNivel 4,5Disponible sáb 16:00–20:00",
      "3CPCamila PazMendiolazaNivel 5,0Disponible sáb 18:00–22:00",
      "4FLFederico LunaVilla AllendeNivel 5,0Disponible sáb 15:00–20:00",
    ]);
  });

  it("muestra cuántos jugadores se pueden invitar, sin aviso de insuficientes", async () => {
    renderizar();
    await esperarPantalla();

    expect(textoDe(screen.getByText(/Podés invitar hasta/).closest("p"))).toBe(
      "Podés invitar hasta 3 jugadores para completar el encuentro.",
    );
    expect(screen.queryByText(/No se encontraron suficientes/)).toBeNull();
  });

  it("HU-008: el botón Seleccionar e invitar lleva al seguimiento del encuentro", async () => {
    renderizar();
    await esperarPantalla();

    expect(
      screen
        .getByRole("link", { name: "Seleccionar e invitar" })
        .getAttribute("href"),
    ).toBe("/encuentros/15");
  });

  it("no muestra el puntaje de compatibilidad", async () => {
    obtenerRecomendados.mockResolvedValue({
      ...SUFICIENTES,
      recomendados: RECOMENDADOS.map((jugador) => ({
        ...jugador,
        puntaje: 0.9453,
      })),
    });
    renderizar();
    await esperarPantalla();

    expect(screen.queryByText(/0[,.]9453/)).toBeNull();
  });

  it("C4: con menos candidatos que lugares libres, avisa y muestra los que hay", async () => {
    obtenerRecomendados.mockResolvedValue({
      lugares_libres: 3,
      suficientes: false,
      recomendados: RECOMENDADOS.slice(0, 1),
    });
    renderizar();
    await esperarPantalla();

    expect(textoDe(screen.getByRole("status"))).toBe(
      "No se encontraron suficientes participantes compatibles. Hay 1 jugador para 3 lugares libres.",
    );
    expect(tarjetas()).toHaveLength(1);
  });

  it("usa el singular con un solo lugar libre", async () => {
    obtenerRecomendados.mockResolvedValue({
      lugares_libres: 1,
      suficientes: true,
      recomendados: RECOMENDADOS,
    });
    renderizar();
    await esperarPantalla();

    expect(textoDe(screen.getByText(/Podés invitar hasta/).closest("p"))).toBe(
      "Podés invitar hasta 1 jugador para completar el encuentro.",
    );
  });

  it("C4: sin candidatos muestra la pantalla 11", async () => {
    obtenerRecomendados.mockResolvedValue({
      lugares_libres: 3,
      suficientes: false,
      recomendados: [],
    });
    renderizar();

    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "No se encontraron suficientes participantes compatibles",
      }),
    ).toBeTruthy();
    expect(
      screen.getByText(
        "Con las condiciones de este encuentro no hay jugadores suficientes para completar los 3 lugares libres.",
      ),
    ).toBeTruthy();
    expect(
      screen
        .getByRole("link", { name: "Volver al inicio" })
        .getAttribute("href"),
    ).toBe("/inicio");
    expect(screen.queryByText(/Podés invitar hasta/)).toBeNull();
  });

  it("pantalla 11 en singular con un lugar libre", async () => {
    obtenerRecomendados.mockResolvedValue({
      lugares_libres: 1,
      suficientes: false,
      recomendados: [],
    });
    renderizar();

    expect(
      await screen.findByText(
        "Con las condiciones de este encuentro no hay jugadores suficientes para completar el lugar libre.",
      ),
    ).toBeTruthy();
  });

  it("sin lugares libres no muestra grilla ni barra inferior", async () => {
    obtenerRecomendados.mockResolvedValue({
      lugares_libres: 0,
      suficientes: true,
      recomendados: RECOMENDADOS,
    });
    renderizar();
    await esperarPantalla();

    expect(
      screen.getByText(
        "No quedan lugares libres. Esperá la respuesta de las invitaciones pendientes.",
      ),
    ).toBeTruthy();
    expect(screen.queryByText("Valentina Sosa")).toBeNull();
    expect(screen.queryByText(/Podés invitar hasta/)).toBeNull();
  });

  it("muestra el aviso con el que se llega al crear el encuentro", async () => {
    renderizar({
      pathname: "/encuentros/15/recomendados",
      state: { aviso: "Encuentro creado correctamente." },
    });
    await esperarPantalla();

    expect(screen.getByRole("status").textContent).toBe(
      "Encuentro creado correctamente.",
    );
  });

  it("si los recomendados no se pueden cargar, muestra el error y permite reintentar", async () => {
    obtenerRecomendados.mockRejectedValueOnce(
      new ErrorApi({ estado: 404, detalle: "El encuentro no existe." }),
    );
    renderizar();

    expect(await screen.findByText("El encuentro no existe.")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Reintentar" }));

    expect(await esperarPantalla()).toBeTruthy();
    expect(obtenerRecomendados).toHaveBeenCalledTimes(2);
  });
});
