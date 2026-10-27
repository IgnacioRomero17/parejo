import { Check } from "lucide-react";
import { PASOS_FORMACION } from "../utilidades/encuentros.js";
import estilos from "./PasosFormacion.module.css";

const ETIQUETAS = {
  listo: "Listo",
  enCurso: "En curso",
  enEspera: "En espera",
};

function estadoDelPaso(indice, enCurso) {
  if (indice < enCurso) return "listo";
  return indice === enCurso ? "enCurso" : "enEspera";
}

// Progreso de la pantalla 15. Es una animación: `enCurso` es el índice del paso que avanza.
function PasosFormacion({ enCurso }) {
  const numero = enCurso + 1;
  return (
    <div className={estilos.pasos}>
      <div className={estilos.encabezado}>
        <p role="status" className={estilos.numero}>
          Paso {numero} de {PASOS_FORMACION.length}
        </p>
        <p className={estilos.demora}>Esto puede tardar unos segundos</p>
      </div>
      <div className={estilos.barra} aria-hidden="true">
        <span
          className={estilos.avance}
          style={{ width: `${(numero / PASOS_FORMACION.length) * 100}%` }}
        />
      </div>
      <ol className={estilos.lista}>
        {PASOS_FORMACION.map((texto, indice) => {
          const estado = estadoDelPaso(indice, enCurso);
          return (
            <li key={texto} className={`${estilos.paso} ${estilos[estado]}`}>
              <span className={estilos.icono} aria-hidden="true">
                {estado === "listo" && <Check size={14} strokeWidth={3} />}
              </span>
              <span className={estilos.texto}>{texto}</span>
              <span className={estilos.estado}>{ETIQUETAS[estado]}</span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

export default PasosFormacion;
