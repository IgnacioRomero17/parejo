import { Info } from "lucide-react";
import { useId } from "react";
import { LUGARES_POR_ENCUENTRO } from "../utilidades/encuentros.js";
import { segunGenero } from "../utilidades/perfil.js";
import Avatar from "./Avatar.jsx";
import estilos from "./TarjetaLugares.module.css";

const LUGARES_POR_INVITAR = Array.from(
  { length: LUGARES_POR_ENCUENTRO - 1 },
  (_, posicion) => posicion + 2,
);

// Tarjeta "Lugares del encuentro" de la pantalla 09: cómo queda el encuentro al crearlo.
// Los textos sobre el jugador usan el `genero` de su perfil.
function TarjetaLugares({ nombre, apellido, genero }) {
  const idTitulo = useId();

  return (
    <aside className={estilos.tarjeta} aria-labelledby={idTitulo}>
      <h2 id={idTitulo} className={estilos.rotulo}>
        Lugares del encuentro
      </h2>
      <p className={estilos.cantidad}>
        <span className={estilos.numero}>1 de 4</span> al crear el encuentro
      </p>
      <ul className={estilos.lugares}>
        <li className={`${estilos.lugar} ${estilos.organizador}`}>
          <Avatar nombre={nombre} apellido={apellido} />
          <span className={estilos.nombre}>
            Vos · {nombre} {apellido}
          </span>
          <span className={estilos.rol}>
            {segunGenero(genero, "Organizadora", "Organizador")}
          </span>
        </li>
        {LUGARES_POR_INVITAR.map((numero) => (
          <li key={numero} className={`${estilos.lugar} ${estilos.libre}`}>
            Lugar {numero} · por invitar
          </li>
        ))}
      </ul>
      <p className={estilos.nota}>
        <Info
          size={18}
          strokeWidth={2}
          aria-hidden="true"
          className={estilos.icono}
        />
        Al crear el encuentro quedás{" "}
        {segunGenero(genero, "registrada", "registrado")} como participante 1.
        Faltan 3 lugares, que se completan con invitaciones.
      </p>
    </aside>
  );
}

export default TarjetaLugares;
