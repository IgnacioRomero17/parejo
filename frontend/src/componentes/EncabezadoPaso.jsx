import estilos from "./EncabezadoPaso.module.css";

// Encabezado de los pasos de la recuperación: rótulo "Paso N de 3", título y texto.
function EncabezadoPaso({ paso, total = 3, icono, titulo, children }) {
  return (
    <div className={estilos.encabezado}>
      <p className={estilos.rotulo}>
        Paso {paso} de {total}
      </p>
      {icono}
      <h1>{titulo}</h1>
      {children && <p className={estilos.texto}>{children}</p>}
    </div>
  );
}

export default EncabezadoPaso;
