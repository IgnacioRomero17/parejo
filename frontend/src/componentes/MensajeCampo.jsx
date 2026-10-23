import { CircleAlert } from "lucide-react";
import estilos from "./MensajeCampo.module.css";

// Error o ayuda debajo de un control. Con error, el mensaje ocupa el lugar de la ayuda.
// Los ids son `${id}-error` y `${id}-ayuda`, los que el control enlaza con aria-describedby.
function MensajeCampo({ id, error, ayuda }) {
  if (error) {
    return (
      <p id={`${id}-error`} className={estilos.error}>
        <CircleAlert
          size={14}
          strokeWidth={2}
          aria-hidden="true"
          className={estilos.icono}
        />
        <span>{error}</span>
      </p>
    );
  }
  if (ayuda) {
    return (
      <p id={`${id}-ayuda`} className={estilos.ayuda}>
        {ayuda}
      </p>
    );
  }
  return null;
}

export default MensajeCampo;
