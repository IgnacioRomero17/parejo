import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { crearEncuentro } from "../api/encuentros.js";
import { listarLocalidades } from "../api/localidades.js";
import { obtenerPerfil } from "../api/perfil.js";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import Boton from "../componentes/Boton.jsx";
import CamposEncuentro from "../componentes/CamposEncuentro.jsx";
import ErrorFormulario from "../componentes/ErrorFormulario.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import Tarjeta from "../componentes/Tarjeta.jsx";
import TarjetaLugares from "../componentes/TarjetaLugares.jsx";
import { useCargarDatos } from "../hooks/useCargarDatos.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import {
  encuentroDeFormulario,
  fechaMaximaEncuentro,
  formularioEncuentro,
  hoyEnCordoba,
  validarEncuentro,
} from "../utilidades/encuentros.js";
import estilos from "./CrearEncuentro.module.css";

function cargarDatos() {
  return Promise.all([obtenerPerfil(), listarLocalidades()]);
}

// Pantalla 09 (HU-006).
function CrearEncuentro() {
  useTituloPagina("Crear encuentro");
  const navigate = useNavigate();
  const carga = useCargarDatos(cargarDatos);
  // null mientras el jugador no tocó nada: se usan los valores iniciales.
  const [cambios, setCambios] = useState(null);
  const [errores, setErrores] = useState({});
  const [errorGeneral, setErrorGeneral] = useState("");
  const [enviando, setEnviando] = useState(false);

  const [perfil, localidades] = carga.datos ?? [];
  const valores =
    cambios ?? (perfil ? formularioEncuentro(perfil.perfil_deportivo) : null);

  function manejarCambio(campo, valor) {
    setCambios((anteriores) => ({
      ...(anteriores ?? valores),
      [campo]: valor,
    }));
  }

  async function manejarEnvio(evento) {
    evento.preventDefault();
    setErrorGeneral("");
    const erroresLocales = validarEncuentro(valores);
    setErrores(erroresLocales);
    if (Object.keys(erroresLocales).length > 0) return;

    setEnviando(true);
    try {
      const encuentro = await crearEncuentro(encuentroDeFormulario(valores));
      navigate(`/encuentros/${encuentro.id}/recomendados`, {
        state: { aviso: "Encuentro creado correctamente." },
      });
    } catch (error) {
      setErrores(error.errores ?? {});
      setErrorGeneral(error.detalle ?? "");
      setEnviando(false);
    }
  }

  return (
    <>
      <BarraSuperior />
      <main className={estilos.pagina}>
        <div className={estilos.encabezado}>
          <h1>Crear encuentro</h1>
          <p className={estilos.texto}>
            Definí las condiciones. Con ellas el sistema buscará jugadores
            compatibles.
          </p>
        </div>

        {valores ? (
          <div className={estilos.columnas}>
            <Tarjeta>
              {errorGeneral && (
                <ErrorFormulario>{errorGeneral}</ErrorFormulario>
              )}
              <form
                className={estilos.formulario}
                onSubmit={manejarEnvio}
                noValidate
              >
                <CamposEncuentro
                  valores={valores}
                  errores={errores}
                  localidades={localidades}
                  fechaMinima={hoyEnCordoba()}
                  fechaMaxima={fechaMaximaEncuentro()}
                  onCambiar={manejarCambio}
                />
                <div className={estilos.acciones}>
                  <Boton variante="secundario" a="/inicio">
                    Cancelar
                  </Boton>
                  <Boton tipo="submit" deshabilitado={enviando}>
                    Crear encuentro y buscar jugadores
                  </Boton>
                </div>
              </form>
            </Tarjeta>
            <TarjetaLugares
              nombre={perfil.datos_personales.nombre}
              apellido={perfil.datos_personales.apellido}
              genero={perfil.perfil_deportivo.genero}
            />
          </div>
        ) : (
          <EstadoCarga error={carga.error} onReintentar={carga.reintentar} />
        )}
      </main>
    </>
  );
}

export default CrearEncuentro;
