import { describe, expect, it } from "vitest";
import { formatearFechaCompacta, formatearNivel } from "./formato.js";

describe("formatearNivel", () => {
  it("usa coma decimal y siempre un decimal", () => {
    expect(formatearNivel(4.5)).toBe("4,5");
    expect(formatearNivel(4)).toBe("4,0");
    expect(formatearNivel(1)).toBe("1,0");
    expect(formatearNivel(7)).toBe("7,0");
  });
});

describe("formatearFechaCompacta", () => {
  it("muestra día abreviado con mayúscula, día, mes abreviado y año", () => {
    expect(formatearFechaCompacta("2026-10-03")).toBe("Sáb 3 oct 2026");
    expect(formatearFechaCompacta("2026-10-05")).toBe("Lun 5 oct 2026");
  });

  it("no corre el día por la zona horaria", () => {
    expect(formatearFechaCompacta("2026-01-01")).toBe("Jue 1 ene 2026");
  });
});
