import Avatar from "./Avatar.jsx";
import estilos from "./EncabezadoPerfil.module.css";
import Etiqueta from "./Etiqueta.jsx";

// Datos guardados del jugador, arriba a la derecha de la pantalla 17.
function EncabezadoPerfil({ nombre, apellido, email, disponible }) {
  return (
    <div className={estilos.encabezado}>
      <Avatar nombre={nombre} apellido={apellido} />
      <div className={estilos.datos}>
        <p className={estilos.nombre}>
          {nombre} {apellido}
        </p>
        <p className={estilos.email}>{email}</p>
      </div>
      {disponible ? (
        <Etiqueta color="verde">Disponible</Etiqueta>
      ) : (
        <Etiqueta>No disponible</Etiqueta>
      )}
    </div>
  );
}

export default EncabezadoPerfil;
