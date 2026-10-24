import estilos from "./SelectorSegmentado.module.css";
import MensajeCampo from "./MensajeCampo.jsx";

// Grupo de radios nativos con estilo de selector segmentado. `opciones`: [{ valor, etiqueta }];
// con `valor` "" no hay ninguna elegida.
function SelectorSegmentado({
  id,
  leyenda,
  opciones,
  valor,
  onCambiar,
  error,
}) {
  return (
    <fieldset
      className={estilos.grupo}
      aria-describedby={error ? `${id}-error` : undefined}
    >
      <legend className={estilos.leyenda}>{leyenda}</legend>
      <div
        className={
          error ? `${estilos.opciones} ${estilos.conError}` : estilos.opciones
        }
      >
        {opciones.map((opcion) => (
          <label key={opcion.valor} className={estilos.opcion}>
            <input
              type="radio"
              name={id}
              value={opcion.valor}
              checked={valor === opcion.valor}
              onChange={() => onCambiar(opcion.valor)}
              aria-invalid={error ? "true" : undefined}
              className={estilos.radio}
            />
            {opcion.etiqueta}
          </label>
        ))}
      </div>
      <MensajeCampo id={id} error={error} />
    </fieldset>
  );
}

export default SelectorSegmentado;
