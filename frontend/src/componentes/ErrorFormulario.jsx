import { CircleAlert } from "lucide-react";
import estilos from "./ErrorFormulario.module.css";

function ErrorFormulario({ children }) {
  return (
    <div role="alert" className={estilos.error}>
      <CircleAlert
        size={16}
        strokeWidth={2}
        aria-hidden="true"
        className={estilos.icono}
      />
      <p>{children}</p>
    </div>
  );
}

export default ErrorFormulario;
