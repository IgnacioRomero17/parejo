import { useCallback, useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

// Aviso de confirmación que llega al navegar (`navigate(ruta, { state: { aviso } })`).
// Devuelve el mensaje y la función para cerrarlo.
export function useAvisoRecibido() {
  const { pathname, state } = useLocation();
  const navigate = useNavigate();
  const [aviso, setAviso] = useState(state?.aviso ?? "");
  const cerrarAviso = useCallback(() => setAviso(""), []);

  // El aviso se muestra una sola vez: si quedara en el historial, volvería al recargar.
  useEffect(() => {
    if (state?.aviso) navigate(pathname, { replace: true, state: null });
  }, [state, pathname, navigate]);

  return { aviso, cerrarAviso };
}
