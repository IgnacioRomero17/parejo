import estilos from "./Interruptor.module.css";
import MensajeCampo from "./MensajeCampo.jsx";

// Checkbox nativo con forma de interruptor, con su título y un texto que lo explica.
function Interruptor({ id, titulo, texto, marcado, onCambiar, error }) {
  const descripcion = [`${id}-texto`, error && `${id}-error`]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={estilos.interruptor}>
      <div className={estilos.fila}>
        <div className={estilos.textos}>
          <label htmlFor={id} className={estilos.titulo}>
            {titulo}
          </label>
          <p id={`${id}-texto`} className={estilos.texto}>
            {texto}
          </p>
        </div>
        <input
          id={id}
          name={id}
          type="checkbox"
          role="switch"
          checked={marcado}
          onChange={(evento) => onCambiar(evento.target.checked)}
          aria-invalid={error ? "true" : undefined}
          aria-describedby={descripcion}
          className={estilos.control}
        />
      </div>
      <MensajeCampo id={id} error={error} />
    </div>
  );
}

export default Interruptor;
