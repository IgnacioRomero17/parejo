import { fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import { formatearNivel } from "../utilidades/formato.js";
import { POSICIONES_NIVEL } from "../utilidades/niveles.js";
import SelectorNivel from "./SelectorNivel.jsx";

const TEXTO_VACIO = "Deslizá para ver qué describe cada nivel.";
const TEXTO_GUIA =
  "Elegí el nivel que mejor describa cómo jugás hoy, no el que aspirás a tener. Si dudás entre dos, elegí el menor.";

// El selector es controlado: este envoltorio guarda el valor como lo haría la página.
function SelectorConEstado({ inicial = null, onCambiar = () => {} }) {
  const [valor, setValor] = useState(inicial);
  return (
    <SelectorNivel
      id="nivel"
      valor={valor}
      onCambiar={(nuevo) => {
        setValor(nuevo);
        onCambiar(nuevo);
      }}
    />
  );
}

function control() {
  return screen.getByRole("slider", { name: "Nivel estimado" });
}

function descripciones() {
  return screen.queryAllByRole("heading", { level: 3 });
}

// Las zonas de clic son decorativas para el lector de pantalla (el control accesible es
// el range), así que se ubican por el nivel que eligen.
function zona(punto) {
  return document.querySelector(`[data-nivel="${punto}"]`);
}

function pista() {
  return zona(1).parentElement;
}

function estiloDe(elemento, propiedad) {
  return elemento.style.getPropertyValue(propiedad);
}

describe("SelectorNivel (HU-004)", () => {
  it("P6: arranca vacío, sin etiqueta flotante y con el texto de ayuda", () => {
    render(<SelectorConEstado />);

    expect(control().getAttribute("aria-valuetext")).toBe("Sin elegir");
    expect(screen.getByText(TEXTO_VACIO)).toBeTruthy();
    expect(screen.queryByText("Intermedio")).toBeNull();
    expect(screen.queryByText(/^\d,\d$/)).toBeNull();
    expect(screen.getByText(TEXTO_GUIA)).toBeTruthy();
  });

  it("P6: es un range de 1 a 7 en pasos de 0,5", () => {
    render(<SelectorConEstado />);

    expect(control().getAttribute("type")).toBe("range");
    expect(control().getAttribute("min")).toBe("1");
    expect(control().getAttribute("max")).toBe("7");
    expect(control().getAttribute("step")).toBe("0.5");
  });

  it("P6: con un valor entero muestra una sola descripción", () => {
    render(<SelectorConEstado />);

    fireEvent.change(control(), { target: { value: "4" } });

    expect(screen.getByText("4,0")).toBeTruthy();
    expect(control().getAttribute("aria-valuetext")).toBe("4,0");
    expect(descripciones().map((titulo) => titulo.textContent)).toEqual([
      "4Intermedio",
    ]);
    expect(
      screen.getByText(
        "Controlás los golpes básicos, jugás bien las paredes y entendés el juego en pareja.",
      ),
    ).toBeTruthy();
    expect(screen.queryByText(TEXTO_VACIO)).toBeNull();
  });

  it("P6: con ,5 muestra las descripciones del nivel inferior y del superior", () => {
    render(<SelectorConEstado />);

    fireEvent.change(control(), { target: { value: "4.5" } });

    expect(screen.getByText("4,5")).toBeTruthy();
    expect(descripciones().map((titulo) => titulo.textContent)).toEqual([
      "4Intermedio",
      "5Intermedio alto",
    ]);
  });

  it("P6: las descripciones se actualizan en vivo al moverlo", () => {
    render(<SelectorConEstado />);

    fireEvent.change(control(), { target: { value: "1.5" } });
    expect(descripciones().map((titulo) => titulo.textContent)).toEqual([
      "1Iniciación",
      "2Principiante",
    ]);

    fireEvent.change(control(), { target: { value: "7" } });
    expect(descripciones().map((titulo) => titulo.textContent)).toEqual([
      "7Élite",
    ]);
  });

  it("P6: la primera tecla fija el valor aunque no cambie la posición", () => {
    const onCambiar = vi.fn();
    render(<SelectorConEstado onCambiar={onCambiar} />);

    fireEvent.keyUp(control(), { key: "ArrowLeft" });

    expect(onCambiar).toHaveBeenCalledWith(1);
    expect(control().getAttribute("aria-valuetext")).toBe("1,0");
    expect(descripciones().map((titulo) => titulo.textContent)).toEqual([
      "1Iniciación",
    ]);
  });

  it("P6: Tab al entrar al control no elige un valor", () => {
    const onCambiar = vi.fn();
    render(<SelectorConEstado onCambiar={onCambiar} />);

    fireEvent.keyUp(control(), { key: "Tab" });

    expect(onCambiar).not.toHaveBeenCalled();
    expect(control().getAttribute("aria-valuetext")).toBe("Sin elegir");
  });

  it("con un valor ya elegido, soltar una tecla no lo vuelve a fijar", () => {
    const onCambiar = vi.fn();
    render(<SelectorConEstado inicial={3} onCambiar={onCambiar} />);

    fireEvent.keyUp(control(), { key: "ArrowRight" });

    expect(onCambiar).not.toHaveBeenCalled();
    expect(control().getAttribute("aria-valuetext")).toBe("3,0");
  });

  it.each(POSICIONES_NIVEL)(
    "P6: el primer clic en el punto %s elige exactamente ese valor",
    (punto) => {
      const onCambiar = vi.fn();
      render(<SelectorConEstado onCambiar={onCambiar} />);

      fireEvent.pointerDown(zona(punto), { buttons: 1 });

      expect(onCambiar).toHaveBeenCalledTimes(1);
      expect(onCambiar).toHaveBeenCalledWith(punto);
      expect(control().getAttribute("aria-valuetext")).toBe(
        formatearNivel(punto),
      );
      expect(screen.getByText(formatearNivel(punto))).toBeTruthy();
    },
  );

  it("P6: con un valor elegido, el clic en cualquier otro punto elige ese punto", () => {
    render(<SelectorConEstado inicial={4} />);

    for (const punto of [...POSICIONES_NIVEL].reverse()) {
      fireEvent.pointerDown(zona(punto), { buttons: 1 });
      expect(control().getAttribute("aria-valuetext")).toBe(
        formatearNivel(punto),
      );
    }
  });

  it.each(POSICIONES_NIVEL)(
    "en %s, el punto, la etiqueta flotante y el relleno usan la misma posición",
    (punto) => {
      render(<SelectorConEstado inicial={punto} />);
      const indice = POSICIONES_NIVEL.indexOf(punto);
      const flotante = screen.getByText(formatearNivel(punto));

      expect(estiloDe(zona(punto), "grid-column")).toBe(String(indice + 1));
      expect(estiloDe(flotante, "grid-column")).toBe(String(indice + 1));
      expect(Number(estiloDe(pista(), "--avance"))).toBeCloseTo(
        indice / (POSICIONES_NIVEL.length - 1),
      );
      expect(estiloDe(pista(), "--posiciones")).toBe(
        String(POSICIONES_NIVEL.length),
      );
    },
  );

  it("sin elegir, el relleno no avanza", () => {
    render(<SelectorConEstado />);

    expect(Number(estiloDe(pista(), "--avance"))).toBe(0);
  });

  it("el clic lleva el foco al range, para seguir con el teclado", () => {
    render(<SelectorConEstado />);

    fireEvent.pointerDown(zona(5), { buttons: 1 });

    expect(document.activeElement).toBe(control());
  });

  it("al deslizar con el botón apretado elige cada punto por el que pasa", () => {
    const onCambiar = vi.fn();
    render(<SelectorConEstado onCambiar={onCambiar} />);

    fireEvent.pointerDown(zona(2), { buttons: 1 });
    fireEvent.pointerEnter(zona(2.5), { buttons: 1 });
    fireEvent.pointerEnter(zona(3), { buttons: 1 });
    // Sin botón apretado, pasar por encima no cambia nada.
    fireEvent.pointerEnter(zona(6), { buttons: 0 });

    expect(onCambiar.mock.calls).toEqual([[2], [2.5], [3]]);
    expect(control().getAttribute("aria-valuetext")).toBe("3,0");
  });

  it("el clic en el punto ya elegido no avisa un cambio", () => {
    const onCambiar = vi.fn();
    render(<SelectorConEstado inicial={4.5} onCambiar={onCambiar} />);

    fireEvent.pointerDown(zona(4.5), { buttons: 1 });

    expect(onCambiar).not.toHaveBeenCalled();
  });

  it("muestra el error enlazado al control", () => {
    render(
      <SelectorNivel
        id="nivel"
        valor={null}
        onCambiar={() => {}}
        error="Completá este campo para poder guardar."
      />,
    );

    expect(control().getAttribute("aria-invalid")).toBe("true");
    const idError = control().getAttribute("aria-describedby");
    expect(document.getElementById(idError).textContent).toBe(
      "Completá este campo para poder guardar.",
    );
  });
});
