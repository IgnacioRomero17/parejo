import Logo from "./Logo.jsx";
import estilos from "./PanelAcceso.module.css";

function IlustracionCancha() {
  return (
    <svg
      className={estilos.cancha}
      viewBox="0 0 410 272"
      width="410"
      height="272"
      aria-hidden="true"
      focusable="false"
    >
      <rect className={estilos.piso} width="410" height="272" rx="16" />
      <path className={estilos.linea} d="M61 0V272M349 0V272M61 136H349" />
      <path className={estilos.red} d="M205 6V266" />
      <circle className={estilos.jugador} cx="133" cy="69" r="20" />
      <circle className={estilos.jugador} cx="277" cy="69" r="20" />
      <circle className={estilos.jugador} cx="133" cy="202" r="20" />
      <circle className={estilos.jugador} cx="277" cy="202" r="20" />
    </svg>
  );
}

// Marco de las pantallas de acceso: panel oscuro a la izquierda y formulario a la derecha.
function PanelAcceso({ titulo, texto, children }) {
  return (
    <div className={estilos.contenedor}>
      <aside className={estilos.panel}>
        <Logo />
        <div className={estilos.presentacion}>
          <IlustracionCancha />
          <p className={estilos.titulo}>{titulo}</p>
          <p className={estilos.texto}>{texto}</p>
        </div>
      </aside>
      <main className={estilos.principal}>
        <div className={estilos.formulario}>{children}</div>
      </main>
    </div>
  );
}

export default PanelAcceso;
