import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  confirmarRecuperacion,
  validarEnlaceRecuperacion,
} from "../api/auth.js";
import { ErrorApi } from "../api/cliente.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import RecuperacionNueva from "./RecuperacionNueva.jsx";

vi.mock("../api/auth.js", () => ({
  confirmarRecuperacion: vi.fn(),
  validarEnlaceRecuperacion: vi.fn(),
}));

const AYUDA = "Entre 8 y 64 caracteres, con al menos una letra y un número.";
const MENSAJE_POLITICA =
  "La contraseña debe tener entre 8 y 64 caracteres, con al menos una letra y un número.";
const MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar.";
const ERROR_ENLACE = new ErrorApi({
  estado: 400,
  detalle: "El enlace no es válido.",
});

let establecerUsuario;

function renderizar() {
  establecerUsuario = vi.fn();
  const sesion = { cargando: false, usuario: null, establecerUsuario };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={["/recuperar/MQ/abc-123"]}>
        <Routes>
          <Route
            path="/recuperar/:uid/:token"
            element={<RecuperacionNueva />}
          />
          <Route path="/onboarding/perfil" element={<p>Onboarding perfil</p>} />
          <Route path="/inicio" element={<p>Panel principal</p>} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

async function renderizarConEnlaceValido() {
  validarEnlaceRecuperacion.mockResolvedValue({
    email: "tomas.rios@example.com",
  });
  renderizar();
  await screen.findByText("tomas.rios@example.com");
}

function completar(contrasena) {
  fireEvent.change(screen.getByLabelText("Nueva contraseña"), {
    target: { value: contrasena },
  });
}

function guardar() {
  fireEvent.click(
    screen.getByRole("button", { name: "Guardar e iniciar sesión" }),
  );
}

function mensajeDe(etiqueta) {
  const campo = screen.getByLabelText(etiqueta);
  return document.getElementById(campo.getAttribute("aria-describedby"))
    .textContent;
}

async function esperarEnlaceInvalido() {
  await screen.findByRole("heading", {
    level: 1,
    name: "El enlace no es válido",
  });
  expect(
    screen.getByText("Puede que ya lo hayas usado. Pedí uno nuevo."),
  ).toBeTruthy();
  expect(
    screen
      .getByRole("link", { name: "Pedir un nuevo enlace" })
      .getAttribute("href"),
  ).toBe("/recuperar");
  expect(screen.queryByLabelText("Nueva contraseña")).toBeNull();
}

describe("Recuperación · paso 3 (HU-003)", () => {
  beforeEach(() => {
    validarEnlaceRecuperacion.mockReset();
    confirmarRecuperacion.mockReset();
  });

  it("valida el enlace de la URL y muestra la cuenta", async () => {
    await renderizarConEnlaceValido();

    expect(validarEnlaceRecuperacion).toHaveBeenCalledWith("MQ", "abc-123");
    expect(screen.getByText("Paso 3 de 3")).toBeTruthy();
    expect(
      screen.getByRole("heading", { level: 1, name: "Nueva contraseña" }),
    ).toBeTruthy();
    expect(screen.getByText("tomas.rios@example.com").tagName).toBe("STRONG");
    expect(screen.getByLabelText("Nueva contraseña").type).toBe("password");
    expect(document.title).toBe("Nueva contraseña · parejo");
  });

  it("no muestra el formulario mientras valida el enlace", () => {
    validarEnlaceRecuperacion.mockReturnValue(new Promise(() => {}));
    renderizar();

    expect(screen.queryByLabelText("Nueva contraseña")).toBeNull();
  });

  it("P2: muestra la política como ayuda del campo", async () => {
    await renderizarConEnlaceValido();

    expect(mensajeDe("Nueva contraseña")).toBe(AYUDA);
    expect(
      screen.getByLabelText("Nueva contraseña").getAttribute("aria-invalid"),
    ).toBeNull();
  });

  it("P3: con un enlace inválido o usado muestra el aviso", async () => {
    validarEnlaceRecuperacion.mockRejectedValue(ERROR_ENLACE);
    renderizar();

    await esperarEnlaceInvalido();
  });

  it("avisa el campo vacío sin llamar a la API", async () => {
    await renderizarConEnlaceValido();

    guardar();

    expect(mensajeDe("Nueva contraseña")).toBe(MENSAJE_CAMPO_VACIO);
    expect(confirmarRecuperacion).not.toHaveBeenCalled();
  });

  it("P2: marca el campo si la contraseña no cumple la política", async () => {
    confirmarRecuperacion.mockRejectedValue(
      new ErrorApi({
        estado: 400,
        errores: { contrasena: [MENSAJE_POLITICA] },
      }),
    );
    await renderizarConEnlaceValido();
    completar("corta1");

    guardar();

    await screen.findByText(MENSAJE_POLITICA);
    expect(
      screen.getByLabelText("Nueva contraseña").getAttribute("aria-invalid"),
    ).toBe("true");
    expect(screen.queryByText(AYUDA)).toBeNull();
    expect(establecerUsuario).not.toHaveBeenCalled();
  });

  it("P5: guarda, inicia la sesión y lleva al onboarding pendiente", async () => {
    const usuario = { id: 7, nombre: "Tomás", onboarding: "perfil" };
    confirmarRecuperacion.mockResolvedValue(usuario);
    await renderizarConEnlaceValido();
    completar("nueva5678");

    guardar();

    await screen.findByText("Onboarding perfil");
    expect(confirmarRecuperacion).toHaveBeenCalledWith({
      uid: "MQ",
      token: "abc-123",
      contrasena: "nueva5678",
    });
    expect(establecerUsuario).toHaveBeenCalledWith(usuario);
  });

  it("P5: con el onboarding completo lleva al panel principal", async () => {
    confirmarRecuperacion.mockResolvedValue({ id: 7, onboarding: null });
    await renderizarConEnlaceValido();
    completar("nueva5678");

    guardar();

    await screen.findByText("Panel principal");
  });

  it("P3: si el enlace se usó mientras tanto, muestra el aviso", async () => {
    confirmarRecuperacion.mockRejectedValue(ERROR_ENLACE);
    await renderizarConEnlaceValido();
    completar("nueva5678");

    guardar();

    await esperarEnlaceInvalido();
  });

  it("deshabilita el botón mientras guarda", async () => {
    confirmarRecuperacion.mockReturnValue(new Promise(() => {}));
    await renderizarConEnlaceValido();
    completar("nueva5678");

    guardar();

    expect(
      screen.getByRole("button", { name: "Guardar e iniciar sesión" }).disabled,
    ).toBe(true);
  });

  it("sin conexión permite reintentar la validación", async () => {
    validarEnlaceRecuperacion
      .mockRejectedValueOnce(
        new ErrorApi({ detalle: "No pudimos conectar con el servidor." }),
      )
      .mockResolvedValueOnce({ email: "tomas.rios@example.com" });
    renderizar();

    const alerta = await screen.findByRole("alert");
    expect(alerta.textContent).toBe("No pudimos conectar con el servidor.");
    fireEvent.click(screen.getByRole("button", { name: "Reintentar" }));

    await screen.findByText("tomas.rios@example.com");
    expect(validarEnlaceRecuperacion).toHaveBeenCalledTimes(2);
  });
});
