import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { obtenerUsuarioActual, pedirCsrf } from "../api/auth.js";
import { configurarReacciones } from "../api/cliente.js";
import { rutaOnboarding } from "../utilidades/rutas.js";
import { ContextoSesion } from "./contextoSesion.js";

function SesionProveedor({ children }) {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const [sesion, setSesion] = useState({ cargando: true, usuario: null });
  const hayUsuario = useRef(false);

  // Antes que el efecto de abajo, que lo lee al cambiar de ruta.
  useEffect(() => {
    hayUsuario.current = sesion.usuario !== null;
  }, [sesion.usuario]);

  useEffect(() => {
    let vigente = true;
    async function cargarSesion() {
      let usuario = null;
      try {
        await pedirCsrf();
        usuario = await obtenerUsuarioActual();
      } catch {
        // Sin sesión o sin conexión: la app arranca como visitante.
        usuario = null;
      }
      if (vigente) setSesion({ cargando: false, usuario });
    }
    cargarSesion();
    return () => {
      vigente = false;
    };
  }, []);

  useEffect(() => {
    configurarReacciones({
      alNoAutenticado: () => {
        setSesion({ cargando: false, usuario: null });
        navigate("/ingresar");
      },
      alFaltarOnboarding: (paso) => navigate(rutaOnboarding(paso)),
    });
  }, [navigate]);

  const establecerUsuario = useCallback((usuario) => {
    setSesion({ cargando: false, usuario });
  }, []);

  // Vuelve a pedir `auth/yo` (por ejemplo, para el indicador de invitaciones pendientes).
  // Si falla, se queda con lo que tenía; si mientras tanto se cerró la sesión, no la revive.
  const refrescarUsuario = useCallback(async () => {
    try {
      const usuario = await obtenerUsuarioActual();
      setSesion((anterior) =>
        anterior.usuario === null ? anterior : { cargando: false, usuario },
      );
    } catch {
      // Sin conexión o sin sesión: la próxima página lo resuelve.
    }
  }, []);

  // Cada página pide sus datos al entrar; la sesión también, para que la barra esté al día.
  useEffect(() => {
    if (hayUsuario.current) refrescarUsuario();
  }, [pathname, refrescarUsuario]);

  const valor = useMemo(
    () => ({ ...sesion, establecerUsuario, refrescarUsuario }),
    [sesion, establecerUsuario, refrescarUsuario],
  );

  return (
    <ContextoSesion.Provider value={valor}>{children}</ContextoSesion.Provider>
  );
}

export default SesionProveedor;
