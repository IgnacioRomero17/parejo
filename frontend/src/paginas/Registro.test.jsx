import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { registrarse } from "../api/auth.js";
import { ErrorApi } from "../api/cliente.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import Registro from "./Registro.jsx";

vi.mock("../api/auth.js", () => ({ registrarse: vi.fn() }));

const MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar.";
const MENSAJE_POLITICA =
  "La contraseña debe tener entre 8 y 64 caracteres, con al menos una letra y un número.";
const MENSAJE_CORREO_REGISTRADO = "Este correo ya está registrado.";

let establecerUsuario;

function renderizar() {
  establecerUsuario = vi.fn();
  const sesion = { cargando: false, usuario: null, establecerUsuario };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={["/registro"]}>
        <Routes>
          <Route path="/registro" element={<Registro />} />
          <Route path="/onboarding/perfil" element={<p>Onboarding perfil</p>} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

function completar(campos) {
  const etiquetas = {
    nombre: "Nombre",
    apellido: "Apellido",
    email: "Correo electrónico",
    contrasena: "Contraseña",
  };
  for (const [campo, valor] of Object.entries(campos)) {
    fireEvent.change(screen.getByLabelText(etiquetas[campo]), {
      target: { value: valor },
    });
  }
}

function completarTodo() {
  completar({
    nombre: "Tomás",
    apellido: "Ríos",
    email: "tomas.rios@example.com",
    contrasena: "clave1234",
  });
}

function enviar() {
  fireEvent.click(screen.getByRole("button", { name: "Registrarse" }));
}

function mensajeDe(etiqueta) {
  const campo = screen.getByLabelText(etiqueta);
  const idMensaje = campo.getAttribute("aria-describedby");
  return idMensaje ? document.getElementById(idMensaje).textContent : null;
}

describe("Registro (HU-001)", () => {
  beforeEach(() => {
    registrarse.mockReset();
  });

  it("arranca con los campos vacíos y sin errores", () => {
    renderizar();

    expect(
      screen.getByRole("heading", { level: 1, name: "Crear cuenta" }),
    ).toBeTruthy();
    expect(screen.getByText("Todos los campos son requeridos.")).toBeTruthy();
    for (const etiqueta of [
      "Nombre",
      "Apellido",
      "Correo electrónico",
      "Contraseña",
    ]) {
      expect(screen.getByLabelText(etiqueta).value).toBe("");
      expect(
        screen.getByLabelText(etiqueta).getAttribute("aria-invalid"),
      ).toBeNull();
    }
    expect(document.title).toBe("Registro · parejo");
  });

  it("C3: avisa que todos los campos son requeridos sin llamar a la API", () => {
    renderizar();

    enviar();

    expect(screen.getAllByText(MENSAJE_CAMPO_VACIO)).toHaveLength(4);
    expect(mensajeDe("Nombre")).toBe(MENSAJE_CAMPO_VACIO);
    expect(
      screen.getByLabelText("Contraseña").getAttribute("aria-invalid"),
    ).toBe("true");
    expect(registrarse).not.toHaveBeenCalled();
  });

  it("C3: marca solo el campo que falta", () => {
    renderizar();
    completarTodo();
    completar({ apellido: "  " });

    enviar();

    expect(mensajeDe("Apellido")).toBe(MENSAJE_CAMPO_VACIO);
    expect(mensajeDe("Nombre")).toBeNull();
    expect(registrarse).not.toHaveBeenCalled();
  });

  it("C1: muestra el error de correo ya registrado en su campo", async () => {
    registrarse.mockRejectedValue(
      new ErrorApi({
        estado: 400,
        errores: { email: [MENSAJE_CORREO_REGISTRADO] },
      }),
    );
    renderizar();
    completarTodo();

    enviar();

    await screen.findByText(MENSAJE_CORREO_REGISTRADO);
    expect(mensajeDe("Correo electrónico")).toBe(MENSAJE_CORREO_REGISTRADO);
    expect(
      screen.getByLabelText("Correo electrónico").getAttribute("aria-invalid"),
    ).toBe("true");
  });

  it("C2: muestra la política de contraseña", async () => {
    registrarse.mockRejectedValue(
      new ErrorApi({
        estado: 400,
        errores: { contrasena: [MENSAJE_POLITICA] },
      }),
    );
    renderizar();
    completarTodo();
    completar({ contrasena: "clave" });

    enviar();

    await screen.findByText(MENSAJE_POLITICA);
    expect(mensajeDe("Contraseña")).toBe(MENSAJE_POLITICA);
  });

  it("muestra varios errores a la vez", async () => {
    registrarse.mockRejectedValue(
      new ErrorApi({
        estado: 400,
        errores: {
          email: [MENSAJE_CORREO_REGISTRADO],
          contrasena: [MENSAJE_POLITICA],
        },
      }),
    );
    renderizar();
    completarTodo();

    enviar();

    await screen.findByText(MENSAJE_CORREO_REGISTRADO);
    expect(screen.getByText(MENSAJE_POLITICA)).toBeTruthy();
  });

  it("muestra los errores generales arriba del formulario", async () => {
    registrarse.mockRejectedValue(
      new ErrorApi({
        detalle:
          "No pudimos conectar con el servidor. Probá de nuevo en unos minutos.",
      }),
    );
    renderizar();
    completarTodo();

    enviar();

    const alerta = await screen.findByRole("alert");
    expect(alerta.textContent).toContain(
      "No pudimos conectar con el servidor.",
    );
    expect(screen.getByRole("button", { name: "Registrarse" }).disabled).toBe(
      false,
    );
  });

  it("deshabilita el botón mientras espera la respuesta", async () => {
    registrarse.mockReturnValue(new Promise(() => {}));
    renderizar();
    completarTodo();

    enviar();

    expect(screen.getByRole("button", { name: "Registrarse" }).disabled).toBe(
      true,
    );
    expect(registrarse).toHaveBeenCalledOnce();
  });

  it("P5: al registrarse inicia la sesión y lleva al onboarding paso 1", async () => {
    const usuario = { id: 7, nombre: "Tomás", onboarding: "perfil" };
    registrarse.mockResolvedValue(usuario);
    renderizar();
    completarTodo();

    enviar();

    await screen.findByText("Onboarding perfil");
    expect(registrarse).toHaveBeenCalledWith({
      nombre: "Tomás",
      apellido: "Ríos",
      email: "tomas.rios@example.com",
      contrasena: "clave1234",
    });
    expect(establecerUsuario).toHaveBeenCalledWith(usuario);
  });

  it("enlaza a iniciar sesión", () => {
    renderizar();

    const enlace = screen.getByRole("link", { name: "Iniciar sesión" });
    expect(enlace.getAttribute("href")).toBe("/ingresar");
  });
});
