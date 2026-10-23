import { CirclePlus, House, Mail, User } from "lucide-react";
import { Link, NavLink } from "react-router-dom";
import estilos from "./BarraSuperior.module.css";
import Logo from "./Logo.jsx";

// El indicador de invitaciones pendientes se suma con la HU-008.
const ENLACES = [
  { ruta: "/inicio", texto: "Inicio", icono: House },
  { ruta: "/encuentros/nuevo", texto: "Crear encuentro", icono: CirclePlus },
  { ruta: "/invitaciones", texto: "Invitaciones", icono: Mail },
  { ruta: "/perfil", texto: "Perfil", icono: User },
];

// En el onboarding (`soloLogo`) la barra muestra solo el logo, sin enlaces.
function BarraSuperior({ soloLogo = false }) {
  return (
    <header className={estilos.barra}>
      <div className={estilos.contenido}>
        {soloLogo ? (
          <Logo />
        ) : (
          <Link to="/inicio" className={estilos.logo}>
            <Logo />
          </Link>
        )}
        {!soloLogo && (
          <nav aria-label="Principal">
            <ul className={estilos.enlaces}>
              {ENLACES.map(({ ruta, texto, icono: Icono }) => (
                <li key={ruta}>
                  <NavLink
                    to={ruta}
                    className={({ isActive }) =>
                      isActive
                        ? `${estilos.enlace} ${estilos.activo}`
                        : estilos.enlace
                    }
                  >
                    <Icono size={18} strokeWidth={2} aria-hidden="true" />
                    {texto}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
        )}
      </div>
    </header>
  );
}

export default BarraSuperior;
