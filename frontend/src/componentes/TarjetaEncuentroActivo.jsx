import { MapPin, Timer, User } from "lucide-react";
import { useId } from "react";
import {
  ESTADOS_COMPLETOS,
  ESTADOS_ENCUENTRO,
  etiquetaTipoEncuentro,
  textoEsperandoFormacion,
  textoInvitacionesPendientes,
} from "../utilidades/encuentros.js";
import { formatearFechaTitulo } from "../utilidades/formato.js";
import Boton from "./Boton.jsx";
import Casilleros from "./Casilleros.jsx";
import Etiqueta from "./Etiqueta.jsx";
import estilos from "./TarjetaEncuentroActivo.module.css";

// Texto y acción de la tarjeta según el estado y el rol, como en la tabla de
// docs/interfaces/08-panel-principal.md.
function situacion(encuentro) {
  const seguimiento = `/encuentros/${encuentro.id}`;
  if (encuentro.estado === "PROPUESTA_GENERADA") {
    return {
      texto: "Parejas formadas.",
      accion: { texto: "Ver propuesta", a: `${seguimiento}/propuesta` },
    };
  }
  if (encuentro.estado === "COMPLETO") {
    return encuentro.organizas
      ? {
          texto: "Listo para formar parejas.",
          accion: { texto: "Formar parejas", a: seguimiento },
        }
      : { texto: textoEsperandoFormacion(encuentro.organizador.genero) };
  }
  if (!encuentro.organizas) return { texto: "confirmados" };
  const pendientes = encuentro.invitaciones_pendientes;
  return {
    texto:
      pendientes > 0
        ? `confirmados · ${textoInvitacionesPendientes(pendientes)}`
        : "confirmados",
    accion: { texto: "Ver seguimiento", a: seguimiento },
  };
}

// Un encuentro de "Tus encuentros activos" en el panel principal (pantalla 08).
function TarjetaEncuentroActivo({ encuentro }) {
  const idTitulo = useId();
  const estado = ESTADOS_ENCUENTRO[encuentro.estado];
  const { organizador } = encuentro;
  const { texto, accion } = situacion(encuentro);
  const datos = [
    {
      clave: "duracion",
      icono: Timer,
      texto: `${encuentro.duracion_minutos} minutos`,
    },
    {
      clave: "lugar",
      icono: MapPin,
      texto: `${encuentro.localidad.nombre} · ${encuentro.ubicacion}`,
    },
  ];
  if (!encuentro.organizas) {
    datos.push({
      clave: "organizador",
      icono: User,
      texto: `Organiza ${organizador.nombre} ${organizador.apellido}`,
    });
  }

  return (
    <li className={estilos.tarjeta}>
      <article aria-labelledby={idTitulo} className={estilos.contenido}>
        <div className={estilos.etiquetas}>
          <Etiqueta color={estado.color}>{estado.etiqueta}</Etiqueta>
          <Etiqueta>
            {encuentro.organizas ? "Organizás vos" : "Te invitaron"}
          </Etiqueta>
          <Etiqueta>{etiquetaTipoEncuentro(encuentro.tipo_encuentro)}</Etiqueta>
        </div>
        <div className={estilos.cabecera}>
          <h3 id={idTitulo} className={estilos.titulo}>
            {formatearFechaTitulo(encuentro.fecha)} · {encuentro.hora_inicio}
          </h3>
          <ul className={estilos.datos}>
            {datos.map(({ clave, icono: Icono, texto: dato }) => (
              <li key={clave} className={estilos.dato}>
                <Icono size={16} strokeWidth={2} aria-hidden="true" />
                {dato}
              </li>
            ))}
          </ul>
        </div>
        <div className={estilos.pie}>
          <Casilleros
            confirmados={encuentro.confirmados}
            completo={ESTADOS_COMPLETOS.includes(encuentro.estado)}
            conFaltan={false}
          />
          <p className={estilos.estado}>{texto}</p>
          {accion && (
            <Boton variante="secundario" a={accion.a}>
              {accion.texto}
            </Boton>
          )}
        </div>
      </article>
    </li>
  );
}

export default TarjetaEncuentroActivo;
