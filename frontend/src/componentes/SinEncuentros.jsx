import { CalendarPlus } from "lucide-react";
import Boton from "./Boton.jsx";
import estilos from "./SinEncuentros.module.css";

// Estado vacío de "Tus encuentros activos" en el panel principal (pantalla 08), con el mismo
// estilo que la pantalla 11.
function SinEncuentros() {
  return (
    <div className={estilos.tarjeta}>
      <span className={estilos.icono}>
        <CalendarPlus size={28} strokeWidth={2} aria-hidden="true" />
      </span>
      <h3 className={estilos.titulo}>Todavía no tenés encuentros</h3>
      <p className={estilos.texto}>
        Creá un encuentro o aceptá una invitación para verlo acá.
      </p>
      <Boton a="/encuentros/nuevo">Crear tu primer encuentro</Boton>
    </div>
  );
}

export default SinEncuentros;
