import { Navigate, Outlet } from "react-router-dom";
import { useSesion } from "../hooks/useSesion.js";
import { rutaOnboarding } from "../utilidades/rutas.js";

// Pantallas que piden el onboarding completo: si falta un paso, se va a ese paso.
// `permitirPaso` deja entrar aunque ese paso esté pendiente: el paso 2 del onboarding
// solo pide el paso 1 hecho. Va dentro de RutaPrivada, que ya resolvió la carga de la sesión.
function RutaConOnboarding({ permitirPaso = null }) {
  const { usuario } = useSesion();

  if (usuario?.onboarding && usuario.onboarding !== permitirPaso) {
    return <Navigate to={rutaOnboarding(usuario.onboarding)} replace />;
  }
  return <Outlet />;
}

export default RutaConOnboarding;
