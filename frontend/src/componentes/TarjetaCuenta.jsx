import { LogOut } from "lucide-react";
import Boton from "./Boton.jsx";
import Tarjeta from "./Tarjeta.jsx";
import estilos from "./TarjetaCuenta.module.css";

function TarjetaCuenta({ onCerrarSesion, cerrando }) {
  return (
    <Tarjeta titulo="Cuenta">
      <div className={estilos.fila}>
        <div>
          <p className={estilos.titulo}>Cerrar sesión</p>
          <p className={estilos.texto}>
            Salís de tu cuenta en este dispositivo. Tus datos se conservan.
          </p>
        </div>
        <Boton
          variante="secundario"
          icono={LogOut}
          onClick={onCerrarSesion}
          deshabilitado={cerrando}
        >
          Cerrar sesión
        </Boton>
      </div>
    </Tarjeta>
  );
}

export default TarjetaCuenta;
