import { render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { obtenerInvitaciones } from "../api/invitaciones.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import PanelPrincipal from "./PanelPrincipal.jsx";

vi.mock("../api/invitaciones.js", () => ({ obtenerInvitaciones: vi.fn() }));

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

function renderizar(entrada) {
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

function seccionInvitaciones() {
  return screen.getByRole("region", { name: "Invitaciones" });
}

describe("PanelPrincipal", () => {
  beforeEach(() => {
    obtenerInvitaciones
      .mockReset()
      .mockResolvedValue({ pendientes: [], respondidas: [] });
  });

  it("saluda al jugador por su nombre", async () => {
    renderizar("/inicio");

    expect(
      screen.getByRole("heading", { level: 1, name: "Hola, Tomás" }),
    ).toBeTruthy();
    expect(
      await screen.findByText("No tenés invitaciones pendientes."),
    ).toBeTruthy();
    expect(screen.queryByRole("status")).toBeNull();
  });

  it("HU-006: ofrece crear un encuentro", () => {
    renderizar("/inicio");

    // Además del enlace de la barra superior, el botón del encabezado.
    const boton = within(screen.getByRole("main")).getByRole("link", {
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
    await screen.findByText("No tenés invitaciones pendientes.");

    expect(screen.getByRole("status").textContent).toBe(
      "Disponibilidad y preferencias guardadas correctamente.",
    );
  });

  it("HU-008: muestra cuántas invitaciones hay pendientes y la más reciente", async () => {
    obtenerInvitaciones.mockResolvedValue({
      pendientes: [
        invitacion(2, "Diego", "Ortiz", "2026-10-07"),
        invitacion(1, "Lucía", "Bravo", "2026-10-08"),
      ],
      respondidas: [],
    });
    renderizar("/inicio");

    expect(await screen.findByText("2 pendientes")).toBeTruthy();
    const seccion = seccionInvitaciones();
    expect(within(seccion).getByText("Diego Ortiz te invitó")).toBeTruthy();
    expect(
      within(seccion).getByText(
        "Mié 7 oct 2026 · 19:00 · 90 min · Villa Allende",
      ),
    ).toBeTruthy();
    expect(within(seccion).queryByText(/Lucía Bravo/)).toBeNull();
    expect(
      within(seccion)
        .getByRole("link", { name: "Ver invitaciones" })
        .getAttribute("href"),
    ).toBe("/invitaciones");
  });

  it("HU-008: con una sola pendiente usa el singular", async () => {
    obtenerInvitaciones.mockResolvedValue({
      pendientes: [invitacion(1, "Diego", "Ortiz", "2026-10-07")],
      respondidas: [],
    });
    renderizar("/inicio");

    expect(await screen.findByText("1 pendiente")).toBeTruthy();
  });

  it("HU-008: sin pendientes lo dice", async () => {
    renderizar("/inicio");

    await screen.findByText("No tenés invitaciones pendientes.");
    expect(within(seccionInvitaciones()).queryByText(/pendiente$/)).toBeNull();
    expect(within(seccionInvitaciones()).queryByText(/te invitó/)).toBeNull();
  });
});
