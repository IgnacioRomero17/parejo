import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { Link, MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { obtenerUsuarioActual, pedirCsrf } from "../api/auth.js";
import { useSesion } from "../hooks/useSesion.js";
import SesionProveedor from "./SesionContexto.jsx";

vi.mock("../api/auth.js", () => ({
  obtenerUsuarioActual: vi.fn(),
  pedirCsrf: vi.fn(),
}));

function Pendientes() {
  const { usuario } = useSesion();
  return (
    <>
      <p>Pendientes: {usuario?.invitaciones_pendientes ?? "sin sesión"}</p>
      <Link to="/otra">Ir</Link>
    </>
  );
}

function renderizar() {
  return render(
    <MemoryRouter initialEntries={["/inicio"]}>
      <SesionProveedor>
        <Routes>
          <Route path="*" element={<Pendientes />} />
        </Routes>
      </SesionProveedor>
    </MemoryRouter>,
  );
}

function usuario(invitacionesPendientes) {
  return {
    id: 1,
    nombre: "Tomás",
    onboarding: null,
    invitaciones_pendientes: invitacionesPendientes,
  };
}

describe("SesionProveedor (HU-008)", () => {
  beforeEach(() => {
    pedirCsrf.mockReset().mockResolvedValue(null);
    obtenerUsuarioActual.mockReset();
  });

  it("al cambiar de ruta vuelve a pedir la sesión para actualizar las pendientes", async () => {
    obtenerUsuarioActual
      .mockResolvedValueOnce(usuario(1))
      .mockResolvedValueOnce(usuario(2));
    renderizar();
    expect(await screen.findByText("Pendientes: 1")).toBeTruthy();

    fireEvent.click(screen.getByRole("link", { name: "Ir" }));

    expect(await screen.findByText("Pendientes: 2")).toBeTruthy();
    expect(obtenerUsuarioActual).toHaveBeenCalledTimes(2);
  });

  it("sin sesión no la pide de nuevo al navegar", async () => {
    obtenerUsuarioActual.mockRejectedValue(new Error("401"));
    renderizar();
    expect(await screen.findByText("Pendientes: sin sesión")).toBeTruthy();

    fireEvent.click(screen.getByRole("link", { name: "Ir" }));

    await waitFor(() => expect(obtenerUsuarioActual).toHaveBeenCalledTimes(1));
  });
});
