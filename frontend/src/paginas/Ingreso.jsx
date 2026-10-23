import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ingresar } from "../api/auth.js";
import Boton from "../componentes/Boton.jsx";
import Campo from "../componentes/Campo.jsx";
import ErrorFormulario from "../componentes/ErrorFormulario.jsx";
import PanelAcceso from "../componentes/PanelAcceso.jsx";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import { rutaInicial } from "../utilidades/rutas.js";
import { validarCamposRequeridos } from "../utilidades/validaciones.js";
import estilos from "./Ingreso.module.css";

const VALORES_INICIALES = {
  email: "",
  contrasena: "",
};

function Ingreso() {
  useTituloPagina("Iniciar sesión");
  const navigate = useNavigate();
  const { establecerUsuario } = useSesion();
  const [valores, setValores] = useState(VALORES_INICIALES);
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [enviando, setEnviando] = useState(false);

  function manejarCambio(campo) {
    return (valor) =>
      setValores((anteriores) => ({ ...anteriores, [campo]: valor }));
  }

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setErrorGeneral("");
    const erroresLocales = validarCamposRequeridos(valores);
    setErrores(erroresLocales);
    if (Object.keys(erroresLocales).length > 0) return;

    setEnviando(true);
    try {
      const usuario = await ingresar(valores);
      establecerUsuario(usuario);
      navigate(rutaInicial(usuario), { replace: true });
    } catch (error) {
      setErrores(error.errores ?? {});
      setErrorGeneral(error.detalle ?? "");
      setEnviando(false);
    }
  }

  function errorDe(campo) {
    return errores[campo]?.join(" ");
  }

  return (
    <PanelAcceso
      titulo="Partidos parejos."
      texto="Ingresá para organizar un encuentro o responder tus invitaciones."
    >
      <h1>Iniciar sesión</h1>

      {errorGeneral && <ErrorFormulario>{errorGeneral}</ErrorFormulario>}

      <form className={estilos.formulario} onSubmit={manejarEnvio} noValidate>
        <Campo
          id="email"
          etiqueta="Correo electrónico"
          tipo="email"
          valor={valores.email}
          onCambiar={manejarCambio("email")}
          error={errorDe("email")}
          autoComplete="email"
          maxLength={254}
          requerido
        />
        <Campo
          id="contrasena"
          etiqueta="Contraseña"
          tipo="password"
          valor={valores.contrasena}
          onCambiar={manejarCambio("contrasena")}
          error={errorDe("contrasena")}
          autoComplete="current-password"
          maxLength={64}
          requerido
          accionEtiqueta={
            <Link to="/recuperar" className={estilos.enlaceRecuperar}>
              ¿Olvidaste tu contraseña?
            </Link>
          }
        />
        <Boton tipo="submit" deshabilitado={enviando} anchoCompleto>
          Ingresar
        </Boton>
      </form>

      <p className={estilos.pie}>
        ¿No tenés cuenta? <Link to="/registro">Registrate</Link>
      </p>
    </PanelAcceso>
  );
}

export default Ingreso;
