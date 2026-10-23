import { FRECUENCIAS_JUEGO, GENEROS } from "../utilidades/perfil.js";
import Campo from "./Campo.jsx";
import estilos from "./CamposPerfilDeportivo.module.css";
import Desplegable from "./Desplegable.jsx";
import SelectorNivel from "./SelectorNivel.jsx";

// Campos del perfil deportivo (pantallas 07a y 17). `valores` y `errores` usan los nombres
// de la API; `onCambiar(campo, valor)` avisa cada cambio.
function CamposPerfilDeportivo({ valores, errores, localidades, onCambiar }) {
  const opcionesLocalidad = localidades.map((localidad) => ({
    valor: String(localidad.id),
    etiqueta: localidad.nombre,
  }));

  function errorDe(campo) {
    return errores?.[campo]?.join(" ");
  }

  return (
    <div className={estilos.campos}>
      <div className={estilos.grilla}>
        <Campo
          id="edad"
          etiqueta="Edad"
          tipo="number"
          valor={valores.edad}
          onCambiar={(valor) => onCambiar("edad", valor)}
          error={errorDe("edad")}
          min={18}
          max={99}
          inputMode="numeric"
          requerido
        />
        <Desplegable
          id="genero"
          etiqueta="Género"
          valor={valores.genero}
          opciones={GENEROS}
          onCambiar={(valor) => onCambiar("genero", valor)}
          error={errorDe("genero")}
          requerido
        />
        <Desplegable
          id="localidad"
          etiqueta="Localidad"
          valor={valores.localidad}
          opciones={opcionesLocalidad}
          onCambiar={(valor) => onCambiar("localidad", valor)}
          error={errorDe("localidad")}
          ayuda="Elegila del listado. Si la tuya no figura, elegí la más cercana."
          requerido
        />
        <Desplegable
          id="frecuencia"
          etiqueta="Frecuencia de juego"
          valor={valores.frecuencia_juego}
          opciones={FRECUENCIAS_JUEGO}
          onCambiar={(valor) => onCambiar("frecuencia_juego", valor)}
          error={errorDe("frecuencia_juego")}
          requerido
        />
      </div>
      <SelectorNivel
        id="nivel"
        valor={valores.nivel_estimado}
        onCambiar={(valor) => onCambiar("nivel_estimado", valor)}
        error={errorDe("nivel_estimado")}
      />
    </div>
  );
}

export default CamposPerfilDeportivo;
