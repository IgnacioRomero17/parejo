import estilos from "./ParejasPropuesta.module.css";
import TarjetaPareja from "./TarjetaPareja.jsx";

// Bloque azul de la pantalla 16 con las dos parejas de la combinación elegida, en el orden de
// su número.
function ParejasPropuesta({ combinacion }) {
  const [pareja1, pareja2] = combinacion.parejas;

  return (
    <div className={estilos.bloque}>
      <TarjetaPareja pareja={pareja1} />
      <p className={estilos.vs}>VS</p>
      <TarjetaPareja pareja={pareja2} />
    </div>
  );
}

export default ParejasPropuesta;
