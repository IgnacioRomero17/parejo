import { ChevronDown } from "lucide-react";
import { nombresDePareja } from "../utilidades/encuentros.js";
import { formatearPuntaje } from "../utilidades/formato.js";
import { notaCombinacion } from "../utilidades/propuesta.js";
import estilos from "./CombinacionesEvaluadas.module.css";
import Etiqueta from "./Etiqueta.jsx";

// Sección desplegable de la pantalla 16, cerrada al entrar: las 3 combinaciones con el
// puntaje guardado y los promedios y equilibrios recalculados. La elegida va resaltada y
// las demás llevan una nota con el motivo por el que no se eligieron.
function CombinacionesEvaluadas({ combinaciones, elegida }) {
  const combinacionElegida = combinaciones.find(
    (combinacion) => combinacion.numero === elegida,
  );
  return (
    <details className={estilos.seccion}>
      <summary className={estilos.resumen}>
        Ver combinaciones evaluadas
        <ChevronDown
          size={18}
          strokeWidth={2}
          aria-hidden="true"
          className={estilos.flecha}
        />
      </summary>
      <table className={estilos.tabla}>
        <thead>
          <tr>
            <th scope="col">N.º</th>
            <th scope="col">Parejas</th>
            <th scope="col">Promedios</th>
            <th scope="col">Equilibrio nivel</th>
            <th scope="col">Equilibrio lado</th>
            <th scope="col">Puntaje</th>
          </tr>
        </thead>
        <tbody>
          {combinaciones.map((combinacion) => {
            const [pareja1, pareja2] = combinacion.parejas;
            const esElegida = combinacion.numero === elegida;
            const nota = notaCombinacion(combinacion, combinacionElegida);
            return (
              <tr
                key={combinacion.numero}
                className={esElegida ? estilos.elegida : undefined}
              >
                <td>{combinacion.numero}</td>
                <td>
                  {nombresDePareja(pareja1)} vs {nombresDePareja(pareja2)}
                  {nota && <span className={estilos.nota}>{nota}</span>}
                </td>
                <td>
                  {formatearPuntaje(pareja1.promedio)} vs{" "}
                  {formatearPuntaje(pareja2.promedio)}
                </td>
                <td>{formatearPuntaje(combinacion.equilibrio_nivel)}</td>
                <td>{formatearPuntaje(combinacion.equilibrio_lado)}</td>
                <td>
                  <span className={estilos.puntaje}>
                    <strong>
                      {formatearPuntaje(combinacion.puntaje_equilibrio)}
                    </strong>
                    {esElegida && (
                      <Etiqueta color="azul">Seleccionada</Etiqueta>
                    )}
                  </span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </details>
  );
}

export default CombinacionesEvaluadas;
