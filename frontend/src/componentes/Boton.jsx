import { Link } from "react-router-dom";
import estilos from "./Boton.module.css";

// Con `a` se dibuja como enlace de navegación; si no, como <button>.
function Boton({
  variante = "primario",
  tipo = "button",
  a,
  icono: Icono,
  deshabilitado = false,
  anchoCompleto = false,
  onClick,
  children,
}) {
  const clases = [
    estilos.boton,
    estilos[variante],
    anchoCompleto && estilos.anchoCompleto,
  ]
    .filter(Boolean)
    .join(" ");
  const contenido = (
    <>
      {Icono && <Icono size={16} strokeWidth={2} aria-hidden="true" />}
      {children}
    </>
  );

  if (a) {
    return (
      <Link to={a} className={clases}>
        {contenido}
      </Link>
    );
  }
  return (
    <button
      type={tipo}
      className={clases}
      disabled={deshabilitado}
      onClick={onClick}
    >
      {contenido}
    </button>
  );
}

export default Boton;
