import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { solicitarRecuperacion } from "../api/auth.js";
import { ErrorApi } from "../api/cliente.js";
import RecuperacionCorreo from "./RecuperacionCorreo.jsx";

vi.mock("../api/auth.js", () => ({ solicitarRecuperacion: vi.fn() }));

const MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar.";
const MENSAJE_CUENTA_INEXISTENTE =
  "La cuenta no existe. Revisá el correo ingresado.";

function DestinoEnviado() {
  return <p>Enviado a {useLocation().state?.email}</p>;
}

function renderizar() {
  return render(
    <MemoryRouter initialEntries={["/recuperar"]}>
      <Routes>
        <Route path="/recuperar" element={<RecuperacionCorreo />} />
        <Route path="/recuperar/enviado" element={<DestinoEnviado />} />
        <Route path="/ingresar" element={<p>Inicio de sesión</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

function completar(email) {
  fireEvent.change(screen.getByLabelText("Correo electrónico"), {
    target: { value: email },
  });
}

function enviar() {
  fireEvent.click(screen.getByRole("button", { name: "Enviar enlace" }));
}

function mensajeDe(etiqueta) {
  const campo = screen.getByLabelText(etiqueta);
  const idMensaje = campo.getAttribute("aria-describedby");
  return idMensaje ? document.getElementById(idMensaje).textContent : null;
}

describe("Recuperación · paso 1 (HU-003)", () => {
  beforeEach(() => {
    solicitarRecuperacion.mockReset();
  });

  it("muestra el paso 1 con el campo vacío", () => {
    renderizar();

    expect(screen.getByText("Paso 1 de 3")).toBeTruthy();
    expect(
      screen.getByRole("heading", {
        level: 1,
        name: "¿Olvidaste tu contraseña?",
      }),
    ).toBeTruthy();
    expect(screen.getByLabelText("Correo electrónico").value).toBe("");
    expect(document.title).toBe("¿Olvidaste tu contraseña? · parejo");
  });

  it("avisa el campo vacío sin llamar a la API", () => {
    renderizar();

    enviar();

    expect(mensajeDe("Correo electrónico")).toBe(MENSAJE_CAMPO_VACIO);
    expect(solicitarRecuperacion).not.toHaveBeenCalled();
  });

  it("C1: envía el correo y lleva al paso 2 con el correo ingresado", async () => {
    solicitarRecuperacion.mockResolvedValue(null);
    renderizar();
    completar("tomas.rios@example.com");

    enviar();

    await screen.findByText("Enviado a tomas.rios@example.com");
    expect(solicitarRecuperacion).toHaveBeenCalledWith({
      email: "tomas.rios@example.com",
    });
  });

  it("C2: muestra que la cuenta no existe debajo del campo", async () => {
    solicitarRecuperacion.mockRejectedValue(
      new ErrorApi({
        estado: 400,
        errores: { email: [MENSAJE_CUENTA_INEXISTENTE] },
      }),
    );
    renderizar();
    completar("valentina.sosa@example.com");

    enviar();

    await screen.findByText(MENSAJE_CUENTA_INEXISTENTE);
    const campo = screen.getByLabelText("Correo electrónico");
    expect(campo.getAttribute("aria-invalid")).toBe("true");
    expect(mensajeDe("Correo electrónico")).toBe(MENSAJE_CUENTA_INEXISTENTE);
    expect(screen.getByRole("button", { name: "Enviar enlace" }).disabled).toBe(
      false,
    );
  });

  it("muestra los errores generales arriba del formulario", async () => {
    solicitarRecuperacion.mockRejectedValue(
      new ErrorApi({ detalle: "No pudimos conectar con el servidor." }),
    );
    renderizar();
    completar("tomas.rios@example.com");

    enviar();

    const alerta = await screen.findByRole("alert");
    expect(alerta.textContent).toBe("No pudimos conectar con el servidor.");
  });

  it("deshabilita el botón mientras espera la respuesta", () => {
    solicitarRecuperacion.mockReturnValue(new Promise(() => {}));
    renderizar();
    completar("tomas.rios@example.com");

    enviar();

    expect(screen.getByRole("button", { name: "Enviar enlace" }).disabled).toBe(
      true,
    );
    expect(solicitarRecuperacion).toHaveBeenCalledOnce();
  });

  it("enlaza a volver a iniciar sesión", () => {
    renderizar();

    expect(
      screen
        .getByRole("link", { name: "Volver a iniciar sesión" })
        .getAttribute("href"),
    ).toBe("/ingresar");
  });
});
