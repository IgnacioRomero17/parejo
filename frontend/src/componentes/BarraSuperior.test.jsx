import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import BarraSuperior from "./BarraSuperior.jsx";

function renderizar(invitacionesPendientes, props = {}) {
  const sesion = {
    cargando: false,
    usuario: {
      id: 1,
      nombre: "Tomás",
      onboarding: null,
      invitaciones_pendientes: invitacionesPendientes,
    },
    establecerUsuario: () => {},
  };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter>
        <BarraSuperior {...props} />
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

function enlaceInvitaciones() {
  return screen.getByRole("link", { name: /^Invitaciones/ });
}

describe("BarraSuperior · indicador de invitaciones (HU-008)", () => {
  it("con invitaciones pendientes muestra la cantidad", () => {
    renderizar(3);

    expect(enlaceInvitaciones().textContent).toBe(
      "Invitaciones3, 3 invitaciones pendientes",
    );
    expect(
      screen.getByRole("link", { name: /, 3 invitaciones pendientes$/ }),
    ).toBeTruthy();
  });

  it("con una sola usa el singular", () => {
    renderizar(1);

    expect(enlaceInvitaciones().textContent).toBe(
      "Invitaciones1, 1 invitación pendiente",
    );
  });

  it("sin pendientes no muestra el indicador", () => {
    renderizar(0);

    expect(enlaceInvitaciones().textContent).toBe("Invitaciones");
  });

  it("en el onboarding no muestra enlaces", () => {
    renderizar(2, { soloLogo: true });

    expect(screen.queryByRole("link")).toBeNull();
  });
});
