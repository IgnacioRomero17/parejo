import BarraCambios from "./BarraCambios.jsx";
import CamposPerfilDeportivo from "./CamposPerfilDeportivo.jsx";
import ErrorFormulario from "./ErrorFormulario.jsx";
import estilos from "./FormularioPerfil.module.css";
import Tarjeta from "./Tarjeta.jsx";
import TarjetaCuenta from "./TarjetaCuenta.jsx";
import TarjetaDatosPersonales from "./TarjetaDatosPersonales.jsx";
import TarjetaDisponibilidad from "./TarjetaDisponibilidad.jsx";

// Secciones de la pantalla 17 con un solo guardado. `valores` y `errores` van agrupados por
// sección; `onCambiar(seccion)` devuelve el callback `(campo, valor)` de esa sección.
function FormularioPerfil({
  valores,
  errores,
  errorGeneral,
  email,
  localidades,
  hayCambios,
  enviando,
  onCambiar,
  onGuardar,
  onDescartar,
  onCambiarContrasena,
  onCerrarSesion,
}) {
  return (
    <form className={estilos.formulario} onSubmit={onGuardar} noValidate>
      {errorGeneral && <ErrorFormulario>{errorGeneral}</ErrorFormulario>}
      <div className={estilos.columnas}>
        <div className={estilos.columna}>
          <TarjetaDatosPersonales
            valores={valores.datos_personales}
            errores={errores.datos_personales}
            email={email}
            onCambiar={onCambiar("datos_personales")}
            onCambiarContrasena={onCambiarContrasena}
          />
          <Tarjeta
            titulo="Perfil deportivo"
            texto="Tu nivel y tu localidad se usan para calcular la compatibilidad; tu lado preferido, para el equilibrio entre parejas."
          >
            <CamposPerfilDeportivo
              valores={valores.perfil_deportivo}
              errores={errores.perfil_deportivo}
              localidades={localidades}
              onCambiar={onCambiar("perfil_deportivo")}
            />
          </Tarjeta>
        </div>
        <div className={estilos.columna}>
          <TarjetaDisponibilidad
            valores={valores.disponibilidad}
            errores={errores.disponibilidad}
            onCambiar={onCambiar("disponibilidad")}
          />
          <TarjetaCuenta onCerrarSesion={onCerrarSesion} />
        </div>
      </div>
      {hayCambios && (
        <BarraCambios enviando={enviando} onDescartar={onDescartar} />
      )}
    </form>
  );
}

export default FormularioPerfil;
