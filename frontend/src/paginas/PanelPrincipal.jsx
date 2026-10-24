import { useCallback, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Aviso from "../componentes/Aviso.jsx";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import estilos from "./PanelPrincipal.module.css";

// Pantalla 08. Por ahora solo el encabezado y el aviso que llega al navegar (por ejemplo, al
// terminar el onboarding); los encuentros y las invitaciones se suman con HU-008 y HU-012.
function PanelPrincipal() {
  useTituloPagina("Inicio");
  const { usuario } = useSesion();
  const { pathname, state } = useLocation();
  const navigate = useNavigate();
  const [aviso, setAviso] = useState(state?.aviso ?? "");
  const cerrarAviso = useCallback(() => setAviso(""), []);

  // El aviso se muestra una sola vez: si quedara en el historial, volvería al recargar.
  useEffect(() => {
    if (state?.aviso) navigate(pathname, { replace: true, state: null });
  }, [state, pathname, navigate]);

  return (
    <>
      <BarraSuperior />
      {aviso && <Aviso mensaje={aviso} onCerrar={cerrarAviso} />}
      <main className={estilos.pagina}>
        <div className={estilos.encabezado}>
          <h1>Hola, {usuario.nombre}</h1>
          <p className={estilos.texto}>
            Organizá un encuentro o respondé las invitaciones que recibiste.
          </p>
        </div>
      </main>
    </>
  );
}

export default PanelPrincipal;
