import estilos from "./CanchaFormando.module.css";

// Las otras tres posiciones todavía no tienen jugador: las decide el sistema.
const POSICIONES_LIBRES = [
  { x: 302, y: 66 },
  { x: 138, y: 164 },
  { x: 302, y: 164 },
];

// Ilustración de la pantalla 15: el organizador en la cancha, "?" en los demás lugares y un
// indicador de carga en el centro. Es decorativa: los nombres se muestran arriba.
function CanchaFormando({ organizador }) {
  const iniciales =
    `${organizador.nombre.charAt(0)}${organizador.apellido.charAt(0)}`.toUpperCase();
  return (
    <svg
      className={estilos.cancha}
      viewBox="0 0 440 230"
      aria-hidden="true"
      focusable="false"
    >
      <rect className={estilos.piso} width="440" height="230" rx="16" />
      <path className={estilos.linea} d="M69 10V220M371 10V220M69 115H371" />
      <path className={estilos.red} d="M220 10V220" />
      <circle className={estilos.organizador} cx="138" cy="66" r="26" />
      <text className={estilos.iniciales} x="138" y="66">
        {iniciales}
      </text>
      {POSICIONES_LIBRES.map(({ x, y }) => (
        <g key={`${x}-${y}`}>
          <circle className={estilos.libre} cx={x} cy={y} r="26" />
          <text className={estilos.incognita} x={x} y={y}>
            ?
          </text>
        </g>
      ))}
      <circle className={estilos.centro} cx="220" cy="115" r="23" />
      <circle className={estilos.giro} cx="220" cy="115" r="11" />
    </svg>
  );
}

export default CanchaFormando;
