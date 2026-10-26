import Avatar from "./Avatar.jsx";
import estilos from "./FilaJugador.module.css";

// Iniciales, nombre y un dato debajo (localidad, rol…); a la derecha, lo que llegue en
// `children` (nivel, estado). Se usa en las listas de las pantallas 12 y 14.
function FilaJugador({ jugador, prefijo, detalle, children }) {
  return (
    <div className={estilos.fila}>
      <Avatar nombre={jugador.nombre} apellido={jugador.apellido} />
      <div className={estilos.identidad}>
        <p className={estilos.nombre}>
          {prefijo}
          {jugador.nombre} {jugador.apellido}
        </p>
        {detalle && <p className={estilos.detalle}>{detalle}</p>}
      </div>
      {children}
    </div>
  );
}

export default FilaJugador;
