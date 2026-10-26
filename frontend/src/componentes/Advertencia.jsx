import { TriangleAlert } from "lucide-react";
import estilos from "./Advertencia.module.css";

// Aviso amarillo fijo dentro de la página (no el flotante de confirmación).
function Advertencia({ children }) {
  return (
    <div role="status" className={estilos.advertencia}>
      <TriangleAlert
        size={16}
        strokeWidth={2}
        aria-hidden="true"
        className={estilos.icono}
      />
      <p>{children}</p>
    </div>
  );
}

export default Advertencia;
