import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ErrorApi } from "../api/cliente.js";
import {
  enviarInvitaciones,
  obtenerEncuentro,
  obtenerRecomendados,
} from "../api/encuentros.js";
import { obtenerPerfil } from "../api/perfil.js";
import { ContextoSesion } from "../contexto/contextoSesion.js";
import SeguimientoEncuentro from "./SeguimientoEncuentro.jsx";

vi.mock("../api/encuentros.js", () => ({
  enviarInvitaciones: vi.fn(),
  obtenerEncuentro: vi.fn(),
  obtenerRecomendados: vi.fn(),
}));
vi.mock("../api/perfil.js", () => ({ obtenerPerfil: vi.fn() }));

function jugador(id, nombre, apellido, localidad, nivel) {
  return {
    id,
    nombre,
    apellido,
    localidad: { id: id + 100, nombre: localidad },
    nivel,
  };
}

const TOMAS = jugador(1, "Tomás", "Ríos", "Río Ceballos", 4.5);
const VALENTINA = jugador(2, "Valentina", "Sosa", "Río Ceballos", 4.5);
const JOAQUIN = jugador(3, "Joaquín", "Medina", "Unquillo", 4.5);
const CAMILA = jugador(4, "Camila", "Paz", "Mendiolaza", 5);

function invitacion(id, invitado, estado) {
  return {
    id,
    jugador: invitado,
    estado,
    fecha_envio: "2026-10-01T18:42:00-03:00",
  };
}

const ENCUENTRO = {
  id: 15,
  fecha: "2026-10-03",
  hora_inicio: "18:00",
  duracion_minutos: 90,
  localidad: { id: 7, nombre: "Río Ceballos" },
  ubicacion: "Av. San Martín 4500",
  tipo_encuentro: "COMPETITIVO",
  estado: "BUSCANDO_PARTICIPANTES",
  confirmados: 2,
  lugares_libres: 1,
  participantes: [
    { ...TOMAS, lado: "DRIVE" },
    { ...VALENTINA, lado: "REVES" },
  ],
  invitaciones: [
    invitacion(31, VALENTINA, "ACEPTADA"),
    invitacion(32, JOAQUIN, "RECHAZADA"),
    invitacion(33, CAMILA, "PENDIENTE"),
  ],
};

function recomendado(id, nombre, apellido, localidad, nivel, inicio, fin) {
  return {
    ...jugador(id, nombre, apellido, localidad, nivel),
    franja: { dia_semana: 6, hora_inicio: inicio, hora_fin: fin },
  };
}

const RECOMENDADOS = [
  recomendado(5, "Federico", "Luna", "Villa Allende", 5, "15:00", "20:00"),
  recomendado(6, "Bruno", "Castro", "Salsipuedes", 4, "18:00", "20:00"),
  recomendado(7, "Agustina", "Rey", "La Calera", 5, "17:30", "21:00"),
];

function recomendacion(lugaresLibres, recomendados = RECOMENDADOS) {
  return {
    lugares_libres: lugaresLibres,
    suficientes: recomendados.length >= lugaresLibres,
    recomendados,
  };
}

function perfil(genero) {
  return { perfil_deportivo: { genero } };
}

function renderizar() {
  const sesion = {
    cargando: false,
    usuario: { id: 1, nombre: "Tomás", onboarding: null },
    establecerUsuario: vi.fn(),
  };
  return render(
    <ContextoSesion.Provider value={sesion}>
      <MemoryRouter initialEntries={["/encuentros/15"]}>
        <Routes>
          <Route path="/encuentros/:id" element={<SeguimientoEncuentro />} />
          <Route path="/inicio" element={<h1>Inicio</h1>} />
        </Routes>
      </MemoryRouter>
    </ContextoSesion.Provider>,
  );
}

function esperarPantalla12() {
  return screen.findByRole("heading", {
    level: 1,
    name: "Seleccionar e invitar jugadores",
  });
}

function textoDe(elemento) {
  return elemento.textContent.replace(/\s+/g, " ").trim();
}

function casilla(nombre) {
  return screen.getByRole("checkbox", { name: nombre });
}

function panelLugares() {
  return screen.getByRole("complementary", { name: "Lugares del encuentro" });
}

function botonEnviar() {
  return screen.getByRole("button", { name: /^Enviar invitación/ });
}

describe("SeguimientoEncuentro · seleccionar e invitar (HU-008)", () => {
  beforeEach(() => {
    obtenerEncuentro.mockReset().mockResolvedValue(ENCUENTRO);
    obtenerRecomendados.mockReset().mockResolvedValue(recomendacion(1));
    obtenerPerfil.mockReset().mockResolvedValue(perfil("MASCULINO"));
    enviarInvitaciones.mockReset();
  });

  it("muestra el encuentro y los ya invitados con su estado, en orden de envío", async () => {
    renderizar();
    await esperarPantalla12();

    expect(obtenerEncuentro).toHaveBeenCalledWith("15");
    expect(obtenerRecomendados).toHaveBeenCalledWith("15");
    expect(
      screen.getByText("Encuentro · Sáb 3 oct 2026 · 18:00 · Río Ceballos"),
    ).toBeTruthy();
    const invitados = screen.getByRole("region", { name: "Ya invitados" });
    expect(within(invitados).getByText("3 invitaciones enviadas")).toBeTruthy();
    expect(within(invitados).getAllByRole("listitem").map(textoDe)).toEqual([
      "VSValentina SosaRío CeballosNivel 4,5Aceptada",
      "JMJoaquín MedinaUnquilloNivel 4,5Rechazada",
      "CPCamila PazMendiolazaNivel 5,0Pendiente",
    ]);
    // Los ya invitados no tienen casilla: no se pueden volver a invitar.
    expect(screen.queryByRole("checkbox", { name: "Camila Paz" })).toBeNull();
  });

  it("lista los disponibles en el orden del motor, con franja y casilla", async () => {
    renderizar();
    await esperarPantalla12();

    const disponibles = screen.getByRole("list", {
      name: "Disponibles para invitar",
    });
    expect(within(disponibles).getAllByRole("listitem").map(textoDe)).toEqual([
      "1FLFederico LunaVilla Allende · sáb 15:00–20:00Nivel 5,0",
      "2BCBruno CastroSalsipuedes · sáb 18:00–20:00Nivel 4,0",
      "3ARAgustina ReyLa Calera · sáb 17:30–21:00Nivel 5,0",
    ]);
    expect(screen.getByText("1 lugar libre · 0 seleccionados")).toBeTruthy();
    expect(botonEnviar().textContent).toBe("Enviar invitación (0)");
    expect(botonEnviar().disabled).toBe(true);
  });

  it("C1: al seleccionar muestra a quién se invita y lo agrega a los lugares", async () => {
    renderizar();
    await esperarPantalla12();

    fireEvent.click(casilla("Federico Luna"));

    expect(casilla("Federico Luna").checked).toBe(true);
    expect(screen.getByText("Seleccionado")).toBeTruthy();
    expect(screen.getByText("1 lugar libre · 1 seleccionado")).toBeTruthy();
    expect(textoDe(screen.getByText(/Vas a invitar a/))).toBe(
      "Vas a invitar a Federico Luna",
    );
    expect(botonEnviar().textContent).toBe("Enviar invitación (1)");
    expect(botonEnviar().disabled).toBe(false);
    expect(
      within(panelLugares()).getByText("Seleccionado · sin enviar"),
    ).toBeTruthy();
  });

  it("P2: al llegar a los lugares libres deshabilita las demás casillas y lo explica", async () => {
    renderizar();
    await esperarPantalla12();

    fireEvent.click(casilla("Federico Luna"));

    expect(casilla("Bruno Castro").disabled).toBe(true);
    expect(casilla("Agustina Rey").disabled).toBe(true);
    expect(casilla("Federico Luna").disabled).toBe(false);
    expect(
      screen.getByText(
        "Como queda 1 lugar libre, podés seleccionar 1 jugador. Para elegir a otro, quitá la selección actual.",
      ),
    ).toBeTruthy();

    fireEvent.click(casilla("Federico Luna"));

    expect(casilla("Bruno Castro").disabled).toBe(false);
    expect(screen.queryByText(/Como queda/)).toBeNull();
  });

  it("P2: con dos lugares libres el límite está en plural", async () => {
    obtenerEncuentro.mockResolvedValue({ ...ENCUENTRO, lugares_libres: 2 });
    obtenerRecomendados.mockResolvedValue(recomendacion(2));
    renderizar();
    await esperarPantalla12();

    fireEvent.click(casilla("Federico Luna"));
    fireEvent.click(casilla("Bruno Castro"));

    expect(casilla("Agustina Rey").disabled).toBe(true);
    expect(
      screen.getByText(
        "Como quedan 2 lugares libres, podés seleccionar 2 jugadores. Para elegir a otro, quitá la selección actual.",
      ),
    ).toBeTruthy();
    expect(textoDe(screen.getByText(/Vas a invitar a/))).toBe(
      "Vas a invitar a Federico Luna y Bruno Castro",
    );
  });

  it("C1: envía las invitaciones, avisa y actualiza los paneles", async () => {
    obtenerEncuentro.mockResolvedValue({ ...ENCUENTRO, lugares_libres: 2 });
    obtenerRecomendados.mockResolvedValue(recomendacion(2));
    enviarInvitaciones.mockResolvedValue([{ id: 40 }, { id: 41 }]);
    renderizar();
    await esperarPantalla12();

    fireEvent.click(casilla("Bruno Castro"));
    fireEvent.click(casilla("Federico Luna"));
    fireEvent.click(botonEnviar());

    expect((await screen.findByRole("status")).textContent).toBe(
      "2 invitaciones enviadas.",
    );
    expect(enviarInvitaciones).toHaveBeenCalledWith("15", [6, 5]);
    await waitFor(() => expect(obtenerEncuentro).toHaveBeenCalledTimes(2));
    await waitFor(() => expect(obtenerRecomendados).toHaveBeenCalledTimes(2));
    expect(casilla("Federico Luna").checked).toBe(false);
  });

  it("con una sola invitación el aviso está en singular", async () => {
    enviarInvitaciones.mockResolvedValue([{ id: 40 }]);
    renderizar();
    await esperarPantalla12();

    fireEvent.click(casilla("Federico Luna"));
    fireEvent.click(botonEnviar());

    expect((await screen.findByRole("status")).textContent).toBe(
      "Invitación enviada.",
    );
  });

  it("si el backend rechaza el envío, muestra el motivo y actualiza la lista", async () => {
    enviarInvitaciones.mockRejectedValue(
      new ErrorApi({
        estado: 409,
        detalle:
          "Alguno de los jugadores ya no está disponible para este encuentro. Actualizá la lista.",
      }),
    );
    renderizar();
    await esperarPantalla12();

    fireEvent.click(casilla("Federico Luna"));
    fireEvent.click(botonEnviar());

    expect((await screen.findByRole("alert")).textContent).toBe(
      "Alguno de los jugadores ya no está disponible para este encuentro. Actualizá la lista.",
    );
    await waitFor(() => expect(obtenerRecomendados).toHaveBeenCalledTimes(2));
  });

  it("sin lugares libres por invitaciones pendientes, pide esperar", async () => {
    obtenerEncuentro.mockResolvedValue({ ...ENCUENTRO, lugares_libres: 0 });
    obtenerRecomendados.mockResolvedValue(recomendacion(0));
    renderizar();
    await esperarPantalla12();

    expect(
      screen.getByText("Esperá la respuesta de las invitaciones pendientes."),
    ).toBeTruthy();
    expect(screen.queryByRole("checkbox")).toBeNull();
    expect(screen.queryByRole("button", { name: /^Enviar/ })).toBeNull();
  });

  it("muestra los lugares del encuentro con confirmados y pendientes", async () => {
    renderizar();
    await esperarPantalla12();

    const panel = panelLugares();
    expect(textoDe(within(panel).getByText("2 de 4").parentElement)).toBe(
      "2 de 4confirmados · 2 lugares restantes",
    );
    expect(within(panel).getAllByRole("listitem").map(textoDe)).toEqual([
      "TRVos · Tomás RíosOrganizadorConfirmado",
      "VSValentina SosaAceptó la invitaciónConfirmado",
      "CPCamila PazInvitación enviadaPendiente",
    ]);
    const formar = within(panel).getByRole("button", {
      name: "Formar parejas equilibradas",
    });
    expect(formar.disabled).toBe(true);
  });

  it.each([
    ["MASCULINO", "Organizador"],
    ["FEMENINO", "Organizadora"],
    ["NO_DECLARA", "Organizás"],
  ])("con género %s el rol propio dice %s", async (genero, rol) => {
    obtenerPerfil.mockResolvedValue(perfil(genero));
    renderizar();
    await esperarPantalla12();

    expect(within(panelLugares()).getByText(rol)).toBeTruthy();
  });

  it("a un participante que no organiza lo lleva al inicio", async () => {
    const { invitaciones: _, ...sinInvitaciones } = ENCUENTRO;
    obtenerEncuentro.mockResolvedValue(sinInvitaciones);
    renderizar();

    expect(
      await screen.findByRole("heading", { level: 1, name: "Inicio" }),
    ).toBeTruthy();
    expect(obtenerRecomendados).not.toHaveBeenCalled();
  });
});

describe("SeguimientoEncuentro · encuentro completo (HU-008)", () => {
  const CAMILA_CONFIRMADA = { ...CAMILA, lado: "REVES" };
  const FEDERICO = { ...jugador(5, "Federico", "Luna", "Villa Allende", 5) };
  const COMPLETO = {
    ...ENCUENTRO,
    estado: "COMPLETO",
    confirmados: 4,
    lugares_libres: 0,
    participantes: [
      ...ENCUENTRO.participantes,
      CAMILA_CONFIRMADA,
      { ...FEDERICO, lado: "DRIVE" },
    ],
    invitaciones: [
      invitacion(31, VALENTINA, "ACEPTADA"),
      invitacion(32, JOAQUIN, "RECHAZADA"),
      invitacion(33, CAMILA, "ACEPTADA"),
      invitacion(34, FEDERICO, "ACEPTADA"),
    ],
  };

  beforeEach(() => {
    obtenerEncuentro.mockReset().mockResolvedValue(COMPLETO);
    obtenerRecomendados.mockReset();
    obtenerPerfil.mockReset();
  });

  it("P4: con 4 confirmados muestra la pantalla 14", async () => {
    renderizar();

    expect(
      await screen.findByRole("heading", {
        level: 1,
        name: "¡Encuentro completo!",
      }),
    ).toBeTruthy();
    expect(screen.getByText("4 de 4 jugadores confirmados")).toBeTruthy();
    expect(
      screen
        .getByRole("list", { name: "Participantes" })
        .querySelectorAll("li"),
    ).toHaveLength(4);
    expect(screen.getByText("Vos · Nivel 4,5")).toBeTruthy();
    expect(screen.getByText("Río Ceballos · Av. San Martín 4500")).toBeTruthy();
    expect(obtenerRecomendados).not.toHaveBeenCalled();
  });

  it("muestra las invitaciones enviadas con su estado", async () => {
    renderizar();

    const panel = await screen.findByRole("complementary", {
      name: "Invitaciones enviadas",
    });
    expect(within(panel).getAllByRole("listitem").map(textoDe)).toEqual([
      "Valentina SosaAceptada",
      "Joaquín MedinaRechazada",
      "Camila PazAceptada",
      "Federico LunaAceptada",
    ]);
  });

  it("el botón para formar parejas queda deshabilitado hasta HU-009", async () => {
    renderizar();
    await screen.findByText("4 de 4 jugadores confirmados");

    expect(
      screen.getByRole("button", { name: "Formar parejas equilibradas" })
        .disabled,
    ).toBe(true);
  });
});
