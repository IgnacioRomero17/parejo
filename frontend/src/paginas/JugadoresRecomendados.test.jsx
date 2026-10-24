import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ErrorApi } from "../api/cliente.js";
import { obtenerEncuentro } from "../api/encuentros.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import JugadoresRecomendados from "./JugadoresRecomendados.jsx";

vi.mock("../api/encuentros.js", () => ({ obtenerEncuentro: vi.fn() }));

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

describe("JugadoresRecomendados (versión parcial de HU-006)", () => {
  beforeEach(() => {
    obtenerEncuentro.mockReset().mockResolvedValue(ENCUENTRO);
  });

  it("C3: muestra las condiciones del encuentro creado", async () => {
    renderizar();
    await esperarPantalla();

    expect(obtenerEncuentro).toHaveBeenCalledWith("15");
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

  it("si el encuentro no se puede cargar, muestra el error y permite reintentar", async () => {
    obtenerEncuentro.mockRejectedValueOnce(
      new ErrorApi({ estado: 404, detalle: "El encuentro no existe." }),
    );
    renderizar();

    expect(await screen.findByText("El encuentro no existe.")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Reintentar" }));

    expect(await esperarPantalla()).toBeTruthy();
    expect(obtenerEncuentro).toHaveBeenCalledTimes(2);
  });
});
