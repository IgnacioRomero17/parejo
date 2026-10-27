import { useEffect, useRef, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { formarParejas, obtenerEncuentro } from "../api/encuentros.js";
import BarraSuperior from "../componentes/BarraSuperior.jsx";
import Boton from "../componentes/Boton.jsx";
import CanchaFormando from "../componentes/CanchaFormando.jsx";
import ErrorFormulario from "../componentes/ErrorFormulario.jsx";
import EstadoCarga from "../componentes/EstadoCarga.jsx";
import PasosFormacion from "../componentes/PasosFormacion.jsx";
import { useSesion } from "../hooks/useSesion.js";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import { PASOS_FORMACION } from "../utilidades/encuentros.js";
import estilos from "./FormandoParejas.module.css";

// Cada paso de la animación dura 1,3 s: la pantalla se ve al menos 3,9 s aunque el backend
// responda antes, para que se pueda leer cada paso. Si el backend tarda más, se espera solo
// la respuesta.
const DURACION_PASO_MS = 1300;

// Pide el encuentro y, si el usuario lo organiza y todavía no tiene propuesta, forma las
// parejas. El backend vuelve a verificar todo.
function iniciarFormacion(id) {
  const carga = obtenerEncuentro(id);
  const formacion = carga.then((encuentro) =>
    encuentro.invitaciones && encuentro.estado !== "PROPUESTA_GENERADA"
      ? formarParejas(id)
      : null,
  );
  return { carga, formacion };
}

// Pantalla 15, solo para el organizador: dispara la formación de parejas y abre la propuesta.
function FormandoParejas() {
  useTituloPagina("Generando una propuesta equilibrada");
  const { id } = useParams();
  const { usuario } = useSesion();
  const [intento, setIntento] = useState(0);
  const [encuentro, setEncuentro] = useState(null);
  const [errorCarga, setErrorCarga] = useState(null);
  const [formadas, setFormadas] = useState(false);
  const [fallo, setFallo] = useState(false);
  const [pasosCumplidos, setPasosCumplidos] = useState(0);
  const pedido = useRef(null);

  // En desarrollo, StrictMode ejecuta los efectos dos veces: el pedido se guarda por intento
  // para llamar al backend una sola vez.
  useEffect(() => {
    const clave = `${id}:${intento}`;
    if (pedido.current?.clave !== clave) {
      pedido.current = { clave, ...iniciarFormacion(id) };
    }
    const { carga, formacion } = pedido.current;
    let vigente = true;
    carga.then(
      (datos) => {
        if (vigente) setEncuentro(datos);
      },
      (error) => {
        if (vigente) setErrorCarga(error);
      },
    );
    formacion.then(
      () => {
        if (vigente) setFormadas(true);
      },
      () => {
        if (vigente) setFallo(true);
      },
    );
    return () => {
      vigente = false;
    };
  }, [id, intento]);

  // Los pasos avanzan desde que se ven, no mientras se carga el encuentro.
  const pasosVisibles = encuentro !== null;
  useEffect(() => {
    if (!pasosVisibles || fallo || pasosCumplidos >= PASOS_FORMACION.length) {
      return undefined;
    }
    const temporizador = setTimeout(
      () => setPasosCumplidos((anterior) => anterior + 1),
      DURACION_PASO_MS,
    );
    return () => clearTimeout(temporizador);
  }, [pasosVisibles, fallo, pasosCumplidos]);

  function manejarReintento() {
    setEncuentro(null);
    setErrorCarga(null);
    setFallo(false);
    setFormadas(false);
    setPasosCumplidos(0);
    setIntento((anterior) => anterior + 1);
  }

  function contenido() {
    if (errorCarga) {
      return <EstadoCarga error={errorCarga} onReintentar={manejarReintento} />;
    }
    if (!encuentro) return <EstadoCarga />;
    if (!encuentro.invitaciones) return <Navigate to="/inicio" replace />;
    const propuesta = `/encuentros/${id}/propuesta`;
    const animacionTerminada = pasosCumplidos >= PASOS_FORMACION.length;
    if (
      encuentro.estado === "PROPUESTA_GENERADA" ||
      (formadas && animacionTerminada)
    ) {
      return <Navigate to={propuesta} replace />;
    }
    const organizador = encuentro.participantes.find(
      (participante) => participante.id === usuario.id,
    );
    const nombres = encuentro.participantes
      .map((participante) => `${participante.nombre} ${participante.apellido}`)
      .join(" · ");
    return (
      <div className={estilos.tarjeta}>
        <div className={estilos.titulo}>
          <p className={estilos.rotulo}>Procesamiento automático</p>
          <h1>Generando una propuesta equilibrada</h1>
          <p className={estilos.nombres}>{nombres}</p>
        </div>
        <CanchaFormando organizador={organizador} />
        {fallo ? (
          <div className={estilos.error}>
            <ErrorFormulario>
              No pudimos generar la propuesta. Intentá de nuevo.
            </ErrorFormulario>
            <div className={estilos.acciones}>
              <Boton onClick={manejarReintento}>Reintentar</Boton>
              <Link to={`/encuentros/${id}`} className={estilos.enlace}>
                Volver al encuentro
              </Link>
            </div>
          </div>
        ) : (
          <>
            <PasosFormacion
              enCurso={Math.min(pasosCumplidos, PASOS_FORMACION.length - 1)}
            />
            <p className={estilos.pie}>
              La propuesta se abrirá automáticamente al terminar.
            </p>
          </>
        )}
      </div>
    );
  }

  return (
    <>
      <BarraSuperior />
      <main className={estilos.pagina}>{contenido()}</main>
    </>
  );
}

export default FormandoParejas;
