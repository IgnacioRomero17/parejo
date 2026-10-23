import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import RutaConOnboarding from "./RutaConOnboarding.jsx";
import RutaPrivada from "./RutaPrivada.jsx";

function renderizar(usuario) {
  const sesion = { cargando: false, usuario, establecerUsuario: () => {} };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={["/perfil"]}>
        <Routes>
          <Route element={<RutaPrivada />}>
            <Route element={<RutaConOnboarding />}>
              <Route path="/perfil" element={<p>Mi perfil</p>} />
            </Route>
            <Route
              path="/onboarding/perfil"
              element={<p>Onboarding perfil</p>}
            />
          </Route>
          <Route path="/ingresar" element={<p>Inicio de sesión</p>} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

describe("RutaConOnboarding (HU-004)", () => {
  it("P8: con el perfil pendiente lleva al paso 1 del onboarding", () => {
    renderizar({ id: 1, onboarding: "perfil" });

    expect(screen.getByText("Onboarding perfil")).toBeTruthy();
    expect(screen.queryByText("Mi perfil")).toBeNull();
  });

  it("con el onboarding completo muestra la página", () => {
    renderizar({ id: 1, onboarding: null });

    expect(screen.getByText("Mi perfil")).toBeTruthy();
  });

  it("sin sesión, RutaPrivada lleva antes al inicio de sesión", () => {
    renderizar(null);

    expect(screen.getByText("Inicio de sesión")).toBeTruthy();
  });
});
