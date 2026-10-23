import { idDescripcion } from "../utilidades/campos.js";
import estilos from "./Campo.module.css";
import MensajeCampo from "./MensajeCampo.jsx";

function Campo({
  id,
  etiqueta,
  tipo = "text",
  valor,
  onCambiar,
  error,
  autoComplete,
  maxLength,
  min,
  max,
  inputMode,
  requerido = false,
  soloLectura = false,
  accionEtiqueta,
  ayuda,
}) {
  const etiquetaCampo = (
    <label htmlFor={id} className={estilos.etiqueta}>
      {etiqueta}
    </label>
  );

  return (
    <div className={estilos.campo}>
      {accionEtiqueta ? (
        <div className={estilos.cabecera}>
          {etiquetaCampo}
          {accionEtiqueta}
        </div>
      ) : (
        etiquetaCampo
      )}
      <input
        id={id}
        name={id}
        type={tipo}
        value={valor}
        onChange={(evento) => onCambiar?.(evento.target.value)}
        autoComplete={autoComplete}
        maxLength={maxLength}
        min={min}
        max={max}
        inputMode={inputMode}
        required={requerido}
        readOnly={soloLectura}
        aria-invalid={error ? "true" : undefined}
        aria-describedby={idDescripcion(id, error, ayuda)}
        className={
          error ? `${estilos.control} ${estilos.conError}` : estilos.control
        }
      />
      <MensajeCampo id={id} error={error} ayuda={ayuda} />
    </div>
  );
}

export default Campo;
