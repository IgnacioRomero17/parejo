import { Check } from "lucide-react";
import { useEffect } from "react";
import estilos from "./Aviso.module.css";

const DURACION_MS = 4000;

// Aviso flotante de confirmación; avisa con `onCerrar` cuando se cumple su tiempo.
function Aviso({ mensaje, onCerrar }) {
  useEffect(() => {
    const temporizador = setTimeout(onCerrar, DURACION_MS);
    return () => clearTimeout(temporizador);
  }, [mensaje, onCerrar]);

  return (
    <div role="status" className={estilos.aviso}>
      <Check
        size={18}
        strokeWidth={2}
        aria-hidden="true"
        className={estilos.icono}
      />
      <p>{mensaje}</p>
    </div>
  );
}

export default Aviso;
