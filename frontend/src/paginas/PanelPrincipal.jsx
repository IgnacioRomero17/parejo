import { Plus } from "lucide-react";
import Aviso from "../componentes/Aviso.jsx";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import Boton from "../componentes/Boton.jsx";
import { useAvisoRecibido } from "../hooks/useAvisoRecibido.js";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import estilos from "./PanelPrincipal.module.css";

// Pantalla 08. Por ahora el encabezado, el botón para crear encuentros y el aviso que llega
// al navegar (por ejemplo, al terminar el onboarding); los encuentros y las invitaciones se
// suman con HU-008 y HU-012.
function PanelPrincipal() {
  useTituloPagina("Inicio");
  const { usuario } = useSesion();
  const { aviso, cerrarAviso } = useAvisoRecibido();

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
      </main>
    </>
  );
}

export default PanelPrincipal;
