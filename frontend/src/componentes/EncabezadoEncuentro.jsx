import { CalendarDays, Clock, MapPin, Timer, Trophy } from "lucide-react";
import {
  ESTADOS_ENCUENTRO,
  etiquetaTipoEncuentro,
} from "../utilidades/encuentros.js";
import { formatearFechaCompacta } from "../utilidades/formato.js";
import Casilleros from "./Casilleros.jsx";
import estilos from "./EncabezadoEncuentro.module.css";
import Etiqueta from "./Etiqueta.jsx";

const ESTADOS_COMPLETOS = ["COMPLETO", "PROPUESTA_GENERADA"];

// Barra con las condiciones del encuentro (pantallas 10, 12 y 14) y sus lugares confirmados.
function EncabezadoEncuentro({ encuentro }) {
  const estado = ESTADOS_ENCUENTRO[encuentro.estado];
  const datos = [
    {
      clave: "fecha",
      icono: CalendarDays,
      texto: formatearFechaCompacta(encuentro.fecha),
    },
    { clave: "hora", icono: Clock, texto: encuentro.hora_inicio },
    {
      clave: "duracion",
      icono: Timer,
      texto: `${encuentro.duracion_minutos} min`,
    },
    {
      clave: "lugar",
      icono: MapPin,
      texto: `${encuentro.localidad.nombre} · ${encuentro.ubicacion}`,
    },
    {
      clave: "tipo",
      icono: Trophy,
      texto: etiquetaTipoEncuentro(encuentro.tipo_encuentro),
    },
  ];

  return (
    <div className={estilos.barra}>
      <Etiqueta color={estado.color}>{estado.etiqueta}</Etiqueta>
      <ul className={estilos.datos}>
        {datos.map(({ clave, icono: Icono, texto }) => (
          <li key={clave} className={estilos.dato}>
            <Icono size={18} strokeWidth={2} aria-hidden="true" />
            {texto}
          </li>
        ))}
      </ul>
      <Casilleros
        confirmados={encuentro.confirmados}
        completo={ESTADOS_COMPLETOS.includes(encuentro.estado)}
      />
    </div>
  );
}

export default EncabezadoEncuentro;
