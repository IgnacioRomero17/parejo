import estilos from "./Avatar.module.css";

// Círculo con las iniciales; es decorativo porque el nombre siempre se muestra al lado.
function Avatar({ nombre, apellido }) {
  const iniciales = `${nombre.charAt(0)}${apellido.charAt(0)}`.toUpperCase();
  return (
    <span className={estilos.avatar} aria-hidden="true">
      {iniciales}
    </span>
  );
}

export default Avatar;
