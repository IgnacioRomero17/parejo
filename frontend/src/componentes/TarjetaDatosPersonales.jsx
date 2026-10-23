import { Lock } from "lucide-react";
import Campo from "./Campo.jsx";
import Tarjeta from "./Tarjeta.jsx";
import estilos from "./TarjetaDatosPersonales.module.css";

// Sección "Datos personales" de la pantalla 17: nombre y apellido editables, correo fijo.
function TarjetaDatosPersonales({
  valores,
  errores,
  email,
  onCambiar,
  onCambiarContrasena,
}) {
  function errorDe(campo) {
    return errores?.[campo]?.join(" ");
  }

  return (
    <Tarjeta
      titulo="Datos personales"
      texto="Los datos con los que te registraste."
    >
      <div className={estilos.fila}>
        <Campo
          id="nombre"
          etiqueta="Nombre"
          valor={valores.nombre}
          onCambiar={(valor) => onCambiar("nombre", valor)}
          error={errorDe("nombre")}
          autoComplete="given-name"
          maxLength={60}
          requerido
        />
        <Campo
          id="apellido"
          etiqueta="Apellido"
          valor={valores.apellido}
          onCambiar={(valor) => onCambiar("apellido", valor)}
          error={errorDe("apellido")}
          autoComplete="family-name"
          maxLength={60}
          requerido
        />
      </div>
      <Campo
        id="email"
        etiqueta="Correo electrónico"
        tipo="email"
        valor={email}
        soloLectura
      />
      <div className={estilos.contrasena}>
        <p className={estilos.etiqueta}>Contraseña</p>
        <div className={estilos.filaContrasena}>
          <span className={estilos.puntos} aria-hidden="true">
            ••••••••
          </span>
          <button
            type="button"
            className={estilos.enlace}
            onClick={onCambiarContrasena}
          >
            <Lock size={16} strokeWidth={2} aria-hidden="true" />
            Cambiar contraseña
          </button>
        </div>
      </div>
    </Tarjeta>
  );
}

export default TarjetaDatosPersonales;
