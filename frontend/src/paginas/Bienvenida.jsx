import { CirclePlus, Scale, UserCheck } from "lucide-react";
import { Link } from "react-router-dom";
import logo from "../assets/parejo-logo.svg";
import Boton from "../componentes/Boton.jsx";
import Logo from "../componentes/Logo.jsx";
import { useTituloPagina } from "../hooks/useTituloPagina.js";
import estilos from "./Bienvenida.module.css";

const PASOS = [
  {
    numero: 1,
    icono: CirclePlus,
    titulo: "Creá tu encuentro",
    texto:
      "Definí fecha, hora, duración y ubicación del partido que querés jugar.",
  },
  {
    numero: 2,
    icono: UserCheck,
    titulo: "Invitá jugadores recomendados",
    texto:
      "El sistema sugiere jugadores compatibles por nivel, horario y preferencias.",
  },
  {
    numero: 3,
    icono: Scale,
    titulo: "Recibí parejas equilibradas",
    texto:
      "Con 4 confirmados, el sistema evalúa las combinaciones y arma las parejas.",
  },
];

function Bienvenida() {
  useTituloPagina("Bienvenida");

  return (
    <div className={estilos.pagina}>
      <header className={estilos.encabezado}>
        <Logo />
        <Link to="/ingresar" className={estilos.ingresar}>
          Iniciar sesión
        </Link>
      </header>

      <main className={estilos.contenido}>
        <section className={estilos.portada}>
          <div className={estilos.presentacion}>
            <p className={estilos.rotulo}>Pádel amateur · 2 contra 2</p>
            <h1 className={estilos.titulo}>
              Partidos parejos, con parejas equilibradas.
            </h1>
            <p className={estilos.texto}>
              Creá un encuentro, recibí recomendaciones de jugadores compatibles
              y dejá que el sistema forme las parejas.
            </p>
            <div className={estilos.acciones}>
              <Boton a="/registro">Crear cuenta</Boton>
              <Boton a="/ingresar" variante="secundario">
                Ya tengo cuenta
              </Boton>
            </div>
          </div>
          <img
            src={logo}
            alt=""
            className={estilos.ilustracion}
            width="320"
            height="320"
          />
        </section>

        <ul className={estilos.pasos}>
          {PASOS.map(({ numero, icono: Icono, titulo, texto }) => (
            <li key={numero} className={estilos.paso}>
              <span className={estilos.iconoPaso}>
                <Icono size={18} strokeWidth={2} aria-hidden="true" />
              </span>
              <h2 className={estilos.tituloPaso}>
                {numero} · {titulo}
              </h2>
              <p className={estilos.textoPaso}>{texto}</p>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}

export default Bienvenida;
