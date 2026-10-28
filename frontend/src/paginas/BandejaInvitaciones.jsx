import { useCallback, useId, useState } from "react";
import {
  aceptarInvitacion,
  obtenerInvitaciones,
  rechazarInvitacion,
} from "../api/invitaciones.js";
import { obtenerPerfil } from "../api/perfil.js";
import Aviso from "../componentes/Aviso.jsx";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import ErrorFormulario from "../componentes/ErrorFormulario.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import SinInvitaciones from "../componentes/SinInvitaciones.jsx";
import TarjetaInvitacionPendiente from "../componentes/TarjetaInvitacionPendiente.jsx";
import TarjetaInvitacionRespondida from "../componentes/TarjetaInvitacionRespondida.jsx";
import { useCargarDatos } from "../hooks/useCargarDatos.js";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import estilos from "./BandejaInvitaciones.module.css";

const RESPUESTAS = {
  aceptar: { pedir: aceptarInvitacion, aviso: "Te sumaste al encuentro." },
  rechazar: { pedir: rechazarInvitacion, aviso: "Rechazaste la invitación." },
};

function Pendientes({ invitaciones, respondiendo, onResponder }) {
  const idTitulo = useId();
  return (
    <section className={estilos.seccion} aria-labelledby={idTitulo}>
      <h2 id={idTitulo} className={estilos.rotulo}>
        Pendientes · {invitaciones.length}
      </h2>
      {invitaciones.length === 0 ? (
        <p className={estilos.texto}>No tenés invitaciones pendientes.</p>
      ) : (
        <ul className={estilos.lista}>
          {invitaciones.map((invitacion) => (
            <TarjetaInvitacionPendiente
              key={invitacion.id}
              invitacion={invitacion}
              respondiendo={respondiendo}
              onAceptar={() => onResponder(invitacion, "aceptar")}
              onRechazar={() => onResponder(invitacion, "rechazar")}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

function Respondidas({ invitaciones }) {
  const idTitulo = useId();
  return (
    <section className={estilos.seccion} aria-labelledby={idTitulo}>
      <h2 id={idTitulo} className={estilos.rotulo}>
        Respondidas
      </h2>
      <ul className={estilos.grilla}>
        {invitaciones.map((invitacion) => (
          <TarjetaInvitacionRespondida
            key={invitacion.id}
            invitacion={invitacion}
          />
        ))}
      </ul>
    </section>
  );
}

// El texto del estado vacío depende de la disponibilidad, que trae el perfil (no la sesión):
// se pide solo cuando no hay ninguna invitación.
function SinNingunaInvitacion() {
  const perfil = useCargarDatos(obtenerPerfil);
  if (!perfil.datos) {
    return (
      <EstadoCarga error={perfil.error} onReintentar={perfil.reintentar} />
    );
  }
  return (
    <SinInvitaciones
      disponible={perfil.datos.disponibilidad.disponible_para_invitaciones}
    />
  );
}

// Pantalla 13: invitaciones recibidas de encuentros que todavía no comenzaron.
function BandejaInvitaciones() {
  useTituloPagina("Invitaciones");
  const { refrescarUsuario } = useSesion();
  const carga = useCargarDatos(obtenerInvitaciones);
  const [respondiendo, setRespondiendo] = useState(false);
  const [error, setError] = useState("");
  const [aviso, setAviso] = useState("");
  const cerrarAviso = useCallback(() => setAviso(""), []);

  async function manejarRespuesta(invitacion, respuesta) {
    setRespondiendo(true);
    setError("");
    try {
      await RESPUESTAS[respuesta].pedir(invitacion.id);
      setAviso(RESPUESTAS[respuesta].aviso);
    } catch (errorApi) {
      setError(errorApi.detalle);
    } finally {
      setRespondiendo(false);
      carga.recargar();
      // El indicador de la barra cuenta las pendientes.
      refrescarUsuario();
    }
  }

  function contenido() {
    const { pendientes, respondidas } = carga.datos;
    if (pendientes.length === 0 && respondidas.length === 0) {
      return <SinNingunaInvitacion />;
    }
    return (
      <>
        {error && <ErrorFormulario>{error}</ErrorFormulario>}
        <Pendientes
          invitaciones={pendientes}
          respondiendo={respondiendo}
          onResponder={manejarRespuesta}
        />
        {respondidas.length > 0 && <Respondidas invitaciones={respondidas} />}
      </>
    );
  }

  return (
    <>
      <BarraSuperior />
      {aviso && <Aviso mensaje={aviso} onCerrar={cerrarAviso} />}
      <main className={estilos.pagina}>
        <div className={estilos.titulo}>
          <h1>Invitaciones recibidas</h1>
          <p className={estilos.texto}>
            Al aceptar una invitación pasás a ser participante confirmado de ese
            encuentro.
          </p>
        </div>
        {carga.datos ? (
          contenido()
        ) : (
          <EstadoCarga error={carga.error} onReintentar={carga.reintentar} />
        )}
      </main>
    </>
  );
}

export default BandejaInvitaciones;
