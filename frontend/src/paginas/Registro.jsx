import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registrarse } from "../api/auth.js";
import Boton from "../componentes/Boton.jsx";
import Campo from "../componentes/Campo.jsx";
import ErrorFormulario from "../componentes/ErrorFormulario.jsx";
import PanelAcceso from "../componentes/PanelAcceso.jsx";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import { rutaInicial } from "../utilidades/rutas.js";
import { validarCamposRequeridos } from "../utilidades/validaciones.js";
import estilos from "./Registro.module.css";

const VALORES_INICIALES = {
  nombre: "",
  apellido: "",
  email: "",
  contrasena: "",
};

function Registro() {
  useTituloPagina("Registro");
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
    // En el navegador solo se avisa lo inmediato (campos vacíos); el resto lo valida el backend.
    const erroresLocales = validarCamposRequeridos(valores);
    setErrores(erroresLocales);
    if (Object.keys(erroresLocales).length > 0) return;

    setEnviando(true);
    try {
      const usuario = await registrarse(valores);
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
      texto="Registrá tu perfil, recibí recomendaciones de jugadores compatibles y dejá que el sistema forme parejas equilibradas."
    >
      <div className={estilos.encabezado}>
        <h1>Crear cuenta</h1>
        <p className={estilos.subtitulo}>Todos los campos son requeridos.</p>
      </div>

      {errorGeneral && <ErrorFormulario>{errorGeneral}</ErrorFormulario>}

      <form className={estilos.formulario} onSubmit={manejarEnvio} noValidate>
        <div className={estilos.fila}>
          <Campo
            id="nombre"
            etiqueta="Nombre"
            valor={valores.nombre}
            onCambiar={manejarCambio("nombre")}
            error={errorDe("nombre")}
            autoComplete="given-name"
            maxLength={60}
            requerido
          />
          <Campo
            id="apellido"
            etiqueta="Apellido"
            valor={valores.apellido}
            onCambiar={manejarCambio("apellido")}
            error={errorDe("apellido")}
            autoComplete="family-name"
            maxLength={60}
            requerido
          />
        </div>
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
          autoComplete="new-password"
          maxLength={64}
          requerido
        />
        <Boton tipo="submit" deshabilitado={enviando} anchoCompleto>
          Registrarse
        </Boton>
      </form>

      <p className={estilos.pie}>
        ¿Ya tenés cuenta? <Link to="/ingresar">Iniciar sesión</Link>
      </p>
    </PanelAcceso>
  );
}

export default Registro;
