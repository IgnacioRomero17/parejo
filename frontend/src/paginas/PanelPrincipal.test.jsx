import { render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { obtenerEncuentrosActivos } from "../api/encuentros.js";
import { obtenerInvitaciones } from "../api/invitaciones.js";
import { listarLocalidades } from "../api/localidades.js";
import { obtenerPerfil } from "../api/perfil.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import PanelPrincipal from "./PanelPrincipal.jsx";

vi.mock("../api/encuentros.js", () => ({ obtenerEncuentrosActivos: vi.fn() }));
vi.mock("../api/invitaciones.js", () => ({ obtenerInvitaciones: vi.fn() }));
vi.mock("../api/localidades.js", () => ({ listarLocalidades: vi.fn() }));
vi.mock("../api/perfil.js", () => ({ obtenerPerfil: vi.fn() }));

function invitacion(id, nombre, apellido, fecha) {
  return {
    id,
    estado: "PENDIENTE",
    fecha_envio: "2026-10-01T18:42:00-03:00",
    organizador: { id: id + 10, nombre, apellido, genero: "MASCULINO" },
    encuentro: {
      id: id + 20,
      fecha,
      hora_inicio: "19:00",
      duracion_minutos: 90,
      localidad: { id: 5, nombre: "Villa Allende" },
      ubicacion: "Club Lomas",
      tipo_encuentro: "RECREATIVO",
      estado: "BUSCANDO_PARTICIPANTES",
      confirmados: 2,
    },
  };
}

const TOMAS = { id: 1, nombre: "Tomás", apellido: "Ríos", genero: "MASCULINO" };
const LUCIA = { id: 9, nombre: "Lucía", apellido: "Bravo", genero: "FEMENINO" };

// Un encuentro de `GET encuentros`: por defecto, organizado por Tomás y buscando participantes.
function encuentroActivo({
  id = 30,
  estado = "BUSCANDO_PARTICIPANTES",
  organizador = TOMAS,
  confirmados = 2,
  invitacionesPendientes = 1,
  ...campos
} = {}) {
  const organizas = organizador.id === TOMAS.id;
  return {
    id,
    fecha: "2026-10-03",
    hora_inicio: "18:00",
    duracion_minutos: 90,
    localidad: { id: 7, nombre: "Río Ceballos" },
    ubicacion: "Av. San Martín 4500",
    tipo_encuentro: "COMPETITIVO",
    estado,
    confirmados,
    organizador,
    organizas,
    ...(organizas && { invitaciones_pendientes: invitacionesPendientes }),
    ...campos,
  };
}

function perfil({ disponible = true, franjas = 2 } = {}) {
  return {
    datos_personales: { nombre: "Tomás", apellido: "Ríos" },
    perfil_deportivo: { localidad: 7, nivel_estimado: 4.5 },
    disponibilidad: {
      franjas: Array.from({ length: franjas }, (_, posicion) => ({
        dia_semana: posicion + 1,
        hora_inicio: "18:00",
        hora_fin: "21:00",
      })),
      tipo_encuentro: "COMPETITIVO",
      lado_preferido: "DRIVE",
      disponible_para_invitaciones: disponible,
    },
  };
}

function renderizar(entrada = "/inicio") {
  const sesion = {
    cargando: false,
    usuario: { id: 1, nombre: "Tomás", onboarding: null },
    establecerUsuario: () => {},
  };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={[entrada]}>
        <Routes>
          <Route path="/inicio" element={<PanelPrincipal />} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

function textoDe(elemento) {
  return elemento.textContent.replace(/\s+/g, " ").trim();
}

function seccion(nombre) {
  return screen.getByRole("region", { name: nombre });
}

// Espera a que carguen los tres bloques del panel.
async function esperarPanel() {
  await screen.findByText("No tenés invitaciones pendientes.");
  await screen.findByText("Franjas cargadas");
  await screen.findByRole("heading", { level: 3 });
}

async function tarjetaEncuentro() {
  const [tarjeta] = await within(
    await screen.findByRole("region", { name: "Tus encuentros activos" }),
  ).findAllByRole("article");
  return tarjeta;
}

describe("PanelPrincipal", () => {
  beforeEach(() => {
    obtenerInvitaciones
      .mockReset()
      .mockResolvedValue({ pendientes: [], respondidas: [] });
    obtenerEncuentrosActivos.mockReset().mockResolvedValue([]);
    obtenerPerfil.mockReset().mockResolvedValue(perfil());
    listarLocalidades.mockReset().mockResolvedValue([
      { id: 5, nombre: "Mendiolaza" },
      { id: 7, nombre: "Río Ceballos" },
    ]);
  });

  it("saluda al jugador por su nombre", async () => {
    renderizar();

    expect(
      screen.getByRole("heading", { level: 1, name: "Hola, Tomás" }),
    ).toBeTruthy();
    await esperarPanel();
    expect(screen.queryByRole("status")).toBeNull();
  });

  it("HU-006: ofrece crear un encuentro", async () => {
    renderizar();
    await esperarPanel();

    // Además del enlace de la barra superior, el botón del encabezado.
    const [boton] = within(screen.getByRole("main")).getAllByRole("link", {
      name: "Crear encuentro",
    });
    expect(boton.getAttribute("href")).toBe("/encuentros/nuevo");
  });

  it("muestra el aviso con el que se llega", async () => {
    renderizar({
      pathname: "/inicio",
      state: {
        aviso: "Disponibilidad y preferencias guardadas correctamente.",
      },
    });
    await esperarPanel();

    expect(screen.getByRole("status").textContent).toBe(
      "Disponibilidad y preferencias guardadas correctamente.",
    );
  });

  describe("Invitaciones (HU-008)", () => {
    it("muestra cuántas invitaciones hay pendientes y la más reciente", async () => {
      obtenerInvitaciones.mockResolvedValue({
        pendientes: [
          invitacion(2, "Diego", "Ortiz", "2026-10-07"),
          invitacion(1, "Lucía", "Bravo", "2026-10-08"),
        ],
        respondidas: [],
      });
      renderizar();

      expect(await screen.findByText("2 pendientes")).toBeTruthy();
      const invitaciones = seccion("Invitaciones");
      expect(
        within(invitaciones).getByText("Diego Ortiz te invitó"),
      ).toBeTruthy();
      expect(
        within(invitaciones).getByText(
          "Mié 7 oct 2026 · 19:00 · 90 min · Villa Allende",
        ),
      ).toBeTruthy();
      expect(within(invitaciones).queryByText(/Lucía Bravo/)).toBeNull();
      expect(
        within(invitaciones)
          .getByRole("link", { name: "Ver invitaciones" })
          .getAttribute("href"),
      ).toBe("/invitaciones");
    });

    it("con una sola pendiente usa el singular", async () => {
      obtenerInvitaciones.mockResolvedValue({
        pendientes: [invitacion(1, "Diego", "Ortiz", "2026-10-07")],
        respondidas: [],
      });
      renderizar();

      expect(await screen.findByText("1 pendiente")).toBeTruthy();
    });

    it("sin pendientes lo dice", async () => {
      renderizar();

      await screen.findByText("No tenés invitaciones pendientes.");
      const invitaciones = seccion("Invitaciones");
      expect(within(invitaciones).queryByText(/pendiente$/)).toBeNull();
      expect(within(invitaciones).queryByText(/te invitó/)).toBeNull();
    });
  });

  describe("Tus encuentros activos (HU-012)", () => {
    it("muestra los encuentros en el orden que llegan, con sus datos", async () => {
      obtenerEncuentrosActivos.mockResolvedValue([
        encuentroActivo(),
        encuentroActivo({
          id: 31,
          fecha: "2026-10-08",
          hora_inicio: "20:00",
          duracion_minutos: 60,
          localidad: { id: 8, nombre: "Unquillo" },
          ubicacion: "Bv. Illia 350",
          tipo_encuentro: "RECREATIVO",
          estado: "COMPLETO",
          organizador: LUCIA,
          confirmados: 4,
        }),
      ]);
      renderizar();
      await tarjetaEncuentro();

      const [primero, segundo] = within(
        seccion("Tus encuentros activos"),
      ).getAllByRole("article");
      expect(textoDe(primero)).toBe(
        "Buscando participantesOrganizás vosCompetitivo" +
          "Sábado 3 de octubre · 18:0090 minutosRío Ceballos · Av. San Martín 4500" +
          "2 de 4confirmados · 1 invitación pendienteVer seguimiento",
      );
      expect(textoDe(segundo)).toBe(
        "CompletoTe invitaronRecreativo" +
          "Jueves 8 de octubre · 20:0060 minutosUnquillo · Bv. Illia 350Organiza Lucía Bravo" +
          "4 de 4Esperando que la organizadora inicie la formación automática de parejas.",
      );
    });

    it("buscando participantes, al organizador: confirmados, pendientes y seguimiento", async () => {
      obtenerEncuentrosActivos.mockResolvedValue([
        encuentroActivo({ invitacionesPendientes: 2 }),
      ]);
      renderizar();
      const tarjeta = await tarjetaEncuentro();

      expect(
        within(tarjeta).getByText("confirmados · 2 invitaciones pendientes"),
      ).toBeTruthy();
      expect(
        within(tarjeta)
          .getByRole("link", { name: "Ver seguimiento" })
          .getAttribute("href"),
      ).toBe("/encuentros/30");
    });

    it("buscando participantes sin invitaciones pendientes dice solo «confirmados»", async () => {
      obtenerEncuentrosActivos.mockResolvedValue([
        encuentroActivo({ invitacionesPendientes: 0 }),
      ]);
      renderizar();
      const tarjeta = await tarjetaEncuentro();

      expect(within(tarjeta).getByText("confirmados")).toBeTruthy();
      expect(within(tarjeta).queryByText(/pendiente/)).toBeNull();
    });

    it("buscando participantes, al invitado: solo confirmados y sin acción", async () => {
      obtenerEncuentrosActivos.mockResolvedValue([
        encuentroActivo({ organizador: LUCIA }),
      ]);
      renderizar();
      const tarjeta = await tarjetaEncuentro();

      expect(within(tarjeta).getByText("Te invitaron")).toBeTruthy();
      expect(within(tarjeta).getByText("confirmados")).toBeTruthy();
      expect(within(tarjeta).queryByRole("link")).toBeNull();
    });

    it("completo, al organizador: listo para formar parejas", async () => {
      obtenerEncuentrosActivos.mockResolvedValue([
        encuentroActivo({ estado: "COMPLETO", confirmados: 4 }),
      ]);
      renderizar();
      const tarjeta = await tarjetaEncuentro();

      expect(
        within(tarjeta).getByText("Listo para formar parejas."),
      ).toBeTruthy();
      expect(
        within(tarjeta)
          .getByRole("link", { name: "Formar parejas" })
          .getAttribute("href"),
      ).toBe("/encuentros/30");
    });

    it.each([
      [
        "MASCULINO",
        "Esperando que el organizador inicie la formación automática de parejas.",
      ],
      [
        "NO_DECLARA",
        "Esperando que se inicie la formación automática de parejas.",
      ],
    ])(
      "completo, al invitado con organizador %s: «%s»",
      async (genero, texto) => {
        obtenerEncuentrosActivos.mockResolvedValue([
          encuentroActivo({
            estado: "COMPLETO",
            confirmados: 4,
            organizador: { ...LUCIA, genero },
          }),
        ]);
        renderizar();
        const tarjeta = await tarjetaEncuentro();

        expect(within(tarjeta).getByText(texto)).toBeTruthy();
        expect(within(tarjeta).queryByRole("link")).toBeNull();
      },
    );

    it.each([
      ["al organizador", TOMAS],
      ["al invitado", LUCIA],
    ])(
      "con propuesta generada, %s: parejas formadas y ver propuesta",
      async (_, organizador) => {
        obtenerEncuentrosActivos.mockResolvedValue([
          encuentroActivo({
            estado: "PROPUESTA_GENERADA",
            confirmados: 4,
            organizador,
          }),
        ]);
        renderizar();
        const tarjeta = await tarjetaEncuentro();

        expect(within(tarjeta).getByText("Propuesta generada")).toBeTruthy();
        expect(within(tarjeta).getByText("Parejas formadas.")).toBeTruthy();
        expect(
          within(tarjeta)
            .getByRole("link", { name: "Ver propuesta" })
            .getAttribute("href"),
        ).toBe("/encuentros/30/propuesta");
      },
    );

    it("sin encuentros activos invita a crear el primero", async () => {
      renderizar();

      const encuentros = await screen.findByRole("region", {
        name: "Tus encuentros activos",
      });
      expect(
        await within(encuentros).findByRole("heading", {
          name: "Todavía no tenés encuentros",
        }),
      ).toBeTruthy();
      expect(
        within(encuentros).getByText(
          "Creá un encuentro o aceptá una invitación para verlo acá.",
        ),
      ).toBeTruthy();
      expect(
        within(encuentros)
          .getByRole("link", { name: "Crear tu primer encuentro" })
          .getAttribute("href"),
      ).toBe("/encuentros/nuevo");
    });
  });

  describe("Tu perfil (HU-012)", () => {
    function datosPerfil() {
      return within(seccion("Tu perfil"))
        .getAllByRole("term")
        .map((rotulo) => [textoDe(rotulo), textoDe(rotulo.nextElementSibling)]);
    }

    it("muestra nivel, localidad, franjas y que recibe invitaciones", async () => {
      renderizar();
      await screen.findByText("Franjas cargadas");

      expect(datosPerfil()).toEqual([
        ["Nivel estimado", "4,5"],
        ["Localidad", "Río Ceballos"],
        ["Franjas cargadas", "2"],
        ["Recibir invitaciones", "Disponible"],
      ]);
      expect(
        within(seccion("Tu perfil"))
          .getByRole("link", { name: "Editar perfil" })
          .getAttribute("href"),
      ).toBe("/perfil");
    });

    it("sin disponibilidad para invitaciones dice «No disponible»", async () => {
      obtenerPerfil.mockResolvedValue(
        perfil({ disponible: false, franjas: 0 }),
      );
      renderizar();
      await screen.findByText("Franjas cargadas");

      expect(datosPerfil().slice(2)).toEqual([
        ["Franjas cargadas", "0"],
        ["Recibir invitaciones", "No disponible"],
      ]);
    });
  });
});
