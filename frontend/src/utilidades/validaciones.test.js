import { describe, expect, it } from "vitest";
import {
  MENSAJE_CAMPO_VACIO,
  validarCamposRequeridos,
} from "./validaciones.js";

describe("validarCamposRequeridos", () => {
  it("no devuelve errores si todos los campos tienen valor", () => {
    expect(
      validarCamposRequeridos({ nombre: "Tomás", email: "tomas@example.com" }),
    ).toEqual({});
  });

  it("marca los campos vacíos, nulos o con solo espacios", () => {
    const errores = validarCamposRequeridos({
      nombre: "",
      apellido: "   ",
      email: null,
      contrasena: "clave1234",
    });

    expect(errores).toEqual({
      nombre: [MENSAJE_CAMPO_VACIO],
      apellido: [MENSAJE_CAMPO_VACIO],
      email: [MENSAJE_CAMPO_VACIO],
    });
  });
});
