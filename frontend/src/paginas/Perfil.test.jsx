import { fireEvent, render, screen, within } from "@testing-library/react";
import { useState } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  obtenerUsuarioActual,
  salir,
  solicitarRecuperacion,
} from "../api/auth.js";
import { ErrorApi } from "../api/cliente.js";
import { listarLocalidades } from "../api/localidades.js";
import { actualizarPerfil, obtenerPerfil } from "../api/perfil.js";
import RutaPrivada from "../componentes/RutaPrivada.jsx";
import RutaPublica from "../componentes/RutaPublica.jsx";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import Perfil from "./Perfil.jsx";

vi.mock("../api/auth.js", () => ({
  obtenerUsuarioActual: vi.fn(),
  salir: vi.fn(),
  solicitarRecuperacion: vi.fn(),
}));
vi.mock("../api/localidades.js", () => ({ listarLocalidades: vi.fn() }));
vi.mock("../api/perfil.js", () => ({
  obtenerPerfil: vi.fn(),
  actualizarPerfil: vi.fn(),
}));

const PERFIL = {
  datos_personales: {
    nombre: "Tomás",
    apellido: "Ríos",
    email: "tomas.rios@example.com",
  },
  perfil_deportivo: {
    edad: 29,
    genero: "MASCULINO",
    localidad: 7,
    frecuencia_juego: "2_3_SEMANA",
    nivel_estimado: 4.5,
  },
  disponibilidad: {
    franjas: [
      { dia_semana: 3, hora_inicio: "19:00", hora_fin: "22:00" },
      { dia_semana: 6, hora_inicio: "17:00", hora_fin: "21:00" },
    ],
    tipo_encuentro: "COMPETITIVO",
    lado_preferido: "DRIVE",
    disponible_para_invitaciones: false,
  },
};
const LOCALIDADES = [
  { id: 7, nombre: "Río Ceballos" },
  { id: 3, nombre: "Unquillo" },
];
const USUARIO = { id: 1, nombre: "Tomás", onboarding: null };

// Proveedor de sesión con estado real, para ver qué pasa al cerrar la sesión.
function SesionDePrueba({ children }) {
  const [usuario, setUsuario] = useState(USUARIO);
  const valor = { cargando: false, usuario, establecerUsuario: setUsuario };
  return (
    <ContextoSesion.Provider value={valor}>{children}</ContextoSesion.Provider>
  );
}

function renderizar() {
  return render(
    <SesionDePrueba>
      <MemoryRouter initialEntries={["/perfil"]}>
        <Routes>
          <Route element={<RutaPublica />}>
            <Route path="/" element={<p>Bienvenida</p>} />
            <Route path="/ingresar" element={<p>Inicio de sesión</p>} />
          </Route>
          <Route element={<RutaPrivada />}>
            <Route path="/perfil" element={<Perfil />} />
          </Route>
          <Route path="/recuperar/enviado" element={<p>Revisá tu correo</p>} />
        </Routes>
      </MemoryRouter>
    </SesionDePrueba>,
  );
}

async function esperarPerfil() {
  return screen.findByLabelText("Nombre");
}

function barraCambios() {
  return screen.queryByText("Tenés cambios sin guardar");
}

describe("Perfil (HU-004)", () => {
  beforeEach(() => {
    obtenerPerfil.mockReset().mockResolvedValue(PERFIL);
    listarLocalidades.mockReset().mockResolvedValue(LOCALIDADES);
    actualizarPerfil.mockReset();
    obtenerUsuarioActual.mockReset().mockResolvedValue(USUARIO);
    salir.mockReset();
    solicitarRecuperacion.mockReset();
  });

  it("muestra los datos guardados, con el selector en el nivel guardado", async () => {
    renderizar();
    await esperarPerfil();

    expect(
      screen.getByRole("heading", { level: 1, name: "Mi perfil" }),
    ).toBeTruthy();
    expect(screen.getByLabelText("Nombre").value).toBe("Tomás");
    expect(screen.getByLabelText("Correo electrónico").readOnly).toBe(true);
    expect(screen.getByLabelText("Edad").value).toBe("29");
    expect(screen.getByLabelText("Localidad").value).toBe("7");
    expect(
      screen.getByLabelText("Nivel estimado").getAttribute("aria-valuetext"),
    ).toBe("4,5");
    expect(screen.getByText("No disponible")).toBeTruthy();
    expect(barraCambios()).toBeNull();
  });

  it("C3: al modificar y guardar actualiza la información y avisa", async () => {
    actualizarPerfil.mockResolvedValue({
      ...PERFIL,
      perfil_deportivo: {
        ...PERFIL.perfil_deportivo,
        localidad: 3,
        nivel_estimado: 5,
      },
    });
    renderizar();
    await esperarPerfil();

    fireEvent.change(screen.getByLabelText("Localidad"), {
      target: { value: "3" },
    });
    fireEvent.change(screen.getByLabelText("Nivel estimado"), {
      target: { value: "5" },
    });
    expect(barraCambios()).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(
      await screen.findByText("Cambios guardados correctamente."),
    ).toBeTruthy();
    expect(actualizarPerfil).toHaveBeenCalledWith({
      perfil_deportivo: {
        edad: 29,
        genero: "MASCULINO",
        localidad: 3,
        frecuencia_juego: "2_3_SEMANA",
        nivel_estimado: 5,
      },
    });
    expect(barraCambios()).toBeNull();
    expect(screen.getByLabelText("Localidad").value).toBe("3");
  });

  it("C3: envía solo la sección que cambió", async () => {
    actualizarPerfil.mockResolvedValue({
      ...PERFIL,
      datos_personales: { ...PERFIL.datos_personales, nombre: "Tomi" },
    });
    renderizar();
    await esperarPerfil();

    fireEvent.change(screen.getByLabelText("Nombre"), {
      target: { value: "Tomi" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    await screen.findByText("Cambios guardados correctamente.");
    expect(actualizarPerfil).toHaveBeenCalledWith({
      datos_personales: { nombre: "Tomi", apellido: "Ríos" },
    });
    expect(obtenerUsuarioActual).toHaveBeenCalled();
  });

  it("si se vuelve al valor guardado, la barra de cambios desaparece", async () => {
    renderizar();
    await esperarPerfil();

    fireEvent.change(screen.getByLabelText("Edad"), {
      target: { value: "30" },
    });
    expect(barraCambios()).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Edad"), {
      target: { value: "29" },
    });

    expect(barraCambios()).toBeNull();
  });

  it("Descartar vuelve a los valores guardados", async () => {
    renderizar();
    await esperarPerfil();

    fireEvent.change(screen.getByLabelText("Apellido"), {
      target: { value: "Sosa" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Descartar" }));

    expect(screen.getByLabelText("Apellido").value).toBe("Ríos");
    expect(barraCambios()).toBeNull();
    expect(actualizarPerfil).not.toHaveBeenCalled();
  });

  it("C1: un campo vaciado impide guardar y se marca", async () => {
    renderizar();
    await esperarPerfil();

    fireEvent.change(screen.getByLabelText("Género"), {
      target: { value: "" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(actualizarPerfil).not.toHaveBeenCalled();
    expect(screen.getByLabelText("Género").getAttribute("aria-invalid")).toBe(
      "true",
    );
    expect(
      screen.getByText("Completá este campo para poder guardar."),
    ).toBeTruthy();
  });

  it("C2: muestra los errores del backend en cada campo y no guarda", async () => {
    actualizarPerfil.mockRejectedValue(
      new ErrorApi({
        estado: 400,
        errores: {
          datos_personales: { nombre: ["Usá como máximo 60 caracteres."] },
          perfil_deportivo: { edad: ["Ingresá una edad entre 18 y 99."] },
        },
      }),
    );
    renderizar();
    await esperarPerfil();

    fireEvent.change(screen.getByLabelText("Nombre"), {
      target: { value: "Tomás Ignacio" },
    });
    fireEvent.change(screen.getByLabelText("Edad"), {
      target: { value: "120" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(
      await screen.findByText("Ingresá una edad entre 18 y 99."),
    ).toBeTruthy();
    expect(screen.getByText("Usá como máximo 60 caracteres.")).toBeTruthy();
    expect(barraCambios()).toBeTruthy();
    expect(screen.queryByText("Cambios guardados correctamente.")).toBeNull();
  });

  it("Cambiar contraseña pide la recuperación con el correo y lleva al paso 2", async () => {
    solicitarRecuperacion.mockResolvedValue(null);
    renderizar();
    await esperarPerfil();

    fireEvent.click(screen.getByRole("button", { name: "Cambiar contraseña" }));

    expect(await screen.findByText("Revisá tu correo")).toBeTruthy();
    expect(solicitarRecuperacion).toHaveBeenCalledWith({
      email: "tomas.rios@example.com",
    });
    expect(salir).not.toHaveBeenCalled();
  });

  it("Cerrar sesión sale de la cuenta y lleva a la bienvenida", async () => {
    salir.mockResolvedValue(null);
    renderizar();
    await esperarPerfil();

    const cuenta = screen.getByRole("region", { name: "Cuenta" });
    fireEvent.click(
      within(cuenta).getByRole("button", { name: "Cerrar sesión" }),
    );

    expect(await screen.findByText("Bienvenida")).toBeTruthy();
    expect(salir).toHaveBeenCalled();
  });
});

function seccionDisponibilidad() {
  return screen.getByRole("region", { name: "Disponibilidad y preferencias" });
}

function valoresDe(seccion, etiqueta) {
  return within(seccion)
    .getAllByLabelText(etiqueta)
    .map((control) => control.value);
}

describe("Perfil · disponibilidad y preferencias (HU-005)", () => {
  beforeEach(() => {
    obtenerPerfil.mockReset().mockResolvedValue(PERFIL);
    listarLocalidades.mockReset().mockResolvedValue(LOCALIDADES);
    actualizarPerfil.mockReset();
    obtenerUsuarioActual.mockReset().mockResolvedValue(USUARIO);
  });

  it("muestra las franjas, las preferencias y el interruptor guardados", async () => {
    renderizar();
    await esperarPerfil();
    const seccion = seccionDisponibilidad();

    expect(valoresDe(seccion, "Día")).toEqual(["3", "6"]);
    expect(valoresDe(seccion, "Desde")).toEqual(["19:00", "17:00"]);
    expect(valoresDe(seccion, "Hasta")).toEqual(["22:00", "21:00"]);
    expect(within(seccion).getByLabelText("Competitivo").checked).toBe(true);
    expect(within(seccion).getByLabelText("Drive").checked).toBe(true);
    expect(within(seccion).getByRole("switch").checked).toBe(false);
    expect(
      within(seccion).getByText(
        "Si lo desactivás, el sistema deja de recomendarte a otros organizadores.",
      ),
    ).toBeTruthy();
  });

  it.each([
    ["MASCULINO", "jugador"],
    ["NO_DECLARA", "jugador"],
    ["FEMENINO", "jugadora"],
  ])("con género %s se refiere al usuario como %s", async (genero, palabra) => {
    obtenerPerfil.mockResolvedValue({
      ...PERFIL,
      perfil_deportivo: { ...PERFIL.perfil_deportivo, genero },
    });
    renderizar();
    await esperarPerfil();

    expect(
      within(seccionDisponibilidad()).getByText(
        `Define en qué encuentros aparecés como ${palabra} compatible.`,
      ),
    ).toBeTruthy();
  });

  it("C2: al activar el interruptor y guardar envía solo esa sección y queda Disponible", async () => {
    actualizarPerfil.mockResolvedValue({
      ...PERFIL,
      disponibilidad: {
        ...PERFIL.disponibilidad,
        disponible_para_invitaciones: true,
      },
    });
    renderizar();
    await esperarPerfil();

    fireEvent.click(within(seccionDisponibilidad()).getByRole("switch"));
    expect(barraCambios()).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(
      await screen.findByText("Cambios guardados correctamente."),
    ).toBeTruthy();
    expect(actualizarPerfil).toHaveBeenCalledWith({
      disponibilidad: {
        ...PERFIL.disponibilidad,
        disponible_para_invitaciones: true,
      },
    });
    expect(screen.getByText("Disponible")).toBeTruthy();
    expect(barraCambios()).toBeNull();
  });

  it("C4: modifica una franja y muestra el resultado unido que devuelve el backend", async () => {
    actualizarPerfil.mockResolvedValue({
      ...PERFIL,
      disponibilidad: {
        ...PERFIL.disponibilidad,
        franjas: [{ dia_semana: 6, hora_inicio: "17:00", hora_fin: "22:00" }],
      },
    });
    renderizar();
    await esperarPerfil();
    const seccion = seccionDisponibilidad();

    fireEvent.change(within(seccion).getAllByLabelText("Día")[0], {
      target: { value: "6" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    await screen.findByText("Cambios guardados correctamente.");
    expect(actualizarPerfil.mock.calls[0][0].disponibilidad.franjas).toEqual([
      { dia_semana: 6, hora_inicio: "19:00", hora_fin: "22:00" },
      { dia_semana: 6, hora_inicio: "17:00", hora_fin: "21:00" },
    ]);
    expect(valoresDe(seccion, "Día")).toEqual(["6"]);
    expect(valoresDe(seccion, "Hasta")).toEqual(["22:00"]);
  });

  it("muestra el error del backend en la fila que corresponde", async () => {
    actualizarPerfil.mockRejectedValue(
      new ErrorApi({
        estado: 400,
        errores: {
          disponibilidad: {
            franjas: {
              1: { hora_fin: ["La franja debe durar al menos 60 minutos."] },
            },
          },
        },
      }),
    );
    renderizar();
    await esperarPerfil();
    const seccion = seccionDisponibilidad();

    fireEvent.change(within(seccion).getAllByLabelText("Hasta")[1], {
      target: { value: "17:30" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(
      await screen.findByText("La franja debe durar al menos 60 minutos."),
    ).toBeTruthy();
    const hasta = within(seccion).getAllByLabelText("Hasta");
    expect(hasta[0].getAttribute("aria-invalid")).toBeNull();
    expect(hasta[1].getAttribute("aria-invalid")).toBe("true");
  });

  it("P6: al quitar la última franja estando disponible muestra el error del interruptor", async () => {
    obtenerPerfil.mockResolvedValue({
      ...PERFIL,
      disponibilidad: {
        ...PERFIL.disponibilidad,
        franjas: [PERFIL.disponibilidad.franjas[0]],
        disponible_para_invitaciones: true,
      },
    });
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
    await esperarPerfil();
    const seccion = seccionDisponibilidad();

    fireEvent.click(
      within(seccion).getByRole("button", { name: "Quitar franja 1" }),
    );
    fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(
      await screen.findByText(
        "Para recibir invitaciones necesitás cargar al menos una franja.",
      ),
    ).toBeTruthy();
    expect(actualizarPerfil.mock.calls[0][0].disponibilidad.franjas).toEqual(
      [],
    );
    expect(
      within(seccion).getByRole("switch").getAttribute("aria-invalid"),
    ).toBe("true");
  });

  it("Agregar franja suma una fila y Descartar vuelve a las guardadas", async () => {
    renderizar();
    await esperarPerfil();
    const seccion = seccionDisponibilidad();

    fireEvent.click(
      within(seccion).getByRole("button", { name: "Agregar franja" }),
    );
    expect(valoresDe(seccion, "Día")).toEqual(["3", "6", ""]);
    fireEvent.click(
      within(seccion).getByRole("button", { name: "Quitar franja 1" }),
    );
    expect(valoresDe(seccion, "Día")).toEqual(["6", ""]);
    expect(barraCambios()).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Descartar" }));

    expect(valoresDe(seccion, "Día")).toEqual(["3", "6"]);
    expect(barraCambios()).toBeNull();
  });

  it("una franja a medio completar impide guardar y se marca", async () => {
    renderizar();
    await esperarPerfil();
    const seccion = seccionDisponibilidad();

    fireEvent.click(
      within(seccion).getByRole("button", { name: "Agregar franja" }),
    );
    fireEvent.change(within(seccion).getAllByLabelText("Día")[2], {
      target: { value: "1" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect(actualizarPerfil).not.toHaveBeenCalled();
    expect(
      within(seccion)
        .getAllByLabelText("Desde")[2]
        .getAttribute("aria-invalid"),
    ).toBe("true");
    expect(
      within(seccion).getAllByText("Completá este campo para poder guardar."),
    ).toHaveLength(2);
  });
});
