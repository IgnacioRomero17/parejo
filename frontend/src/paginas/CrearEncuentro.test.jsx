import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ErrorApi } from "../api/cliente.js";
import { crearEncuentro } from "../api/encuentros.js";
import { listarLocalidades } from "../api/localidades.js";
import { obtenerPerfil } from "../api/perfil.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import CrearEncuentro from "./CrearEncuentro.jsx";

vi.mock("../api/encuentros.js", () => ({ crearEncuentro: vi.fn() }));
vi.mock("../api/localidades.js", () => ({ listarLocalidades: vi.fn() }));
vi.mock("../api/perfil.js", () => ({ obtenerPerfil: vi.fn() }));

const MENSAJE_CAMPO_VACIO = "Completá este campo para poder guardar.";
const ETIQUETAS = [
  "Fecha",
  "Hora de inicio",
  "Duración",
  "Localidad",
  "Dirección o lugar",
];
const LOCALIDADES = [
  { id: 7, nombre: "Río Ceballos" },
  { id: 3, nombre: "Unquillo" },
];

function perfil(genero = "MASCULINO") {
  return {
    datos_personales: {
      nombre: "Tomás",
      apellido: "Ríos",
      email: "tomas.rios@example.com",
    },
    perfil_deportivo: {
      edad: 29,
      genero,
      localidad: 7,
      frecuencia_juego: "1_SEMANA",
      nivel_estimado: 4.5,
    },
    disponibilidad: {
      franjas: [],
      tipo_encuentro: "COMPETITIVO",
      lado_preferido: "DRIVE",
      disponible_para_invitaciones: false,
    },
  };
}

function Destino() {
  const { pathname, state } = useLocation();
  return (
    <p>
      Destino {pathname} {state?.aviso}
    </p>
  );
}

function renderizar() {
  const sesion = {
    cargando: false,
    usuario: { id: 1, nombre: "Tomás", apellido: "Ríos", onboarding: null },
    establecerUsuario: vi.fn(),
  };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={["/encuentros/nuevo"]}>
        <Routes>
          <Route path="/encuentros/nuevo" element={<CrearEncuentro />} />
          <Route path="*" element={<Destino />} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

async function esperarFormulario() {
  return screen.findByRole("button", {
    name: "Crear encuentro y buscar jugadores",
  });
}

function mensajeDe(etiqueta) {
  const campo = screen.getByLabelText(etiqueta);
  const idMensaje = campo.getAttribute("aria-describedby");
  return idMensaje ? document.getElementById(idMensaje).textContent : null;
}

function completarTodo() {
  fireEvent.change(screen.getByLabelText("Fecha"), {
    target: { value: "2026-10-03" },
  });
  fireEvent.change(screen.getByLabelText("Hora de inicio"), {
    target: { value: "18:00" },
  });
  fireEvent.change(screen.getByLabelText("Duración"), {
    target: { value: "90" },
  });
  fireEvent.click(screen.getByLabelText("Competitivo"));
  fireEvent.change(screen.getByLabelText("Dirección o lugar"), {
    target: { value: "Av. San Martín 4500" },
  });
}

function crear() {
  fireEvent.click(
    screen.getByRole("button", { name: "Crear encuentro y buscar jugadores" }),
  );
}

describe("CrearEncuentro (HU-006)", () => {
  beforeEach(() => {
    obtenerPerfil.mockReset().mockResolvedValue(perfil());
    listarLocalidades.mockReset().mockResolvedValue(LOCALIDADES);
    crearEncuentro.mockReset();
  });

  it("arranca con la localidad del jugador precargada y el resto vacío", async () => {
    renderizar();
    await esperarFormulario();

    expect(
      screen.getByRole("heading", { level: 1, name: "Crear encuentro" }),
    ).toBeTruthy();
    expect(screen.getByLabelText("Localidad").value).toBe("7");
    for (const etiqueta of ["Fecha", "Hora de inicio", "Duración"]) {
      expect(screen.getByLabelText(etiqueta).value).toBe("");
    }
    expect(screen.getByLabelText("Dirección o lugar").value).toBe("");
    for (const tipo of ["Recreativo", "Competitivo", "Indiferente"]) {
      expect(screen.getByLabelText(tipo).checked).toBe(false);
    }
    expect(mensajeDe("Localidad")).toBe(
      "Localidad donde se jugará. El sistema la usa para calcular la distancia con cada jugador.",
    );
  });

  it("P4: el calendario va de hoy a hoy + 60 días, en fecha de Córdoba", async () => {
    // Solo se simula la fecha: los temporizadores reales siguen para findBy.
    vi.useFakeTimers({ toFake: ["Date"] });
    // 01:30 UTC del 4 de octubre todavía es 3 de octubre en Córdoba.
    vi.setSystemTime(new Date("2026-10-04T01:30:00Z"));
    try {
      renderizar();
      await esperarFormulario();

      const fecha = screen.getByLabelText("Fecha");
      expect(fecha.getAttribute("min")).toBe("2026-10-03");
      expect(fecha.getAttribute("max")).toBe("2026-12-02");
    } finally {
      vi.useRealTimers();
    }
  });

  it("P2: ofrece horas de 08:00 a 22:30 en pasos de 30 minutos", async () => {
    renderizar();
    await esperarFormulario();

    const horas = Array.from(screen.getByLabelText("Hora de inicio").options)
      .map((opcion) => opcion.value)
      .filter(Boolean);
    expect(horas).toHaveLength(30);
    expect(horas[0]).toBe("08:00");
    expect(horas.at(-1)).toBe("22:30");
  });

  it("P3: ofrece duraciones de 60, 90 y 120 minutos", async () => {
    renderizar();
    await esperarFormulario();

    const duraciones = Array.from(screen.getByLabelText("Duración").options)
      .map((opcion) => opcion.textContent)
      .slice(1);
    expect(duraciones).toEqual(["60 minutos", "90 minutos", "120 minutos"]);
  });

  it("muestra los lugares del encuentro con el jugador como organizador", async () => {
    renderizar();
    await esperarFormulario();

    expect(screen.getByText("Vos · Tomás Ríos")).toBeTruthy();
    expect(screen.getByText("Lugar 2 · por invitar")).toBeTruthy();
    expect(screen.getByText("Lugar 4 · por invitar")).toBeTruthy();
  });

  it.each([
    ["MASCULINO", "Organizador", "quedás registrado como participante 1"],
    ["FEMENINO", "Organizadora", "quedás registrada como participante 1"],
    ["NO_DECLARA", "Organizás", "ocupás el lugar 1"],
  ])(
    "con género %s dice %s y %s, según el perfil",
    async (genero, rol, lugarPropio) => {
      obtenerPerfil.mockResolvedValue(perfil(genero));
      renderizar();
      await esperarFormulario();

      expect(screen.getByText(rol)).toBeTruthy();
      expect(
        screen.getByText(
          `Al crear el encuentro ${lugarPropio}. Faltan 3 lugares, que se completan con invitaciones.`,
        ),
      ).toBeTruthy();
    },
  );

  it("C2: con condiciones faltantes no crea el encuentro y marca cada campo", async () => {
    renderizar();
    await esperarFormulario();
    fireEvent.change(screen.getByLabelText("Localidad"), {
      target: { value: "" },
    });

    crear();

    expect(crearEncuentro).not.toHaveBeenCalled();
    for (const etiqueta of ETIQUETAS) {
      expect(screen.getByLabelText(etiqueta).getAttribute("aria-invalid")).toBe(
        "true",
      );
      expect(mensajeDe(etiqueta)).toBe(MENSAJE_CAMPO_VACIO);
    }
    const tipo = screen.getByRole("group", { name: "Tipo de encuentro" });
    expect(
      document.getElementById(tipo.getAttribute("aria-describedby"))
        .textContent,
    ).toBe(MENSAJE_CAMPO_VACIO);
  });

  it.each([
    ["fecha", "Fecha", "Elegí una fecha y hora futuras."],
    ["fecha", "Fecha", "Elegí una fecha dentro de los próximos 60 días."],
    ["hora_inicio", "Hora de inicio", "Elegí una fecha y hora futuras."],
    [
      "duracion_minutos",
      "Duración",
      "El encuentro tiene que terminar a las 23:30 como máximo.",
    ],
  ])(
    "P4 y P6: muestra en %s el error que devuelve el backend",
    async (campo, etiqueta, mensaje) => {
      crearEncuentro.mockRejectedValue(
        new ErrorApi({ estado: 400, errores: { [campo]: [mensaje] } }),
      );
      renderizar();
      await esperarFormulario();
      completarTodo();

      crear();

      expect(await screen.findByText(mensaje)).toBeTruthy();
      expect(mensajeDe(etiqueta)).toBe(mensaje);
      expect(
        screen.getByRole("button", {
          name: "Crear encuentro y buscar jugadores",
        }).disabled,
      ).toBe(false);
    },
  );

  it("C1: crea el encuentro con las condiciones y lleva a los recomendados", async () => {
    crearEncuentro.mockResolvedValue({ id: 15 });
    renderizar();
    await esperarFormulario();
    completarTodo();

    crear();

    expect(
      await screen.findByText(
        "Destino /encuentros/15/recomendados Encuentro creado correctamente.",
      ),
    ).toBeTruthy();
    expect(crearEncuentro).toHaveBeenCalledWith({
      fecha: "2026-10-03",
      hora_inicio: "18:00",
      duracion_minutos: 90,
      localidad: 7,
      ubicacion: "Av. San Martín 4500",
      tipo_encuentro: "COMPETITIVO",
    });
  });

  it("P5: permite elegir otra localidad del catálogo", async () => {
    crearEncuentro.mockResolvedValue({ id: 15 });
    renderizar();
    await esperarFormulario();
    completarTodo();
    fireEvent.change(screen.getByLabelText("Localidad"), {
      target: { value: "3" },
    });

    crear();

    await screen.findByText(/Destino/);
    expect(crearEncuentro.mock.calls[0][0].localidad).toBe(3);
  });

  it("Cancelar vuelve al inicio sin guardar", async () => {
    renderizar();
    await esperarFormulario();

    fireEvent.click(screen.getByRole("link", { name: "Cancelar" }));

    expect(await screen.findByText(/Destino \/inicio/)).toBeTruthy();
    expect(crearEncuentro).not.toHaveBeenCalled();
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
