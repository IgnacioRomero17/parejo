import { Plus } from "lucide-react";
import { useId } from "react";
import { obtenerInvitaciones } from "../api/invitaciones.js";
import Aviso from "../componentes/Aviso.jsx";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import Boton from "../componentes/Boton.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import TarjetaInvitaciones from "../componentes/TarjetaInvitaciones.jsx";
import { useAvisoRecibido } from "../hooks/useAvisoRecibido.js";
import { useCargarDatos } from "../hooks/useCargarDatos.js";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import estilos from "./PanelPrincipal.module.css";

// Pantalla 08. Por ahora el encabezado, el botón para crear encuentros, el aviso que llega
// al navegar (por ejemplo, al terminar el onboarding) y la tarjeta de invitaciones; los
// encuentros activos y el perfil de la columna derecha se suman con HU-012.
function PanelPrincipal() {
  useTituloPagina("Inicio");
  const { usuario } = useSesion();
  const { aviso, cerrarAviso } = useAvisoRecibido();
  const invitaciones = useCargarDatos(obtenerInvitaciones);
  const idInvitaciones = useId();

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
          <section className={estilos.derecha} aria-labelledby={idInvitaciones}>
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
        </div>
      </main>
    </>
  );
}

export default PanelPrincipal;
