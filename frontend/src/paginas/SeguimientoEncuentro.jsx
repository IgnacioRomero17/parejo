import { useCallback, useState } from "react";
import { Navigate, useParams } from "react-router-dom";
import {
  enviarInvitaciones,
  obtenerEncuentro,
  obtenerRecomendados,
} from "../api/encuentros.js";
import { obtenerPerfil } from "../api/perfil.js";
import Aviso from "../componentes/Aviso.jsx";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import EncuentroCompleto from "../componentes/EncuentroCompleto.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import PanelInvitar from "../componentes/PanelInvitar.jsx";
import PanelLugares from "../componentes/PanelLugares.jsx";
import { useCargarDatos } from "../hooks/useCargarDatos.js";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import { avisoInvitacionesEnviadas } from "../utilidades/encuentros.js";
import { formatearFechaCompacta } from "../utilidades/formato.js";
import estilos from "./SeguimientoEncuentro.module.css";

// Con el encuentro buscando participantes hacen falta también los recomendados (el ranking se
// recalcula en cada consulta) y el género del organizador para nombrar su rol.
async function cargarSeguimiento(id) {
  const encuentro = await obtenerEncuentro(id);
  // Solo el organizador recibe las invitaciones: cualquier otro participante no tiene
  // seguimiento que ver.
  if (
    !encuentro.invitaciones ||
    encuentro.estado !== "BUSCANDO_PARTICIPANTES"
  ) {
    return { encuentro };
  }
  const [recomendacion, perfil] = await Promise.all([
    obtenerRecomendados(id),
    obtenerPerfil(),
  ]);
  return { encuentro, recomendacion, genero: perfil.perfil_deportivo.genero };
}

// El mensaje de un error de la API: el general o el primero de un campo.
function mensajeDeError(error) {
  return error.detalle || Object.values(error.errores ?? {})[0]?.[0] || "";
}

// Pantallas 12 (buscando participantes) y 14 (completo), solo para el organizador.
function SeguimientoEncuentro() {
  useTituloPagina("Seguimiento del encuentro");
  const { id } = useParams();
  const { usuario } = useSesion();
  const cargar = useCallback(() => cargarSeguimiento(id), [id]);
  const carga = useCargarDatos(cargar);
  const [seleccionados, setSeleccionados] = useState([]);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const cerrarAviso = useCallback(() => setAviso(""), []);

  function manejarCambio(idJugador) {
    setSeleccionados((anteriores) =>
      anteriores.includes(idJugador)
        ? anteriores.filter((elegido) => elegido !== idJugador)
        : [...anteriores, idJugador],
    );
  }

  async function manejarEnvio() {
    setEnviando(true);
    setError("");
    try {
      const creadas = await enviarInvitaciones(id, seleccionados);
      setAviso(avisoInvitacionesEnviadas(creadas.length));
    } catch (errorApi) {
      setError(mensajeDeError(errorApi));
    } finally {
      // La lista cambia en cualquier caso: al enviar, o porque algún jugador ya no está.
      setSeleccionados([]);
      setEnviando(false);
      carga.recargar();
    }
  }

  function seleccionarEInvitar() {
    const { encuentro, recomendacion, genero } = carga.datos;
    const candidatos = recomendacion.recomendados;
    const elegidos = candidatos.filter((jugador) =>
      seleccionados.includes(jugador.id),
    );
    return (
      <>
        <div className={estilos.titulo}>
          <p className={estilos.rotulo}>
            Encuentro · {formatearFechaCompacta(encuentro.fecha)} ·{" "}
            {encuentro.hora_inicio} · {encuentro.localidad.nombre}
          </p>
          <h1>Seleccionar e invitar jugadores</h1>
        </div>
        <div className={estilos.columnas}>
          <PanelInvitar
            invitaciones={encuentro.invitaciones}
            candidatos={candidatos}
            lugaresLibres={encuentro.lugares_libres}
            seleccionados={seleccionados}
            enviando={enviando}
            error={error}
            onCambiar={manejarCambio}
            onEnviar={manejarEnvio}
          />
          <PanelLugares
            encuentro={encuentro}
            idUsuario={usuario.id}
            genero={genero}
            elegidos={elegidos}
          />
        </div>
      </>
    );
  }

  function contenido() {
    const { encuentro } = carga.datos;
    if (!encuentro.invitaciones) return <Navigate to="/inicio" replace />;
    if (encuentro.estado === "BUSCANDO_PARTICIPANTES") {
      return seleccionarEInvitar();
    }
    return <EncuentroCompleto encuentro={encuentro} idUsuario={usuario.id} />;
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

export default SeguimientoEncuentro;
