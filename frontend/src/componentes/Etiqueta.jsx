import estilos from "./Etiqueta.module.css";

// Píldora de estado. `color`: azul, verde, rojo, amarillo, lima o gris.
function Etiqueta({ color = "gris", children }) {
  return (
    <span className={`${estilos.etiqueta} ${estilos[color]}`}>{children}</span>
  );
}

export default Etiqueta;
