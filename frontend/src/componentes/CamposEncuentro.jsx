import { TIPOS_ENCUENTRO } from "../utilidades/disponibilidad.js";
import { DURACIONES, HORAS_INICIO } from "../utilidades/encuentros.js";
import Campo from "./Campo.jsx";
import estilos from "./CamposEncuentro.module.css";
import Desplegable from "./Desplegable.jsx";
import SelectorSegmentado from "./SelectorSegmentado.jsx";

// Condiciones del encuentro (pantalla 09). `valores` y `errores` usan los nombres de la API;
// `onCambiar(campo, valor)` avisa cada cambio. `fechaMinima` y `fechaMaxima` limitan el
// calendario, en "AAAA-MM-DD".
function CamposEncuentro({
  valores,
  errores,
  localidades,
  fechaMinima,
  fechaMaxima,
  onCambiar,
}) {
  const opcionesLocalidad = localidades.map((localidad) => ({
    valor: String(localidad.id),
    etiqueta: localidad.nombre,
  }));

  function errorDe(campo) {
    return errores?.[campo]?.join(" ");
  }

  return (
    <div className={estilos.grilla}>
      <Campo
        id="fecha"
        etiqueta="Fecha"
        tipo="date"
        valor={valores.fecha}
        onCambiar={(valor) => onCambiar("fecha", valor)}
        error={errorDe("fecha")}
        min={fechaMinima}
        max={fechaMaxima}
        requerido
      />
      <Desplegable
        id="hora_inicio"
        etiqueta="Hora de inicio"
        valor={valores.hora_inicio}
        opciones={HORAS_INICIO}
        onCambiar={(valor) => onCambiar("hora_inicio", valor)}
        error={errorDe("hora_inicio")}
        requerido
      />
      <div className={estilos.anchoCompleto}>
        <Desplegable
          id="duracion_minutos"
          etiqueta="Duración"
          valor={valores.duracion_minutos}
          opciones={DURACIONES}
          onCambiar={(valor) => onCambiar("duracion_minutos", valor)}
          error={errorDe("duracion_minutos")}
          requerido
        />
      </div>
      <div className={estilos.anchoCompleto}>
        <Desplegable
          id="localidad"
          etiqueta="Localidad"
          valor={valores.localidad}
          opciones={opcionesLocalidad}
          onCambiar={(valor) => onCambiar("localidad", valor)}
          error={errorDe("localidad")}
          ayuda="Localidad donde se jugará. El sistema la usa para calcular la distancia con cada jugador."
          requerido
        />
      </div>
      {/* Las tres opciones no entran en media columna: el selector va a todo el ancho. */}
      <div className={estilos.anchoCompleto}>
        <SelectorSegmentado
          id="tipo_encuentro"
          leyenda="Tipo de encuentro"
          opciones={TIPOS_ENCUENTRO}
          valor={valores.tipo_encuentro}
          onCambiar={(valor) => onCambiar("tipo_encuentro", valor)}
          error={errorDe("tipo_encuentro")}
        />
      </div>
      <div className={estilos.anchoCompleto}>
        <Campo
          id="ubicacion"
          etiqueta="Dirección o lugar"
          valor={valores.ubicacion}
          onCambiar={(valor) => onCambiar("ubicacion", valor)}
          error={errorDe("ubicacion")}
          maxLength={150}
          ayuda="Dirección o nombre del lugar. Es solo informativo: los jugadores lo ven al recibir la invitación."
          requerido
        />
      </div>
    </div>
  );
}

export default CamposEncuentro;
