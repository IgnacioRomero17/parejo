import { Plus } from "lucide-react";
import { useId } from "react";
import { obtenerEncuentrosActivos } from "../api/encuentros.js";
import { obtenerInvitaciones } from "../api/invitaciones.js";
import { listarLocalidades } from "../api/localidades.js";
import { obtenerPerfil } from "../api/perfil.js";
import Aviso from "../componentes/Aviso.jsx";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import Boton from "../componentes/Boton.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import SinEncuentros from "../componentes/SinEncuentros.jsx";
import TarjetaEncuentroActivo from "../componentes/TarjetaEncuentroActivo.jsx";
import TarjetaInvitaciones from "../componentes/TarjetaInvitaciones.jsx";
import TarjetaPerfil from "../componentes/TarjetaPerfil.jsx";
import { useAvisoRecibido } from "../hooks/useAvisoRecibido.js";
import { useCargarDatos } from "../hooks/useCargarDatos.js";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import estilos from "./PanelPrincipal.module.css";

// El perfil trae la localidad como id: el nombre sale del catálogo.
function cargarPerfil() {
  return Promise.all([obtenerPerfil(), listarLocalidades()]);
}

function EncuentrosActivos({ encuentros }) {
  if (encuentros.length === 0) return <SinEncuentros />;
  return (
    <ul className={estilos.encuentros}>
      {encuentros.map((encuentro) => (
        <TarjetaEncuentroActivo key={encuentro.id} encuentro={encuentro} />
      ))}
    </ul>
  );
}

// Pantalla 08: encuentros activos a la izquierda; invitaciones y perfil a la derecha. Cada
// bloque carga sus datos por separado, así un error en uno no oculta los demás.
function PanelPrincipal() {
  useTituloPagina("Inicio");
  const { usuario } = useSesion();
  const { aviso, cerrarAviso } = useAvisoRecibido();
  const encuentros = useCargarDatos(obtenerEncuentrosActivos);
  const invitaciones = useCargarDatos(obtenerInvitaciones);
  const perfil = useCargarDatos(cargarPerfil);
  const idEncuentros = useId();
  const idInvitaciones = useId();
  const idPerfil = useId();

  return (
    <>
      <BarraSuperior />
      {aviso && <Aviso mensaje={aviso} onCerrar={cerrarAviso} />}
      <main className={estilos.pagina}>
        <div className={estilos.encabezado}>
          <div className={estilos.titulo}>
            <h1>Hola, {usuario.nombre}</h1>
            <p className={estilos.texto}>
              Organizá un encuentro o respondé las invitaciones que recibiste.
            </p>
          </div>
          <Boton a="/encuentros/nuevo" icono={Plus}>
            Crear encuentro
          </Boton>
        </div>
        <div className={estilos.columnas}>
          <section
            className={estilos.encuentrosActivos}
            aria-labelledby={idEncuentros}
          >
            <div>
              <h2 id={idEncuentros} className={estilos.subtitulo}>
                Tus encuentros activos
              </h2>
              <p className={estilos.ayuda}>
                Los que organizás y aquellos a los que te invitaron y aceptaste.
              </p>
            </div>
            {encuentros.datos ? (
              <EncuentrosActivos encuentros={encuentros.datos} />
            ) : (
              <EstadoCarga
                error={encuentros.error}
                onReintentar={encuentros.reintentar}
              />
            )}
          </section>
          <section
            className={estilos.invitaciones}
            aria-labelledby={idInvitaciones}
          >
            <h2 id={idInvitaciones} className={estilos.subtitulo}>
              Invitaciones
            </h2>
            {invitaciones.datos ? (
              <TarjetaInvitaciones pendientes={invitaciones.datos.pendientes} />
            ) : (
              <EstadoCarga
                error={invitaciones.error}
                onReintentar={invitaciones.reintentar}
              />
            )}
          </section>
          <section className={estilos.perfil} aria-labelledby={idPerfil}>
            <h2 id={idPerfil} className={estilos.subtitulo}>
              Tu perfil
            </h2>
            {perfil.datos ? (
              <TarjetaPerfil
                perfil={perfil.datos[0]}
                localidades={perfil.datos[1]}
              />
            ) : (
              <EstadoCarga
                error={perfil.error}
                onReintentar={perfil.reintentar}
              />
            )}
          </section>
        </div>
      </main>
    </>
  );
}

export default PanelPrincipal;
