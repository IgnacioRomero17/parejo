import {
  LADOS_PREFERIDOS,
  TIPOS_ENCUENTRO,
} from "../utilidades/disponibilidad.js";
import estilos from "./CamposPreferencias.module.css";
import SelectorSegmentado from "./SelectorSegmentado.jsx";

// Tipo de encuentro y lado preferido (pantallas 07b y 17), uno debajo del otro y a todo el
// ancho. `valores` y `errores` usan los nombres de la API; `onCambiar(campo, valor)` avisa
// cada cambio.
function CamposPreferencias({ valores, errores, onCambiar }) {
  function errorDe(campo) {
    return errores?.[campo]?.join(" ");
  }

  return (
    <div className={estilos.preferencias}>
      <SelectorSegmentado
        id="tipo_encuentro"
        leyenda="Tipo de encuentro"
        opciones={TIPOS_ENCUENTRO}
        valor={valores.tipo_encuentro}
        onCambiar={(valor) => onCambiar("tipo_encuentro", valor)}
        error={errorDe("tipo_encuentro")}
      />
      <SelectorSegmentado
        id="lado_preferido"
        leyenda="Lado preferido"
        opciones={LADOS_PREFERIDOS}
        valor={valores.lado_preferido}
        onCambiar={(valor) => onCambiar("lado_preferido", valor)}
        error={errorDe("lado_preferido")}
      />
    </div>
  );
}

export default CamposPreferencias;
