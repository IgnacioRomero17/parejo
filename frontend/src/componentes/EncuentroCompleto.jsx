import { useId } from "react";
import {
  ESTADOS_ENCUENTRO,
  ESTADOS_INVITACION,
  LUGARES_POR_ENCUENTRO,
  etiquetaTipoEncuentro,
} from "../utilidades/encuentros.js";
import {
  formatearFechaCompacta,
  formatearNivel,
} from "../utilidades/formato.js";
import Avatar from "./Avatar.jsx";
import Boton from "./Boton.jsx";
import estilos from "./EncuentroCompleto.module.css";
import Etiqueta from "./Etiqueta.jsx";

// Pantalla 14: los 4 confirmados, las condiciones y las invitaciones enviadas. El botón lleva
// a la pantalla 15, que es la que dispara la formación de parejas.
function EncuentroCompleto({ encuentro, idUsuario }) {
  const idInvitaciones = useId();
  const idFormar = useId();
  const estado = ESTADOS_ENCUENTRO[encuentro.estado];
  const datos = [
    formatearFechaCompacta(encuentro.fecha),
    encuentro.hora_inicio,
    `${encuentro.duracion_minutos} min`,
    `${encuentro.localidad.nombre} · ${encuentro.ubicacion}`,
    etiquetaTipoEncuentro(encuentro.tipo_encuentro),
  ];

  return (
    <>
      <div className={estilos.titulo}>
        <p className={estilos.rotulo}>Seguimiento del encuentro</p>
        <h1>¡Encuentro completo!</h1>
      </div>
      <div className={estilos.columnas}>
        <div className={estilos.principal}>
          <div className={estilos.bloque}>
            <div className={estilos.cabecera}>
              <Etiqueta color={estado.color}>{estado.etiqueta}</Etiqueta>
              <p className={estilos.confirmados}>
                {encuentro.confirmados} de {LUGARES_POR_ENCUENTRO} jugadores
                confirmados
              </p>
              <span className={estilos.cuadros} aria-hidden="true">
                {encuentro.participantes.map((participante) => (
                  <span key={participante.id} className={estilos.cuadro} />
                ))}
              </span>
            </div>
            <ul className={estilos.jugadores} aria-label="Participantes">
              {encuentro.participantes.map((participante) => (
                <li key={participante.id} className={estilos.jugador}>
                  <Avatar
                    nombre={participante.nombre}
                    apellido={participante.apellido}
                  />
                  <p className={estilos.nombre}>
                    {participante.nombre} {participante.apellido}
                  </p>
                  <p className={estilos.nivel}>
                    {participante.id === idUsuario && "Vos · "}Nivel{" "}
                    {formatearNivel(participante.nivel)}
                  </p>
                </li>
              ))}
            </ul>
            <ul className={estilos.datos}>
              {datos.map((dato) => (
                <li key={dato}>{dato}</li>
              ))}
            </ul>
          </div>
          <section className={estilos.formar} aria-labelledby={idFormar}>
            <div>
              <h2 id={idFormar} className={estilos.subtitulo}>
                Formar parejas equilibradas
              </h2>
              <p className={estilos.texto}>
                Al presionar el botón, el sistema evalúa las 3 combinaciones
                posibles de 2 parejas con los 4 jugadores y selecciona
                automáticamente la de mejor resultado de equilibrio. Vos no
                armás las parejas.
              </p>
            </div>
            <Boton a={`/encuentros/${encuentro.id}/formando`}>
              Formar parejas equilibradas
            </Boton>
          </section>
        </div>
        <aside
          className={estilos.invitaciones}
          aria-labelledby={idInvitaciones}
        >
          <h2 id={idInvitaciones} className={estilos.rotulo}>
            Invitaciones enviadas
          </h2>
          <ul>
            {encuentro.invitaciones.map(
              ({ id, jugador, estado: estadoInv }) => {
                const etiqueta = ESTADOS_INVITACION[estadoInv];
                return (
                  <li key={id} className={estilos.invitacion}>
                    {jugador.nombre} {jugador.apellido}
                    <Etiqueta color={etiqueta.color}>
                      {etiqueta.etiqueta}
                    </Etiqueta>
                  </li>
                );
              },
            )}
          </ul>
          <p className={estilos.texto}>
            Los demás participantes ven el encuentro como “Completo” hasta que
            inicies la formación de parejas.
          </p>
        </aside>
      </div>
    </>
  );
}

export default EncuentroCompleto;
