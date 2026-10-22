import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import RutaPublica from "./RutaPublica.jsx";

function renderizar(sesion) {
  const valor = {
    cargando: false,
    usuario: null,
    establecerUsuario: () => {},
    ...sesion,
  };
  return render(
    <ContextoSesion.Provider value={valor}>
      <MemoryRouter initialEntries={["/registro"]}>
        <Routes>
          <Route element={<RutaPublica />}>
            <Route path="/registro" element={<p>Formulario de registro</p>} />
          </Route>
          <Route path="/onboarding/perfil" element={<p>Onboarding perfil</p>} />
          <Route path="/inicio" element={<p>Panel principal</p>} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

describe("RutaPublica", () => {
  it("muestra la página si no hay sesión", () => {
    renderizar({ usuario: null });

    expect(screen.getByText("Formulario de registro")).toBeTruthy();
  });

  it("no muestra nada mientras se consulta la sesión", () => {
    const { container } = renderizar({ cargando: true });

    expect(container.textContent).toBe("");
  });

  it("con sesión y perfil pendiente lleva al onboarding", () => {
    renderizar({ usuario: { id: 1, onboarding: "perfil" } });

    expect(screen.getByText("Onboarding perfil")).toBeTruthy();
    expect(screen.queryByText("Formulario de registro")).toBeNull();
  });

  it("con sesión y onboarding completo lleva al panel principal", () => {
    renderizar({ usuario: { id: 1, onboarding: null } });

    expect(screen.getByText("Panel principal")).toBeTruthy();
  });
});
