import { Link } from "react-router-dom";
import {
  ESTADOS_ENCUENTRO,
  ESTADOS_INVITACION,
  LUGARES_POR_ENCUENTRO,
  textoEsperandoParejas,
} from "../utilidades/encuentros.js";
import { formatearFechaCompacta } from "../utilidades/formato.js";
import Avatar from "./Avatar.jsx";
import Etiqueta from "./Etiqueta.jsx";
import estilos from "./TarjetaInvitacion.module.css";

// Qué se dice del encuentro de una invitación aceptada, según su estado actual; con propuesta,
// el enlace para verla.
function EstadoEncuentro({ encuentro, organizador }) {
  if (encuentro.estado === "PROPUESTA_GENERADA") {
    return (
      <Link
        to={`/encuentros/${encuentro.id}/propuesta`}
        className={estilos.enlace}
      >
        Ver propuesta
      </Link>
    );
  }
  if (encuentro.estado === "COMPLETO") {
    return <p>{textoEsperandoParejas(organizador.genero)}</p>;
  }
  return (
    <p>
      {encuentro.confirmados} de {LUGARES_POR_ENCUENTRO} confirmados.
    </p>
  );
}

// Invitación aceptada o rechazada de la pantalla 13.
function TarjetaInvitacionRespondida({ invitacion }) {
  const { organizador, encuentro } = invitacion;
  const estado = ESTADOS_INVITACION[invitacion.estado];
  const estadoEncuentro = ESTADOS_ENCUENTRO[encuentro.estado];
  const resumen = [
    formatearFechaCompacta(encuentro.fecha),
    encuentro.hora_inicio,
    `${encuentro.duracion_minutos} min`,
    encuentro.localidad.nombre,
    encuentro.ubicacion,
  ].join(" · ");

  return (
    <li className={estilos.tarjeta}>
      <div className={estilos.cabecera}>
        <Avatar nombre={organizador.nombre} apellido={organizador.apellido} />
        <div className={estilos.identidad}>
          <h3 className={estilos.titulo}>
            {organizador.nombre} {organizador.apellido}
          </h3>
          <p className={estilos.detalle}>{resumen}</p>
        </div>
        <Etiqueta color={estado.color}>{estado.etiqueta}</Etiqueta>
      </div>
      <div className={estilos.estado}>
        {invitacion.estado === "ACEPTADA" ? (
          <>
            <Etiqueta color={estadoEncuentro.color}>
              {estadoEncuentro.etiqueta}
            </Etiqueta>
            <EstadoEncuentro encuentro={encuentro} organizador={organizador} />
          </>
        ) : (
          <p>Rechazaste esta invitación.</p>
        )}
      </div>
    </li>
  );
}

export default TarjetaInvitacionRespondida;
