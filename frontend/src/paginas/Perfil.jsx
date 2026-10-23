import { startTransition, useCallback, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  obtenerUsuarioActual,
  salir,
  solicitarRecuperacion,
} from "../api/auth.js";
import { listarLocalidades } from "../api/localidades.js";
import { actualizarPerfil, obtenerPerfil } from "../api/perfil.js";
import Aviso from "../componentes/Aviso.jsx";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import EncabezadoPerfil from "../componentes/EncabezadoPerfil.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import FormularioPerfil from "../componentes/FormularioPerfil.jsx";
import { useCargarDatos } from "../hooks/useCargarDatos.js";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import {
  cuerpoActualizacion,
  formularioPerfil,
  seccionesModificadas,
} from "../utilidades/perfil.js";
import { validarCamposRequeridos } from "../utilidades/validaciones.js";
import estilos from "./Perfil.module.css";

function cargarDatos() {
  return Promise.all([obtenerPerfil(), listarLocalidades()]);
}

function Perfil() {
  useTituloPagina("Mi perfil");
  const navigate = useNavigate();
  const { establecerUsuario } = useSesion();
  const carga = useCargarDatos(cargarDatos);
  const [perfilGuardado, setPerfilGuardado] = useState(null);
  // null mientras no hay cambios sin guardar.
  const [cambios, setCambios] = useState(null);
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [aviso, setAviso] = useState("");
  const cerrarAviso = useCallback(() => setAviso(""), []);

  const [perfilCargado, localidades] = carga.datos ?? [];
  const perfil = perfilGuardado ?? perfilCargado;
  const guardados = perfil ? formularioPerfil(perfil) : null;
  const valores = cambios ?? guardados;
  const modificadas = valores ? seccionesModificadas(valores, guardados) : [];

  function manejarCambio(seccion) {
    return (campo, valor) =>
      setCambios((anteriores) => {
        const base = anteriores ?? guardados;
        return { ...base, [seccion]: { ...base[seccion], [campo]: valor } };
      });
  }

  function manejarDescarte() {
    setCambios(null);
    setErrores({});
    setErrorGeneral("");
  }

  async function manejarGuardado(evento) {
    evento.preventDefault();
    setErrorGeneral("");
    const erroresLocales = {};
    for (const seccion of modificadas) {
      const erroresSeccion = validarCamposRequeridos(valores[seccion]);
      if (Object.keys(erroresSeccion).length > 0) {
        erroresLocales[seccion] = erroresSeccion;
      }
    }
    setErrores(erroresLocales);
    if (modificadas.length === 0 || Object.keys(erroresLocales).length > 0) {
      return;
    }

    setEnviando(true);
    try {
      setPerfilGuardado(
        await actualizarPerfil(cuerpoActualizacion(valores, modificadas)),
      );
      setCambios(null);
      setAviso("Cambios guardados correctamente.");
      // Los cambios ya se guardaron: si falla, la sesión se actualiza al recargar.
      obtenerUsuarioActual().then(establecerUsuario, () => {});
    } catch (error) {
      setErrores(error.errores ?? {});
      setErrorGeneral(error.detalle ?? "");
    } finally {
      setEnviando(false);
    }
  }

  async function manejarCambioContrasena() {
    const email = perfil.datos_personales.email;
    setErrorGeneral("");
    try {
      await solicitarRecuperacion({ email });
      navigate("/recuperar/enviado", { state: { email } });
    } catch (error) {
      setErrorGeneral(error.detalle);
    }
  }

  async function manejarCierreSesion() {
    try {
      await salir();
    } catch (error) {
      setErrorGeneral(error.detalle);
      return;
    }
    navigate("/");
    // En la misma transición que la navegación: si la sesión se limpiara antes,
    // RutaPrivada mandaría a /ingresar en lugar de a la bienvenida.
    startTransition(() => establecerUsuario(null));
  }

  return (
    <>
      <BarraSuperior />
      {aviso && <Aviso mensaje={aviso} onCerrar={cerrarAviso} />}
      <main className={estilos.pagina}>
        <div className={estilos.encabezado}>
          <div className={estilos.titulo}>
            <h1>Mi perfil</h1>
            <p className={estilos.texto}>
              Actualizá tus datos cuando quieras. Los cambios se usan en las
              próximas recomendaciones.
            </p>
          </div>
          {perfil && (
            <EncabezadoPerfil
              nombre={perfil.datos_personales.nombre}
              apellido={perfil.datos_personales.apellido}
              email={perfil.datos_personales.email}
              disponible={perfil.disponibilidad.disponible_para_invitaciones}
            />
          )}
        </div>

        {valores ? (
          <FormularioPerfil
            valores={valores}
            errores={errores}
            errorGeneral={errorGeneral}
            email={perfil.datos_personales.email}
            localidades={localidades}
            hayCambios={modificadas.length > 0}
            enviando={enviando}
            onCambiar={manejarCambio}
            onGuardar={manejarGuardado}
            onDescartar={manejarDescarte}
            onCambiarContrasena={manejarCambioContrasena}
            onCerrarSesion={manejarCierreSesion}
          />
        ) : (
          <EstadoCarga error={carga.error} onReintentar={carga.reintentar} />
        )}
      </main>
    </>
  );
}

export default Perfil;
