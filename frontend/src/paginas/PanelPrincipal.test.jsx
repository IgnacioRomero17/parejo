import { render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import PanelPrincipal from "./PanelPrincipal.jsx";

function renderizar(entrada) {
  const sesion = {
    cargando: false,
    usuario: { id: 1, nombre: "Tomás", onboarding: null },
    establecerUsuario: () => {},
  };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={[entrada]}>
        <Routes>
          <Route path="/inicio" element={<PanelPrincipal />} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

describe("PanelPrincipal", () => {
  it("saluda al jugador por su nombre", () => {
    renderizar("/inicio");

    expect(
      screen.getByRole("heading", { level: 1, name: "Hola, Tomás" }),
    ).toBeTruthy();
    expect(screen.queryByRole("status")).toBeNull();
  });

  it("HU-006: ofrece crear un encuentro", () => {
    renderizar("/inicio");

    // Además del enlace de la barra superior, el botón del encabezado.
    const boton = within(screen.getByRole("main")).getByRole("link", {
      name: "Crear encuentro",
    });
    expect(boton.getAttribute("href")).toBe("/encuentros/nuevo");
  });

  it("muestra el aviso con el que se llega", () => {
    renderizar({
      pathname: "/inicio",
      state: {
        aviso: "Disponibilidad y preferencias guardadas correctamente.",
      },
    });

    expect(screen.getByRole("status").textContent).toBe(
      "Disponibilidad y preferencias guardadas correctamente.",
    );
  });
});
