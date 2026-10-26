import { textoJugadores } from "../utilidades/encuentros.js";
import Boton from "./Boton.jsx";
import estilos from "./BarraInvitar.module.css";

// Barra inferior de la pantalla 10: cuántos se pueden invitar y el paso a la pantalla 12.
function BarraInvitar({ idEncuentro, lugaresLibres }) {
  return (
    <div className={estilos.barra}>
      <p>
        Podés invitar hasta <strong>{textoJugadores(lugaresLibres)}</strong>{" "}
        para completar el encuentro.
      </p>
      <Boton a={`/encuentros/${idEncuentro}`}>Seleccionar e invitar</Boton>
    </div>
  );
}

export default BarraInvitar;
