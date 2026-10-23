import { useRef } from "react";
import { formatearNivel } from "../utilidades/formato.js";
import {
  NIVEL_MAXIMO,
  NIVEL_MINIMO,
  PASO_NIVEL,
  POSICIONES_NIVEL,
  indiceNivel,
  nivelesDescriptos,
} from "../utilidades/niveles.js";
import MensajeCampo from "./MensajeCampo.jsx";
import estilos from "./SelectorNivel.module.css";

// Teclas con las que el range nativo cambia de valor.
const TECLAS_DE_VALOR = [
  "ArrowLeft",
  "ArrowRight",
  "ArrowUp",
  "ArrowDown",
  "Home",
  "End",
  "PageUp",
  "PageDown",
];
const ULTIMO_INDICE = POSICIONES_NIVEL.length - 1;

function clasePunto(punto, valor) {
  const clases = [Number.isInteger(punto) ? estilos.entero : estilos.medio];
  if (valor !== null && punto < valor) clases.push(estilos.alcanzado);
  if (punto === valor) clases.push(estilos.elegido);
  return clases.join(" ");
}

// Selector de nivel de la pantalla 07a. `valor` es un número de 1 a 7 en pasos de 0,5,
// o null mientras el jugador no eligió (un range nativo siempre tiene valor, por eso el
// estado "sin elegir" se guarda aparte y el control se dibuja sin marca).
//
// La pista es un grid de 13 columnas, una por posición. Todo se ubica con el índice de la
// posición (indiceNivel): la columna de cada punto y de la etiqueta flotante, el relleno
// azul y el valor que elige el mouse. El range nativo queda debajo, sin recibir el mouse,
// para el teclado y los lectores de pantalla.
function SelectorNivel({ id, valor, onCambiar, error }) {
  const control = useRef(null);
  const sinElegir = valor === null;
  const indice = sinElegir ? 0 : indiceNivel(valor);

  function elegir(punto) {
    if (punto !== valor) onCambiar(punto);
  }

  function manejarPresion(evento, punto) {
    // Con el dedo, el navegador captura el puntero en la zona tocada; se libera para que
    // al deslizar se entere cada zona por la que pasa.
    if (evento.currentTarget.hasPointerCapture?.(evento.pointerId)) {
      evento.currentTarget.releasePointerCapture(evento.pointerId);
    }
    control.current.focus();
    elegir(punto);
  }

  function manejarArrastre(evento, punto) {
    if (evento.buttons % 2 === 1) elegir(punto);
  }

  function fijarValorActual(evento) {
    // Una tecla que no mueve el range (← en el 1) no dispara onChange: igual elige.
    if (sinElegir && TECLAS_DE_VALOR.includes(evento.key)) {
      onCambiar(Number(evento.currentTarget.value));
    }
  }

  return (
    <div className={estilos.selector}>
      <label htmlFor={id} className={estilos.etiqueta}>
        Nivel estimado
      </label>
      <div
        className={sinElegir ? estilos.pistaSinElegir : estilos.pista}
        style={{
          "--posiciones": POSICIONES_NIVEL.length,
          "--avance": indice / ULTIMO_INDICE,
        }}
        // Evita que el mouse mueva el foco fuera del range o seleccione texto.
        onMouseDown={(evento) => evento.preventDefault()}
      >
        <span
          className={estilos.flotante}
          style={{ gridColumn: indice + 1 }}
          aria-hidden="true"
        >
          {sinElegir ? "" : formatearNivel(valor)}
        </span>
        <span className={estilos.linea} aria-hidden="true" />
        <input
          ref={control}
          id={id}
          name={id}
          type="range"
          min={NIVEL_MINIMO}
          max={NIVEL_MAXIMO}
          step={PASO_NIVEL}
          value={valor ?? NIVEL_MINIMO}
          onChange={(evento) => onCambiar(Number(evento.target.value))}
          onKeyUp={fijarValorActual}
          aria-valuetext={sinElegir ? "Sin elegir" : formatearNivel(valor)}
          aria-invalid={error ? "true" : undefined}
          aria-describedby={error ? `${id}-error` : undefined}
          className={estilos.control}
        />
        {POSICIONES_NIVEL.map((punto, indicePunto) => (
          <span
            key={punto}
            className={estilos.zona}
            style={{ gridColumn: indicePunto + 1 }}
            data-nivel={punto}
            aria-hidden="true"
            onPointerDown={(evento) => manejarPresion(evento, punto)}
            onPointerEnter={(evento) => manejarArrastre(evento, punto)}
          >
            <span className={clasePunto(punto, valor)}>
              {Number.isInteger(punto) ? punto : null}
            </span>
          </span>
        ))}
      </div>
      <div className={estilos.extremos} aria-hidden="true">
        <span>Iniciación</span>
        <span>Élite</span>
      </div>
      <MensajeCampo id={id} error={error} />
      <div className={estilos.descripciones} aria-live="polite">
        {sinElegir ? (
          <p className={estilos.vacio}>
            Deslizá para ver qué describe cada nivel.
          </p>
        ) : (
          nivelesDescriptos(valor).map((nivel) => (
            <div key={nivel.numero} className={estilos.descripcion}>
              <h3 className={estilos.nombreNivel}>
                <span className={estilos.numeroNivel}>{nivel.numero}</span>
                {nivel.nombre}
              </h3>
              <p>{nivel.descripcion}</p>
            </div>
          ))
        )}
      </div>
      <p className={estilos.ayuda}>
        Elegí el nivel que mejor describa cómo jugás hoy, no el que aspirás a
        tener. Si dudás entre dos, elegí el menor.
      </p>
    </div>
  );
}

export default SelectorNivel;
