import { segunGenero } from "../utilidades/perfil.js";
import CamposFranjas from "./CamposFranjas.jsx";
import CamposPreferencias from "./CamposPreferencias.jsx";
import Interruptor from "./Interruptor.jsx";
import Tarjeta from "./Tarjeta.jsx";
import estilos from "./TarjetaDisponibilidad.module.css";

// Sección "Disponibilidad y preferencias" de la pantalla 17: franjas, preferencias e
// interruptor, con los mismos campos que el paso 2 del onboarding (07b). `genero` es el
// guardado en el perfil, para el texto que se refiere al jugador.
function TarjetaDisponibilidad({ valores, errores, genero, onCambiar }) {
  return (
    <Tarjeta
      titulo="Disponibilidad y preferencias"
      texto={`Define en qué encuentros aparecés como ${segunGenero(genero, "jugadora", "jugador")} compatible.`}
    >
      <CamposFranjas
        franjas={valores.franjas}
        errores={errores?.franjas}
        onCambiar={(franjas) => onCambiar("franjas", franjas)}
      />
      <hr className={estilos.division} />
      <CamposPreferencias
        valores={valores}
        errores={errores}
        onCambiar={onCambiar}
      />
      <hr className={estilos.division} />
      <Interruptor
        id="disponible_para_invitaciones"
        titulo="Disponible para recibir invitaciones"
        texto="Si lo desactivás, el sistema deja de recomendarte a otros organizadores."
        marcado={valores.disponible_para_invitaciones}
        onCambiar={(valor) => onCambiar("disponible_para_invitaciones", valor)}
        error={errores?.disponible_para_invitaciones?.join(" ")}
      />
    </Tarjeta>
  );
}

export default TarjetaDisponibilidad;
