import { Navigate, Outlet } from "react-router-dom";
import { useSesion } from "../hooks/useSesion.js";
import { rutaInicial } from "../utilidades/rutas.js";

// Solo para /, /registro e /ingresar: con sesión iniciada no tiene sentido mostrarlas.
function RutaPublica() {
  const { cargando, usuario } = useSesion();

  if (cargando) return null;
  if (usuario) return <Navigate to={rutaInicial(usuario)} replace />;
  return <Outlet />;
}

export default RutaPublica;
