import { describe, expect, it } from "vitest";
import { formatearNivel } from "./formato.js";

describe("formatearNivel", () => {
  it("usa coma decimal y siempre un decimal", () => {
    expect(formatearNivel(4.5)).toBe("4,5");
    expect(formatearNivel(4)).toBe("4,0");
    expect(formatearNivel(1)).toBe("1,0");
    expect(formatearNivel(7)).toBe("7,0");
  });
});
