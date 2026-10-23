import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { obtenerUsuarioActual } from "../api/auth.js";
import { ErrorApi } from "../api/cliente.js";
import { listarLocalidades } from "../api/localidades.js";
import { actualizarPerfil, obtenerPerfil } from "../api/perfil.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import OnboardingPerfil from "./OnboardingPerfil.jsx";

vi.mock("../api/auth.js", () => ({ obtenerUsuarioActual: vi.fn() }));
vi.mock("../api/localidades.js", () => ({ listarLocalidades: vi.fn() }));
vi.mock("../api/perfil.js", () => ({
  obtenerPerfil: vi.fn(),
  actualizarPerfil: vi.fn(),
}));

const MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar.";
const ETIQUETAS = [
  "Edad",
  "Género",
  "Localidad",
  "Frecuencia de juego",
  "Nivel estimado",
];
const PERFIL_VACIO = {
  datos_personales: {
    nombre: "Tomás",
    apellido: "Ríos",
    email: "tomas.rios@example.com",
  },
  perfil_deportivo: {
    edad: null,
    genero: null,
    localidad: null,
    frecuencia_juego: null,
    nivel_estimado: null,
  },
  disponibilidad: { disponible_para_invitaciones: false },
};
const LOCALIDADES = [
  { id: 7, nombre: "Río Ceballos" },
  { id: 3, nombre: "Unquillo" },
];

let establecerUsuario;

function renderizar() {
  establecerUsuario = vi.fn();
  const sesion = {
    cargando: false,
    usuario: { id: 1, onboarding: "perfil" },
    establecerUsuario,
  };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={["/onboarding/perfil"]}>
        <Routes>
          <Route path="/onboarding/perfil" element={<OnboardingPerfil />} />
          <Route
            path="/onboarding/disponibilidad"
            element={<p>Onboarding disponibilidad</p>}
          />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

async function esperarFormulario() {
  return screen.findByRole("button", { name: "Guardar y continuar" });
}

function mensajeDe(etiqueta) {
  const campo = screen.getByLabelText(etiqueta);
  const idMensaje = campo.getAttribute("aria-describedby");
  return idMensaje ? document.getElementById(idMensaje).textContent : null;
}

function completarTodo() {
  fireEvent.change(screen.getByLabelText("Edad"), { target: { value: "29" } });
  fireEvent.change(screen.getByLabelText("Género"), {
    target: { value: "MASCULINO" },
  });
  fireEvent.change(screen.getByLabelText("Localidad"), {
    target: { value: "7" },
  });
  fireEvent.change(screen.getByLabelText("Frecuencia de juego"), {
    target: { value: "2_3_SEMANA" },
  });
  fireEvent.change(screen.getByLabelText("Nivel estimado"), {
    target: { value: "4.5" },
  });
}

function guardar() {
  fireEvent.click(screen.getByRole("button", { name: "Guardar y continuar" }));
}

describe("OnboardingPerfil (HU-004)", () => {
  beforeEach(() => {
    obtenerPerfil.mockReset().mockResolvedValue(PERFIL_VACIO);
    listarLocalidades.mockReset().mockResolvedValue(LOCALIDADES);
    actualizarPerfil.mockReset();
    obtenerUsuarioActual.mockReset();
  });

  it("arranca con todo vacío, el selector sin elegir y 5 campos pendientes", async () => {
    renderizar();
    await esperarFormulario();

    expect(
      screen.getByRole("heading", {
        level: 1,
        name: "Configurá tu perfil deportivo",
      }),
    ).toBeTruthy();
    expect(screen.getByText("Primer ingreso · Paso 1 de 2")).toBeTruthy();
    expect(screen.getByLabelText("Edad").value).toBe("");
    for (const etiqueta of ["Género", "Localidad", "Frecuencia de juego"]) {
      expect(screen.getByLabelText(etiqueta).value).toBe("");
    }
    expect(
      screen.getByLabelText("Nivel estimado").getAttribute("aria-valuetext"),
    ).toBe("Sin elegir");
    expect(screen.getByText("5 campos pendientes")).toBeTruthy();
  });

  it("lista las localidades en el orden que llega y con la ayuda", async () => {
    renderizar();
    await esperarFormulario();

    const opciones = Array.from(screen.getByLabelText("Localidad").options).map(
      (opcion) => opcion.textContent,
    );
    expect(opciones).toEqual([
      "Seleccioná una opción",
      "Río Ceballos",
      "Unquillo",
    ]);
    expect(mensajeDe("Localidad")).toBe(
      "Elegila del listado. Si la tuya no figura, elegí la más cercana.",
    );
  });

  it("C1: con datos faltantes no guarda y marca cada campo pendiente", async () => {
    renderizar();
    await esperarFormulario();

    guardar();

    expect(actualizarPerfil).not.toHaveBeenCalled();
    for (const etiqueta of ETIQUETAS) {
      expect(screen.getByLabelText(etiqueta).getAttribute("aria-invalid")).toBe(
        "true",
      );
      expect(mensajeDe(etiqueta)).toBe(MENSAJE_CAMPO_VACIO);
    }
  });

  it("C1: el contador de pendientes baja en vivo y desaparece al completar", async () => {
    renderizar();
    await esperarFormulario();

    fireEvent.change(screen.getByLabelText("Edad"), {
      target: { value: "29" },
    });
    expect(screen.getByText("4 campos pendientes")).toBeTruthy();

    completarTodo();
    fireEvent.change(screen.getByLabelText("Frecuencia de juego"), {
      target: { value: "" },
    });
    expect(screen.getByText("1 campo pendiente")).toBeTruthy();

    fireEvent.change(screen.getByLabelText("Frecuencia de juego"), {
      target: { value: "1_SEMANA" },
    });
    expect(screen.queryByText(/pendiente/)).toBeNull();
  });

  it("C2: muestra en su campo el error que devuelve el backend", async () => {
    actualizarPerfil.mockRejectedValue(
      new ErrorApi({
        estado: 400,
        errores: {
          perfil_deportivo: { edad: ["Ingresá una edad entre 18 y 99."] },
        },
      }),
    );
    renderizar();
    await esperarFormulario();
    completarTodo();
    fireEvent.change(screen.getByLabelText("Edad"), {
      target: { value: "17" },
    });

    guardar();

    expect(
      await screen.findByText("Ingresá una edad entre 18 y 99."),
    ).toBeTruthy();
    expect(mensajeDe("Edad")).toBe("Ingresá una edad entre 18 y 99.");
    expect(
      screen.getByRole("button", { name: "Guardar y continuar" }).disabled,
    ).toBe(false);
    expect(establecerUsuario).not.toHaveBeenCalled();
  });

  it("guarda, actualiza la sesión y lleva al paso 2", async () => {
    actualizarPerfil.mockResolvedValue(PERFIL_VACIO);
    obtenerUsuarioActual.mockResolvedValue({ id: 1, onboarding: null });
    renderizar();
    await esperarFormulario();
    completarTodo();

    guardar();

    expect(await screen.findByText("Onboarding disponibilidad")).toBeTruthy();
    expect(actualizarPerfil).toHaveBeenCalledWith({
      perfil_deportivo: {
        edad: 29,
        genero: "MASCULINO",
        localidad: 7,
        frecuencia_juego: "2_3_SEMANA",
        nivel_estimado: 4.5,
      },
    });
    expect(establecerUsuario).toHaveBeenCalledWith({ id: 1, onboarding: null });
  });

  it("si no se pueden cargar los datos, permite reintentar", async () => {
    obtenerPerfil.mockRejectedValueOnce(
      new ErrorApi({
        detalle:
          "No pudimos conectar con el servidor. Probá de nuevo en unos minutos.",
      }),
    );
    renderizar();

    fireEvent.click(await screen.findByRole("button", { name: "Reintentar" }));

    expect(await esperarFormulario()).toBeTruthy();
    expect(obtenerPerfil).toHaveBeenCalledTimes(2);
  });
});
