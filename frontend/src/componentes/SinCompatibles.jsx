import { UserX } from "lucide-react";
import { textoLugaresACompletar } from "../utilidades/encuentros.js";
import Boton from "./Boton.jsx";
import estilos from "./SinCompatibles.module.css";

// Pantalla 11: estado de la 10 cuando no hay ningún candidato. Su título es el h1 de la página.
function SinCompatibles({ lugaresLibres }) {
  return (
    <section className={estilos.tarjeta}>
      <span className={estilos.icono}>
        <UserX size={28} strokeWidth={2} aria-hidden="true" />
      </span>
      <h1 className={estilos.titulo}>
        No se encontraron suficientes participantes compatibles
      </h1>
      <p className={estilos.texto}>
        Con las condiciones de este encuentro no hay jugadores suficientes para
        completar {textoLugaresACompletar(lugaresLibres)}.
      </p>
      <Boton variante="secundario" a="/inicio">
        Volver al inicio
      </Boton>
    </section>
  );
}

export default SinCompatibles;
