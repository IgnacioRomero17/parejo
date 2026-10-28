import { LUGARES_POR_ENCUENTRO } from "../utilidades/encuentros.js";
import estilos from "./Casilleros.module.css";

const NUMEROS_DE_LUGAR = Array.from(
  { length: LUGARES_POR_ENCUENTRO },
  (_, posicion) => posicion + 1,
);

// Cuatro casilleros de lugares con "N de 4 · faltan M": confirmados en azul (lima si el
// encuentro está completo) y libres con borde punteado. Los cuadros son decorativos: el texto
// dice lo mismo. El panel principal no muestra "faltan M" (`conFaltan` en falso).
function Casilleros({ confirmados, completo = false, conFaltan = true }) {
  const faltan = LUGARES_POR_ENCUENTRO - confirmados;
  const claseConfirmado = completo ? estilos.completo : estilos.confirmado;

  return (
    <div className={estilos.casilleros}>
      <span className={estilos.cuadros} aria-hidden="true">
        {NUMEROS_DE_LUGAR.map((numero) => (
          <span
            key={numero}
            className={`${estilos.cuadro} ${numero <= confirmados ? claseConfirmado : estilos.libre}`}
          />
        ))}
      </span>
      <span className={estilos.cantidad}>
        {confirmados} de {LUGARES_POR_ENCUENTRO}
      </span>
      {conFaltan && faltan > 0 && (
        <span className={estilos.faltan}>· faltan {faltan}</span>
      )}
    </div>
  );
}

export default Casilleros;
