import { Navigate, Outlet } from "react-router-dom";
import { useSesion } from "../hooks/useSesion.js";

// Pantallas internas: sin sesión iniciada se va al inicio de sesión.
function RutaPrivada() {
  const { cargando, usuario } = useSesion();

  if (cargando) return null;
  if (!usuario) return <Navigate to="/ingresar" replace />;
  return <Outlet />;
}

export default RutaPrivada;
