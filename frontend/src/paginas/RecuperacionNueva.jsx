import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  confirmarRecuperacion,
  validarEnlaceRecuperacion,
} from "../api/auth.js";
import Boton from "../componentes/Boton.jsx";
import Campo from "../componentes/Campo.jsx";
import EncabezadoPaso from "../componentes/EncabezadoPaso.jsx";
import ErrorFormulario from "../componentes/ErrorFormulario.jsx";
import PanelAcceso from "../componentes/PanelAcceso.jsx";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import { rutaInicial } from "../utilidades/rutas.js";
import { validarCamposRequeridos } from "../utilidades/validaciones.js";
import estilos from "./RecuperacionNueva.module.css";

const AYUDA_CONTRASENA =
  "Entre 8 y 64 caracteres, con al menos una letra y un número.";

// El backend responde 400 solo con `detalle` cuando el enlace no es válido o ya se usó.
function esEnlaceInvalido(error) {
  return error.estado === 400 && Object.keys(error.errores ?? {}).length === 0;
}

function RecuperacionNueva() {
  useTituloPagina("Nueva contraseña");
  const { uid, token } = useParams();
  const navigate = useNavigate();
  const { establecerUsuario } = useSesion();
  const [carga, setCarga] = useState({ estado: "cargando" });
  const [intento, setIntento] = useState(0);
  const [contrasena, setContrasena] = useState("");
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    let vigente = true;
    validarEnlaceRecuperacion(uid, token)
      .then(({ email }) => {
        if (vigente) setCarga({ estado: "listo", email });
      })
      .catch((error) => {
        if (!vigente) return;
        setCarga(
          esEnlaceInvalido(error)
            ? { estado: "invalido" }
            : { estado: "error", detalle: error.detalle },
        );
      });
    return () => {
      vigente = false;
    };
  }, [uid, token, intento]);

  function manejarReintento() {
    setCarga({ estado: "cargando" });
    setIntento((anterior) => anterior + 1);
  }

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setErrorGeneral("");
    const erroresLocales = validarCamposRequeridos({ contrasena });
    setErrores(erroresLocales);
    if (Object.keys(erroresLocales).length > 0) return;

    setEnviando(true);
    try {
      const usuario = await confirmarRecuperacion({ uid, token, contrasena });
      establecerUsuario(usuario);
      navigate(rutaInicial(usuario), { replace: true });
    } catch (error) {
      setEnviando(false);
      if (esEnlaceInvalido(error)) {
        setCarga({ estado: "invalido" });
        return;
      }
      setErrores(error.errores ?? {});
      setErrorGeneral(error.detalle ?? "");
    }
  }

  let contenido;
  if (carga.estado === "invalido") {
    contenido = (
      <>
        <div className={estilos.encabezado}>
          <h1>El enlace no es válido</h1>
          <p className={estilos.texto}>
            Puede que ya lo hayas usado. Pedí uno nuevo.
          </p>
        </div>
        <Boton a="/recuperar" anchoCompleto>
          Pedir un nuevo enlace
        </Boton>
      </>
    );
  } else if (carga.estado === "error") {
    contenido = (
      <>
        <EncabezadoPaso paso={3} titulo="Nueva contraseña" />
        <ErrorFormulario>{carga.detalle}</ErrorFormulario>
        <Boton variante="secundario" onClick={manejarReintento} anchoCompleto>
          Reintentar
        </Boton>
      </>
    );
  } else {
    contenido = (
      <>
        <EncabezadoPaso paso={3} titulo="Nueva contraseña">
          {carga.estado === "listo" && (
            <>
              Cuenta: <strong>{carga.email}</strong>
            </>
          )}
        </EncabezadoPaso>
        {errorGeneral && <ErrorFormulario>{errorGeneral}</ErrorFormulario>}
        {carga.estado === "listo" && (
          <form
            className={estilos.formulario}
            onSubmit={manejarEnvio}
            noValidate
          >
            <Campo
              id="contrasena"
              etiqueta="Nueva contraseña"
              tipo="password"
              valor={contrasena}
              onCambiar={setContrasena}
              error={errores.contrasena?.join(" ")}
              ayuda={AYUDA_CONTRASENA}
              autoComplete="new-password"
              maxLength={64}
              requerido
            />
            <Boton tipo="submit" deshabilitado={enviando} anchoCompleto>
              Guardar e iniciar sesión
            </Boton>
          </form>
        )}
      </>
    );
  }

  return (
    <PanelAcceso
      titulo="Recuperá tu acceso."
      texto="Definí una nueva contraseña y volvé a ingresar."
    >
      {contenido}
    </PanelAcceso>
  );
}

export default RecuperacionNueva;
