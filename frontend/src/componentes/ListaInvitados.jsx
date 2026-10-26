import { useId } from "react";
import {
  ESTADOS_INVITACION,
  textoInvitacionesEnviadas,
} from "../utilidades/encuentros.js";
import { formatearNivel } from "../utilidades/formato.js";
import Etiqueta from "./Etiqueta.jsx";
import FilaJugador from "./FilaJugador.jsx";
import estilos from "./PanelInvitar.module.css";

// Sección "Ya invitados" de la pantalla 12, en orden de envío. No se pueden volver a invitar.
function ListaInvitados({ invitaciones }) {
  const idTitulo = useId();

  return (
    <section aria-labelledby={idTitulo}>
      <div className={estilos.seccion}>
        <h3 id={idTitulo} className={estilos.rotulo}>
          Ya invitados
        </h3>
        <p className={estilos.dato}>
          {textoInvitacionesEnviadas(invitaciones.length)}
        </p>
      </div>
      <ul aria-labelledby={idTitulo}>
        {invitaciones.map(({ id, jugador, estado }) => {
          const etiqueta = ESTADOS_INVITACION[estado];
          return (
            <li key={id} className={estilos.fila}>
              <FilaJugador jugador={jugador} detalle={jugador.localidad.nombre}>
                <Etiqueta>Nivel {formatearNivel(jugador.nivel)}</Etiqueta>
                <Etiqueta color={etiqueta.color}>{etiqueta.etiqueta}</Etiqueta>
              </FilaJugador>
            </li>
          );
        })}
      </ul>
    </section>
  );
}

export default ListaInvitados;
