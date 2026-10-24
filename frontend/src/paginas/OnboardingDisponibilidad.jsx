import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { obtenerUsuarioActual } from "../api/auth.js";
import { actualizarPerfil, obtenerPerfil } from "../api/perfil.js";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import Boton from "../componentes/Boton.jsx";
import CamposFranjas from "../componentes/CamposFranjas.jsx";
import CamposPreferencias from "../componentes/CamposPreferencias.jsx";
import ErrorFormulario from "../componentes/ErrorFormulario.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import Interruptor from "../componentes/Interruptor.jsx";
import ProgresoOnboarding from "../componentes/ProgresoOnboarding.jsx";
import Tarjeta from "../componentes/Tarjeta.jsx";
import { useCargarDatos } from "../hooks/useCargarDatos.js";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import {
  clavesEnviadas,
  disponibilidadDeFormulario,
  erroresDeDisponibilidad,
  formularioDisponibilidad,
  validarDisponibilidad,
} from "../utilidades/disponibilidad.js";
import estilos from "./OnboardingDisponibilidad.module.css";

function OnboardingDisponibilidad() {
  useTituloPagina("Disponibilidad y preferencias");
  const navigate = useNavigate();
  const { establecerUsuario } = useSesion();
  const carga = useCargarDatos(obtenerPerfil);
  // null mientras el jugador no tocó nada: se usan los valores que llegaron de la API.
  const [cambios, setCambios] = useState(null);
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [enviando, setEnviando] = useState(false);

  // Memorizado: cada llamada da claves nuevas a las franjas, que tienen que seguir estables.
  const guardados = useMemo(
    () =>
      carga.datos
        ? formularioDisponibilidad(carga.datos.disponibilidad, {
            conFilaVacia: true,
          })
        : null,
    [carga.datos],
  );
  const valores = cambios ?? guardados;

  function manejarCambio(campo, valor) {
    setCambios((anteriores) => ({
      ...(anteriores ?? guardados),
      [campo]: valor,
    }));
  }

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setErrorGeneral("");
    const erroresLocales = validarDisponibilidad(valores);
    setErrores(erroresLocales);
    if (Object.keys(erroresLocales).length > 0) return;

    const claves = clavesEnviadas(valores);
    setEnviando(true);
    try {
      await actualizarPerfil({
        disponibilidad: disponibilidadDeFormulario(valores),
      });
      // La sesión tiene que saber que el onboarding ya está completo.
      establecerUsuario(await obtenerUsuarioActual());
      navigate("/inicio", {
        state: {
          aviso: "Disponibilidad y preferencias guardadas correctamente.",
        },
      });
    } catch (error) {
      setErrores(
        erroresDeDisponibilidad(error.errores?.disponibilidad, claves),
      );
      setErrorGeneral(error.detalle ?? "");
      setEnviando(false);
    }
  }

  return (
    <>
      <BarraSuperior soloLogo />
      <main className={estilos.pagina}>
        <ProgresoOnboarding paso={2} nombre="Disponibilidad y preferencias" />
        <div className={estilos.encabezado}>
          <h1>¿Cuándo y cómo te gusta jugar?</h1>
          <p className={estilos.texto}>
            El sistema usa tus franjas y preferencias para determinar si sos
            compatible con un encuentro.
          </p>
        </div>

        {valores ? (
          <form
            className={estilos.formulario}
            onSubmit={manejarEnvio}
            noValidate
          >
            {errorGeneral && <ErrorFormulario>{errorGeneral}</ErrorFormulario>}
            <Tarjeta titulo="Disponibilidad horaria">
              <CamposFranjas
                franjas={valores.franjas}
                errores={errores.franjas}
                onCambiar={(franjas) => manejarCambio("franjas", franjas)}
              />
            </Tarjeta>
            <Tarjeta>
              <CamposPreferencias
                valores={valores}
                errores={errores}
                onCambiar={manejarCambio}
              />
            </Tarjeta>
            <Tarjeta>
              <Interruptor
                id="disponible_para_invitaciones"
                titulo="Disponible para recibir invitaciones"
                texto="Permite que el sistema te recomiende a otros organizadores. No te suma a ningún encuentro: solo participás si aceptás una invitación."
                marcado={valores.disponible_para_invitaciones}
                onCambiar={(valor) =>
                  manejarCambio("disponible_para_invitaciones", valor)
                }
                error={errores.disponible_para_invitaciones?.join(" ")}
              />
            </Tarjeta>
            <div className={estilos.acciones}>
              <Boton variante="secundario" a="/onboarding/perfil">
                Volver
              </Boton>
              <Boton tipo="submit" deshabilitado={enviando}>
                Guardar
              </Boton>
            </div>
          </form>
        ) : (
          <EstadoCarga error={carga.error} onReintentar={carga.reintentar} />
        )}
      </main>
    </>
  );
}

export default OnboardingDisponibilidad;
