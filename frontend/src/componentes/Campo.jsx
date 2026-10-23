import { CircleAlert } from "lucide-react";
import estilos from "./Campo.module.css";

function Campo({
  id,
  etiqueta,
  tipo = "text",
  valor,
  onCambiar,
  error,
  autoComplete,
  maxLength,
  requerido = false,
  accionEtiqueta,
}) {
  const idError = `${id}-error`;
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
        onChange={(evento) => onCambiar(evento.target.value)}
        autoComplete={autoComplete}
        maxLength={maxLength}
        required={requerido}
        aria-invalid={error ? "true" : undefined}
        aria-describedby={error ? idError : undefined}
        className={
          error ? `${estilos.control} ${estilos.conError}` : estilos.control
        }
      />
      {error && (
        <p id={idError} className={estilos.error}>
          <CircleAlert
            size={14}
            strokeWidth={2}
            aria-hidden="true"
            className={estilos.icono}
          />
          <span>{error}</span>
        </p>
      )}
    </div>
  );
}

export default Campo;
