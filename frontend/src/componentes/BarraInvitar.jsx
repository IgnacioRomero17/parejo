import { textoJugadores } from "../utilidades/encuentros.js";
import estilos from "./BarraInvitar.module.css";

// Barra inferior de la pantalla 10. El botón "Seleccionar e invitar" se suma con HU-008.
function BarraInvitar({ lugaresLibres }) {
  return (
    <div className={estilos.barra}>
      <p>
        Podés invitar hasta <strong>{textoJugadores(lugaresLibres)}</strong>{" "}
        para completar el encuentro.
      </p>
    </div>
  );
}

export default BarraInvitar;
