import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ErrorApi } from "../api/cliente.js";
import {
  aceptarInvitacion,
  obtenerInvitaciones,
  rechazarInvitacion,
} from "../api/invitaciones.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import BandejaInvitaciones from "./BandejaInvitaciones.jsx";

vi.mock("../api/invitaciones.js", () => ({
  aceptarInvitacion: vi.fn(),
  obtenerInvitaciones: vi.fn(),
  rechazarInvitacion: vi.fn(),
}));

function invitacion({
  id = 1,
  estado = "PENDIENTE",
  genero = "MASCULINO",
  estadoEncuentro = "BUSCANDO_PARTICIPANTES",
  confirmados = 2,
} = {}) {
  return {
    id,
    estado,
    fecha_envio: "2026-09-20T18:42:00-03:00",
    organizador: { id: 9, nombre: "Tomás", apellido: "Ríos", genero },
    encuentro: {
      id: id + 20,
      fecha: "2026-10-03",
      hora_inicio: "18:00",
      duracion_minutos: 90,
      localidad: { id: 7, nombre: "Río Ceballos" },
      ubicacion: "Av. San Martín 4500",
      tipo_encuentro: "COMPETITIVO",
      estado: estadoEncuentro,
      confirmados,
    },
  };
}

function bandeja(pendientes = [], respondidas = []) {
  return { pendientes, respondidas };
}

let refrescarUsuario;

function renderizar() {
  refrescarUsuario = vi.fn();
  const sesion = {
    cargando: false,
    usuario: { id: 2, nombre: "Valentina", onboarding: null },
    establecerUsuario: vi.fn(),
    refrescarUsuario,
  };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={["/invitaciones"]}>
        <BandejaInvitaciones />
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

describe("BandejaInvitaciones (HU-008)", () => {
  beforeEach(() => {
    obtenerInvitaciones.mockReset().mockResolvedValue(bandeja([invitacion()]));
    aceptarInvitacion.mockReset().mockResolvedValue({});
    rechazarInvitacion.mockReset().mockResolvedValue({});
  });

  it("C2: muestra la información del encuentro y las opciones aceptar y rechazar", async () => {
    renderizar();

    const tarjeta = await screen.findByRole("article", {
      name: "Tomás Ríos te invitó a un encuentro",
    });
    expect(
      screen.getByRole("heading", { name: "Pendientes · 1" }),
    ).toBeTruthy();
    expect(textoDe(within(tarjeta).getByText(/· enviada/))).toBe(
      "Organizador · enviada Dom 20 sep 2026 18:42",
    );
    expect(within(tarjeta).getByText("Pendiente")).toBeTruthy();
    const datos = within(tarjeta)
      .getAllByRole("term")
      .map((termino) => [
        termino.textContent,
        textoDe(termino.nextElementSibling),
      ]);
    expect(datos).toEqual([
      ["Fecha", "Sáb 3 oct 2026"],
      ["Hora", "18:00"],
      ["Duración", "90 min"],
      ["Tipo", "Competitivo"],
      ["Lugar", "Río Ceballos · Av. San Martín 4500"],
      ["Lugares", "2 de 4· faltan 2"],
    ]);
    expect(
      within(tarjeta).getByRole("button", { name: "Rechazar" }),
    ).toBeTruthy();
    expect(
      within(tarjeta).getByRole("button", { name: "Aceptar invitación" }),
    ).toBeTruthy();
  });

  it.each([
    ["MASCULINO", "Organizador"],
    ["FEMENINO", "Organizadora"],
    ["NO_DECLARA", "Organiza el encuentro"],
  ])("con género %s nombra al organizador como %s", async (genero, rol) => {
    obtenerInvitaciones.mockResolvedValue(bandeja([invitacion({ genero })]));
    renderizar();

    expect(
      await screen.findByText(new RegExp(`^${rol} · enviada`)),
    ).toBeTruthy();
  });

  it("C3: al aceptar, avisa, actualiza la bandeja y el indicador", async () => {
    renderizar();
    fireEvent.click(
      await screen.findByRole("button", { name: "Aceptar invitación" }),
    );

    expect((await screen.findByRole("status")).textContent).toBe(
      "Te sumaste al encuentro.",
    );
    expect(aceptarInvitacion).toHaveBeenCalledWith(1);
    expect(rechazarInvitacion).not.toHaveBeenCalled();
    await waitFor(() => expect(obtenerInvitaciones).toHaveBeenCalledTimes(2));
    expect(refrescarUsuario).toHaveBeenCalled();
  });

  it("C3: al rechazar, avisa y actualiza la bandeja", async () => {
    renderizar();
    fireEvent.click(await screen.findByRole("button", { name: "Rechazar" }));

    expect((await screen.findByRole("status")).textContent).toBe(
      "Rechazaste la invitación.",
    );
    expect(rechazarInvitacion).toHaveBeenCalledWith(1);
    await waitFor(() => expect(obtenerInvitaciones).toHaveBeenCalledTimes(2));
    expect(refrescarUsuario).toHaveBeenCalled();
  });

  it("P6: si el encuentro ya comenzó, muestra el motivo", async () => {
    aceptarInvitacion.mockRejectedValue(
      new ErrorApi({ estado: 409, detalle: "Este encuentro ya comenzó." }),
    );
    renderizar();
    fireEvent.click(
      await screen.findByRole("button", { name: "Aceptar invitación" }),
    );

    expect((await screen.findByRole("alert")).textContent).toBe(
      "Este encuentro ya comenzó.",
    );
    expect(screen.queryByRole("status")).toBeNull();
  });

  it.each([
    ["FEMENINO", "Esperando que la organizadora forme las parejas."],
    ["MASCULINO", "Esperando que el organizador forme las parejas."],
    [
      "NO_DECLARA",
      "Esperando que se inicie la formación automática de parejas.",
    ],
  ])(
    "una aceptada de un encuentro completo con organizador %s dice: %s",
    async (genero, texto) => {
      obtenerInvitaciones.mockResolvedValue(
        bandeja(
          [],
          [
            invitacion({
              estado: "ACEPTADA",
              genero,
              estadoEncuentro: "COMPLETO",
              confirmados: 4,
            }),
          ],
        ),
      );
      renderizar();

      expect(await screen.findByText(texto)).toBeTruthy();
      const respondidas = seccion("Respondidas");
      expect(within(respondidas).getByText("Completo")).toBeTruthy();
      expect(within(respondidas).getByText("Aceptada")).toBeTruthy();
    },
  );

  it("muestra las respondidas con su estado", async () => {
    obtenerInvitaciones.mockResolvedValue(
      bandeja(
        [],
        [
          invitacion({ id: 1, estado: "ACEPTADA", confirmados: 3 }),
          invitacion({ id: 2, estado: "RECHAZADA" }),
        ],
      ),
    );
    renderizar();

    expect(
      await screen.findByText("No tenés invitaciones pendientes."),
    ).toBeTruthy();
    expect(
      within(seccion("Respondidas")).getAllByRole("listitem").map(textoDe),
    ).toEqual([
      "TRTomás RíosSáb 3 oct 2026 · 18:00 · 90 min · Río Ceballos · Av. San Martín 4500AceptadaBuscando participantes3 de 4 confirmados.",
      "TRTomás RíosSáb 3 oct 2026 · 18:00 · 90 min · Río Ceballos · Av. San Martín 4500RechazadaRechazaste esta invitación.",
    ]);
  });

  it("sin ninguna invitación explica cómo recibirlas", async () => {
    obtenerInvitaciones.mockResolvedValue(bandeja());
    renderizar();

    expect(
      await screen.findByText(
        "Todavía no recibiste invitaciones. Para recibirlas, activá «Disponible para recibir invitaciones» en tu perfil.",
      ),
    ).toBeTruthy();
    expect(screen.queryByRole("heading", { name: /Pendientes/ })).toBeNull();
  });
});
