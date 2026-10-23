import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { obtenerUsuarioActual } from "../api/auth.js";
import { listarLocalidades } from "../api/localidades.js";
import { actualizarPerfil, obtenerPerfil } from "../api/perfil.js";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import Boton from "../componentes/Boton.jsx";
import CamposPerfilDeportivo from "../componentes/CamposPerfilDeportivo.jsx";
import ErrorFormulario from "../componentes/ErrorFormulario.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import ProgresoOnboarding from "../componentes/ProgresoOnboarding.jsx";
import Tarjeta from "../componentes/Tarjeta.jsx";
import { useCargarDatos } from "../hooks/useCargarDatos.js";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import {
  formularioPerfilDeportivo,
  perfilDeportivoDeFormulario,
  textoCamposPendientes,
} from "../utilidades/perfil.js";
import { validarCamposRequeridos } from "../utilidades/validaciones.js";
import estilos from "./OnboardingPerfil.module.css";

function cargarDatos() {
  return Promise.all([obtenerPerfil(), listarLocalidades()]);
}

function OnboardingPerfil() {
  useTituloPagina("Perfil deportivo");
  const navigate = useNavigate();
  const { establecerUsuario } = useSesion();
  const carga = useCargarDatos(cargarDatos);
  // null mientras el jugador no tocó nada: se usan los valores que llegaron de la API.
  const [cambios, setCambios] = useState(null);
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [enviando, setEnviando] = useState(false);

  const [perfil, localidades] = carga.datos ?? [];
  const valores =
    cambios ??
    (perfil ? formularioPerfilDeportivo(perfil.perfil_deportivo) : null);
  const pendientes = valores
    ? Object.keys(validarCamposRequeridos(valores)).length
    : 0;

  function manejarCambio(campo, valor) {
    setCambios((anteriores) => ({
      ...(anteriores ?? valores),
      [campo]: valor,
    }));
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
      await actualizarPerfil({
        perfil_deportivo: perfilDeportivoDeFormulario(valores),
      });
      // La sesión tiene que saber que este paso ya no está pendiente.
      establecerUsuario(await obtenerUsuarioActual());
      navigate("/onboarding/disponibilidad");
    } catch (error) {
      setErrores(error.errores?.perfil_deportivo ?? {});
      setErrorGeneral(error.detalle ?? "");
      setEnviando(false);
    }
  }

  return (
    <>
      <BarraSuperior soloLogo />
      <main className={estilos.pagina}>
        <ProgresoOnboarding paso={1} nombre="Perfil deportivo" />
        <div className={estilos.encabezado}>
          <h1>Configurá tu perfil deportivo</h1>
          <p className={estilos.texto}>
            Tu nivel y tu localidad se usan para recomendarte a otros
            organizadores y para formar parejas equilibradas.
          </p>
        </div>

        {valores ? (
          <Tarjeta>
            {errorGeneral && <ErrorFormulario>{errorGeneral}</ErrorFormulario>}
            <form
              className={estilos.formulario}
              onSubmit={manejarEnvio}
              noValidate
            >
              <CamposPerfilDeportivo
                valores={valores}
                errores={errores}
                localidades={localidades}
                onCambiar={manejarCambio}
              />
              <div className={estilos.pie}>
                <p className={estilos.pendientes} aria-live="polite">
                  {pendientes > 0 && textoCamposPendientes(pendientes)}
                </p>
                <Boton tipo="submit" deshabilitado={enviando}>
                  Guardar y continuar
                </Boton>
              </div>
            </form>
          </Tarjeta>
        ) : (
          <EstadoCarga error={carga.error} onReintentar={carga.reintentar} />
        )}
      </main>
    </>
  );
}

export default OnboardingPerfil;
