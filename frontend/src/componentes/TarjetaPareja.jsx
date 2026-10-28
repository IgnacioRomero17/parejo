import { useId } from "react";
import { etiquetaLado } from "../utilidades/encuentros.js";
import { formatearNivel, formatearPuntaje } from "../utilidades/formato.js";
import Avatar from "./Avatar.jsx";
import Etiqueta from "./Etiqueta.jsx";
import estilos from "./TarjetaPareja.module.css";

// Una pareja de la propuesta (pantalla 16): su promedio recalculado y sus dos integrantes. La
// Pareja 2 se distingue en verde.
function TarjetaPareja({ pareja }) {
  const idTitulo = useId();
  const segunda = pareja.numero === 2;

  return (
    <section
      aria-labelledby={idTitulo}
      className={`${estilos.pareja} ${segunda ? estilos.segunda : estilos.primera}`}
    >
      <div className={estilos.cabecera}>
        <h2 id={idTitulo} className={estilos.titulo}>
          Pareja {pareja.numero}
        </h2>
        <Etiqueta>Promedio {formatearPuntaje(pareja.promedio)}</Etiqueta>
      </div>
      <ul className={estilos.integrantes}>
        {pareja.integrantes.map((jugador) => (
          <li key={jugador.id} className={estilos.integrante}>
            <Avatar
              nombre={jugador.nombre}
              apellido={jugador.apellido}
              color={segunda ? "verde" : "azul"}
            />
            <div className={estilos.identidad}>
              <p className={estilos.nombre}>
                {jugador.nombre} {jugador.apellido}
              </p>
              <p className={estilos.detalle}>
                {jugador.localidad.nombre} · {etiquetaLado(jugador.lado)}
              </p>
            </div>
            <p className={estilos.nivel}>
              Nivel {formatearNivel(jugador.nivel)}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default TarjetaPareja;
