import { useId } from "react";
import {
  ESTADOS_ENCUENTRO,
  ESTADOS_INVITACION,
  LUGARES_POR_ENCUENTRO,
  textoLugaresRestantes,
} from "../utilidades/encuentros.js";
import { segunGenero } from "../utilidades/perfil.js";
import Boton from "./Boton.jsx";
import Etiqueta from "./Etiqueta.jsx";
import FilaJugador from "./FilaJugador.jsx";
import estilos from "./PanelLugares.module.css";

// Panel "Lugares del encuentro" de la pantalla 12: confirmados, invitaciones pendientes y los
// seleccionados que todavía no se enviaron. El organizador es `idUsuario`; su rol se nombra
// según el `genero` de su perfil.
function PanelLugares({ encuentro, idUsuario, genero, elegidos }) {
  const idTitulo = useId();
  const estado = ESTADOS_ENCUENTRO[encuentro.estado];
  const pendientes = encuentro.invitaciones.filter(
    (invitacion) => invitacion.estado === "PENDIENTE",
  );
  const restantes = LUGARES_POR_ENCUENTRO - encuentro.confirmados;
  const confirmado = ESTADOS_INVITACION.ACEPTADA.color;

  return (
    <aside className={estilos.panel} aria-labelledby={idTitulo}>
      <div className={estilos.encabezado}>
        <h2 id={idTitulo} className={estilos.rotulo}>
          Lugares del encuentro
        </h2>
        <Etiqueta color={estado.color}>{estado.etiqueta}</Etiqueta>
      </div>
      <p className={estilos.cantidad}>
        <span className={estilos.numero}>
          {encuentro.confirmados} de {LUGARES_POR_ENCUENTRO}
        </span>
        confirmados · {textoLugaresRestantes(restantes)}
      </p>
      <ul className={estilos.lugares}>
        {encuentro.participantes.map((participante) => {
          const esVos = participante.id === idUsuario;
          return (
            <li key={participante.id} className={estilos.lugar}>
              <FilaJugador
                jugador={participante}
                prefijo={esVos ? "Vos · " : ""}
                detalle={
                  esVos
                    ? segunGenero(
                        genero,
                        "Organizadora",
                        "Organizador",
                        "Organizás",
                      )
                    : "Aceptó la invitación"
                }
              >
                <Etiqueta color={confirmado}>Confirmado</Etiqueta>
              </FilaJugador>
            </li>
          );
        })}
        {pendientes.map(({ id, jugador }) => (
          <li key={id} className={`${estilos.lugar} ${estilos.pendiente}`}>
            <FilaJugador jugador={jugador} detalle="Invitación enviada">
              <Etiqueta color={ESTADOS_INVITACION.PENDIENTE.color}>
                {ESTADOS_INVITACION.PENDIENTE.etiqueta}
              </Etiqueta>
            </FilaJugador>
          </li>
        ))}
        {elegidos.map((jugador) => (
          <li
            key={jugador.id}
            className={`${estilos.lugar} ${estilos.elegido}`}
          >
            <FilaJugador
              jugador={jugador}
              detalle="Seleccionado · sin enviar"
            />
          </li>
        ))}
      </ul>
      <div className={estilos.formar}>
        <p className={estilos.texto}>
          Con 4 participantes confirmados se habilita el inicio de la formación
          automática de parejas.
        </p>
        <Boton deshabilitado anchoCompleto>
          Formar parejas equilibradas
        </Boton>
      </div>
    </aside>
  );
}

export default PanelLugares;
