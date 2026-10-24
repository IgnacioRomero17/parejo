import { ChevronDown } from "lucide-react";
import { idDescripcion } from "../utilidades/campos.js";
import estilos from "./Desplegable.module.css";
import MensajeCampo from "./MensajeCampo.jsx";

// <select> nativo con estilo propio. `opciones`: [{ valor, etiqueta }]; "" es "sin elegir".
// Con `etiquetaOculta`, la etiqueta solo la leen los lectores de pantalla (filas repetidas
// que comparten los rótulos de la primera, como las franjas).
function Desplegable({
  id,
  etiqueta,
  valor,
  opciones,
  onCambiar,
  error,
  ayuda,
  requerido = false,
  etiquetaOculta = false,
}) {
  return (
    <div className={estilos.campo}>
      <label
        htmlFor={id}
        className={etiquetaOculta ? estilos.etiquetaOculta : estilos.etiqueta}
      >
        {etiqueta}
      </label>
      <div className={estilos.contenedor}>
        <select
          id={id}
          name={id}
          value={valor}
          onChange={(evento) => onCambiar(evento.target.value)}
          required={requerido}
          aria-invalid={error ? "true" : undefined}
          aria-describedby={idDescripcion(id, error, ayuda)}
          className={
            error ? `${estilos.control} ${estilos.conError}` : estilos.control
          }
        >
          <option value="">Seleccioná una opción</option>
          {opciones.map((opcion) => (
            <option key={opcion.valor} value={opcion.valor}>
              {opcion.etiqueta}
            </option>
          ))}
        </select>
        <ChevronDown
          size={18}
          strokeWidth={2}
          aria-hidden="true"
          className={estilos.flecha}
        />
      </div>
      <MensajeCampo id={id} error={error} ayuda={ayuda} />
    </div>
  );
}

export default Desplegable;
