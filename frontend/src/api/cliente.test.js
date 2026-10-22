import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { configurarReacciones, ErrorApi, pedir } from "./cliente.js";

function respuestaJson(estado, cuerpo) {
  return new Response(cuerpo === undefined ? null : JSON.stringify(cuerpo), {
    status: estado,
    headers: { "Content-Type": "application/json" },
  });
}

describe("cliente de la API", () => {
  let alNoAutenticado;
  let alFaltarOnboarding;

  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    document.cookie = "csrftoken=token-de-prueba";
    alNoAutenticado = vi.fn();
    alFaltarOnboarding = vi.fn();
    configurarReacciones({ alNoAutenticado, alFaltarOnboarding });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("envía JSON con prefijo, credenciales y token CSRF al escribir", async () => {
    fetch.mockResolvedValue(respuestaJson(201, { id: 1 }));

    const cuerpo = await pedir("POST", "auth/registro", { nombre: "Tomás" });

    expect(cuerpo).toEqual({ id: 1 });
    const [url, opciones] = fetch.mock.calls[0];
    expect(url).toBe("/api/auth/registro");
    expect(opciones.method).toBe("POST");
    expect(opciones.credentials).toBe("include");
    expect(opciones.headers["X-CSRFToken"]).toBe("token-de-prueba");
    expect(opciones.headers["Content-Type"]).toBe("application/json");
    expect(opciones.body).toBe(JSON.stringify({ nombre: "Tomás" }));
  });

  it("no manda token CSRF ni cuerpo al leer", async () => {
    fetch.mockResolvedValue(respuestaJson(200, { id: 1 }));

    await pedir("GET", "auth/yo");

    const [, opciones] = fetch.mock.calls[0];
    expect(opciones.headers["X-CSRFToken"]).toBeUndefined();
    expect(opciones.body).toBeUndefined();
  });

  it("devuelve null en respuestas sin cuerpo", async () => {
    fetch.mockResolvedValue(new Response(null, { status: 204 }));

    expect(await pedir("GET", "auth/csrf")).toBeNull();
  });

  it("convierte los errores de campo del backend", async () => {
    const errores = { email: ["Este correo ya está registrado."] };
    fetch.mockResolvedValue(respuestaJson(400, { errores }));

    const error = await pedir("POST", "auth/registro", {}).catch((e) => e);

    expect(error).toBeInstanceOf(ErrorApi);
    expect(error.estado).toBe(400);
    expect(error.errores).toEqual(errores);
    expect(error.detalle).toBe("");
  });

  it("convierte el error general del backend", async () => {
    fetch.mockResolvedValue(
      respuestaJson(409, { detalle: "Este encuentro ya comenzó." }),
    );

    const error = await pedir("POST", "encuentros/1/formar-parejas", {}).catch(
      (e) => e,
    );

    expect(error.estado).toBe(409);
    expect(error.errores).toEqual({});
    expect(error.detalle).toBe("Este encuentro ya comenzó.");
  });

  it("usa un mensaje general si el backend no manda ninguno", async () => {
    fetch.mockResolvedValue(new Response("<html>", { status: 500 }));

    const error = await pedir("GET", "auth/yo").catch((e) => e);

    expect(error.estado).toBe(500);
    expect(error.detalle).toBe(
      "Algo salió mal. Probá de nuevo en unos minutos.",
    );
  });

  it("avisa cuando no puede conectar con el servidor", async () => {
    fetch.mockRejectedValue(new TypeError("Failed to fetch"));

    const error = await pedir("GET", "auth/yo").catch((e) => e);

    expect(error).toBeInstanceOf(ErrorApi);
    expect(error.detalle).toBe(
      "No pudimos conectar con el servidor. Probá de nuevo en unos minutos.",
    );
  });

  it("reacciona a un 401 limpiando la sesión", async () => {
    fetch.mockResolvedValue(
      respuestaJson(401, { detalle: "Iniciá sesión para continuar." }),
    );

    await pedir("GET", "perfil").catch(() => {});

    expect(alNoAutenticado).toHaveBeenCalledOnce();
    expect(alFaltarOnboarding).not.toHaveBeenCalled();
  });

  it("reacciona a un 403 con onboarding llevando al paso pendiente", async () => {
    fetch.mockResolvedValue(
      respuestaJson(403, {
        detalle: "Completá tu perfil.",
        onboarding: "perfil",
      }),
    );

    const error = await pedir("GET", "encuentros").catch((e) => e);

    expect(error.onboarding).toBe("perfil");
    expect(alFaltarOnboarding).toHaveBeenCalledWith("perfil");
  });

  it("no reacciona a un 403 sin onboarding", async () => {
    fetch.mockResolvedValue(respuestaJson(403, { detalle: "Sin permiso." }));

    await pedir("GET", "encuentros/1").catch(() => {});

    expect(alFaltarOnboarding).not.toHaveBeenCalled();
    expect(alNoAutenticado).not.toHaveBeenCalled();
  });

  it("no reacciona si el pedido lo desactiva", async () => {
    fetch.mockResolvedValue(
      respuestaJson(401, { detalle: "Iniciá sesión para continuar." }),
    );

    await pedir("GET", "auth/yo", undefined, { reaccionar: false }).catch(
      () => {},
    );

    expect(alNoAutenticado).not.toHaveBeenCalled();
  });
});
