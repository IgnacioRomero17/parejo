import { Clock } from "lucide-react";
import { formatearFranja, formatearNivel } from "../utilidades/formato.js";
import Avatar from "./Avatar.jsx";
import Etiqueta from "./Etiqueta.jsx";
import estilos from "./TarjetaRecomendado.module.css";

// Tarjeta de la grilla de la pantalla 10: posición en el ranking, jugador, nivel y la franja
// que cubre el encuentro. El puntaje de compatibilidad no se muestra.
function TarjetaRecomendado({ posicion, jugador }) {
  return (
    <li className={estilos.tarjeta}>
      <div className={estilos.encabezado}>
        <span className={estilos.posicion}>{posicion}</span>
        <Avatar nombre={jugador.nombre} apellido={jugador.apellido} />
        <div className={estilos.identidad}>
          <p className={estilos.nombre}>
            {jugador.nombre} {jugador.apellido}
          </p>
          <p className={estilos.localidad}>{jugador.localidad.nombre}</p>
        </div>
        <Etiqueta>Nivel {formatearNivel(jugador.nivel)}</Etiqueta>
      </div>
      <p className={estilos.franja}>
        <Clock size={16} strokeWidth={2} aria-hidden="true" />
        Disponible {formatearFranja(jugador.franja)}
      </p>
    </li>
  );
}

export default TarjetaRecomendado;
