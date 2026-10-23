import { Navigate, Outlet } from "react-router-dom";
import { useSesion } from "../hooks/useSesion.js";
import { rutaOnboarding } from "../utilidades/rutas.js";

// Pantallas que piden el onboarding completo: si falta un paso, se va a ese paso.
// Va dentro de RutaPrivada, que ya resolvió la carga de la sesión.
function RutaConOnboarding() {
  const { usuario } = useSesion();

  if (usuario?.onboarding) {
    return <Navigate to={rutaOnboarding(usuario.onboarding)} replace />;
  }
  return <Outlet />;
}

export default RutaConOnboarding;
