import { useCallback } from "react";
import { useParams } from "react-router-dom";
import { obtenerEncuentro } from "../api/encuentros.js";
import Aviso from "../componentes/Aviso.jsx";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import EncabezadoEncuentro from "../componentes/EncabezadoEncuentro.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import { useAvisoRecibido } from "../hooks/useAvisoRecibido.js";
import { useCargarDatos } from "../hooks/useCargarDatos.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import estilos from "./JugadoresRecomendados.module.css";

// Pantalla 10, versión parcial de HU-006: el encabezado con las condiciones del encuentro
// recién creado, el título y el texto. La grilla de recomendados, el aviso de candidatos
// insuficientes, la pantalla 11 y la barra inferior se suman con HU-007.
function JugadoresRecomendados() {
  useTituloPagina("Jugadores recomendados");
  const { id } = useParams();
  const cargar = useCallback(() => obtenerEncuentro(id), [id]);
  const carga = useCargarDatos(cargar);
  const { aviso, cerrarAviso } = useAvisoRecibido();

  return (
    <>
      <BarraSuperior />
      {aviso && <Aviso mensaje={aviso} onCerrar={cerrarAviso} />}
      <main className={estilos.pagina}>
        {carga.datos ? (
          <>
            <EncabezadoEncuentro encuentro={carga.datos} />
            <div className={estilos.encabezado}>
              <h1>Jugadores recomendados para este encuentro</h1>
              <p className={estilos.texto}>
                Ordenados según los criterios de compatibilidad del sistema.
                Solo aparecen jugadores disponibles para recibir invitaciones.
              </p>
            </div>
          </>
        ) : (
          <EstadoCarga error={carga.error} onReintentar={carga.reintentar} />
        )}
      </main>
    </>
  );
}

export default JugadoresRecomendados;
