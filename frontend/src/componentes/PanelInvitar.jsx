import { useId } from "react";
import { listarNombres } from "../utilidades/encuentros.js";
import Boton from "./Boton.jsx";
import ErrorFormulario from "./ErrorFormulario.jsx";
import ListaDisponibles from "./ListaDisponibles.jsx";
import ListaInvitados from "./ListaInvitados.jsx";
import estilos from "./PanelInvitar.module.css";

// Panel izquierdo de la pantalla 12: los ya invitados, los disponibles con su casilla y el
// pie para enviar. La selección y el envío los maneja la página.
function PanelInvitar({
  invitaciones,
  candidatos,
  lugaresLibres,
  seleccionados,
  enviando,
  error,
  onCambiar,
  onEnviar,
}) {
  const idTitulo = useId();
  const elegidos = candidatos.filter((jugador) =>
    seleccionados.includes(jugador.id),
  );
  const conPie = lugaresLibres > 0 && candidatos.length > 0;

  return (
    <section className={estilos.panel} aria-labelledby={idTitulo}>
      <div className={estilos.encabezado}>
        <h2 id={idTitulo} className={estilos.titulo}>
          Jugadores recomendados
        </h2>
        <p className={estilos.dato}>Ordenados por compatibilidad</p>
      </div>
      {invitaciones.length > 0 && (
        <ListaInvitados invitaciones={invitaciones} />
      )}
      <ListaDisponibles
        candidatos={candidatos}
        lugaresLibres={lugaresLibres}
        seleccionados={seleccionados}
        onCambiar={onCambiar}
      />
      {error && (
        <div className={estilos.error}>
          <ErrorFormulario>{error}</ErrorFormulario>
        </div>
      )}
      {conPie && (
        <div className={estilos.pie}>
          <p>
            {elegidos.length > 0 && (
              <>
                Vas a invitar a <strong>{listarNombres(elegidos)}</strong>
              </>
            )}
          </p>
          <Boton
            deshabilitado={elegidos.length === 0 || enviando}
            onClick={onEnviar}
          >
            Enviar invitación ({elegidos.length})
          </Boton>
        </div>
      )}
    </section>
  );
}

export default PanelInvitar;
