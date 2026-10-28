import { House } from "lucide-react";
import { useCallback } from "react";
import { Navigate, useParams } from "react-router-dom";
import { obtenerPropuesta } from "../api/encuentros.js";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import Boton from "../componentes/Boton.jsx";
import CombinacionesEvaluadas from "../componentes/CombinacionesEvaluadas.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import Etiqueta from "../componentes/Etiqueta.jsx";
import ParejasPropuesta from "../componentes/ParejasPropuesta.jsx";
import ResultadoEquilibrio from "../componentes/ResultadoEquilibrio.jsx";
import { useCargarDatos } from "../hooks/useCargarDatos.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import {
  ESTADOS_ENCUENTRO,
  etiquetaTipoEncuentro,
} from "../utilidades/encuentros.js";
import { formatearFechaLarga } from "../utilidades/formato.js";
import estilos from "./Propuesta.module.css";

// El backend responde 409 si el encuentro todavía no tiene propuesta.
const SIN_PROPUESTA = 409;

function DatosEncuentro({ encuentro }) {
  const datos = [
    { rotulo: "Fecha", valor: formatearFechaLarga(encuentro.fecha) },
    { rotulo: "Hora", valor: encuentro.hora_inicio },
    { rotulo: "Duración", valor: `${encuentro.duracion_minutos} minutos` },
    { rotulo: "Tipo", valor: etiquetaTipoEncuentro(encuentro.tipo_encuentro) },
    {
      rotulo: "Lugar",
      valor: `${encuentro.localidad.nombre} · ${encuentro.ubicacion}`,
    },
  ];
  return (
    <dl className={estilos.datos}>
      {datos.map(({ rotulo, valor }) => (
        <div key={rotulo}>
          <dt className={estilos.rotulo}>{rotulo}</dt>
          <dd className={estilos.valor}>{valor}</dd>
        </div>
      ))}
    </dl>
  );
}

// Pantalla 16, para los 4 participantes. El puntaje es el guardado; promedios y equilibrios
// llegan recalculados con el nivel y el lado actuales (limitación aceptada de HU-012).
function Propuesta() {
  useTituloPagina("Propuesta de encuentro");
  const { id } = useParams();
  const cargar = useCallback(() => obtenerPropuesta(id), [id]);
  const carga = useCargarDatos(cargar);

  function contenido() {
    const {
      encuentro,
      combinacion_elegida,
      puntaje_equilibrio,
      combinaciones,
    } = carga.datos;
    const estado = ESTADOS_ENCUENTRO.PROPUESTA_GENERADA;
    return (
      <>
        <div className={estilos.encabezado}>
          <div className={estilos.titulo}>
            <span>
              <Etiqueta color={estado.color}>{estado.etiqueta}</Etiqueta>
            </span>
            <h1>Propuesta de encuentro</h1>
            <p className={estilos.texto}>
              Resultado generado automáticamente por el sistema: la combinación
              de parejas con mejor resultado de equilibrio.
            </p>
          </div>
          <Boton variante="secundario" a="/inicio" icono={House}>
            Volver al inicio
          </Boton>
        </div>
        <DatosEncuentro encuentro={encuentro} />
        <ParejasPropuesta
          combinacion={combinaciones[combinacion_elegida - 1]}
        />
        <ResultadoEquilibrio puntaje={puntaje_equilibrio} />
        <CombinacionesEvaluadas
          combinaciones={combinaciones}
          elegida={combinacion_elegida}
        />
      </>
    );
  }

  if (carga.error?.estado === SIN_PROPUESTA) {
    return <Navigate to="/inicio" replace />;
  }
  return (
    <>
      <BarraSuperior />
      <main className={estilos.pagina}>
        {carga.datos ? (
          contenido()
        ) : (
          <EstadoCarga error={carga.error} onReintentar={carga.reintentar} />
        )}
      </main>
    </>
  );
}

export default Propuesta;
