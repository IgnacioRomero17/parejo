import estilos from "./Avatar.module.css";

// Círculo con las iniciales; es decorativo porque el nombre siempre se muestra al lado.
// `color`: azul (por defecto) o verde, que distingue a la Pareja 2 de la propuesta.
function Avatar({ nombre, apellido, color = "azul" }) {
  const iniciales = `${nombre.charAt(0)}${apellido.charAt(0)}`.toUpperCase();
  return (
    <span className={`${estilos.avatar} ${estilos[color]}`} aria-hidden="true">
      {iniciales}
    </span>
  );
}

export default Avatar;
