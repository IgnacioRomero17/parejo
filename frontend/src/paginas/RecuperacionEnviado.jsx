import { Info, MailCheck } from "lucide-react";
import { Link, Navigate, useLocation } from "react-router-dom";
import Boton from "../componentes/Boton.jsx";
import EncabezadoPaso from "../componentes/EncabezadoPaso.jsx";
import PanelAcceso from "../componentes/PanelAcceso.jsx";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import estilos from "./RecuperacionEnviado.module.css";

function RecuperacionEnviado() {
  useTituloPagina("Revisá tu correo");
  const email = useLocation().state?.email;

  // Solo se llega desde el paso 1, que pasa el correo al navegar.
  if (!email) return <Navigate to="/recuperar" replace />;

  return (
    <PanelAcceso
      titulo="Recuperá tu acceso."
      texto="Te enviamos un enlace a tu correo para que definas una nueva contraseña."
    >
      <EncabezadoPaso
        paso={2}
        titulo="Revisá tu correo"
        icono={
          <span className={estilos.icono}>
            <MailCheck size={22} strokeWidth={2} aria-hidden="true" />
          </span>
        }
      >
        Te enviamos un enlace a <strong>{email}</strong>. Abrilo para definir tu
        nueva contraseña.
      </EncabezadoPaso>

      <div className={estilos.informacion}>
        <Info
          size={16}
          strokeWidth={2}
          aria-hidden="true"
          className={estilos.iconoInformacion}
        />
        <p>¿No lo encontrás? Revisá la carpeta de correo no deseado.</p>
      </div>

      <Boton a="/ingresar" anchoCompleto>
        Volver a iniciar sesión
      </Boton>
      <Link to="/recuperar" className={estilos.otroCorreo}>
        Usar otro correo
      </Link>
    </PanelAcceso>
  );
}

export default RecuperacionEnviado;
