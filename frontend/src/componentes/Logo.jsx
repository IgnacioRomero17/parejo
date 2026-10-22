import logo from "../assets/parejo-logo.svg";
import estilos from "./Logo.module.css";

// El nombre se lee del alt de la imagen; el texto visible se oculta para no repetirlo.
function Logo() {
  return (
    <span className={estilos.logo}>
      <img src={logo} alt="parejo" width="30" height="30" />
      <span className={estilos.nombre} aria-hidden="true">
        parejo
      </span>
    </span>
  );
}

export default Logo;
