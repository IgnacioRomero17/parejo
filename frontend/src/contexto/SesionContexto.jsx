import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { obtenerUsuarioActual, pedirCsrf } from "../api/auth.js";
import { configurarReacciones } from "../api/cliente.js";
import { rutaOnboarding } from "../utilidades/rutas.js";
import { ContextoSesion } from "./contextoSesion.js";

function SesionProveedor({ children }) {
  const navigate = useNavigate();
  const [sesion, setSesion] = useState({ cargando: true, usuario: null });

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

  const valor = useMemo(
    () => ({ ...sesion, establecerUsuario }),
    [sesion, establecerUsuario],
  );

  return (
    <ContextoSesion.Provider value={valor}>{children}</ContextoSesion.Provider>
  );
}

export default SesionProveedor;
