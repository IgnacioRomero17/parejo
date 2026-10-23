import { useId } from "react";
import estilos from "./Tarjeta.module.css";

// Tarjeta blanca; con `titulo`, es una sección con su encabezado y texto.
function Tarjeta({ titulo, texto, children }) {
  const idTitulo = useId();

  if (!titulo) return <div className={estilos.tarjeta}>{children}</div>;
  return (
    <section className={estilos.tarjeta} aria-labelledby={idTitulo}>
      <div className={estilos.encabezado}>
        <h2 id={idTitulo} className={estilos.titulo}>
          {titulo}
        </h2>
        {texto && <p className={estilos.texto}>{texto}</p>}
      </div>
      {children}
    </section>
  );
}

export default Tarjeta;
