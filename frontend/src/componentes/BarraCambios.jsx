import Boton from "./Boton.jsx";
import estilos from "./BarraCambios.module.css";

// Barra inferior de la pantalla 17. Va dentro del formulario: "Guardar cambios" lo envía.
function BarraCambios({ enviando, onDescartar }) {
  return (
    <div className={estilos.barra}>
      <p className={estilos.texto}>
        <span className={estilos.punto} aria-hidden="true" />
        Tenés cambios sin guardar
      </p>
      <div className={estilos.acciones}>
        <Boton
          variante="sobreOscuro"
          onClick={onDescartar}
          deshabilitado={enviando}
        >
          Descartar
        </Boton>
        <Boton tipo="submit" deshabilitado={enviando}>
          Guardar cambios
        </Boton>
      </div>
    </div>
  );
}

export default BarraCambios;
