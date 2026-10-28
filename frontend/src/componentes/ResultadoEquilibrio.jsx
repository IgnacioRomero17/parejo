import { useId } from "react";
import { formatearPuntaje } from "../utilidades/formato.js";
import estilos from "./ResultadoEquilibrio.module.css";

// Tarjeta de la pantalla 16 con el puntaje guardado de la combinación elegida. Es solo
// informativa: no hay avisos de equilibrio bajo (HU-012).
function ResultadoEquilibrio({ puntaje }) {
  const idTitulo = useId();

  return (
    <section aria-labelledby={idTitulo} className={estilos.tarjeta}>
      <div className={estilos.contenido}>
        <div className={estilos.resultado}>
          <h2 id={idTitulo} className={estilos.rotulo}>
            Resultado de equilibrio · informativo
          </h2>
          <p className={estilos.puntaje}>{formatearPuntaje(puntaje)}</p>
        </div>
        <p className={estilos.texto}>
          Puntaje de equilibrio de la combinación seleccionada, entre 0 y 1 (1 =
          parejas perfectamente equilibradas). Considera la diferencia de nivel
          promedio entre las parejas y la complementariedad del lado preferido.
          Es el mejor resultado entre las 3 combinaciones evaluadas y se muestra
          solo como información.
        </p>
      </div>
    </section>
  );
}

export default ResultadoEquilibrio;
