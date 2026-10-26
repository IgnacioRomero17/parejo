import { useId } from "react";
import {
  ESTADOS_INVITACION,
  etiquetaTipoEncuentro,
  rolOrganizador,
} from "../utilidades/encuentros.js";
import {
  formatearEnvio,
  formatearFechaCompacta,
} from "../utilidades/formato.js";
import Avatar from "./Avatar.jsx";
import Boton from "./Boton.jsx";
import Casilleros from "./Casilleros.jsx";
import Etiqueta from "./Etiqueta.jsx";
import estilos from "./TarjetaInvitacion.module.css";

// Invitación pendiente de la pantalla 13, con los datos del encuentro y las dos respuestas.
function TarjetaInvitacionPendiente({
  invitacion,
  respondiendo,
  onAceptar,
  onRechazar,
}) {
  const idTitulo = useId();
  const { organizador, encuentro } = invitacion;
  const pendiente = ESTADOS_INVITACION.PENDIENTE;
  const datos = [
    { rotulo: "Fecha", valor: formatearFechaCompacta(encuentro.fecha) },
    { rotulo: "Hora", valor: encuentro.hora_inicio },
    { rotulo: "Duración", valor: `${encuentro.duracion_minutos} min` },
    { rotulo: "Tipo", valor: etiquetaTipoEncuentro(encuentro.tipo_encuentro) },
    {
      rotulo: "Lugar",
      valor: `${encuentro.localidad.nombre} · ${encuentro.ubicacion}`,
    },
  ];

  return (
    <li className={`${estilos.tarjeta} ${estilos.pendiente}`}>
      <article aria-labelledby={idTitulo} className={estilos.contenido}>
        <div className={estilos.cabecera}>
          <Avatar nombre={organizador.nombre} apellido={organizador.apellido} />
          <div className={estilos.identidad}>
            <h3 id={idTitulo} className={estilos.titulo}>
              {organizador.nombre} {organizador.apellido} te invitó a un
              encuentro
            </h3>
            <p className={estilos.detalle}>
              {rolOrganizador(organizador.genero)} · enviada{" "}
              {formatearEnvio(invitacion.fecha_envio)}
            </p>
          </div>
          <Etiqueta color={pendiente.color}>{pendiente.etiqueta}</Etiqueta>
        </div>
        <dl className={estilos.datos}>
          {datos.map(({ rotulo, valor }) => (
            <div key={rotulo}>
              <dt className={estilos.rotulo}>{rotulo}</dt>
              <dd className={estilos.valor}>{valor}</dd>
            </div>
          ))}
          <div>
            <dt className={estilos.rotulo}>Lugares</dt>
            <dd className={estilos.valor}>
              <Casilleros confirmados={encuentro.confirmados} />
            </dd>
          </div>
        </dl>
        <div className={estilos.acciones}>
          <Boton
            variante="secundario"
            deshabilitado={respondiendo}
            onClick={onRechazar}
          >
            Rechazar
          </Boton>
          <Boton deshabilitado={respondiendo} onClick={onAceptar}>
            Aceptar invitación
          </Boton>
        </div>
      </article>
    </li>
  );
}

export default TarjetaInvitacionPendiente;
