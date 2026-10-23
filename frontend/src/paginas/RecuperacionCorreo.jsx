import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { solicitarRecuperacion } from "../api/auth.js";
import Boton from "../componentes/Boton.jsx";
import Campo from "../componentes/Campo.jsx";
import EncabezadoPaso from "../componentes/EncabezadoPaso.jsx";
import ErrorFormulario from "../componentes/ErrorFormulario.jsx";
import PanelAcceso from "../componentes/PanelAcceso.jsx";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import { validarCamposRequeridos } from "../utilidades/validaciones.js";
import estilos from "./RecuperacionCorreo.module.css";

function RecuperacionCorreo() {
  useTituloPagina("¿Olvidaste tu contraseña?");
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setErrorGeneral("");
    const erroresLocales = validarCamposRequeridos({ email });
    setErrores(erroresLocales);
    if (Object.keys(erroresLocales).length > 0) return;

    setEnviando(true);
    try {
      await solicitarRecuperacion({ email });
      navigate("/recuperar/enviado", { state: { email: email.trim() } });
    } catch (error) {
      setErrores(error.errores ?? {});
      setErrorGeneral(error.detalle ?? "");
      setEnviando(false);
    }
  }

  return (
    <PanelAcceso
      titulo="Recuperá tu acceso."
      texto="Te enviamos un enlace a tu correo para que definas una nueva contraseña."
    >
      <EncabezadoPaso paso={1} titulo="¿Olvidaste tu contraseña?">
        Ingresá el correo de tu cuenta y te enviaremos un enlace para
        restablecerla.
      </EncabezadoPaso>

      {errorGeneral && <ErrorFormulario>{errorGeneral}</ErrorFormulario>}

      <form className={estilos.formulario} onSubmit={manejarEnvio} noValidate>
        <Campo
          id="email"
          etiqueta="Correo electrónico"
          tipo="email"
          valor={email}
          onCambiar={setEmail}
          error={errores.email?.join(" ")}
          autoComplete="email"
          maxLength={254}
          requerido
        />
        <Boton tipo="submit" deshabilitado={enviando} anchoCompleto>
          Enviar enlace
        </Boton>
      </form>

      <Link to="/ingresar" className={estilos.volver}>
        Volver a iniciar sesión
      </Link>
    </PanelAcceso>
  );
}

export default RecuperacionCorreo;
