import { Mail } from "lucide-react";
import Boton from "./Boton.jsx";
import estilos from "./SinInvitaciones.module.css";

// Estado vacío de la bandeja (pantalla 13) cuando no hay ninguna invitación, con el mismo
// estilo que el del panel principal. El texto depende de si el jugador está disponible.
function SinInvitaciones({ disponible }) {
  return (
    <div className={estilos.tarjeta}>
      <span className={estilos.icono}>
        <Mail size={28} strokeWidth={2} aria-hidden="true" />
      </span>
      <h2 className={estilos.titulo}>Todavía no recibiste invitaciones</h2>
      {disponible ? (
        <p className={estilos.texto}>
          Estás disponible para recibir invitaciones. Cuando te inviten a un
          encuentro, van a aparecer acá.
        </p>
      ) : (
        <>
          <p className={estilos.texto}>
            Para recibirlas, activá «Disponible para recibir invitaciones» en tu
            perfil.
          </p>
          <Boton a="/perfil">Ir a mi perfil</Boton>
        </>
      )}
    </div>
  );
}

export default SinInvitaciones;
