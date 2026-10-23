import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import RutaPrivada from "./RutaPrivada.jsx";

function renderizar(sesion) {
  const valor = {
    cargando: false,
    usuario: null,
    establecerUsuario: () => {},
    ...sesion,
  };
  return render(
    <ContextoSesion.Provider value={valor}>
      <MemoryRouter initialEntries={["/inicio"]}>
        <Routes>
          <Route element={<RutaPrivada />}>
            <Route path="/inicio" element={<p>Panel principal</p>} />
          </Route>
          <Route path="/ingresar" element={<p>Inicio de sesión</p>} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

describe("RutaPrivada (HU-002)", () => {
  it("P2: sin sesión lleva al inicio de sesión", () => {
    renderizar({ usuario: null });

    expect(screen.getByText("Inicio de sesión")).toBeTruthy();
    expect(screen.queryByText("Panel principal")).toBeNull();
  });

  it("no muestra nada mientras se consulta la sesión", () => {
    const { container } = renderizar({ cargando: true });

    expect(container.textContent).toBe("");
  });

  it("con sesión muestra la página", () => {
    renderizar({ usuario: { id: 1, onboarding: null } });

    expect(screen.getByText("Panel principal")).toBeTruthy();
  });
});
