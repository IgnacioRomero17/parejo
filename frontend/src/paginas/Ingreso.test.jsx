import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ingresar } from "../api/auth.js";
import { ErrorApi } from "../api/cliente.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import Ingreso from "./Ingreso.jsx";

vi.mock("../api/auth.js", () => ({ ingresar: vi.fn() }));

const MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar.";
const MENSAJE_CREDENCIALES = "Las credenciales ingresadas no son válidas.";

let establecerUsuario;

function renderizar() {
  establecerUsuario = vi.fn();
  const sesion = { cargando: false, usuario: null, establecerUsuario };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={["/ingresar"]}>
        <Routes>
          <Route path="/ingresar" element={<Ingreso />} />
          <Route path="/onboarding/perfil" element={<p>Onboarding perfil</p>} />
          <Route path="/inicio" element={<p>Panel principal</p>} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

function completar({ email, contrasena }) {
  fireEvent.change(screen.getByLabelText("Correo electrónico"), {
    target: { value: email },
  });
  fireEvent.change(screen.getByLabelText("Contraseña"), {
    target: { value: contrasena },
  });
}

function completarTodo() {
  completar({ email: "tomas.rios@example.com", contrasena: "clave1234" });
}

function enviar() {
  fireEvent.click(screen.getByRole("button", { name: "Ingresar" }));
}

function mensajeDe(etiqueta) {
  const campo = screen.getByLabelText(etiqueta);
  const idMensaje = campo.getAttribute("aria-describedby");
  return idMensaje ? document.getElementById(idMensaje).textContent : null;
}

describe("Ingreso (HU-002)", () => {
  beforeEach(() => {
    ingresar.mockReset();
  });

  it("arranca con los campos vacíos y sin errores", () => {
    renderizar();

    expect(
      screen.getByRole("heading", { level: 1, name: "Iniciar sesión" }),
    ).toBeTruthy();
    for (const etiqueta of ["Correo electrónico", "Contraseña"]) {
      expect(screen.getByLabelText(etiqueta).value).toBe("");
      expect(
        screen.getByLabelText(etiqueta).getAttribute("aria-invalid"),
      ).toBeNull();
    }
    expect(screen.getByLabelText("Contraseña").type).toBe("password");
    expect(screen.queryByRole("alert")).toBeNull();
    expect(document.title).toBe("Iniciar sesión · parejo");
  });

  it("avisa los campos vacíos sin llamar a la API", () => {
    renderizar();

    enviar();

    expect(mensajeDe("Correo electrónico")).toBe(MENSAJE_CAMPO_VACIO);
    expect(mensajeDe("Contraseña")).toBe(MENSAJE_CAMPO_VACIO);
    expect(ingresar).not.toHaveBeenCalled();
  });

  it("marca solo el campo que falta", () => {
    renderizar();
    completar({ email: "tomas.rios@example.com", contrasena: "" });

    enviar();

    expect(mensajeDe("Contraseña")).toBe(MENSAJE_CAMPO_VACIO);
    expect(mensajeDe("Correo electrónico")).toBeNull();
    expect(ingresar).not.toHaveBeenCalled();
  });

  it("C1: con onboarding pendiente inicia la sesión y lleva a ese paso", async () => {
    const usuario = { id: 7, nombre: "Tomás", onboarding: "perfil" };
    ingresar.mockResolvedValue(usuario);
    renderizar();
    completarTodo();

    enviar();

    await screen.findByText("Onboarding perfil");
    expect(ingresar).toHaveBeenCalledWith({
      email: "tomas.rios@example.com",
      contrasena: "clave1234",
    });
    expect(establecerUsuario).toHaveBeenCalledWith(usuario);
  });

  it("C1: con onboarding completo lleva al panel principal", async () => {
    const usuario = { id: 7, nombre: "Tomás", onboarding: null };
    ingresar.mockResolvedValue(usuario);
    renderizar();
    completarTodo();

    enviar();

    await screen.findByText("Panel principal");
    expect(establecerUsuario).toHaveBeenCalledWith(usuario);
  });

  it("C2 y C3: muestra el error de credenciales arriba del formulario", async () => {
    ingresar.mockRejectedValue(
      new ErrorApi({ estado: 400, detalle: MENSAJE_CREDENCIALES }),
    );
    renderizar();
    completarTodo();

    enviar();

    const alerta = await screen.findByRole("alert");
    expect(alerta.textContent).toBe(MENSAJE_CREDENCIALES);
    expect(establecerUsuario).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "Ingresar" }).disabled).toBe(
      false,
    );
  });

  it("borra el error anterior al volver a enviar", async () => {
    ingresar.mockRejectedValueOnce(
      new ErrorApi({ estado: 400, detalle: MENSAJE_CREDENCIALES }),
    );
    ingresar.mockReturnValueOnce(new Promise(() => {}));
    renderizar();
    completarTodo();
    enviar();
    await screen.findByRole("alert");

    enviar();

    expect(screen.queryByRole("alert")).toBeNull();
  });

  it("deshabilita el botón mientras espera la respuesta", () => {
    ingresar.mockReturnValue(new Promise(() => {}));
    renderizar();
    completarTodo();

    enviar();

    expect(screen.getByRole("button", { name: "Ingresar" }).disabled).toBe(
      true,
    );
    expect(ingresar).toHaveBeenCalledOnce();
  });

  it("enlaza a recuperar la contraseña y a registrarse", () => {
    renderizar();

    expect(
      screen
        .getByRole("link", { name: "¿Olvidaste tu contraseña?" })
        .getAttribute("href"),
    ).toBe("/recuperar");
    expect(
      screen.getByRole("link", { name: "Registrate" }).getAttribute("href"),
    ).toBe("/registro");
  });
});
