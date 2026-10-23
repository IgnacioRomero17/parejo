import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";
import RecuperacionEnviado from "./RecuperacionEnviado.jsx";

function renderizar(entrada) {
  return render(
    <MemoryRouter initialEntries={[entrada]}>
      <Routes>
        <Route path="/recuperar/enviado" element={<RecuperacionEnviado />} />
        <Route path="/recuperar" element={<p>Paso 1</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("Recuperación · paso 2 (HU-003)", () => {
  it("muestra el correo al que se envió el enlace", () => {
    renderizar({
      pathname: "/recuperar/enviado",
      state: { email: "tomas.rios@example.com" },
    });

    expect(screen.getByText("Paso 2 de 3")).toBeTruthy();
    expect(
      screen.getByRole("heading", { level: 1, name: "Revisá tu correo" }),
    ).toBeTruthy();
    const correo = screen.getByText("tomas.rios@example.com");
    expect(correo.tagName).toBe("STRONG");
    expect(correo.parentElement.textContent).toBe(
      "Te enviamos un enlace a tomas.rios@example.com. Abrilo para definir tu nueva contraseña.",
    );
    expect(
      screen.getByText(
        "¿No lo encontrás? Revisá la carpeta de correo no deseado.",
      ),
    ).toBeTruthy();
    expect(document.title).toBe("Revisá tu correo · parejo");
  });

  it("sin un correo previo redirige al paso 1", () => {
    renderizar("/recuperar/enviado");

    expect(screen.getByText("Paso 1")).toBeTruthy();
  });

  it("enlaza a iniciar sesión y a usar otro correo", () => {
    renderizar({
      pathname: "/recuperar/enviado",
      state: { email: "tomas.rios@example.com" },
    });

    expect(
      screen
        .getByRole("link", { name: "Volver a iniciar sesión" })
        .getAttribute("href"),
    ).toBe("/ingresar");
    expect(
      screen
        .getByRole("link", { name: "Usar otro correo" })
        .getAttribute("href"),
    ).toBe("/recuperar");
  });
});
