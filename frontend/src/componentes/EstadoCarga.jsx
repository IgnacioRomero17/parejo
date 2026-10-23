import Boton from "./Boton.jsx";
import ErrorFormulario from "./ErrorFormulario.jsx";
import estilos from "./EstadoCarga.module.css";

// Lo que muestra una página mientras carga sus datos o si la carga falló.
function EstadoCarga({ error, onReintentar }) {
  if (!error) {
    return (
      <p role="status" className={estilos.cargando}>
        Cargando…
      </p>
    );
  }
  return (
    <div className={estilos.error}>
      <ErrorFormulario>{error.detalle || error.message}</ErrorFormulario>
      <Boton variante="secundario" onClick={onReintentar}>
        Reintentar
      </Boton>
    </div>
  );
}

export default EstadoCarga;
