import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { obtenerUsuarioActual } from "../api/auth.js";
import { ErrorApi } from "../api/cliente.js";
import { actualizarPerfil, obtenerPerfil } from "../api/perfil.js";
import RutaConOnboarding from "../componentes/RutaConOnboarding.jsx";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import OnboardingDisponibilidad from "./OnboardingDisponibilidad.jsx";

vi.mock("../api/auth.js", () => ({ obtenerUsuarioActual: vi.fn() }));
vi.mock("../api/perfil.js", () => ({
  obtenerPerfil: vi.fn(),
  actualizarPerfil: vi.fn(),
}));

const MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar.";
const SIN_DISPONIBILIDAD = {
  franjas: [],
  tipo_encuentro: null,
  lado_preferido: null,
  disponible_para_invitaciones: false,
};
const PERFIL = {
  datos_personales: { nombre: "Tomás", apellido: "Ríos", email: "t@x.com" },
  perfil_deportivo: {
    edad: 29,
    genero: "MASCULINO",
    localidad: 7,
    frecuencia_juego: "2_3_SEMANA",
    nivel_estimado: 4.5,
  },
  disponibilidad: SIN_DISPONIBILIDAD,
};

let establecerUsuario;

function AvisoRecibido() {
  return <p>Panel: {useLocation().state?.aviso}</p>;
}

function renderizar(onboarding = "disponibilidad") {
  establecerUsuario = vi.fn();
  const sesion = {
    cargando: false,
    usuario: { id: 1, nombre: "Tomás", onboarding },
    establecerUsuario,
  };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={["/onboarding/disponibilidad"]}>
        <Routes>
          <Route element={<RutaConOnboarding permitirPaso="disponibilidad" />}>
            <Route
              path="/onboarding/disponibilidad"
              element={<OnboardingDisponibilidad />}
            />
          </Route>
          <Route path="/onboarding/perfil" element={<p>Onboarding perfil</p>} />
          <Route path="/inicio" element={<AvisoRecibido />} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

async function esperarFormulario() {
  return screen.findByRole("button", { name: "Guardar" });
}

function filas() {
  return within(
    screen.getByRole("region", { name: "Disponibilidad horaria" }),
  ).queryAllByRole("listitem");
}

function completarFila(fila, dia, desde, hasta) {
  fireEvent.change(within(fila).getByLabelText("Día"), {
    target: { value: dia },
  });
  fireEvent.change(within(fila).getByLabelText("Desde"), {
    target: { value: desde },
  });
  fireEvent.change(within(fila).getByLabelText("Hasta"), {
    target: { value: hasta },
  });
}

function elegirPreferencias() {
  fireEvent.click(screen.getByLabelText("Competitivo"));
  fireEvent.click(screen.getByLabelText("Drive"));
}

function guardar() {
  fireEvent.click(screen.getByRole("button", { name: "Guardar" }));
}

describe("OnboardingDisponibilidad (HU-005)", () => {
  beforeEach(() => {
    obtenerPerfil.mockReset().mockResolvedValue(PERFIL);
    actualizarPerfil.mockReset();
    obtenerUsuarioActual
      .mockReset()
      .mockResolvedValue({ id: 1, nombre: "Tomás", onboarding: null });
  });

  it("arranca con una fila vacía, sin preferencias y con el interruptor apagado", async () => {
    renderizar();
    await esperarFormulario();

    expect(
      screen.getByRole("heading", {
        level: 1,
        name: "¿Cuándo y cómo te gusta jugar?",
      }),
    ).toBeTruthy();
    expect(screen.getByText("Primer ingreso · Paso 2 de 2")).toBeTruthy();
    expect(filas()).toHaveLength(1);
    expect(within(filas()[0]).getByLabelText("Día").value).toBe("");
    for (const opcion of ["Recreativo", "Competitivo", "Indiferente"]) {
      expect(screen.getAllByLabelText(opcion)[0].checked).toBe(false);
    }
    expect(screen.getByRole("switch").checked).toBe(false);
  });

  it("P2: las horas se eligen de 08:00 a 23:30 en pasos de 30 minutos", async () => {
    renderizar();
    await esperarFormulario();

    for (const etiqueta of ["Desde", "Hasta"]) {
      const horas = Array.from(
        within(filas()[0]).getByLabelText(etiqueta).options,
      ).map((opcion) => opcion.value);
      // La primera opción es la vacía, "Seleccioná una opción".
      expect(horas.slice(1, 4)).toEqual(["08:00", "08:30", "09:00"]);
      expect(horas.at(-1)).toBe("23:30");
      expect(horas).toHaveLength(33);
    }
  });

  it("P4: agrega y quita franjas", async () => {
    renderizar();
    await esperarFormulario();

    fireEvent.click(screen.getByRole("button", { name: "Agregar franja" }));
    fireEvent.click(screen.getByRole("button", { name: "Agregar franja" }));
    expect(filas()).toHaveLength(3);

    completarFila(filas()[1], "3", "19:00", "22:00");
    fireEvent.click(screen.getByRole("button", { name: "Quitar franja 1" }));

    expect(filas()).toHaveLength(2);
    expect(within(filas()[0]).getByLabelText("Día").value).toBe("3");
  });

  it("C1: guarda franjas y preferencias, sin la fila vacía, y lleva al panel con el aviso", async () => {
    actualizarPerfil.mockResolvedValue(PERFIL);
    renderizar();
    await esperarFormulario();

    completarFila(filas()[0], "6", "17:00", "21:00");
    fireEvent.click(screen.getByRole("button", { name: "Agregar franja" }));
    elegirPreferencias();
    fireEvent.click(screen.getByRole("switch"));
    guardar();

    expect(
      await screen.findByText(
        "Panel: Disponibilidad y preferencias guardadas correctamente.",
      ),
    ).toBeTruthy();
    expect(actualizarPerfil).toHaveBeenCalledWith({
      disponibilidad: {
        franjas: [{ dia_semana: 6, hora_inicio: "17:00", hora_fin: "21:00" }],
        tipo_encuentro: "COMPETITIVO",
        lado_preferido: "DRIVE",
        disponible_para_invitaciones: true,
      },
    });
    expect(establecerUsuario).toHaveBeenCalledWith({
      id: 1,
      nombre: "Tomás",
      onboarding: null,
    });
  });

  it("se puede terminar sin franjas y con el interruptor apagado", async () => {
    actualizarPerfil.mockResolvedValue(PERFIL);
    renderizar();
    await esperarFormulario();

    elegirPreferencias();
    guardar();

    await screen.findByText(/^Panel:/);
    expect(actualizarPerfil.mock.calls[0][0].disponibilidad).toMatchObject({
      franjas: [],
      disponible_para_invitaciones: false,
    });
  });

  it("C1: sin preferencias o con una fila a medio completar no guarda y marca lo pendiente", async () => {
    renderizar();
    await esperarFormulario();

    fireEvent.change(within(filas()[0]).getByLabelText("Día"), {
      target: { value: "6" },
    });
    guardar();

    expect(actualizarPerfil).not.toHaveBeenCalled();
    expect(
      within(filas()[0]).getByLabelText("Desde").getAttribute("aria-invalid"),
    ).toBe("true");
    expect(screen.getAllByText(MENSAJE_CAMPO_VACIO)).toHaveLength(4);
  });

  it("P1 y P3: muestra en cada fila el error que devuelve el backend", async () => {
    actualizarPerfil.mockRejectedValue(
      new ErrorApi({
        estado: 400,
        errores: {
          disponibilidad: {
            franjas: {
              0: {
                hora_fin: ["La hora de fin debe ser posterior a la de inicio."],
              },
              1: { hora_fin: ["La franja debe durar al menos 60 minutos."] },
            },
          },
        },
      }),
    );
    renderizar();
    await esperarFormulario();

    fireEvent.click(screen.getByRole("button", { name: "Agregar franja" }));
    fireEvent.click(screen.getByRole("button", { name: "Agregar franja" }));
    completarFila(filas()[1], "6", "19:00", "17:00");
    completarFila(filas()[2], "3", "17:00", "17:30");
    elegirPreferencias();
    guardar();

    expect(
      await within(filas()[1]).findByText(
        "La hora de fin debe ser posterior a la de inicio.",
      ),
    ).toBeTruthy();
    expect(
      within(filas()[2]).getByText("La franja debe durar al menos 60 minutos."),
    ).toBeTruthy();
    expect(screen.queryByText(/^Panel:/)).toBeNull();
  });

  it("P6: avisa que hace falta una franja para recibir invitaciones", async () => {
    actualizarPerfil.mockRejectedValue(
      new ErrorApi({
        estado: 400,
        errores: {
          disponibilidad: {
            disponible_para_invitaciones: [
              "Para recibir invitaciones necesitás cargar al menos una franja.",
            ],
          },
        },
      }),
    );
    renderizar();
    await esperarFormulario();

    elegirPreferencias();
    fireEvent.click(screen.getByRole("switch"));
    guardar();

    expect(
      await screen.findByText(
        "Para recibir invitaciones necesitás cargar al menos una franja.",
      ),
    ).toBeTruthy();
    expect(screen.getByRole("switch").getAttribute("aria-invalid")).toBe(
      "true",
    );
    expect(screen.getByRole("button", { name: "Guardar" }).disabled).toBe(
      false,
    );
  });

  it("C4: al volver muestra lo ya guardado, con las franjas unidas", async () => {
    obtenerPerfil.mockResolvedValue({
      ...PERFIL,
      disponibilidad: {
        franjas: [{ dia_semana: 6, hora_inicio: "17:00", hora_fin: "21:00" }],
        tipo_encuentro: "RECREATIVO",
        lado_preferido: "REVES",
        disponible_para_invitaciones: true,
      },
    });
    renderizar(null);
    await esperarFormulario();

    expect(filas()).toHaveLength(1);
    expect(within(filas()[0]).getByLabelText("Hasta").value).toBe("21:00");
    expect(screen.getByLabelText("Recreativo").checked).toBe(true);
    expect(screen.getByLabelText("Revés").checked).toBe(true);
    expect(screen.getByRole("switch").checked).toBe(true);
  });

  it("Volver lleva al paso 1", async () => {
    renderizar();
    await esperarFormulario();

    fireEvent.click(screen.getByRole("link", { name: "Volver" }));

    expect(screen.getByText("Onboarding perfil")).toBeTruthy();
  });

  it("con el paso 1 pendiente lleva a ese paso", () => {
    renderizar("perfil");

    expect(screen.getByText("Onboarding perfil")).toBeTruthy();
  });
});
