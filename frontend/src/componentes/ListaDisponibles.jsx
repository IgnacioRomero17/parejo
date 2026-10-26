import { useId } from "react";
import {
  textoLimiteSeleccion,
  textoLugaresLibres,
  textoSeleccionados,
} from "../utilidades/encuentros.js";
import { formatearFranja, formatearNivel } from "../utilidades/formato.js";
import Etiqueta from "./Etiqueta.jsx";
import FilaJugador from "./FilaJugador.jsx";
import estilos from "./PanelInvitar.module.css";

function Candidatos({ candidatos, lugaresLibres, seleccionados, onCambiar }) {
  const enElLimite = seleccionados.length >= lugaresLibres;

  return (
    <>
      <ul aria-label="Disponibles para invitar">
        {candidatos.map((jugador, posicion) => {
          const seleccionado = seleccionados.includes(jugador.id);
          return (
            <li key={jugador.id}>
              <label
                className={`${estilos.fila} ${estilos.candidato} ${seleccionado ? estilos.seleccionado : ""}`}
              >
                <input
                  type="checkbox"
                  className={estilos.casilla}
                  checked={seleccionado}
                  disabled={!seleccionado && enElLimite}
                  aria-label={`${jugador.nombre} ${jugador.apellido}`}
                  onChange={() => onCambiar(jugador.id)}
                />
                <span className={estilos.posicion}>{posicion + 1}</span>
                <FilaJugador
                  jugador={jugador}
                  detalle={`${jugador.localidad.nombre} · ${formatearFranja(jugador.franja)}`}
                >
                  <Etiqueta>Nivel {formatearNivel(jugador.nivel)}</Etiqueta>
                  {seleccionado && (
                    <span className={estilos.marca}>Seleccionado</span>
                  )}
                </FilaJugador>
              </label>
            </li>
          );
        })}
      </ul>
      {enElLimite && (
        <p className={estilos.nota}>{textoLimiteSeleccion(lugaresLibres)}</p>
      )}
    </>
  );
}

// Sección "Disponibles para invitar" de la pantalla 12: los recomendados que todavía no
// fueron invitados, con casilla. Se pueden marcar hasta tantos como lugares libres.
function ListaDisponibles({
  candidatos,
  lugaresLibres,
  seleccionados,
  onCambiar,
}) {
  const idTitulo = useId();

  function contenido() {
    if (lugaresLibres === 0) {
      return (
        <p className={estilos.nota}>
          Esperá la respuesta de las invitaciones pendientes.
        </p>
      );
    }
    if (candidatos.length === 0) {
      return (
        <p className={estilos.nota}>
          No se encontraron suficientes participantes compatibles.
        </p>
      );
    }
    return (
      <Candidatos
        candidatos={candidatos}
        lugaresLibres={lugaresLibres}
        seleccionados={seleccionados}
        onCambiar={onCambiar}
      />
    );
  }

  return (
    <section aria-labelledby={idTitulo}>
      <div className={estilos.seccion}>
        <h3 id={idTitulo} className={estilos.rotulo}>
          Disponibles para invitar
        </h3>
        <Etiqueta color="azul">
          {textoLugaresLibres(lugaresLibres)} ·{" "}
          {textoSeleccionados(seleccionados.length)}
        </Etiqueta>
      </div>
      {contenido()}
    </section>
  );
}

export default ListaDisponibles;
