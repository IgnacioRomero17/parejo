import { useCallback } from "react";
import { useParams } from "react-router-dom";
import { obtenerEncuentro, obtenerRecomendados } from "../api/encuentros.js";
import Advertencia from "../componentes/Advertencia.jsx";
import Aviso from "../componentes/Aviso.jsx";
import BarraInvitar from "../componentes/BarraInvitar.jsx";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import EncabezadoEncuentro from "../componentes/EncabezadoEncuentro.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import SinCompatibles from "../componentes/SinCompatibles.jsx";
import TarjetaRecomendado from "../componentes/TarjetaRecomendado.jsx";
import { useAvisoRecibido } from "../hooks/useAvisoRecibido.js";
import { useCargarDatos } from "../hooks/useCargarDatos.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import {
  textoJugadores,
  textoLugaresLibres,
} from "../utilidades/encuentros.js";
import estilos from "./JugadoresRecomendados.module.css";

// Lo que va debajo del título según los lugares libres y los recomendados, en el orden de
// docs/interfaces/10-recomendados.md. La lista se pide cada vez: el ranking no se guarda.
function Recomendados({ recomendacion }) {
  const { lugares_libres: lugaresLibres, recomendados } = recomendacion;

  if (lugaresLibres === 0) {
    return (
      <p className={estilos.texto}>
        No quedan lugares libres. Esperá la respuesta de las invitaciones
        pendientes.
      </p>
    );
  }
  return (
    <>
      {!recomendacion.suficientes && (
        <Advertencia>
          No se encontraron suficientes participantes compatibles. Hay{" "}
          {textoJugadores(recomendados.length)} para{" "}
          {textoLugaresLibres(lugaresLibres)}.
        </Advertencia>
      )}
      <ol className={estilos.grilla} aria-label="Jugadores recomendados">
        {recomendados.map((jugador, posicion) => (
          <TarjetaRecomendado
            key={jugador.id}
            posicion={posicion + 1}
            jugador={jugador}
          />
        ))}
      </ol>
      <BarraInvitar lugaresLibres={lugaresLibres} />
    </>
  );
}

// Pantalla 10 (y 11, cuando no hay ningún candidato). Solo para el organizador: a cualquier
// otro el backend le responde que el encuentro no existe.
function JugadoresRecomendados() {
  useTituloPagina("Jugadores recomendados");
  const { id } = useParams();
  const cargar = useCallback(
    () => Promise.all([obtenerEncuentro(id), obtenerRecomendados(id)]),
    [id],
  );
  const carga = useCargarDatos(cargar);
  const { aviso, cerrarAviso } = useAvisoRecibido();

  function contenido() {
    const [encuentro, recomendacion] = carga.datos;
    const sinCandidatos =
      recomendacion.lugares_libres > 0 &&
      recomendacion.recomendados.length === 0;

    return (
      <>
        <EncabezadoEncuentro encuentro={encuentro} />
        {sinCandidatos ? (
          <SinCompatibles lugaresLibres={recomendacion.lugares_libres} />
        ) : (
          <>
            <div className={estilos.encabezado}>
              <h1>Jugadores recomendados para este encuentro</h1>
              <p className={estilos.texto}>
                Ordenados según los criterios de compatibilidad del sistema.
                Solo aparecen jugadores disponibles para recibir invitaciones.
              </p>
            </div>
            <Recomendados recomendacion={recomendacion} />
          </>
        )}
      </>
    );
  }

  return (
    <>
      <BarraSuperior />
      {aviso && <Aviso mensaje={aviso} onCerrar={cerrarAviso} />}
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

export default JugadoresRecomendados;
