import estilos from "./ProgresoOnboarding.module.css";

// Encabezado de los pasos del onboarding: rótulo, nombre del paso y barra de progreso.
function ProgresoOnboarding({ paso, total = 2, nombre }) {
  return (
    <div className={estilos.progreso}>
      <div className={estilos.cabecera}>
        <p className={estilos.rotulo}>
          Primer ingreso · Paso {paso} de {total}
        </p>
        <p className={estilos.nombre}>{nombre}</p>
      </div>
      <div className={estilos.barra} aria-hidden="true">
        <div
          className={estilos.avance}
          style={{ width: `${(paso / total) * 100}%` }}
        />
      </div>
    </div>
  );
}

export default ProgresoOnboarding;
