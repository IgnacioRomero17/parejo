import {
  ESTADOS_INVITACION,
  textoPendientes,
} from "../utilidades/encuentros.js";
import { formatearFechaCompacta } from "../utilidades/formato.js";
import Avatar from "./Avatar.jsx";
import Boton from "./Boton.jsx";
import Etiqueta from "./Etiqueta.jsx";
import estilos from "./TarjetaInvitaciones.module.css";

// Tarjeta "Invitaciones" del panel principal: cuántas pendientes hay y la más reciente.
// `pendientes` llega ordenada de la más reciente a la más antigua.
function TarjetaInvitaciones({ pendientes }) {
  const [reciente] = pendientes;

  return (
    <div className={estilos.tarjeta}>
      {reciente ? (
        <>
          <Etiqueta color={ESTADOS_INVITACION.PENDIENTE.color}>
            {textoPendientes(pendientes.length)}
          </Etiqueta>
          <div className={estilos.invitacion}>
            <Avatar
              nombre={reciente.organizador.nombre}
              apellido={reciente.organizador.apellido}
            />
            <div>
              <p className={estilos.nombre}>
                {reciente.organizador.nombre} {reciente.organizador.apellido} te
                invitó
              </p>
              <p className={estilos.detalle}>
                {[
                  formatearFechaCompacta(reciente.encuentro.fecha),
                  reciente.encuentro.hora_inicio,
                  `${reciente.encuentro.duracion_minutos} min`,
                  reciente.encuentro.localidad.nombre,
                ].join(" · ")}
              </p>
            </div>
          </div>
        </>
      ) : (
        <p className={estilos.detalle}>No tenés invitaciones pendientes.</p>
      )}
      <Boton variante="secundario" a="/invitaciones" anchoCompleto>
        Ver invitaciones
      </Boton>
    </div>
  );
}

export default TarjetaInvitaciones;
